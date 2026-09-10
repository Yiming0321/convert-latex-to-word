#!/usr/bin/env python3
"""Local-only inventory, anchor validation, native comments and review export.

This program writes human/agent-authored findings; it does not perform peer review.
Original files are never overwritten. See references/annotation-contract.md.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import math
import posixpath
import re
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from lxml import etree as E

BASE = Path(__file__).resolve().parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/package/2006/relationships'
C = 'http://schemas.openxmlformats.org/package/2006/content-types'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments'
CTYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'
NS = {'w': W}
TEXT = {'.txt', '.md', '.markdown', '.tex'}
MAX_BYTES = 200 * 1024 * 1024


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def source(root: Path, name: str) -> Path:
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('Input paths must be relative, forward-slash paths within --root.')
    result = (root / p).resolve()
    if not result.is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError(f'Input is missing or outside --root: {name}')
    if result.stat().st_size > MAX_BYTES:
        raise ValueError(f'Input exceeds the 200 MiB safety limit: {name}')
    return result


def save(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as out:
        out.write(data)


def save_json(path: Path, data: Any) -> None:
    save(path, (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode())


def xml(data: bytes) -> E._Element:
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('DTD/entity declarations are not supported.')
    return E.fromstring(data, parser=E.XMLParser(resolve_entities=False, no_network=True))


def serial(node: E._Element) -> bytes:
    return E.tostring(node, xml_declaration=True, encoding='UTF-8', standalone=True)


def package(path: Path) -> tuple[list, dict[str, bytes], E._Element]:
    with zipfile.ZipFile(path) as z:
        info = z.infolist()
        if len(info) > 10000 or sum(i.file_size for i in info) > MAX_BYTES:
            raise ValueError('DOCX archive exceeds entry or expanded-size limit.')
        if len({i.filename for i in info}) != len(info):
            raise ValueError('Duplicate ZIP member names are not supported.')
        parts = {i.filename: z.read(i) for i in info}
    document = xml(parts['word/document.xml'])
    if document.find(f'{{{W}}}body') is None:
        raise ValueError('Only transitional WordprocessingML DOCX is supported.')
    return info, parts, document


def paragraphs(document: E._Element) -> list:
    return document.xpath('./w:body//w:p[not(ancestor::w:txbxContent)]', namespaces=NS)


def ptext(p: E._Element) -> str:
    return ''.join(p.xpath('.//w:t[not(ancestor::w:txbxContent)]/text()', namespaces=NS))


def exact(text: str, quote: str) -> None:
    if not quote.strip() or text.count(quote) != 1:
        raise ValueError('Exact quote is absent or repeated at the specified location.')


def word_anchor(document: E._Element, loc: dict) -> E._Element:
    n = loc.get('paragraph', 0)
    ps = paragraphs(document)
    if not 1 <= n <= len(ps):
        raise ValueError('A valid 1-based body paragraph is required for DOCX.')
    p = ps[n - 1]
    exact(ptext(p), loc.get('quote', ''))
    if p.xpath('.//w:ins | .//w:del | .//w:moveFrom | .//w:moveTo | '
               'ancestor::w:ins | ancestor::w:del', namespaces=NS):
        raise ValueError('Target intersects tracked changes; inspect and annotate manually.')
    return p


def blocked_lines(lines: list[str], suffix: str) -> set[int]:
    """Conservatively avoid literal/code regions rather than changing their meaning."""
    blocked: set[int] = set()
    text = ''.join(lines)
    if suffix == '.tex':
        if re.search(r'\\(?:catcode|obeylines|endlinechar)\b', text):
            return set(range(1, len(lines) + 1))
        active = False
        for n, line in enumerate(lines, 1):
            if re.search(r'\\begin\{(?:verbatim\*?|Verbatim|lstlisting|minted|comment|filecontents\*?)\}', line):
                active = True
            if active:
                blocked.add(n)
            if re.search(r'\\end\{(?:verbatim\*?|Verbatim|lstlisting|minted|comment|filecontents\*?)\}', line):
                active = False
    elif suffix in {'.md', '.markdown'}:
        fence = None
        front = bool(lines and lines[0].strip() == '---')
        for n, line in enumerate(lines, 1):
            m = re.match(r'^\s*(`{3,}|~{3,})', line)
            if fence or front or m or '|' in line or line.startswith(('    ', '\t')):
                blocked.add(n)
            if front:
                if n > 1 and line.strip() in {'---', '...'}:
                    front = False
            elif m:
                token = m.group(1)
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
        if re.search(r'<(?:pre|script|style|textarea)\b', text, re.I):
            return set(range(1, len(lines) + 1))
    return blocked


def text_anchor(lines: list[str], suffix: str, loc: dict) -> int:
    n = loc.get('line', 0)
    if not 1 <= n <= len(lines):
        raise ValueError('A valid 1-based original source line is required.')
    exact(lines[n - 1], loc.get('quote', ''))
    if n in blocked_lines(lines, suffix):
        raise ValueError('Literal/code/frontmatter/table region: use the sidecar review.')
    return n


def fitz_module():
    try:
        import pymupdf
    except ImportError as exc:
        raise ValueError('PDF support requires PyMuPDF; see requirements.txt.') from exc
    return pymupdf


def pdf_anchor(doc: Any, loc: dict) -> tuple[Any, list]:
    fitz = fitz_module()
    n = loc.get('page', 0)
    if not 1 <= n <= len(doc):
        raise ValueError('A valid 1-based physical PDF page is required.')
    page = doc[n - 1]
    if 'bbox' in loc:
        box = loc['bbox']
        if not loc.get('verified_visual') or not all(math.isfinite(x) for x in box):
            raise ValueError('Figure rectangles require a documented visual check.')
        rect = fitz.Rect(box)
        bounds = fitz.Rect(0, 0, page.cropbox.width, page.cropbox.height)
        if rect.is_empty or rect.is_infinite or not bounds.contains(rect):
            raise ValueError('Bounding box is empty or outside the unrotated page.')
        return page, [rect]
    needle = loc.get('quote', '').split()
    words = page.get_text('words', sort=True)
    tokens = [w[4] for w in words]
    hits = [i for i in range(len(tokens) - len(needle) + 1)
            if needle and tokens[i:i + len(needle)] == needle]
    if len(hits) != 1:
        raise ValueError('PDF quote must match one whole-token sequence on this page.')
    start = hits[0]
    return page, [fitz.Rect(w[:4]) for w in words[start:start + len(needle)]]


def comment(issue: dict, loc: dict) -> str:
    fields = [f"[{issue['id']} | {issue['priority']} | {issue['confidence']}]",
              f"Perspective: {', '.join(issue['perspective'])}",
              f"Original: {loc.get('quote') or '[verified visual region]'}",
              f"Problem: {issue['problem']}", f"Evidence: {issue['evidence']}",
              f"Impact: {issue['impact']}", f"Action: {issue['action']}"]
    if issue.get('suggested_english'):
        fields.append('Suggested English: ' + issue['suggested_english'])
    fields.extend([f"Effort: {issue['effort']}",
                   f"Author confirmation: {issue['requires_author_confirmation']}",
                   f"Meaning change: {issue.get('meaning_change', False)}",
                   f"Dependencies: {', '.join(issue.get('dependencies', [])) or 'none'}"])
    return '\n'.join(fields)


def load(path: Path, root: Path | None = None) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))
    schema = json.loads((BASE / 'assets/issues.schema.json').read_text(encoding='utf-8'))
    error = next(Draft202012Validator(schema).iter_errors(data), None)
    if error is not None:
        where = '.'.join(str(x) for x in error.absolute_path) or '<root>'
        raise ValueError(f'Schema violation at {where} (rule: {error.validator}).')
    file_ids = [f['id'] for f in data['files']]
    issue_ids = [i['id'] for i in data['issues']]
    if len(file_ids) != len(set(file_ids)) or len(issue_ids) != len(set(issue_ids)):
        raise ValueError('File IDs and issue IDs must each be unique.')
    graph = {i['id']: i.get('dependencies', []) for i in data['issues']}
    done, visiting = set(), set()

    def visit(node: str) -> None:
        if node not in graph or node in visiting:
            raise ValueError('Unknown or cyclic issue dependency.')
        if node not in done:
            visiting.add(node)
            for child in graph[node]:
                visit(child)
            visiting.remove(node)
            done.add(node)

    for issue in data['issues']:
        visit(issue['id'])
        for loc in issue['locations']:
            if loc['file_id'] not in file_ids:
                raise ValueError('Location references an unknown file ID.')
    if root is not None:
        paths = []
        for f in data['files']:
            p = source(root, f['path'])
            paths.append(p)
            if digest(p) != f['sha256']:
                raise ValueError(f"Source hash changed: {f['id']}. Re-anchor against this version.")
        if len(paths) != len(set(paths)):
            raise ValueError('The same source file was registered more than once.')
    return data


def add_word_comments(path: Path, rows: list, output: Path | None) -> list:
    info, parts, document = package(path)
    if any(name.startswith('_xmlsignatures/') for name in parts):
        raise ValueError('Signed DOCX: annotation would invalidate signatures.')
    relpath = 'word/_rels/document.xml.rels'
    rels = xml(parts[relpath]) if relpath in parts else E.Element(f'{{{R}}}Relationships', nsmap={None: R})
    targets = [r for r in rels if r.get('Type') == REL]
    if len(targets) > 1:
        raise ValueError('Multiple comments relationships require manual inspection.')
    cp = 'word/comments.xml'
    if targets:
        target = targets[0].get('Target', '')
        cp = posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'word/' + target)
        if targets[0].get('TargetMode') == 'External' or not cp.startswith('word/') or cp not in parts:
            raise ValueError('Unsupported or missing comments part.')
    comments = xml(parts[cp]) if cp in parts else E.Element(f'{{{W}}}comments', nsmap={'w': W})
    used = [int(x) for tree in (document, comments)
            for x in tree.xpath('//@w:id', namespaces=NS) if x.isdigit()]
    number = max(used, default=-1) + 1
    results = []
    for issue, index, loc in rows:
        result = {'issue_id': issue['id'], 'location_index': index, 'file_id': loc['file_id']}
        try:
            p = word_anchor(document, loc)
            if output is not None:
                attrs = {f'{{{W}}}id': str(number)}
                start = E.Element(f'{{{W}}}commentRangeStart', attrs)
                p.insert(1 if len(p) and p[0].tag == f'{{{W}}}pPr' else 0, start)
                E.SubElement(p, f'{{{W}}}commentRangeEnd', attrs)
                run = E.SubElement(p, f'{{{W}}}r')
                E.SubElement(run, f'{{{W}}}commentReference', attrs)
                c = E.SubElement(comments, f'{{{W}}}comment', {
                    **attrs, f'{{{W}}}author': 'Submission audit',
                    f'{{{W}}}initials': 'JSA', f'{{{W}}}date': stamp()})
                for line in comment(issue, loc).splitlines():
                    t = E.SubElement(E.SubElement(E.SubElement(c, f'{{{W}}}p'), f'{{{W}}}r'), f'{{{W}}}t')
                    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                    t.text = line
                result['native_comment_id'] = str(number)
                number += 1
            result['status'] = 'annotated' if output is not None else 'resolvable'
        except ValueError as exc:
            result.update(status='unresolved', reason=str(exc))
        results.append(result)
    if output is not None:
        if not targets:
            ids = {r.get('Id') for r in rels}
            rid = 1
            while f'rId{rid}' in ids:
                rid += 1
            E.SubElement(rels, f'{{{R}}}Relationship', Id=f'rId{rid}', Type=REL, Target='comments.xml')
        types = xml(parts['[Content_Types].xml'])
        if not any(t.get('PartName') == '/' + cp for t in types):
            E.SubElement(types, f'{{{C}}}Override', PartName='/' + cp, ContentType=CTYPE)
        parts.update({'word/document.xml': serial(document), cp: serial(comments),
                      relpath: serial(rels), '[Content_Types].xml': serial(types)})
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            for item in info:
                z.writestr(item, parts.pop(item.filename))
            for name, content in parts.items():
                z.writestr(name, content)
        save(output, stream.getvalue())
    return results


def process(path: Path, rows: list, output: Path | None) -> list:
    suffix = path.suffix.lower()
    if suffix == '.docx':
        return add_word_comments(path, rows, output)
    results, insertions = [], defaultdict(list)
    doc = None
    raw, lines = b'', []
    try:
        if suffix == '.pdf':
            doc = fitz_module().open(path)
            if doc.needs_pass:
                raise ValueError('Encrypted PDF requires an authorized unlocked copy.')
            if doc.get_sigflags() > 0:
                raise ValueError('PDF signature fields require manual inspection before annotation.')
        elif suffix in TEXT:
            raw = path.read_bytes()
            lines = raw.decode('utf-8-sig').splitlines(keepends=True)
        for issue, index, loc in rows:
            result = {'issue_id': issue['id'], 'location_index': index, 'file_id': loc['file_id']}
            try:
                if suffix == '.pdf':
                    page, boxes = pdf_anchor(doc, loc)
                    if output is not None:
                        a = page.add_rect_annot(boxes[0]) if 'bbox' in loc else page.add_highlight_annot(boxes)
                        a.set_info(title='Submission audit', subject=issue['id'], content=comment(issue, loc))
                        a.update()
                        result['native_annotation_xref'] = a.xref
                elif suffix in TEXT:
                    n = text_anchor(lines, suffix, loc)
                    body = comment(issue, loc)
                    if suffix == '.tex':
                        block = '\n'.join('% ' + s for s in body.splitlines()) + '\n'
                    elif suffix in {'.md', '.markdown'}:
                        block = '<!--\n' + html.escape(body).replace('--', '\u2014') + '\n-->\n'
                    else:
                        block = '[AUDIT COMMENT]\n' + body + '\n[/AUDIT COMMENT]\n'
                    newline = '\r\n' if b'\r\n' in raw else '\n'
                    insertions[n].append(block.replace('\n', newline))
                else:
                    raise ValueError('Unsupported annotation format; retain this location in the report.')
                result['status'] = 'annotated' if output is not None else 'resolvable'
            except ValueError as exc:
                result.update(status='unresolved', reason=str(exc))
            results.append(result)
        if output is not None:
            if suffix == '.pdf':
                save(output, doc.tobytes())
            elif suffix in TEXT:
                content = ''.join(''.join(insertions[n]) + line for n, line in enumerate(lines, 1))
                save(output, (b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'') + content.encode())
    finally:
        if doc is not None:
            doc.close()
    return results


def run_annotations(data: dict, root: Path, out: Path | None) -> dict:
    if out is not None:
        out.mkdir(parents=True, exist_ok=False)
    by_file = defaultdict(list)
    for issue in data['issues']:
        for index, loc in enumerate(issue['locations']):
            by_file[loc['file_id']].append((issue, index, loc))
    results, outputs = [], []
    for f in data['files']:
        rows = by_file[f['id']]
        if not rows:
            continue
        p = source(root, f['path'])
        dest = out / (f['id'] + '__' + p.stem + '.annotated' + p.suffix) if out is not None else None
        try:
            current = process(p, rows, dest)
            results.extend(current)
            if dest is not None and dest.exists():
                outputs.append({'file_id': f['id'], 'path': dest.name, 'sha256': digest(dest)})
        except (ValueError, OSError, KeyError, E.XMLSyntaxError, zipfile.BadZipFile) as exc:
            results.extend({'issue_id': i['id'], 'location_index': n, 'file_id': f['id'],
                            'status': 'unresolved', 'reason': str(exc)} for i, n, _ in rows)
    for f in data['files']:
        if digest(source(root, f['path'])) != f['sha256']:
            raise ValueError('Input changed during processing; discard outputs and re-anchor.')
    manifest = {'created_at': stamp(), 'locations': results, 'outputs': outputs,
                'unresolved': sum(x['status'] == 'unresolved' for x in results),
                'rendering': 'not_run_by_helper', 'scientific_review': 'not_performed_by_helper'}
    if out is not None:
        save_json(out / 'annotations.json', manifest)
    return manifest


def inventory(root: Path, names: list[str]) -> dict:
    files, extraction, seen = [], {}, set()
    for n, name in enumerate(names, 1):
        p = source(root, name)
        if p in seen:
            raise ValueError('Duplicate input file.')
        seen.add(p)
        fid = f'F{n:03d}'
        files.append({'id': fid, 'path': name, 'role': 'other', 'sha256': digest(p)})
        item = {'status': 'extracted_not_reviewed', 'bytes': p.stat().st_size}
        if p.suffix.lower() == '.docx':
            _, parts, document = package(p)
            item['paragraphs'] = [{'paragraph': i, 'text': ptext(p)}
                                  for i, p in enumerate(paragraphs(document), 1)]
            item['limitations'] = 'Body paragraphs only; equations, drawings, textboxes, notes and rendering need separate inspection.'
        elif p.suffix.lower() == '.pdf':
            with fitz_module().open(p) as doc:
                if doc.needs_pass:
                    raise ValueError('Encrypted PDF requires an authorized unlocked copy.')
                item['pages'] = [{'page': i, 'text': page.get_text()} for i, page in enumerate(doc, 1)]
                item['limitations'] = 'Text extraction is not visual inspection.'
        elif p.suffix.lower() in TEXT:
            item['lines'] = [{'line': i, 'text': line} for i, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(), 1)]
        else:
            item['status'] = 'hash_only_not_read'
        extraction[fid] = item
    return {'version': '1.0', 'files': files, 'issues': [], 'extraction': extraction}


def report(data: dict) -> str:
    lines = ['# Location-indexed submission review', '',
             'Author-side working draft. See the separate scientific review and coverage manifest.', '']
    for f in data['files']:
        lines.extend([f"## {f['id']} — {f['path']}", '', f"SHA-256: `{f['sha256']}`", ''])
        for issue in sorted(data['issues'], key=lambda x: (x['priority'], x['id'])):
            for loc in issue['locations']:
                if loc['file_id'] != f['id']:
                    continue
                position = ', '.join(f'{k}={loc[k]}' for k in ('section', 'paragraph', 'page', 'line', 'bbox') if k in loc)
                lines.extend([f"### {issue['id']} — {position}", '', comment(issue, loc), ''])
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)
    inv = sub.add_parser('inventory')
    inv.add_argument('--root', type=Path, required=True)
    inv.add_argument('--out', type=Path, required=True)
    inv.add_argument('files', nargs='+')
    for command in ('validate', 'annotate', 'report'):
        p = sub.add_parser(command)
        p.add_argument('issues', type=Path)
        if command != 'report':
            p.add_argument('--root', type=Path, required=True)
        if command == 'annotate':
            p.add_argument('--out-dir', type=Path, required=True)
        if command == 'report':
            p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.cmd == 'inventory':
            save_json(args.out, inventory(args.root, args.files))
        else:
            data = load(args.issues, getattr(args, 'root', None))
            if args.cmd == 'report':
                save(args.out, report(data).encode())
            else:
                result = run_annotations(data, args.root, getattr(args, 'out_dir', None))
                print(json.dumps({'locations': len(result['locations']), 'unresolved': result['unresolved']}))
                return 2 if result['unresolved'] else 0
        return 0
    except Exception as exc:
        print(f'ERROR ({type(exc).__name__}): {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
