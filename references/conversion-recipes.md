# Conversion recipes

## Contents

1. Chinese theses and fonts
2. Custom and bilingual macros
3. Figures and graphics
4. Tables
5. Equations and references
6. Citations and bibliographies
7. Sections, pagination, and navigation
8. Fidelity expectations

## 1. Chinese theses and fonts

Map `ctexart`, `ctexrep`, `ctexbook`, `\ctexset`, `\zihao`, `\songti`,
`\heiti`, `\kaishu`, `\fangsong`, `\CJKfamily`, `\setCJKmainfont`,
`\newCJKfontfamily`, `\setmainfont`, and `\setsansfont` to Word paragraph or
character styles. Set OOXML `ascii`, `hAnsi`, `eastAsia`, and `cs` fonts
explicitly and set the language to `zh-CN` where appropriate.

Use explicit point sizes. Common CTEX mappings include 小四 = 12 pt and 五号 =
10.5 pt, but treat the class or school specification as authoritative. Do not
silently substitute a missing font. Record the requested font, installed font,
and any substitute. A local renderer may substitute even when the DOCX stores
the correct Word font name; distinguish those cases in the report.

Normalize the working copy to UTF-8 only after recording each source encoding.
Scan the result for the replacement character `�` and common mojibake. Word and
XeTeX do not use identical CJK punctuation compression or Latin–CJK spacing, so
evaluate these visually rather than promising pixel identity.

## 2. Custom and bilingual macros

Read macro definitions from the main file, `.cls`, and `.sty` files. Classify
each custom macro or environment as:

- structure;
- bilingual structure;
- inline semantic content;
- mathematics;
- citation or cross-reference;
- formatting wrapper whose content must survive;
- graphic-only content;
- unresolved.

Do not parse nested arguments with a single regular expression. Use balanced
argument parsing, a Pandoc Lua filter, or a TeX-aware expansion tool. Audit all
Pandoc `RawInline` and `RawBlock` nodes. Unknown raw TeX that carries content is
a blocking error.

For `\BiChapter`, `\BiSection`, and related commands, inspect the macro, `.toc`,
and baseline PDF. When both languages form one directory entry, generate one
Word heading with a controlled line break. When only Chinese belongs in the
TOC, apply a Heading style to Chinese and a non-outline bilingual subtitle
style to English. Keep both with the following paragraph.

For `\bicaption`, create only one numbering source. Put the second language in
a separate style or reuse the number through `REF`; never increment the Figure
or Table sequence twice. Follow `.lof` and `.lot` to decide which caption enters
the list of figures or tables.

## 3. Figures and graphics

Prefer native SVG for current Word, then EMF where an older Word target requires
it. Preserve PNG, JPEG, and TIFF without unnecessary resampling. Apply LaTeX
`trim`, `clip`, `viewport`, `angle`, `page`, width, and height before embedding.
Set a stable inline anchor and preserve aspect ratio.

Convert EPS and PDF figures after applying crop and page selection. Prefer SVG
or EMF; use 600 dpi PNG only when vector output is unstable. Verify fonts,
transparency, color, crop box, and physical size.

Compile TikZ, PGFPlots, PSTricks, chemfig, and similar graphics independently
with the source engine. Treat the result as a figure: it may remain visually
faithful but is not expected to be editable as Word shapes. Record the fallback.

Build ordinary subfigures as a borderless Word table containing images and
subcaptions, with the main caption outside. Preserve `(a)`, `(b)`, and subfigure
references. Render irregular overlays or overlapping panels as one vector image.

## 4. Tables

Build a rectangular cell grid first, then apply merges and formatting. Set
table width, grid columns, cell widths, and indent in DXA; do not rely on
autofit. Never use fixed row heights that can clip text.

| LaTeX feature | Word mapping |
| --- | --- |
| `booktabs` | Top, mid, bottom, and partial cell borders; no default vertical rules |
| `tabularx` `X` | Relative widths after fixed columns are allocated |
| `p/m/b{}` | Fixed width with top/middle/bottom vertical alignment |
| `multirow` | Vertical cell merge |
| `multicolumn` | Grid span and the source alignment/border override |
| `longtable` | One multi-page table with repeated heading rows |
| `threeparttable` | Native table followed by a dedicated table-note paragraph |
| `siunitx` columns | Parsed numeric text with deliberate decimal alignment |
| landscape/sideways | Separate landscape section before and after the table |

