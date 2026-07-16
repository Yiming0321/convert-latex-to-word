---
name: convert-latex-to-word
description: Convert complete LaTeX projects into high-fidelity editable Microsoft Word DOCX files. Use for papers, reports, books, theses, and dissertations supplied as a compilation folder or archive containing a main .tex file, chapter or section files, figures, bibliography files, custom .cls/.sty macros, auxiliary compilation files, and optionally a compiled PDF or Word template. Preserve and verify document structure, Chinese and bilingual typography, equations, tables, figures, captions, citations, cross-references, footnotes, sections, headers, footers, page numbering, and Word styles through source-aware preprocessing, Pandoc, OOXML postprocessing, and mandatory render comparison.
---

# Convert LaTeX to Word

Convert from the LaTeX source for semantics and editability. Use the compiled
PDF as the visual baseline. Treat the DOCX as unfinished until it passes
structural, semantic, and page-render checks.

## Conversion contract

Use `hybrid` mode unless the user requests another mode.

| Mode | Required behavior |
| --- | --- |
| `hybrid` | Keep text, headings, ordinary tables, formulas, footnotes, captions, and fields native; render only inherently graphical or unsupported objects as SVG/EMF/high-resolution PNG. |
| `editable-first` | Keep every feasible element native even when Word pagination or local appearance differs. Do not rasterize tables or formulas without approval. |
| `visual-first` | Favor the baseline PDF and allow more object-level image fallbacks. Use whole-page images only after explicit user approval and label the result as poorly editable. |

Never promise an arbitrary TeX project will become both pixel-identical and
fully editable. TeX and Word use different pagination, float, font, CJK
spacing, equation, and field models. Report any residual differences or
non-native fallbacks precisely.

## Non-negotiable safeguards

- Preserve the original project byte-for-byte. Work in a separate directory.
- Treat source and auxiliary files as untrusted input. Do not execute a
  project `Makefile`, script, hook, or `.latexmkrc`.
- Compile with `latexmk -norc` and a fixed command. Do not enable
  `--shell-escape`; request permission if a necessary object cannot otherwise
  be reproduced.
- Reject archive entries with absolute paths, `..` traversal, escaping
  symlinks, or unreasonable expansion size before extraction.
- Keep all processing local. Do not upload unpublished content to converters.
- Do not use PDF-to-Word as the primary route or place every PDF page into a
  DOCX and call it converted.
- Do not silently delete unknown TeX, substitute fonts, invent bibliography
  metadata, flatten formulas to Unicode, or turn formulas/tables into images.
- Do not overwrite an existing output. Use a versioned filename.
- Do not claim successful high-fidelity conversion until every shipping gate
  below passes.

## 1. Resolve inputs and create a work area

Identify the project root, requested output, conversion mode, user-provided
`reference.docx`, and baseline PDF. Ask the user only when two plausible main
files remain tied, two PDFs represent different revisions, or a missing choice
would materially change editability.

Resolve the main file in this order:

1. explicit user choice;
2. `% !TeX root` metadata;
3. `.fls` and log evidence;
4. a file containing both `\documentclass` and `\begin{document}`, scored by
   include graph, same-stem PDF, and root-level location.

Create a work directory containing `source-copy/`, `baseline/`, `intermediate/`,
`rendered/`, and `reports/`. Preserve relative paths and record hashes. Copy
only; never normalize files in the original folder.

Preflight and record versions for Pandoc, `latexmk`, the candidate TeX engines,
BibTeX/Biber, Python, LibreOffice, and Poppler. Use the approved/bundled runtime
when available. Do not fetch or execute an arbitrary converter binary to fill a
missing dependency; report or request the dependency instead.

Locate this skill directory and set `SKILL_DIR` to it. Run the bundled inventory
tool from the work directory:

```bash
python3 "$SKILL_DIR/scripts/inventory_project.py" source-copy \
  --main path/to/main.tex \
  --json reports/conversion-manifest.json \
  --markdown reports/conversion-inventory.md
```

Review the generated candidates, include graph, file encodings, packages,
custom macros, figure and bibliography paths, duplicate labels, and unresolved
references. Resolve every missing content dependency before conversion.

## 2. Establish the LaTeX baseline

