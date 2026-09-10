# 英文期刊投稿前审核 / Journal Submission Audit

对英文论文**正文与全部 Supporting Information（SI/ESI）联合审核**，先检查技术与科学内容，再从模拟编辑及审稿人的角度评估，并把问题与英文修改建议标注在原文对应位置。默认中文解释、英文改写。

这不是仅用于语法润色的提示词，也不是独立的自动审稿模型。科学判断由调用本 skill 的 AI 与作者完成；附带 Python 工具负责清点文件、校验位置、写入批注和导出问题清单，不会自行得出科研结论，也不会自动改写数据。

## 获取与安装

GitHub 保存位置：

```text
Yiming0321/convert-latex-to-word
└── .agents/skills/journal-submission-audit/
```

本技能放在独立子目录，原有 LaTeX 转 Word 技能不变。按照已核查的 [Codex 官方文档](https://learn.chatgpt.com/docs/build-skills)，把整个 `journal-submission-audit` 文件夹复制到稿件项目的 `.agents/skills/`，或用户级 `~/.agents/skills/`。**不能只复制 SKILL.md**，因为它需要附带的检查清单、模板、schema 和脚本。项目级结构应为：

```text
manuscript-project/
├── manuscript.docx
├── Supporting_Information.docx
└── .agents/skills/journal-submission-audit/
    ├── SKILL.md
    ├── README.md
    ├── agents/openai.yaml
    ├── references/
    ├── assets/
    ├── scripts/review_tools.py
    ├── tests/
    └── evals/
```

在 Codex CLI/IDE 中可使用 `$journal-submission-audit` 调用；未出现时重新打开会话。保存到 GitHub **不等于已安装到所有 Codex/ChatGPT 客户端**，不同客户端应按其支持的安装方式使用。

需要批注脚本时，先在 Python 虚拟环境中安装依赖：

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r /path/to/journal-submission-audit/requirements.txt
```

依赖安装可能需要网络；安装后的附带工具没有网络或外部模型调用。宿主 AI 是否联网、如何处理上传文件，仍取决于实际使用的平台和授权设置。

## 调用示例

```text
$journal-submission-audit

请全面审核当前项目中准备投稿的英文论文。
目标期刊：[填写期刊名称和文章类型]
正文：manuscript.docx
SI：Supporting_Information.docx

先完整检查正文及全部 SI，再分别从编辑和审稿人角度评估。
请在正文和 SI 对应位置插入批注，中文解释问题，英文给出修改建议。
重点核对科学结论与证据、正文与 SI 一致性、可重复性、图表及期刊适配性。
每条意见标明优先级、依据、修改方式，以及是否确实需要补充实验。
只生成带批注副本，不覆盖原稿，不擅自修改数据，不上传稿件到 GitHub。
```

目标期刊未确定时仍可检查科学内容，但期刊适配与具体要求会标为待核查。缺少 SI、原始数据或源文件时，会明确未完成范围，不宣称已全面通过。

## 审核流程与交付内容

先建立文件版本和覆盖范围清单，完整阅读正文及 SI，并目视检查图表、公式和版面。随后核查题目、摘要、引言、方法、结果讨论、结论、引用与声明，建立“论断—结果—方法—SI—数据”关系，核对数值、单位、样本量、实验条件和交叉引用。

模拟编辑关注范围、贡献、叙事和送审风险；模拟审稿人分别检查领域贡献、方法统计与可重复性，以及适用的工程/应用问题。它们是不同审阅视角，不冒充真实编辑或独立的人类审稿人。最后进行英文润色、优先级排序和原位批注。

结果应包含带批注正文/SI、编辑及审稿意见、定位问题清单、正文–SI 对照表、证据矩阵、修改计划、英文修改记录，以及审核覆盖与验证状态。P0/P1 优先处理关键矛盾和证据问题，P2/P3 再处理报告、表达和格式。科学判断仍需作者核实，不给出虚构录用概率。

## 原位批注方式

| 输入 | 输出形式 | 边界 |
|---|---|---|
| Word `.docx` | 原生 Word 段落范围批注；批注内附目标原句与建议 | 不是逐字符修订；文本框、脚注等特殊位置可能需人工补注 |
| PDF | 唯一匹配文字高亮或经目视确认的图表区域框，附原生评论 | 扫描件、复杂阅读顺序或重复原句可能无法自动定位 |
| LaTeX | 独立源文件副本的对应行前插入 `%` 注释 | 源码注释不显示在 PDF；编译及编译后 PDF 检查是另一步 |
| Markdown / 文本 | 在独立副本对应行前插入说明 | 代码块等易破坏语义的位置保守列为待处理 |

正文与 SI 冲突使用同一问题编号，在两处分别批注。不会擅自选择其中一个数字覆盖另一个。原句重复、输入版本变化或位置不明确时，不猜测位置，而是生成 `unresolved` 记录。没有发现问题的文件可交付未改动副本或引用原文件，不为凑数量制造批注。

## 工具命令与验证

从 skill 文件夹运行示例；完整接口见 `references/annotation-contract.md`：

```bash
python scripts/review_tools.py inventory --root /project --out /private/run/inventory.json manuscript.docx SI.docx
# 审阅后按 assets/issues.schema.json 生成 issues.json；inventory 不会生成科学意见。
python scripts/review_tools.py validate /private/run/issues.json --root /project
python scripts/review_tools.py annotate /private/run/issues.json --root /project --out-dir /private/run/annotated
python scripts/review_tools.py report /private/run/issues.json --out /private/run/location-indexed-review.md
```

可用内置虚构文本验证定位功能，不涉及真实论文：

```bash
python scripts/review_tools.py validate assets/issues.example.json --root .
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

输出路径已存在时拒绝覆盖；退出码 2 表示仍有未解决位置。测试记录见 `tests/VALIDATION.md`。`evals/evals.json` 是待执行的模型级评估场景，不能把程序测试通过解释为科学审稿准确率。

## 保密、来源与限制

GitHub 只存储技能、程序和虚构测试材料。未发表论文、SI、批注稿和原始数据应放在私有工作目录，未经独立授权不得上传。`.gitignore` 仅为辅助，不能替代发布前检查。公开检索不发送未公开的原句或数据。不会自动投稿、联系编辑或发送邮件。

设计参考与官方文档记录见 `references/provenance.md`。本包没有复制上游执行脚本，也没有附带商业服务推广、强制第三方模型调用或向论文中自动插入引用的指令。
