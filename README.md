# LaTeX Thesis to Word Skill

> 面向硕士、博士学位论文（“大论文”）设计的 Codex Skill，用于将完整的多文件 LaTeX 工程高保真转换为可编辑的 Microsoft Word 文档。

This Codex skill is designed for high-fidelity conversion of complete LaTeX thesis and dissertation projects into editable Microsoft Word documents.

## 适用对象

本技能主要面向结构复杂的学位论文工程，而非仅包含单个 `.tex` 文件的简单文档。支持处理：

- 主文件及 `chapters`、`figures`、`references` 等子目录；
- 自定义文档类、宏命令和中英文双语标题；
- 章节、目录、图目录、表目录、页眉页脚和分节页码；
- 可编辑公式、表格、图片、题注、脚注和参考文献；
- 公式、图表、章节及参考文献的编号与交叉引用；
- 已编译 PDF 与生成 DOCX 的逐页视觉核验。

## 核心思路

技能默认采用 `hybrid` 模式：优先保留 Word 原生、可编辑的内容，并对难以可靠转换的复杂对象使用受控回退方案。转换流程综合使用 LaTeX 源文件、辅助编译文件和基准 PDF：

1. 盘点工程结构、依赖、字体、宏命令、引用和资源文件；
2. 在隔离副本中安全编译并建立 PDF 视觉基准；
3. 展开多文件工程，规范化 Pandoc 难以直接处理的 LaTeX 结构；
4. 使用 Pandoc 和 `reference.docx` 生成语义化 Word 文档；
5. 通过 OOXML 修复目录、编号、交叉引用、分节、页码和样式；
6. 执行结构审计，并将 DOCX 渲染后与基准 PDF 逐页比较；
7. 只有通过内容完整性和视觉检查后才交付结果。

## 转换模式

- `hybrid`：默认模式，在可编辑性与视觉一致性之间取得平衡。
- `editable-first`：尽可能使用 Word 原生公式、表格、域和样式。
- `visual-first`：优先保持页面外观，对极难转换的对象允许使用高质量图形回退。

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── conversion-recipes.md
│   └── open-source-tooling.md
└── scripts/
    ├── inventory_project.py
    ├── flatten_tex_project.py
    └── audit_docx.py
```

其中三个辅助脚本分别用于工程盘点、多文件 LaTeX 展开和 DOCX 结构审计。

## 使用方式

安装该技能后，将完整 LaTeX 工程文件夹或压缩包提供给 Codex，并给出类似指令：

```text
使用 $convert-latex-to-word 将这个完整的博士学位论文 LaTeX 工程转换为 Word。
采用 hybrid 模式，以已编译 PDF 为版式基准，保留公式、表格、题注、
参考文献和交叉引用的可编辑性，并完成逐页核验后再交付。
```

如果学校提供官方 Word 模板，应同时提供该模板，以便生成和校准 `reference.docx`。

## 交付原则

复杂 LaTeX 与 Word 使用不同的排版模型，因此任意论文都无法同时无条件保证“像素完全相同”和“所有对象完全可编辑”。本技能采用以下可验证标准：

- 不静默遗漏正文、公式、图表、脚注、引用或交叉引用；
- 关键内容优先保持可编辑；
- 所有回退、替代和已知差异均写入转换报告；
- 未通过结构审计或视觉核验时，不把结果标记为完整转换。

## 主要开源工具

工作流可结合 Pandoc、TeX/LaTeX、LibreOffice、Poppler、python-docx、make4ht/TeX4ht 和 LaTeXML。具体用途、限制及官方链接见 [`references/open-source-tooling.md`](references/open-source-tooling.md)。

