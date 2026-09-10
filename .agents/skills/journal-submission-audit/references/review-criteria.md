# Review criteria

Use this as a coverage checklist, not an automatic scoring system. Record `checked`, `issue_found`, `not_applicable` (with reason), or `not_verifiable` for each applicable item. Apply scientific criteria proportionately to study design. Domain modules are conditional, not universal publication requirements. Live official journal instructions override dated venue-specific examples in any source.

## 1. Submission package and technical presentation

Inventory all main, SI, graphical abstract/TOC, figures, source, reference and data/code files actually supplied. Identify competing versions, missing includes, unusable files and incompatible units or sample names before reviewing prose. Confirm article type, anonymous-review requirements, author/affiliation correspondence and required statements using official guidance. Do not infer approvals from an author's institution.

For Word/PDF, inspect title block, two-column flow, embedded fonts, symbol fidelity, sub/superscripts, equation rendering, overflows, page breaks, blank pages, floating objects, cropped captions and legibility at final publication size. Check vector/raster quality and actual image dimensions against the journal's current rules, not a universal DPI assumption. Check bookmarks/links and whether metadata exposes identities in an anonymized submission.

For TeX, locate main roots, `input`/`include` files, bibliographies, class/style files and image paths. Keep source review separate from compiler execution. Check undefined references/citations, duplicate labels, unresolved placeholders, missing assets, bibliography output, overfull boxes and unintended blank pages. Record actual engine/build log; never call an unrun build successful. Do not execute untrusted build hooks or enable shell escape.

## 2. Section-by-section scientific and narrative review

| Section | Questions to resolve |
|---|---|
| Title | Does it identify the actual contribution and system without claiming unsupported generality, mechanisms or primacy? Are abbreviations necessary? |
| Abstract | Is the problem, approach, main result and bounded implication clear? Do all numbers and conditions agree with the body/SI? Are relative improvements given with a defined comparator? |
| Introduction | Does it establish a material problem, verified closest work, a specific remaining gap and the study's response? Is the paper positioned fairly rather than against an artificially weak baseline? |
| Methods | Can a skilled reader reproduce the essential procedures, apparatus, calculations and analyses? Are controls, independent units, exclusions and conditions identifiable? |
| Results | Is each claim supported by the actual figure/table/data? Are denominators, units, uncertainty and test conditions reported? Is unsuccessful or contradictory evidence necessary to interpretation omitted from discussion? |
| Discussion | Are observations separated from mechanisms and hypotheses? Are alternatives, uncertainty, boundary conditions and practical relevance addressed? |
| Conclusion | Does it stay within demonstrated scope without introducing new results or converting preliminary evidence into universal claims? |
| SI | Is it independently intelligible, reproducible and consistent with the main article? Does it contain all referenced methods, characterizations, figures and calculations? |
| Statements and references | Are required contribution, conflict, funding, ethics, availability and AI-use statements present and accurate? Do cited records exist and support the associated statements? |

## 3. Claim–evidence audit

Trace each central claim to a result, the method generating it, relevant SI and supplied raw data/code. Assess direction, magnitude, uncertainty, population/system, conditions, time horizon, comparator and inference type together. A related citation is not sufficient support for a stronger statement.

Distinguish observation, association, prediction, causation, mechanism and extrapolation. Ask what plausible alternative explanation remains. Unsupported central claims require necessary evidence or narrower wording. Use conditional phrasing where evidence is incomplete. Give verified strengths as well as defects.

For novelty and “first/best/unprecedented” claims, search current public primary literature with public topic terms, record queries/date/scope and compare closest relevant work. Do not claim exhaustive novelty verification from a few hits. Where access is limited, report that limitation rather than inventing comparative results. Do not demand novelty merely through more ornate language.

## 4. Design, statistics and quantitative consistency

Determine the actual experimental/observational unit. Distinguish independent syntheses/devices/subjects from repeated technical measurements or serial timepoints. Check controls, calibration references, sampling, order effects, batching, blinding/randomization where meaningful, inclusion/exclusion, missingness and the scope of generalization. Do not mechanically require clinical-study practices for a device characterization.

