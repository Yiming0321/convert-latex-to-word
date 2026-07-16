#!/usr/bin/env python3
"""Inventory a multi-file LaTeX project without executing project code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {".git", ".svn", "build", "_build", "out", "output", "node_modules"}
VERBATIM_ENVS = ("verbatim", "Verbatim", "lstlisting", "minted", "comment")
INCLUDE_COMMANDS = {"input": 1, "include": 1, "subfile": 1, "import": 2, "subimport": 2}
MATH_ENVS = {
    "equation", "equation*", "align", "align*", "alignat", "alignat*",
    "gather", "gather*", "multline", "multline*", "flalign", "flalign*",
    "split", "cases", "subequations",
}
NUMBERED_MATH_ENVS = {"equation", "align", "alignat", "gather", "multline", "flalign"}


@dataclass(frozen=True)
class CommandCall:
    name: str
    args: tuple[str, ...]
    start: int
    end: int


def read_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    encodings = ("utf-8-sig", "utf-8", "gb18030", "latin-1") if raw.startswith(b"\xef\xbb\xbf") else ("utf-8", "gb18030", "latin-1")
    for encoding in encodings:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError("unknown", raw, 0, 1, f"cannot decode {path}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mask_comments_and_verbatim(text: str) -> str:
    """Mask comments and verbatim bodies while retaining offsets and newlines."""
    chars = list(text)
    i = 0
    while i < len(chars):
        backslashes = 0
        k = i - 1
        while k >= 0 and chars[k] == "\\":
            backslashes += 1
            k -= 1
        if chars[i] == "%" and backslashes % 2 == 0:
            j = i
            while j < len(chars) and chars[j] not in "\r\n":
                chars[j] = " "
                j += 1
            i = j
            continue
        i += 1
    masked = "".join(chars)
    for env in VERBATIM_ENVS:
        pattern = re.compile(
            rf"\\begin\s*\{{{re.escape(env)}\}}.*?\\end\s*\{{{re.escape(env)}\}}",
            re.DOTALL,
        )
        for match in pattern.finditer(masked):
            segment = masked[match.start():match.end()]
            replacement = "".join("\n" if c == "\n" else "\r" if c == "\r" else " " for c in segment)
            masked = masked[:match.start()] + replacement + masked[match.end():]
    return masked


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def _balanced(text: str, i: int, opening: str, closing: str) -> tuple[str, int] | None:
    if i >= len(text) or text[i] != opening:
        return None
    depth = 1
    j = i + 1
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == opening:
            depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return None


def find_calls(text: str, specs: dict[str, int]) -> list[CommandCall]:
    """Find TeX commands with balanced required arguments; optional args are skipped."""
    masked = mask_comments_and_verbatim(text)
    calls: list[CommandCall] = []
    i = 0
    while i < len(masked):
        if masked[i] != "\\":
            i += 1
            continue
        match = re.match(r"\\([A-Za-z@]+)", masked[i:])
        if not match:
            i += 2
            continue
        name = match.group(1)
        if name not in specs:
            i += len(match.group(0))
            continue
        j = i + len(match.group(0))
        if j < len(masked) and masked[j] == "*":
            j += 1
        j = _skip_ws(masked, j)
        while j < len(masked) and masked[j] == "[":
            optional = _balanced(masked, j, "[", "]")
            if not optional:
                break
            _, j = optional
            j = _skip_ws(masked, j)
        args: list[str] = []
        ok = True
        for _ in range(specs[name]):
            parsed = _balanced(masked, j, "{", "}")
            if not parsed:
                ok = False
                break
            value, j = parsed
            args.append(text[j - len(value) - 1:j - 1])
            j = _skip_ws(masked, j)
        if ok:
            calls.append(CommandCall(name, tuple(args), i, j))
            i = j
        else:
            i += len(match.group(0))
    return calls


def tex_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.tex")
        if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)
    )


def main_candidates(root: Path) -> list[dict]:
    candidates = []
    for path in tex_files(root):
        text, encoding = read_text(path)
        masked = mask_comments_and_verbatim(text)
        if not (re.search(r"\\documentclass(?:\[[^]]*\])?\s*\{", masked)
                and re.search(r"\\begin\s*\{document\}", masked)):
            continue
        rel = path.relative_to(root)
        score = 0
        reasons = []
        if len(rel.parts) == 1:
            score += 20
            reasons.append("top-level")
        if re.search(r"main|thesis|dissertation|book|论文|学位", path.stem, re.I):
            score += 20
            reasons.append("main-like name")
        includes = find_calls(text, INCLUDE_COMMANDS)
        score += min(len(includes), 30)
        if includes:
            reasons.append(f"{len(includes)} includes")
        if path.with_suffix(".pdf").exists():
            score += 15
            reasons.append("same-stem PDF")
        candidates.append({
            "path": rel.as_posix(), "score": score, "reasons": reasons, "encoding": encoding,
        })
    return sorted(candidates, key=lambda x: (-x["score"], x["path"]))


def resolve_tex_path(root: Path, current: Path, token: str, import_dir: str | None = None) -> Path | None:
    token = token.strip()
    if not token or "\\" in token or "#" in token:
        return None
    base = current.parent
    if import_dir:
        base = (base / import_dir).resolve()
    raw = Path(token)
    options = [base / raw, root / raw]
    if not raw.suffix:
        options += [p.with_suffix(".tex") for p in list(options)]
    root_resolved = root.resolve()
    for option in options:
        try:
            resolved = option.resolve()
            resolved.relative_to(root_resolved)
        except (OSError, ValueError):
            continue
        if resolved.is_file():
            return resolved
    return None


def walk_includes(root: Path, main: Path) -> tuple[list[Path], list[dict], list[tuple[Path, Path]]]:
    ordered: list[Path] = []
    missing: list[dict] = []
    edges: list[tuple[Path, Path]] = []
    active: set[Path] = set()
    seen: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in active:
            missing.append({"from": path.relative_to(root).as_posix(), "token": "<cycle>", "command": "cycle"})
            return
        if path in seen:
            return
        active.add(path)
        seen.add(path)
        ordered.append(path)
        text, _ = read_text(path)
        for call in find_calls(text, INCLUDE_COMMANDS):
            if call.name in {"import", "subimport"}:
                target = resolve_tex_path(root, path, call.args[1], call.args[0])
                token = f"{call.args[0]}::{call.args[1]}"
            else:
                target = resolve_tex_path(root, path, call.args[0])
                token = call.args[0]
            if target:
                edges.append((path, target))
                visit(target)
            else:
                missing.append({
                    "from": path.relative_to(root).as_posix(), "token": token, "command": call.name,
                })
        active.remove(path)

    visit(main)
    return ordered, missing, edges


def split_csv_tokens(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def resolve_resource(
    root: Path,
    current: Path,
    token: str,
    extensions: Iterable[str],
    graphic_paths: Iterable[str] = (),
) -> Path | None:
    token = token.strip()
    if not token or "\\" in token or "#" in token:
        return None
    raw = Path(token)
    candidates = [current.parent / raw, root / raw]
    for graphic_path in graphic_paths:
        gp = Path(graphic_path.strip())
        candidates.extend([current.parent / gp / raw, root / gp / raw])
    if not raw.suffix:
        candidates += [Path(str(p) + ext) for p in list(candidates) for ext in extensions]
    root_resolved = root.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root_resolved)
        except (OSError, ValueError):
            continue
        if resolved.is_file():
            return resolved
    return None


def build_manifest(root: Path, main: Path, candidates: list[dict]) -> dict:
    files, missing_includes, edges = walk_includes(root, main)
    style_files = sorted(
        p for suffix in ("*.cls", "*.sty") for p in root.rglob(suffix)
        if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts)
    )
    packages: set[str] = set()
    classes: set[str] = set()
    figures: list[dict] = []
    bibliographies: list[dict] = []
    labels: list[str] = []
    refs: list[str] = []
    cites: list[str] = []
    macros: set[str] = set()
    encodings: dict[str, str] = {}
    counts = Counter()
    engine_hints: set[str] = set()
    input_records = []
    graphic_paths: list[str] = []

    for path in files:
        text, _ = read_text(path)
        for call in find_calls(text, {"graphicspath": 1}):
            entries = re.findall(r"\{([^{}]+)\}", call.args[0])
            graphic_paths.extend(entries or [call.args[0]])

    for path in files:
        rel = path.relative_to(root).as_posix()
        text, encoding = read_text(path)
        encodings[rel] = encoding
        masked = mask_comments_and_verbatim(text)
        begin_document = re.search(r"\\begin\s*\{document\}", masked)
        body_masked = masked[begin_document.end():] if begin_document else masked
        input_records.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})

        magic = re.findall(r"^\s*%\s*!TeX\s+program\s*=\s*([^\s]+)", text, re.I | re.M)
        engine_hints.update(x.lower() for x in magic)
        for call in find_calls(text, {"documentclass": 1, "usepackage": 1}):
            target = classes if call.name == "documentclass" else packages
            target.update(split_csv_tokens(call.args[0]))
        if packages & {"fontspec", "xeCJK", "ctex", "ctexcap"} or classes & {"ctexart", "ctexrep", "ctexbook"}:
            engine_hints.add("xelatex-or-lualatex")

        for call in find_calls(text, {"includegraphics": 1}):
            resolved = resolve_resource(
                root, path, call.args[0],
                (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps", ".tif", ".tiff"),
                graphic_paths,
            )
            figures.append({
                "from": rel, "token": call.args[0],
                "resolved": resolved.relative_to(root).as_posix() if resolved else None,
            })
        for call in find_calls(text, {"bibliography": 1, "addbibresource": 1}):
            for token in split_csv_tokens(call.args[0]):
                resolved = resolve_resource(root, path, token, (".bib",))
                bibliographies.append({
                    "from": rel, "token": token,
                    "resolved": resolved.relative_to(root).as_posix() if resolved else None,
                })
        for call in find_calls(text, {"label": 1}):
            labels.append(call.args[0].strip())
        for call in find_calls(text, {"ref": 1, "eqref": 1, "pageref": 1, "autoref": 1, "cref": 1, "Cref": 1, "subref": 1}):
            refs.extend(split_csv_tokens(call.args[0]))
        for call in find_calls(text, {
            "cite": 1, "citep": 1, "citet": 1, "citealp": 1, "citeauthor": 1,
            "parencite": 1, "textcite": 1, "autocite": 1, "supercite": 1,
        }):
            cites.extend(split_csv_tokens(call.args[0]))

        macros.update(re.findall(r"\\(?:newcommand|renewcommand|providecommand)\*?\s*\{?\\([A-Za-z@]+)", masked))
        macros.update(re.findall(r"\\(?:NewDocumentCommand|RenewDocumentCommand)\s*\{\\([A-Za-z@]+)\}", masked))
        counts["chapters"] += len(re.findall(r"\\chapter\*?\s*\{", body_masked))
        counts["sections"] += len(re.findall(r"\\section\*?\s*\{", body_masked))
        counts["subsections"] += len(re.findall(r"\\subsection\*?\s*\{", body_masked))
        counts["figures"] += len(re.findall(r"\\begin\s*\{figure\*?\}", body_masked))
        counts["tables"] += len(re.findall(r"\\begin\s*\{(?:table\*?|longtable|sidewaystable\*?)\}", body_masked))
        counts["footnotes"] += len(re.findall(r"\\footnote\s*(?:\[[^]]*\])?\s*\{", body_masked))
        counts["table_of_contents"] += len(re.findall(r"\\tableofcontents\b", body_masked))
        counts["list_of_figures"] += len(re.findall(r"\\listoffigures\b", body_masked))
        counts["list_of_tables"] += len(re.findall(r"\\listoftables\b", body_masked))
        for env in MATH_ENVS:
            counts["display_math_environments"] += len(re.findall(rf"\\begin\s*\{{{re.escape(env)}\}}", body_masked))
        for env in NUMBERED_MATH_ENVS:
            counts["numbered_equation_environments"] += len(re.findall(rf"\\begin\s*\{{{re.escape(env)}\}}", body_masked))
        counts["bilingual_headings"] += len(re.findall(r"\\Bi(?:Chapter|Section|Subsection|Subsubsection)\s*\{", body_masked))
        counts["bilingual_captions"] += len(re.findall(r"\\bicaption\s*\{", body_masked))

    for path in style_files:
        rel = path.relative_to(root).as_posix()
        text, encoding = read_text(path)
        masked = mask_comments_and_verbatim(text)
        encodings[rel] = encoding
        input_records.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})
        macros.update(re.findall(r"\\(?:newcommand|renewcommand|providecommand)\*?\s*\{?\\([A-Za-z@]+)", masked))
        macros.update(re.findall(r"\\(?:NewDocumentCommand|RenewDocumentCommand)\s*\{\\([A-Za-z@]+)\}", masked))

    label_counts = Counter(labels)
    label_set = set(labels)
    ref_set = set(refs)
    bib_entry_keys: set[str] = set()
    recorded_paths = {item["path"] for item in input_records}
    for item in bibliographies:
        if not item["resolved"]:
            continue
        bib_path = root / item["resolved"]
        bib_text, bib_encoding = read_text(bib_path)
        bib_entry_keys.update(re.findall(r"@(?:article|book|inbook|incollection|inproceedings|proceedings|phdthesis|mastersthesis|techreport|manual|misc|unpublished|online)\s*\{\s*([^,\s]+)", bib_text, re.I))
        if item["resolved"] not in recorded_paths:
            encodings[item["resolved"]] = bib_encoding
            input_records.append({"path": item["resolved"], "sha256": sha256(bib_path), "size": bib_path.stat().st_size})
            recorded_paths.add(item["resolved"])
    manifest = {
        "project_root": str(root),
        "main": main.relative_to(root).as_posix(),
        "main_candidates": candidates,
        "engine_hints": sorted(engine_hints),
        "classes": sorted(classes),
        "packages": sorted(packages),
        "encodings": encodings,
        "graphic_paths": graphic_paths,
        "style_files": [p.relative_to(root).as_posix() for p in style_files],
        "input_files": input_records,
        "include_edges": [
            {"from": a.relative_to(root).as_posix(), "to": b.relative_to(root).as_posix()}
            for a, b in edges
        ],
        "missing_includes": missing_includes,
        "figures": figures,
        "missing_figures": [x for x in figures if not x["resolved"]],
        "bibliographies": bibliographies,
        "missing_bibliographies": [x for x in bibliographies if not x["resolved"]],
        "counts": dict(counts),
        "labels": sorted(label_set),
        "duplicate_labels": sorted(k for k, v in label_counts.items() if v > 1),
        "references": sorted(ref_set),
        "unresolved_reference_keys": sorted(ref_set - label_set),
        "citation_keys": sorted(set(cites)),
        "bibliography_entry_keys": sorted(bib_entry_keys),
        "unresolved_citation_keys": sorted(set(cites) - bib_entry_keys) if bib_entry_keys else [],
        "custom_macros": sorted(macros),
    }
    return manifest


def manifest_markdown(data: dict) -> str:
    c = data["counts"]
    problems = (
        len(data["missing_includes"]) + len(data["missing_figures"]) +
        len(data["missing_bibliographies"]) + len(data["duplicate_labels"]) +
        len(data["unresolved_reference_keys"]) + len(data["unresolved_citation_keys"])
    )
    lines = [
        "# LaTeX project inventory", "",
        f"- Main file: `{data['main']}`",
        f"- Reachable TeX files: {len(data['input_files'])}",
        f"- Figures referenced: {len(data['figures'])}",
        f"- Bibliography files referenced: {len(data['bibliographies'])}",
        f"- Labels / references / citations: {len(data['labels'])} / {len(data['references'])} / {len(data['citation_keys'])}",
        f"- Structural counts: {json.dumps(c, ensure_ascii=False, sort_keys=True)}",
        f"- Preflight problems: {problems}", "",
        "## Problems", "",
    ]
    groups = [
        ("Missing includes", data["missing_includes"]),
        ("Missing figures", data["missing_figures"]),
        ("Missing bibliographies", data["missing_bibliographies"]),
        ("Duplicate labels", data["duplicate_labels"]),
        ("Unresolved reference keys", data["unresolved_reference_keys"]),
        ("Unresolved citation keys", data["unresolved_citation_keys"]),
    ]
    for title, values in groups:
        lines.append(f"### {title}")
        lines.append("")
        if not values:
            lines.append("None.")
        else:
            lines.extend(f"- `{json.dumps(v, ensure_ascii=False)}`" for v in values)
        lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path, help="LaTeX project root")
    p.add_argument("--main", type=Path, help="main .tex path, relative to root or absolute")
    p.add_argument("--json", type=Path, default=Path("conversion-manifest.json"))
    p.add_argument("--markdown", type=Path, default=Path("conversion-inventory.md"))
    return p.parse_args()


def cli() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    candidates = main_candidates(root)
    if args.main:
        main = args.main if args.main.is_absolute() else root / args.main
        main = main.resolve()
        try:
            main.relative_to(root)
        except ValueError:
            print("error: --main must stay inside project root", file=sys.stderr)
            return 2
    elif not candidates:
        print("error: no main TeX candidate found", file=sys.stderr)
        return 2
    elif len(candidates) > 1 and candidates[0]["score"] == candidates[1]["score"]:
        print("error: ambiguous main file; pass --main. Candidates:", file=sys.stderr)
        for item in candidates:
            print(f"  {item['path']} (score {item['score']})", file=sys.stderr)
        return 2
    else:
        main = root / candidates[0]["path"]
    if not main.is_file():
        print(f"error: main file not found: {main}", file=sys.stderr)
        return 2
    data = build_manifest(root, main, candidates)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(manifest_markdown(data), encoding="utf-8")
    print(json.dumps({"main": data["main"], "json": str(args.json), "markdown": str(args.markdown)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
