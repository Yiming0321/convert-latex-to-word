# Annotation and local-tool contract

The agent performs the scientific review; `scripts/review_tools.py` only inventories explicit inputs, checks a structured register, places supplied comments and exports a location-indexed report. It does not browse, call a model, execute manuscript code, detect plagiarism, check statistical validity or compile TeX. Work in an authorized private directory. Output files and extracted text may contain unpublished content.

## Dependencies and commands

Install `requirements.txt` in a virtual environment. Run from any working directory using an absolute skill path. Paths in an issue register are relative to `--root` and use forward slashes. The output path must be new; annotation output directories must not already exist.

```bash
python <skill>/scripts/review_tools.py inventory --root <project> --out <private>/inventory.json main.docx SI.docx
python <skill>/scripts/review_tools.py validate <private>/issues.json --root <project>
python <skill>/scripts/review_tools.py annotate <private>/issues.json --root <project> --out-dir <private>/annotated
python <skill>/scripts/review_tools.py report <private>/issues.json --out <private>/location-indexed-review.md
```

`inventory` records SHA-256 values and extracts supported text with paragraph/page/line identifiers. It sets roles to `other`: assign `main` and `si` after inspecting the package. Inventory extraction is **not** an audit. It excludes Word notes, textboxes, equations and visual content from its paragraph text; inspect these separately. Unknown formats are hash-inventoried, not interpreted. Maximum individual input/expanded Word archive size is 200 MiB and maximum Word ZIP entries is 10,000. Large or nonstandard inputs need a separately authorized reader; do not silently omit them.

Use `assets/issues.schema.json` as the exact contract. `assets/issues.example.json` works with the synthetic fixture files under `evals/fixtures/`. To try the local tool without a manuscript:

```bash
python scripts/review_tools.py validate assets/issues.example.json --root .
python scripts/review_tools.py annotate assets/issues.example.json --root . --out-dir /private/new-demo-folder
```

The `files` and optional `extraction` fields from an inventory can be reused in `issues.json`. Add an `issues` array after review. IDs must be unique, file hashes current and dependencies acyclic. Store stable issue IDs across revisions; re-anchor after any source change. Validation checks schema, hashes, dependency references and available source anchors, not scientific truth or review coverage.

## Required issue fields

Every issue includes `id` (e.g. `JSA-0001`), `priority` (`P0`–`P3`), `confidence` (`confirmed`, `probable`, `question`), `category`, one or more `perspective` values, `problem`, `evidence`, `impact`, `action`, `effort`, `requires_author_confirmation`, and `locations`. Optional fields are `suggested_english`, `meaning_change`, `dependencies`, and `status`.

Put external evidence/criteria identifiers in the `evidence` text and resolve them in the review's source ledger. A journal requirement needs its actual official source and access date. Do not attach a citation merely because the topic is similar. For scientific wording changes, set `meaning_change=true` and require author confirmation. Do not replace numbers until the authoritative evidence is established.

Each location has `file_id`, `quote`, and exactly one of `paragraph`, `page`, or `line`. All numbers are **1-based**. Add an optional human-readable `section` and `label`; these do not override numerical/quote checks. Cross-file discrepancies use two or more locations within the same issue.

## Word DOCX

Use the `paragraph` identifiers from the inventory: all `w:p` elements under `w:body` in XML order, including empty paragraphs and table cells, excluding textbox paragraphs. This is **not** a page number or the index in `python-docx.Document.paragraphs`. Quote an exact substring of the displayed `w:t` text within one paragraph. Matching is case-sensitive and must be unique in the specified paragraph. Equations/fields may require a nearby explanatory sentence or a rendered-PDF anchor.

The helper inserts a **native paragraph-range Word comment**, with the exact target quote printed in the comment. It does not split individual runs or create tracked changes. This avoids rewriting scientific runs, images or equations. Original ZIP parts are copied, changing only main document XML, comments XML, document relationships and content types as needed. Existing comments and nonstandard local comments-part targets are retained.

Targets intersecting tracked changes are unresolved; do not silently accept/reject the author's revisions. Headers, footnotes, endnotes, textboxes, strict-OOXML files and digitally signed packages need separate/manual handling. Comments elsewhere do not establish that these areas were reviewed. When broad paragraph comments are insufficient, use an available native Word tool or a verified rendered-PDF anchor and record that method.

## PDF

Use a physical `page` number. Text quotes must match exactly one contiguous **whole-token** sequence in PyMuPDF's sorted word extraction; whitespace between tokens may differ. Matching is case-sensitive. Quotes split across pages, ligatures, unusual reading order, complex equations or repeated occurrences may be unresolved. Inspect the actual page; never guess the first occurrence or invent coordinates.

Text comments are native highlights over the matched word rectangles. A figure/table region uses `bbox=[x0,y0,x1,y1]` in **unrotated page coordinates**, measured in PDF points, plus `verified_visual=true`. Empty/invalid/out-of-page boxes are rejected. A visual quote may be empty, but the finding must identify the inspected object and evidence in its text. `verified_visual` records the reviewing agent's assertion; the program cannot establish that the visual check occurred.

Native rectangle/highlight annotations contain the issue ID, rationale and English suggestion. Reopen and inspect them in a viewer with comments enabled. Text extraction and native annotation counts cannot replace page-image inspection. Handle signed PDFs separately; annotation can invalidate signatures. Encrypted PDFs require an authorized unlocked copy. The helper neither cracks passwords nor edits source data.

## TeX, Markdown and text

Use original 1-based `line` and an exact substring contained once on that line. The helper writes a separate copy with a comment before that line; original text bytes, BOM and newline convention are preserved. Later line numbers in the annotated copy shift, so the register always points to the immutable original.

TeX uses `%` line comments, not visible PDF annotations. Literal environments such as `verbatim`, `minted`, `lstlisting`, `comment`, `filecontents`, and custom catcode/line-ending behavior are conservatively unresolved. Unusual macros still require inspection. The helper does not compile or execute TeX. Prefer annotating a compiled PDF as well when available; record the source-to-PDF mapping separately.

Markdown uses HTML comments; they appear in source, not necessarily in the rendered reading view. Code fences, YAML frontmatter, indented code, tables and raw HTML literal blocks are conservatively unresolved. Plain text uses explicit audit-comment blocks. Use the location-indexed report to read comments without opening source.

## Exit codes and QA

- `0`: requested operation completed; for `validate`, every supplied location is resolvable. This says nothing about scientific correctness.
- `1`: invalid inputs/schema/hash, an existing output path, or another fatal error. Read the diagnostic; never call this success.
- `2`: some supplied locations are unresolved. Other comments may have been written. Read `annotations.json`, repair anchors, and rerun into a new directory.

Every annotation manifest lists each issue/location pair, status, native ID when available, output hashes, and explicit `rendering=not_run_by_helper` / `scientific_review=not_performed_by_helper`. The reviewing agent must separately verify page rendering, comment geometry, manuscript integrity, coverage and scientific findings. Do not turn these helper statuses into a readiness decision.

Recheck original hashes before and after the run. Reopen outputs; verify native comment ranges, relationship targets, issue IDs and original content. Render every annotated page and inspect visually. Headless Word rendering may hide comments, so also inspect comments XML or a native viewer. If rendering/build tools are unavailable, state that limitation. No permission to publish the reviewed documents is implied by running the tool.