Read, but do not execute, engine hints from magic comments, logs, the class,
font packages, and build configuration. Prefer XeLaTeX or LuaLaTeX for CTEX,
`fontspec`, or `xeCJK`; otherwise preserve the source engine.

Compile the copied main file with a controlled equivalent of:

```bash
latexmk -norc -xelatex -recorder \
  -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

Replace `-xelatex` only when the evidence calls for another engine. Use an
isolated output directory when supported. Record tool versions and the exact
command. Inspect `.log`, `.fls`, `.aux`, `.toc`, `.lof`, `.lot`, `.bbl`, and
`.bcf` rather than relying only on terminal status.

Block high-fidelity delivery when the baseline has compilation errors, missing
glyphs or files, unresolved citations/references, duplicate labels that affect
numbering, or visible `??`. If compilation is impossible but an existing PDF
clearly matches the source, continue with that PDF as a declared visual proxy;
otherwise ask which revision is authoritative.

Compare a newly compiled PDF with the supplied PDF using page metadata, text,
headings, captions, and representative figures. A binary difference alone is
not a mismatch; a content or numbering difference is.

## 3. Build the conversion map

Use the manifest plus `.aux/.toc/.lof/.lot/.bbl` to record:

- title/front matter, chapter/section hierarchy, abstracts, acknowledgements,
  appendices, and intentional blank pages;
- every figure, subfigure, table, equation, caption, note, footnote, and label;
- label → displayed number → reference relationships;
- citation keys, displayed citations, bibliography entries, order, and style;
- page geometry, font families and sizes, paragraph rhythm, section breaks,
  page-number regimes, headers, and footers;
- every custom command/environment, classified as structure, bilingual
  structure, inline semantic content, math, reference, formatting wrapper,
  graphic, or unresolved.

Read [conversion-recipes.md](references/conversion-recipes.md) when the project
contains CTEX, bilingual macros, complex tables, special math, custom
bibliographies, landscape material, or nontrivial front matter. Use
[open-source-tooling.md](references/open-source-tooling.md) to choose or verify
tooling and fallbacks.

Do not parse nested TeX arguments with one regular expression. Inspect macro
definitions in `.tex`, `.cls`, and `.sty`; use balanced parsing, a Pandoc Lua
filter, or a TeX-aware expander. Preserve the text argument of an unknown
formatting wrapper even when its styling cannot be mapped.

## 4. Flatten and normalize the working source

Prefer an installed, reviewed `latexpand` for conventional `\input` and
`\include` projects. Otherwise use the bundled conservative expander:

```bash
python3 "$SKILL_DIR/scripts/flatten_tex_project.py" \
  source-copy path/to/main.tex \
  --output intermediate/flattened.tex \
  --report reports/flatten-report.json
```

Treat any expander warning as unresolved. Verify include order, cycles,
`\includeonly`, `\subfile`, `\import`, and image paths. Add every source and
figure directory to Pandoc's resource path. If duplicate figure basenames make
search ambiguous, rewrite those paths explicitly in the working copy and log
the mapping.

Normalize custom structural macros to standard semantic elements. Examples:

- map bilingual chapter/section macros according to the actual `.toc` and PDF;
- map bilingual captions to one numbering source plus two caption styles;
- unwrap content-preserving style macros;
- keep math as TeX math while expanding project-defined math aliases;
- replace TikZ/PGFPlots and similar graphics with separately rendered assets;
- leave a unique marker for each label, citation, and cross-reference that
  requires OOXML field creation later.

Preserve the page boundaries implied by `\include`, but collapse adjacent
`\clearpage` markers only after confirming that doing so does not remove an
intentional blank page or an odd-page chapter start.

Create a Pandoc JSON AST before DOCX generation:

```bash
pandoc intermediate/flattened.tex \
  --from=latex+latex_macros+raw_tex \
  --to=json \
  --resource-path="source-copy:source-copy/figures:source-copy/chapters" \
  --output=intermediate/source-ast.json
