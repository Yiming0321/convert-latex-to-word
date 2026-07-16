# Open-source tooling

Use these projects as components, not as a claim that one command can preserve
an arbitrary thesis perfectly.

- [Pandoc](https://github.com/jgm/pandoc) and its
  [User's Guide](https://pandoc.org/MANUAL.html): primary LaTeX reader, Pandoc
  AST, DOCX writer, `reference.docx`, citeproc, custom styles, native Word math,
  and Lua filters.
- [Pandoc Lua filters](https://github.com/pandoc/lua-filters): maintained filter
  examples, including `mhchem` support. Pin or record the exact revision used.
- [texmath](https://github.com/jgm/texmath): Pandoc's TeX math conversion layer;
  DOCX output uses OMML.
- [latexpand](https://gitlab.com/latexpand/latexpand) and its
  [CTAN package](https://ctan.org/pkg/latexpand): established project flattening.
  Prefer it when installed; the bundled flattener is a conservative fallback.
- [Citation Style Language styles](https://github.com/citation-style-language/styles)
  and the [CSL specification](https://docs.citationstyles.org/en/stable/specification.html):
  citation formatting when a verified CSL equivalent exists.
- [make4ht](https://github.com/michal-h21/make4ht) and
  [TeX4ht](https://tug.org/tex4ht/): fallback through HTML or ODT when the Pandoc
  LaTeX reader cannot represent a package-heavy document. ODT-to-DOCX adds a
  second lossy boundary and therefore requires the same audits.
- [LaTeXML](https://github.com/brucemiller/LaTeXML): fallback for semantic HTML,
  MathML, or XML recovery. It has no DOCX writer and may need bindings for custom
  classes or packages.
- [python-docx](https://python-docx.readthedocs.io/en/latest/): high-level Word
  styles, paragraphs, tables, images, and section editing. Use direct OOXML for
  OMML, fields, bookmarks, complex numbering, and unsupported features.
- [Open XML SDK](https://github.com/dotnet/Open-XML-SDK) and Microsoft's
  [WordprocessingML overview](https://learn.microsoft.com/en-us/office/open-xml/word/overview):
  authoritative models for fields, relationships, numbering, sections, and
  package validation.
- [LibreOffice command-line parameters](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html):
  headless DOCX rendering and compatibility checks.
- [Poppler](https://poppler.freedesktop.org/): PDF page metadata, text extraction,
  and rasterization for comparison.

Do not use `pandoc-crossref` directly on raw LaTeX as the default path. Its own
[caveats](https://github.com/lierdakil/pandoc-crossref/blob/master/docs/index.md#caveats)
state that it is designed around Markdown and that LaTeX syntax is generally not
recognized; released binaries also need a matching Pandoc version. Consider it
only after the document has been normalized to Pandoc Markdown or JSON AST.
