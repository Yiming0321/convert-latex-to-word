#!/usr/bin/env python3
"""Audit DOCX structure and compare it with a LaTeX conversion manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "v": "urn:schemas-microsoft-com:vml",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
W_VAL = f"{{{NS['w']}}}val"
R_ID = f"{{{NS['r']}}}id"


def xml_root(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def paragraph_text(p: ET.Element) -> str:
    return "".join((node.text or "") for node in p.findall(".//w:t", NS))


def paragraph_style(p: ET.Element) -> str:
    style = p.find("./w:pPr/w:pStyle", NS)
    return style.get(W_VAL, "") if style is not None else ""


def relationship_targets(zf: zipfile.ZipFile) -> tuple[dict[str, str], list[str]]:
    rel_name = "word/_rels/document.xml.rels"
    if rel_name not in zf.namelist():
        return {}, ["missing word/_rels/document.xml.rels"]
    rels = xml_root(zf, rel_name)
    mapping = {}
    errors = []
    for rel in rels.findall("pr:Relationship", NS):
        rid = rel.get("Id", "")
        target = rel.get("Target", "")
        mode = rel.get("TargetMode")
        rel_type = rel.get("Type", "").lower()
        mapping[rid] = target
        if mode == "External":
            if any(kind in rel_type for kind in ("image", "oleobject", "attachedtemplate", "package")):
                errors.append(f"unsafe external relationship {rid} -> {target}")
        else:
            normalized = Path("word") / target
            parts = []
            for part in normalized.parts:
                if part == "..":
                    if parts:
                        parts.pop()
                elif part != ".":
                    parts.append(part)
            package_path = "/".join(parts)
            if package_path not in zf.namelist():
                errors.append(f"broken relationship {rid} -> {target}")
    return mapping, errors


def inspect_docx(path: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    required = {"[Content_Types].xml", "word/document.xml", "word/styles.xml"}
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            if bad:
                errors.append(f"corrupt ZIP member: {bad}")
            missing = sorted(required - set(zf.namelist()))
            errors.extend(f"missing package part: {name}" for name in missing)
            dangerous = [
                name for name in zf.namelist()
                if name.endswith("vbaProject.bin") or name.startswith("word/activeX/")
            ]
            errors.extend(f"unexpected active content: {name}" for name in dangerous)
            embedded_objects = [name for name in zf.namelist() if name.startswith("word/embeddings/") and not name.endswith("/")]
            warnings.extend(f"embedded OLE/package object requires review: {name}" for name in embedded_objects)
            if "word/document.xml" not in zf.namelist():
                return {"errors": errors, "warnings": warnings}
            doc = xml_root(zf, "word/document.xml")
            rels, rel_errors = relationship_targets(zf)
            errors.extend(rel_errors)

            paragraphs = doc.findall(".//w:p", NS)
            texts = [paragraph_text(p) for p in paragraphs]
            full_text = "\n".join(texts)
            styles = Counter(paragraph_style(p) for p in paragraphs)
            heading_counts = {
                style: count for style, count in styles.items()
                if re.fullmatch(r"Heading[1-9]|[1-9]", style, re.I)
            }
            bookmark_starts = doc.findall(".//w:bookmarkStart", NS)
            bookmark_names = [x.get(f"{{{NS['w']}}}name", "") for x in bookmark_starts]
            duplicates = sorted(k for k, v in Counter(bookmark_names).items() if k and v > 1)
            if duplicates:
                errors.append(f"duplicate bookmark names: {duplicates[:20]}")

            field_instr_parts = [(x.text or "") for x in doc.findall(".//w:instrText", NS)]
            field_instr_parts.extend(
                x.get(f"{{{NS['w']}}}instr", "") for x in doc.findall(".//w:fldSimple", NS)
            )
            field_instr = " ".join(field_instr_parts)
            begin_fields = sum(1 for x in doc.findall(".//w:fldChar", NS) if x.get(f"{{{NS['w']}}}fldCharType") == "begin")
            end_fields = sum(1 for x in doc.findall(".//w:fldChar", NS) if x.get(f"{{{NS['w']}}}fldCharType") == "end")
            if begin_fields != end_fields:
                errors.append(f"unbalanced complex fields: begin={begin_fields}, end={end_fields}")

            embed_ids = [x.get(f"{{{NS['r']}}}embed") for x in doc.findall(".//a:blip", NS)]
            embed_ids += [x.get(R_ID) for x in doc.findall(".//v:imagedata", NS)]
            missing_image_rels = sorted({rid for rid in embed_ids if rid and rid not in rels})
            if missing_image_rels:
                errors.append(f"missing image relationships: {missing_image_rels}")

            tex_patterns = {
                "raw_begin_end": r"\\(?:begin|end)\s*\{",
                "raw_refs": r"\\(?:ref|eqref|pageref|autoref|cref|Cref|cite\w*)\s*(?:\[[^]]*\])?\s*\{",
                "raw_structure": r"\\(?:chapter|section|subsection|caption|includegraphics)\*?\s*(?:\[[^]]*\])?\s*\{",
                "unresolved_markers": r"(?:\?\?|Error! Reference source not found|\[\?\])",
                "replacement_character": "\ufffd",
            }
            residuals = {name: len(re.findall(pattern, full_text)) for name, pattern in tex_patterns.items()}
            for name, count in residuals.items():
                if count:
                    errors.append(f"{name}: {count}")

            return {
                "path": str(path),
                "paragraphs": len(paragraphs),
                "heading_styles": heading_counts,
                "caption_paragraphs": sum(count for style, count in styles.items() if "caption" in style.lower()),
                "bibliography_paragraphs": sum(count for style, count in styles.items() if "bibliograph" in style.lower()),
                "tables": len(doc.findall(".//w:tbl", NS)),
                "drawings": len(doc.findall(".//w:drawing", NS)) + len(doc.findall(".//w:pict", NS)),
                "embedded_image_references": len([x for x in embed_ids if x]),
                "media_files": len([n for n in zf.namelist() if n.startswith("word/media/") and not n.endswith("/")]),
                "omml_objects": len(doc.findall(".//m:oMath", NS)),
                "footnote_references": len(doc.findall(".//w:footnoteReference", NS)),
                "hyperlinks": len(doc.findall(".//w:hyperlink", NS)),
                "internal_hyperlinks": len([
                    x for x in doc.findall(".//w:hyperlink", NS)
                    if x.get(f"{{{NS['w']}}}anchor")
                ]),
                "bookmarks": len(bookmark_starts),
                "field_codes": {
                    "TOC": len(re.findall(r"\bTOC\b", field_instr, re.I)),
                    "SEQ": len(re.findall(r"\bSEQ\b", field_instr, re.I)),
                    "REF": len(re.findall(r"\bREF\b", field_instr, re.I)),
                    "PAGEREF": len(re.findall(r"\bPAGEREF\b", field_instr, re.I)),
                    "STYLEREF": len(re.findall(r"\bSTYLEREF\b", field_instr, re.I)),
                },
                "residuals": residuals,
                "text_characters": len(full_text),
                "errors": errors,
                "warnings": warnings,
            }
    except (zipfile.BadZipFile, ET.ParseError, OSError) as exc:
        errors.append(str(exc))
        return {"path": str(path), "errors": errors, "warnings": warnings}


def compare_manifest(report: dict, manifest: dict) -> None:
    counts = manifest.get("counts", {})
    source_figures = len(manifest.get("figures", []))
    if source_figures and report.get("embedded_image_references", 0) < source_figures:
        report["errors"].append(
            f"fewer embedded image references than source includegraphics calls: "
            f"{report.get('embedded_image_references', 0)} < {source_figures}"
        )
    source_tables = counts.get("tables", 0)
    if source_tables and report.get("tables", 0) < source_tables:
        report["errors"].append(f"fewer Word tables than source table environments: {report.get('tables', 0)} < {source_tables}")
    source_footnotes = counts.get("footnotes", 0)
    if source_footnotes and report.get("footnote_references", 0) < source_footnotes:
        report["errors"].append(
            f"fewer Word footnotes than source footnotes: {report.get('footnote_references', 0)} < {source_footnotes}"
        )
    source_math = counts.get("display_math_environments", 0)
    if source_math and report.get("omml_objects", 0) < source_math:
        report["warnings"].append(
            f"fewer OMML objects than source display-math environments: {report.get('omml_objects', 0)} < {source_math}; inspect fallbacks"
        )
    source_refs = len(manifest.get("references", []))
    field_codes = report.get("field_codes", {})
    linked_refs = field_codes.get("REF", 0) + field_codes.get("PAGEREF", 0) + report.get("internal_hyperlinks", 0)
    if source_refs and linked_refs < source_refs:
        report["errors"].append(
            "fewer Word REF/PAGEREF fields or hyperlinks than distinct LaTeX reference keys: "
            f"{linked_refs} < {source_refs}"
        )
    if counts.get("table_of_contents", 0) and field_codes.get("TOC", 0) == 0:
        report["errors"].append("source requests a table of contents but no Word TOC field was found")
    expected_caption_sequences = (
        counts.get("figures", 0) + counts.get("tables", 0) +
        counts.get("numbered_equation_environments", 0)
    )
    if expected_caption_sequences and field_codes.get("SEQ", 0) < expected_caption_sequences:
        report["errors"].append(
            "fewer Word SEQ fields than source numbered figure/table/equation environments: "
            f"{field_codes.get('SEQ', 0)} < {expected_caption_sequences}"
        )
    source_citations = len(manifest.get("citation_keys", []))
    if source_citations and report.get("bibliography_paragraphs", 0) < source_citations:
        report["errors"].append(
            "fewer Bibliography-style paragraphs than distinct cited keys: "
            f"{report.get('bibliography_paragraphs', 0)} < {source_citations}"
        )


def report_markdown(data: dict) -> str:
    lines = ["# DOCX conversion audit", ""]
    for key in ("paragraphs", "tables", "drawings", "embedded_image_references", "media_files", "omml_objects", "footnote_references", "caption_paragraphs", "bibliography_paragraphs", "hyperlinks", "internal_hyperlinks", "bookmarks"):
        if key in data:
            lines.append(f"- {key}: {data[key]}")
    lines += ["", "## Errors", ""]
    lines += [f"- {x}" for x in data.get("errors", [])] or ["None."]
    lines += ["", "## Warnings", ""]
    lines += [f"- {x}" for x in data.get("warnings", [])] or ["None."]
    lines += ["", "## Field codes", "", f"`{json.dumps(data.get('field_codes', {}), ensure_ascii=False, sort_keys=True)}`", ""]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("docx", type=Path)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--json", type=Path, default=Path("docx-audit.json"))
    p.add_argument("--markdown", type=Path, default=Path("docx-audit.md"))
    return p.parse_args()


def cli() -> int:
    args = parse_args()
    report = inspect_docx(args.docx)
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        compare_manifest(report, manifest)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(report_markdown(report), encoding="utf-8")
    print(json.dumps({"errors": len(report.get("errors", [])), "warnings": len(report.get("warnings", [])), "json": str(args.json)}, ensure_ascii=False))
    return 2 if report.get("errors") else 1 if report.get("warnings") else 0


if __name__ == "__main__":
    raise SystemExit(cli())
