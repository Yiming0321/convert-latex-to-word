#!/usr/bin/env python3
"""Flatten TeX include commands into one file while preserving an audit trail."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from inventory_project import INCLUDE_COMMANDS, find_calls, read_text, resolve_tex_path


def flatten(root: Path, main: Path) -> tuple[str, dict]:
    active: list[Path] = []
    used: list[str] = []
    warnings: list[dict] = []

    def expand(path: Path) -> str:
        path = path.resolve()
        rel = path.relative_to(root).as_posix()
        if path in active:
            warnings.append({"type": "cycle", "path": rel, "stack": [p.relative_to(root).as_posix() for p in active]})
            return f"\n% LATEX-TO-WORD: include cycle omitted: {rel}\n"
        active.append(path)
        used.append(rel)
        text, _ = read_text(path)
        calls = find_calls(text, INCLUDE_COMMANDS)
        replacements: list[tuple[int, int, str]] = []
        for call in calls:
            if call.name in {"import", "subimport"}:
                target = resolve_tex_path(root, path, call.args[1], call.args[0])
                token = f"{call.args[0]}::{call.args[1]}"
            else:
                target = resolve_tex_path(root, path, call.args[0])
                token = call.args[0]
            if not target:
                warnings.append({"type": "missing_include", "from": rel, "command": call.name, "token": token})
                continue
            target_rel = target.relative_to(root).as_posix()
            body = expand(target)
            page_break_before = "\\clearpage\n" if call.name == "include" else ""
            page_break_after = "\n\\clearpage" if call.name == "include" else ""
            replacement = (
                f"\n% LATEX-TO-WORD: BEGIN {target_rel}\n"
                f"{page_break_before}{body}{page_break_after}\n"
                f"% LATEX-TO-WORD: END {target_rel}\n"
            )
            replacements.append((call.start, call.end, replacement))
        for start, end, replacement in sorted(replacements, reverse=True):
            text = text[:start] + replacement + text[end:]
        active.pop()
        return text

    content = expand(main)
    report = {
        "project_root": str(root),
        "main": main.relative_to(root).as_posix(),
        "files_in_expansion_order": used,
        "warnings": warnings,
    }
    return content, report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("main", type=Path, help="main .tex, relative to root or absolute")
    p.add_argument("--output", type=Path, default=Path("flattened.tex"))
    p.add_argument("--report", type=Path, default=Path("flatten-report.json"))
    return p.parse_args()


def cli() -> int:
    args = parse_args()
    root = args.root.resolve()
    main = args.main if args.main.is_absolute() else root / args.main
    main = main.resolve()
    try:
        main.relative_to(root)
    except ValueError:
        print("error: main file must stay inside project root", file=sys.stderr)
        return 2
    if not main.is_file():
        print(f"error: main file not found: {main}", file=sys.stderr)
        return 2
    content, report = flatten(root, main)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "report": str(args.report), "warnings": len(report["warnings"])}, ensure_ascii=False))
    return 1 if report["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(cli())