For a wide table, first optimize widths and wrapping, then use a landscape
section. Do not shrink text to unreadable sizes. Prevent page breaks inside
vertical merge regions; allow ordinary rows to expand and split when needed.

Use an object-level vector or high-resolution raster fallback only for tables
that Word cannot express reliably, such as diagonal headers, arbitrary rotation,
overdrawn cells, or highly nested grids. Obtain user approval when editability
is a stated requirement and record every such fallback.

## 5. Equations and references

Preserve supported TeX math until Pandoc converts it to native OMML. Expand
custom math macros in the working copy, but retain labels, `\notag`, `\tag`, and
`subequations` semantics. Check `aligned`, `cases`, `split`, matrices, and each
numbered row of `align` visually.

Use a centered equation paragraph with a right-aligned tab stop, or a stable
borderless layout table, for numbered equations. Generate Word `SEQ Equation`
fields and bookmarks. Map `\eqref` to parentheses plus a `REF` field; map
`\pageref` to `PAGEREF`; add the appropriate static prefix for `\autoref` and
`\cref`. Validate label targets against `.aux`.

Only render an unsupported equation as SVG/EMF or a high-resolution PNG after
OMML conversion fails. Record its label, source TeX, and loss of editability.
Do not silently downgrade math to Unicode text.

## 6. Citations and bibliographies

Recognize BibTeX, Biber, natbib, biblatex, chapterbib, bibunit, and refsection.
Prefer a verified CSL only when it reproduces the baseline. A `.bst` name does
not establish CSL equivalence.

For highly customized styles or GB/T 7714 variants, use the final `.bbl` as a
frozen display source when that better preserves visible order and punctuation.
Keep per-chapter bibliographies in their original locations. Compare citation
keys, displayed citations, entry count, order, DOI/URL text, and punctuation.

Pandoc citations are normally rendered text, not native Word Citation Manager,
EndNote, Zotero, or Mendeley fields. Never claim dynamic citation-manager
integration unless it was separately created and tested.

## 7. Sections, pagination, and navigation

Map `\frontmatter`, `\mainmatter`, `\backmatter`, `\pagenumbering`, and page
counter resets to Word sections with the correct number format and start value.
Use sections for cover pages, declarations, abstracts, TOC, main text,
appendices, landscape material, and any header/footer regime changes.

Map `openright` or `\cleardoublepage` to an odd-page section start. Preserve
intentional blank pages but remove duplicates caused by a page break immediately
before an odd/even section break. Map `fancyhdr`, `\pagestyle`, `\thispagestyle`,
`\markboth`, `\leftmark`, and `\rightmark` to first/even/default headers and
`STYLEREF` fields as appropriate.

Generate TOC, list-of-figures, and list-of-tables fields from Word styles and
captions. Set `w:updateFields` and preserve cached visible results. A Word-native
TOC is self-consistent with Word pagination; it need not retain LaTeX PDF page
numbers.

Convert `\footnote` to native footnotes. Pair `\footnotemark` and
`\footnotetext`. Do not misclassify table notes, minipage notes, or endnotes.

## 8. Fidelity expectations

| Content | Reasonable expectation |
| --- | --- |
| Body text, headings, lists, emphasis | High fidelity and editable |
| CTEX fonts and sizes | High style fidelity; punctuation spacing may differ |
| Ordinary figures and captions | High fidelity; float placement may move |
| Simple and medium tables | High fidelity and editable after table-specific QA |
| Long or heavily merged tables | Structured conversion with mandatory per-table QA |
| Standard mathematics | Usually native OMML |
| Special math and chemical macros | May require audited vector fallback |
| TOC, numbering, cross-references | Word-native fields after OOXML processing |
| Custom `.bst` / GB/T 7714 | Frozen `.bbl` can preserve display, not citation-manager semantics |
| Headers, front matter, page numbering | High fidelity with explicit section mapping |
| Exact float placement and pagination | Approximate; Word reflows content |
| Highly designed cover/authorization pages | Dedicated template or declared page-image fallback |
| Pixel-identical and fully editable for arbitrary TeX | Cannot be guaranteed simultaneously |