```

Inspect every `RawInline` and `RawBlock`. Map content-bearing raw TeX or render
the specific graphical object. Remove only verified formatting-only raw nodes
and list them in the report. Re-run the AST inspection until no unaccounted
content-bearing raw TeX remains.

Use project-specific Lua filters in the work directory for repeatable AST
changes. Do not add one-off rules to the installed skill unless the rule
generalizes across projects.

## 5. Build the Word style reference

Use a user-supplied Word template when it is authoritative. Validate its style
IDs and section properties first. For a new reference file, start from Pandoc's
default as its manual recommends:

```bash
pandoc --output=intermediate/reference.docx \
  --print-default-data-file reference.docx
```

Modify styles and OOXML, not sample body text. Derive values from the class,
school specification, and baseline PDF. Define at least:

- Normal/body, first paragraph, title, subtitle, and Heading 1–4;
- Chinese and English heading variants when the source needs them;
- Chinese/English abstract, figure caption, table caption, table note,
  equation, bibliography, footnote, and TOC styles;
- page size, margins, gutter, default tabs, line spacing, paragraph spacing,
  first-line indent, keep rules, and widow/orphan behavior;
- separate ASCII/HAnsi/East Asian fonts and language settings;
- header/footer and section defaults.

Set values explicitly. Do not depend on Word defaults, automatic table widths,
or renderer font substitution. A missing local font may prevent accurate visual
QA even if its intended name is stored correctly in the DOCX; report that case.

## 6. Convert semantic content

Choose exactly one bibliography route:

- use `--citeproc`, all source `.bib` files, and a verified CSL that matches the
  PDF; or
- preserve the final `.bbl` as frozen visible citations and bibliography when
  the `.bst`/biblatex/GB/T style has no verified CSL equivalent.

Do not assume `.bst` and similarly named CSL files are equivalent. Do not claim
the result contains Word Citation Manager, EndNote, Zotero, or Mendeley fields
unless those fields were deliberately created and tested.

Run Pandoc from normalized AST or normalized TeX. A representative command is:

```bash
pandoc intermediate/normalized.json \
  --from=json \
  --to=docx+native_numbering \
  --standalone \
  --top-level-division=chapter \
  --number-sections \
  --toc --toc-depth=3 \
  --resource-path="source-copy:source-copy/figures:intermediate" \
  --reference-doc=intermediate/reference.docx \
  --output=intermediate/stage.docx
```

Add the verified citeproc options or normalized filters as required. Disable
`--number-sections` if normalized headings already contain authoritative
numbers. Record all versions and arguments. Treat `stage.docx` as an
intermediate, never as the deliverable.

Pandoc writes supported TeX math as editable OMML in DOCX. Verify matrices,
cases, aligned equations, special macros, numbered rows, and chemical equations.
Do not use `pandoc-crossref` directly on raw LaTeX; it targets Markdown-oriented
input and has tight Pandoc-version coupling.

## 7. Apply deterministic DOCX/OOXML repairs

Use `python-docx` for styles, paragraphs, ordinary tables, images, and basic
sections. Use `lxml`, Open XML SDK, or the available documents skill helpers for
features the high-level library does not preserve. Never use regular
expressions to edit XML.

Apply and verify:

- real Word styles and multilevel heading numbering;
- native OMML without rewriting its containing runs destructively;
- `SEQ`, `REF`, `PAGEREF`, and `STYLEREF` fields plus stable unique bookmarks;
- one Figure/Table number for bilingual captions;
- TOC, list-of-figures, and list-of-tables fields;
- Roman front-matter and Arabic main-matter page-number sections;
- first/even/default headers and footers, odd-page chapter starts, landscape
  sections, and restoration to portrait;
- exact table grid/widths in DXA, merged cells, repeat headings, cell margins,
  borders, alignment, and safe row splitting;
- equation number alignment, footnotes/endnotes, image crop and physical size,
  alt text, and local embedded media;
- `w:updateFields` plus cached visible field results for headless preview.

Use the available documents skill's caption, cross-reference, table-geometry,
field, section, and rendering helpers when their behavior matches the source.
Patch by semantic label or stable marker, not by fragile paragraph index.

After every repair, test ZIP integrity, parse all XML, validate relationships
and content types, check bookmark uniqueness and field pairing, and ensure no
external template/image relationship or unintended macro/OLE/ActiveX object was
introduced.

## 8. Run structural and semantic QA

Run the bundled audit:

```bash
python3 "$SKILL_DIR/scripts/audit_docx.py" intermediate/final-candidate.docx \
  --manifest reports/conversion-manifest.json \
  --json reports/docx-audit.json \
  --markdown reports/docx-audit.md