Check independent replicate counts, reported `n`, raw versus averaged observations, analysis assumptions, effect sizes, uncertainty intervals, error-bar definitions, multiplicity and test sidedness. Verify whether SD, SEM, confidence intervals and instrument uncertainty are being conflated. Repeated observations are not automatically independent. A nonsignificant result is not evidence of equivalence without a suitable equivalence analysis/design. Avoid post hoc “observed power” as a substitute for uncertainty assessment.

Recalculate available ratios, percentage changes, mean/dispersion, derived performance indices and fitted parameters using supplied inputs. Record formulas, units, assumptions, rounding and scripts. Distinguish percentage points from relative percentages; compare like conditions and denominators. Check significant figures against measurement precision, mass/charge/energy balances where applicable, dimensional consistency, sign conventions, variable definitions, logs and normalization. Do not recover precise values from a small plot image and present them as raw data.

## 5. Figures, tables, images and equations

Inspect every panel, not only captions. Check the panel order, sample IDs, legends, axis labels/ranges, scale bars, unit prefixes, missing/ambiguous color encoding, uncertainty, replicate counts and trace provenance. Inspect readability in final-size layout. Check consistency across graphical abstract, main plots and SI plots.

Check whether different axes/scales or normalization create misleading comparisons. Verify stated regression/correlation measures against the fitted quantity. Look for observable duplicate panels or unexplained alterations, but label suspected issues as questions; visual similarity alone is not proof of misconduct. Do not synthesize missing data, “repair” spectra, redraw micrographs or beautify evidence.

Check table totals, units, footnotes, significant figures and comparison conditions. Check equation derivations, assumptions, dimensions, definitions, numbering, signs and consistency with code/calculation examples. Formula extraction is not enough: inspect rendered symbols.

## 6. Main–SI joint audit

Perform both directions: every main-text pointer must resolve to the correct SI object, and each SI result used to justify a main claim must actually match that claim. Check figure/table/scheme/equation numbering, suffixes, sample labels, experiment descriptions, compound identifiers, concentrations, temperatures, flow rates, reaction/residence times, fitting windows, conversion/yield/selectivity definitions and data-processing versions.

For each apparent numerical discrepancy, first ask whether it refers to a different batch, operating condition, definition, rounding rule or uncertainty. Only call it a contradiction when the contexts conflict. Record exact quotes and contexts from both files under the same issue ID. Ask the author to verify the authoritative record; never choose a value by intuition.

SI should provide the full experimental route, calculations, characterization, calibration and analysis details needed for interpretation and repetition. Essential evidence supporting the central claim should not be hidden solely in SI when the main text needs it to be understandable. Do not impose a universal main/SI allocation; align with article type and official guidance.

## 7. Reproducibility, references and declarations

Check reagents/materials, instrument and configuration information, fabrication dimensions, calibration, operating conditions, software/model/library versions, analysis parameters, preprocessing, exclusions, seeds where relevant and data/code/material availability. Describe restricted data honestly; do not infer availability from an inaccessible link or a statement alone. Run code only with authorization, appropriate isolation and inspected dependencies. Record what was actually executed.

Check citation keys/order, duplicate entries, author/year/title/journal/DOI consistency and whether the original source supports the exact claim. Distinguish `metadata_verified`, `abstract_checked`, `full_text_checked` and `claim_support_checked`. Verify foundational references, strongest comparisons and disputed claims first, then account for the remainder. Use primary literature where possible and do not fabricate missing bibliographic fields. Identify correction/retraction notices when relevant; a citation-format linter does not verify source credibility or claim support.

Check applicable ethics approvals/consent, animal welfare, chemical/biological safety disclosures, funding, sponsor roles, contributions, conflicts and AI-use disclosure against current journal requirements. Use appropriate public policies and avoid allegations. Third-party confidential peer review requires its own authorization check; this skill defaults to the author's own pre-submission review.

## 8. Conditional domain modules

### Chemistry, catalysis and materials

Check identities and sample naming, purity/characterization, stoichiometry, limiting reagents, concentrations, catalyst amount/loading, atmosphere, solvent, temperature history, quench/workup, analytical/internal standards and yield basis. Distinguish conversion, selectivity, assay yield and isolated yield; document recovery and balances when required for conclusions. Assess selectivity/enantioselectivity/regioselectivity reporting with relevant characterization. Do not infer absolute configuration or mechanism without supporting evidence.

