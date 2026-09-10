# Required output templates

Populate with real observations. Empty headings are not completed work. Use Chinese explanation and English manuscript wording by default. For checks not possible, state why, what remains unknown and the minimum needed input. Save reports in the authorized private run directory, not the public skill checkout. Markdown/CSV are sufficient; native DOCX/PDF reports are optional unless requested.

## Suggested run outputs

```text
private-run/
  inventory.json
  issues.json
  annotated/                         # Main and SI annotated copies + annotations.json
  location-indexed-review.md
  editorial-and-reviewer-assessment.md
  main-si-consistency.csv
  claim-evidence-matrix.csv
  journal-profile.md
  revision-plan.md
  english-change-log.md
  coverage-and-qa.md
```

No-findings files need not acquire artificial comments; identify them explicitly and provide an unchanged copy or an unambiguous reference to the reviewed original. Unresolved anchors remain in the issue register and report, not hidden in a success message.

## Editorial and reviewer assessment

```markdown
# Author-side pre-submission assessment
Review date / target journal / article type / input versions
Status: simulated perspectives, not independent human reviews or a journal decision

## What was actually reviewed
Main files, every SI file, raw data/code availability, verified external sources
Missing or inaccessible material and consequences

## Neutral scientific summary
Research question, system, design, contribution and demonstrated results

## Simulated editor
Supported strengths and fit
Verified closest-work comparison; search limits
Decisive desk-review risks, linked to issue IDs and locations
Positioning/narrative changes
Readiness: not_ready / conditionally_ready / ready_for_author_final_check
Reasoning, explicit unresolved blockers and necessary author checks

## Simulated domain reviewer
Strengths
Major concerns: issue ID, original location, evidence, impact, action
Minor concerns with locations
Interpretation limits and proportionate evidence requests

## Simulated methods/reproducibility reviewer
Design, independent units, controls, quantitative analysis, uncertainty and SI
Major/minor concerns with evidence and locations
What could and could not be recalculated or reproduced

## Relevant specialist perspective, when warranted
Engineering/application or other expertise; omit irrelevant modules with a reason

## Reconciliation
Duplicate/contradictory requests resolved
Minimum evidence needed to retain each central claim
Reanalysis/narrowing alternatives versus genuinely necessary experiments
```

## Main–SI consistency matrix

Use these columns:

```csv
check_id,topic,main_file,main_location,main_quote,si_file,si_location,si_quote,context_comparable,status,issue_id,verification_needed
```

Include quantitative results, experimental conditions, sample names, figure/table pointers, equations and terminology. `status` is `consistent`, `conflict`, `not_verifiable`, or `not_applicable`. Do not manufacture a conflict between different conditions.

## Claim–evidence matrix

```csv
claim_id,claim_location,claim_text,evidence_location,methods_location,si_location,data_code_available,inference_type,support_status,limits,issue_id
```

Use `supported`, `partly_supported`, `unsupported_in_supplied_material`, or `not_verifiable`. Missing reporting and disproven claims are different. Explain uncertainty and access limits. Each central claim needs a row; do not restrict the matrix to problems only.

## Journal profile and source ledger

```markdown
# Journal profile
Journal / article type / date / official scope URL
Requirement | Mandatory or recommended | Official source/access date | Manuscript location | Status | Action

# Public-source ledger
Source ID | URL/DOI | Title/record metadata | Access date | Metadata/abstract/full text/support checked | Claim or rule supported | Limits

# Novelty search record
Public search terms, sources/databases, dates, relevant closest work, comparison conditions and search limits
```

Do not copy confidential manuscript sentences into searches. Source existence does not establish support. Do not hard-code journal rankings or stale word/page/figure limits.

## Revision plan

```markdown
# Revision plan
Order | Issue IDs | Priority | Required resolution | Effort type | Dependencies | Author decision | Verification after change

## New work triage
Affected claim | Minimum necessary experiment/analysis | Why necessary | Lower-burden alternative | Consequence of retaining/narrowing/removing claim
```

Order evidence verification before rewriting the dependent conclusion. P0/P1 are not diluted by many P3 grammar comments. Distinguish essential work from optional expansion. Keep deferred/disputed issues visible; an author disagreement alone is not evidence of resolution.

## English change log

```markdown
Issue ID | File and original location | Verbatim original | Proposed English | Chinese explanation | Scientific meaning changed? | Author confirmation needed? | Status
```

When evidence is missing, record an explicit conditional suggestion rather than a ready-to-paste sentence with invented facts. Show English edits in native comments too, not solely in this log.

## Coverage and QA manifest

```markdown
# Coverage and QA
Input file | SHA-256 | Role/version | Total pages/sections | Text fully read? | Pages visually inspected | Figures/tables/equations inspected | Status/limits

## Per-section coverage
File | Section/page range/object ID | Text review | Technical/scientific review | Language review | Visual review | Issue IDs | Remaining work

## Cross-file and source verification
Central claims traced: actual / identified
Main–SI pointers checked: actual / identified
References: metadata checked / full text checked / support checked / not verified
Raw data/code: supplied / executed / not supplied / not executed

## Artifact validation
Expected issue-location pairs / successfully anchored / unresolved
Original hashes unchanged?
Native comment IDs/ranges and attachment relationships verified?
Every annotated Word/PDF page rendered and inspected?
Rendered PDF page count and visible defects?
LaTeX main/SI compilation: commands/engine/exit codes/logs, or compile_not_run
Any undefined citations/references, missing assets or overflow warnings?
Final claim/data/wording consistency rechecked after approved edits?

## Remaining limitations and handoff
Unreviewed sections, unavailable files, unverified requirements, unresolved anchors and necessary author decisions
Overall coverage: complete_for_supplied_material / partial
Final accountability and no guarantee of error-free review or journal acceptance
```

For text-only source projects, physical page totals may be `not_applicable`; list complete source files/line ranges instead. Do not mark visual inspection complete from text extraction, or imply a successful Word GUI test from XML checks alone.
