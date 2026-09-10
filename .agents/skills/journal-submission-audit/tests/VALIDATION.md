# Validation record — version 1.0.0

Executed 2026-09-10 in a Linux container, Python 3.13.5. All inputs were explicitly synthetic. No actual unpublished manuscript, SI, experimental record or private repository content was used as a test fixture.

## Automated regression tests

Command, run from the skill directory:

```bash
python -m unittest discover -s tests -v
```

Final observed result: **27 tests passed**, zero failures or errors (2.965 seconds in the recorded run). Dependencies observed: lxml 6.1.1; jsonschema 4.26.0; PyMuPDF 1.26.7; python-docx 1.2.0; PyYAML 6.0.3. Version bounds in requirements files describe supported installation ranges to try, not a claim that every combination was tested.

Coverage includes metadata/resource links, schema and synthetic example anchors, extraction-not-review labeling, Word table/body indexing, path traversal and external symlink rejection, changed hashes, duplicate IDs, cyclic dependencies, unknown file references, non-echoing schema diagnostics, preservation of existing Word comments and alternate comment parts, unchanged non-comment ZIP members, repeated/ambiguous quotes, tracked-change targets, native PDF annotations, multiline PDF text, validated visual rectangles, invalid pages, UTF-8 BOM/CRLF preservation, Markdown code/frontmatter/table guards, TeX literal-environment guards, overwrite refusal, DTD rejection, paired cross-file report entries and CLI exit codes.

The native Word tests include text split across bold/plain runs. PDF tests preserve an existing note and confirm the source bytes remain unchanged. Invalid or ambiguous targets are expected to remain unresolved, not to be silently marked elsewhere.

## Synthetic rendering and artifact inspection

A one-page Word fixture containing a heading, mixed-format target paragraph, table, header and existing author comment was annotated with a Chinese explanation and English replacement. Both original and annotated files were rendered using LibreOffice through `render_docx.py`; both page images were visually inspected. Their rendered body-page images were pixel-identical. The DOCX comments XML was separately checked: both the original author comment and new Chinese/English audit comment were present, with appropriate native anchors and relationships covered by the tests.

A one-page PDF fixture with one existing note received a whole-sentence highlight and a visually verified rectangle annotation. Before/after rendered pages were inspected: text highlight and rectangle aligned with the intended targets, and the existing note remained. Native annotation objects contained all three comments, including the Chinese audit text. Original file hashes were checked during processing.

These checks validate the tested mechanical cases. Headless Word page rendering does not show the comments sidebar. Microsoft Word desktop interaction, every PDF viewer, arbitrary third-party DOCX packages, scanned PDFs, complex rotated text and all LaTeX constructs were not exhaustively tested.

## Explicitly not established

- No scientific-review accuracy, recall, novelty detection or publication-success rate has been measured.
- The model-level scenarios in `evals/evals.json` are **designed, not run**; no with-skill versus without-skill benchmark is claimed.
- No full real-manuscript audit or live target-journal compliance review was performed during skill construction.
- The helper does not compile LaTeX, create tracked changes, repair research figures or replace author judgment.

During actual use, revalidate input versions, inspect every annotated file, disclose unresolved locations and rerun all applicable scientific and presentation checks.