For catalysts/materials, connect synthesis and treatment conditions to characterization and performance. Assess appropriate blank/reference controls, normalization basis, leaching/deactivation, reuse protocol and batch/device reproducibility only as needed by the claims. Distinguish apparent stability over limited cycles from demonstrated long-term durability. For photochemical/electrochemical work, inspect optical/electrical input definitions, geometry, irradiated/electrode area, wavelength/current/potential conventions, mixing and heating confounds.

### Microfluidics, flow chemistry and engineering

Check geometry, materials, fabrication/bonding, channel dimensions, wettability, pumps/connections, flow control, back pressure, mixing, residence time/distribution, startup versus steady state, dead volumes, hold-up and sensor location. Check whether total or single-stream flow is used to calculate residence time. Test boundary-condition consistency among drawings, CFD, experiments and SI.

Separate proof-of-concept from industrial scale-up, on-chip component capability from whole-system performance, and biological compatibility from demonstrated biological function. Compare throughput, sensitivity, accuracy, response time, resource use and device footprint on matched bases. Do not require unrelated DNA/protein experiments solely because the journal publishes biological applications; retained biological claims still require appropriate evidence.

### Instrumentation, calorimetry and control

Check signal-chain definitions, reference/sample roles, thermal/electrical baselines, calibration traceability, heat-loss corrections, dynamic response, sampling/filtering, control-law implementation and measurement uncertainty. Distinguish resolution, noise, detection limit, accuracy, precision and bandwidth. Check calibration and validation independence, response lag, startup transients, sign conventions and steady/dynamic energy balances.

For adaptive controls/digital twins/optimization, distinguish observed variables from inferred states and model predictions. Audit training/update data, validation conditions, objective/constraint definitions, holdout tests, controller settings, safety margins and limitations. Claiming safety from predicted mean behavior without accounting for uncertainty or failure modes needs scrutiny. Do not treat a simulated optimum as experimental confirmation.

### Computation, statistics and machine learning

Check sample-unit and time-aware data splitting, leakage, preprocessing fit only on training data, validation protocol, hyperparameter tuning, independent testing, baselines/ablations, seeds, uncertainty, calibration and external/shifted-condition performance. Avoid presenting multiple resamples as independent experiments. Check compute/settings and executable environment. For CFD/numerics, inspect governing assumptions, geometry, mesh/time-step checks, solver/boundary settings, convergence criteria and experimental validation appropriate to the claims.

### Biological/clinical work, only when actually present

Select the design-appropriate current reporting standard from its official source; do not attach CONSORT/STROBE/PRISMA indiscriminately. Check biological versus technical replicates, models, controls, authentication/contamination reporting where relevant, sample handling, approvals and confounders. Request specialist review where a central claim exceeds competence. Engineering-only demonstrations do not automatically require biological experiments, and biological claims cannot be excused solely because the authors specialize in engineering.

## 9. English-language pass

Review every section and SI, including legends and notes. Prefer correct, direct English over promotional phrases and nominalization-heavy rewrites. Preserve technical meaning, cautious claims, exact variable names, chemical nomenclature and data. Standardize defined terms/abbreviations, articles, agreement, tense, comparisons, prepositions and paragraph logic. Resolve unclear antecedents and ambiguous comparisons.

Give original quote → proposed English → reason → meaning-change flag → author confirmation. Do not change a numerical value without verified evidence and authorization. Separate pure language edits from scientific reinterpretation. Skip already clear sentences rather than generating edits to reach a quota.

## 10. Simulated editor and reviewer synthesis

Editor: verified scope fit, contribution for the audience, closest-work positioning, significance and narrative readiness. Reviewers: domain interpretation; methods/uncertainty/reproducibility; application/boundaries when relevant. Each perspective should identify both strengths and evidenced concerns. These are simulated perspectives, not independent real reviews.

For every major request specify the affected claim, supporting location, why it matters, minimum acceptable resolution and viable alternatives. Classify a new experiment as necessary to retain a central claim, beneficial but optional, or out of scope. Reconcile contradictory demands and set the order: verify source facts → repair evidence/claims → fix main–SI consistency → restructure → polish English → check format/build → final QA. Map every P0/P1 issue to the exact required resolution; no acceptance percentages.