```

Treat errors as blocking. Investigate warnings rather than dismissing count
differences. Supplement the audit with source-specific assertions for:

- chapter/section titles and order;
- figure, subfigure, table, equation, footnote, citation, and bibliography
  counts and displayed numbers;
- label → bookmark and reference → field coverage;
- media order, caption text, table cell text, and bibliography order;
- no `??`, `[?]`, broken-reference messages, replacement characters, raw
  `\begin`, `\ref`, `\cite`, or missing-image placeholders;
- no omitted or duplicated substantive text.

Extract text from both baseline PDF and a rendered DOCX PDF. Normalize Unicode,
whitespace, soft hyphens, and line-wrap hyphenation, then compare by chapter and
stable anchors. Do not compare only raw page text because Word reflows lines.

## 9. Render, inspect, repair, and repeat

Follow the available documents skill's render-and-verify workflow. Prefer its
`render_docx.py` with `--emit_pdf`; otherwise use isolated LibreOffice headless
conversion plus Poppler. Render every candidate after the last modification.

Compare the DOCX render with the source PDF page by page and by object. Inspect
every output page, using a contact sheet only as navigation and viewing any
detail at 100% or higher. Check:

- missing glyphs, wrong CJK/Latin fonts, equation damage, and blurry figures;
- page size, margins, gutter, paragraph rhythm, indentation, and heading scale;
- cover/front matter, section starts, blank pages, headers, footers, and page
  number formats;
- figure crop, aspect ratio, caption pairing, float order, and subfigure layout;
- table overflow, clipped text, incorrect merges, broken three-line borders,
  repeated headings, and landscape restoration;
- orphan headings/captions, widows, overlaps, unusually large gaps, and empty
  pages not justified by source semantics;
- TOC and field display after update.

Page-count equality is not a hard requirement; content loss, wrong order,
clipping, overlap, broken numbering, or unreadable math is. Fix stable rules in
the conversion map or postprocessor, rebuild from the source, re-audit, and
re-render. Do not repair only the final DOCX by unrecorded manual edits.

LibreOffice rendering is a compatibility proxy, not proof of identical
Microsoft Word rendering. When submission fidelity is critical and Word is
available, perform a final Word field update and render check. Otherwise state
that Word itself was not used for validation.

## 10. Use controlled fallbacks

Use fallback routes only for the smallest failing scope:

1. render an inherently graphical environment separately as SVG/EMF/PNG;
2. normalize a difficult fragment through Pandoc Markdown/JSON AST;
3. use make4ht/TeX4ht to HTML or ODT for package-heavy fragments or, after a
   documented decision, the whole document;
4. use LaTeXML to recover semantic HTML/MathML/XML when its package bindings are
   adequate;
5. use PDF-derived object images only when source conversion fails and the loss
   of editability is declared;
6. use whole-page reproduction only in explicit `visual-first` mode with user
   approval.

Every fallback must record the source element or label, selected route, reason,
output format/resolution, and editability impact. Re-run the same QA afterward.

## Shipping gate

Deliver the final `.docx` only when all applicable conditions hold:

- the source baseline is identified and the conversion command is reproducible;
- no substantive content is missing or duplicated;
- all citations and cross-references resolve;
- figure, table, equation, footnote, and bibliography inventories reconcile;
- bilingual headings/captions and their single numbering sources are correct;
- native elements remain editable except for explicitly logged fallbacks;
- fonts, page geometry, sections, headers, footers, and numbering are correct;
- the package opens without a repair prompt and contains no broken relationship;
- no text, table, image, or equation is clipped, overlapped, or unreadable;
- Word fields have valid cached text and are marked for update;
- the final DOCX was rendered after its last change and every page was checked.

Keep `conversion-manifest.json`, commands/tool versions, macro mappings,
fallback ledger, structural audit, and render notes in the work area. Return the
DOCX and a concise fidelity summary. Include the detailed report when the user
requests it or when any limitation remains. Never describe a result with known
exceptions as a perfect conversion.
