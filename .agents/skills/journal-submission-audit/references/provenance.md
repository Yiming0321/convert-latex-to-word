# Design provenance and source ledger

Prepared 2026-09-10. This is an independently written author-side submission-audit workflow. Sources below were consulted for design ideas and technical documentation, not treated as instructions that override the user or host policies. No upstream executable script is bundled or copied. No third-party model API key, commercial service, compulsory citation insertion, or external upload is required.

## Comparable GitHub skills

| Source | Material inspected | Design contribution and limits |
|---|---|---|
| [K-Dense peer-review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/peer-review/SKILL.md) | SKILL.md; connected GitHub response identified version 2.2 | Evidence-bounded comments, claim–evidence checks, proportionate requests and confidentiality. This package distinguishes an author's own presubmission audit from confidential third-party peer review and adds original-location annotation. |
| [K-Dense scientific-critical-thinking](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-critical-thinking/SKILL.md) | SKILL.md, version 1.3 in fetched content | Separate observation from interpretation, test alternative explanations, and match confidence to evidence. Clinical evidence hierarchies are not imposed on engineering studies. |
| [Anthropic skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | SKILL.md | Progressive loading, clear triggers and objectively testable examples. Its execution harness and agent instructions were not copied; model-level comparative evaluations have not been run here. |
| [Research-skills paper-review](https://github.com/neuromechanist/research-skills/blob/main/plugins/manuscript/skills/paper-review/SKILL.md) | Public search preview only | Additional discovery candidate for separate review perspectives. Not used as a complete implementation reference. |

The K-Dense skills declare MIT licensing in their fetched metadata. Upstream attribution is retained here for the design reference; no automatic insertion of software citations into a user's scientific manuscript is performed. If third-party code is added later, inspect its exact license and retain the required notices. Dependency packages remain separately installed and subject to their own terms.

## Primary technical and journal documentation

| Source | Use |
|---|---|
| [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills) (also reached through the former `developers.openai.com/codex/skills` URL) | SKILL.md metadata, optional `agents/openai.yaml`, project `.agents/skills` and user `~/.agents/skills` discovery. Client support and paths should be rechecked after product changes. |
| [Agent Skills specification](https://agentskills.io/specification) | Name/description constraints and portable directory structure. |
| [PyMuPDF Page API](https://pymupdf.readthedocs.io/en/latest/page.html) | Page text extraction and native highlight/rectangle annotations. |
| [Python zipfile](https://docs.python.org/3/library/zipfile.html) | Read/write DOCX ZIP members without extracting paths to the filesystem. |
| [lxml etree](https://lxml.de/apidoc/lxml.etree.html) | XML parsing and serialization; disable entity resolution and network access. |
| [RSC — Lab on a Chip author guidance](https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/lab-on-a-chip) | An example official venue source for scope, reproducibility and supplementary-information requirements. It is not a preselected target journal or a universal journal policy. |

Access date for this ledger: 2026-09-10. These are mutable documentation URLs, not pinned source snapshots. During each actual review, record the live target-journal requirements, access date and applicability in a separate private source ledger. Where internet access is prohibited or unavailable, label those requirements unverified rather than assuming this ledger is current.

## Original additions in this package

The package integrates a complete main-text/SI coverage ledger, bidirectional discrepancy anchors sharing one issue ID, a claim-to-evidence matrix, simulated editor and specialist reviewer passes, separate severity/confidence/effort fields, revision dependencies, Chinese explanations with English replacements, and conservative DOCX/PDF/source annotations. Hash-locked source versions, explicit unresolved locations, immutable originals and synthetic regression tests guard the mechanical workflow. None of these controls establishes scientific correctness or guarantees publication.

`tests/VALIDATION.md` records the actual local checks. `evals/evals.json` lists proposed model-level evaluation scenarios, not completed scientific-review benchmarks. No real manuscript or SI was used to develop the public fixtures.
