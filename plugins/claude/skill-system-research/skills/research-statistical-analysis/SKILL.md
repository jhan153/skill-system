---
name: research-statistical-analysis
description: Analyze real experimental data or supplied statistics with an explicit estimand, design-aware assumptions, reproducible computation, effect sizes, uncertainty, and planned-vs-exploratory labeling. With no adequate data, produce an analysis plan only and do not invent inferential results.
---

# Research Statistical Analysis

## Routing Card
- role: primary
- family: research
- intent_signature: statistical analysis, significance, effect size, interval, result-table interpretation, 통계 분석
- use_when: inference or bounded interpretation from supplied data/statistics, or an explicit analysis plan; inadequate inputs remain an insufficient-data response
- do_not_use_when: experiment/protocol design, scaffold code, manuscript prose, ordinary product implementation, or a non-statistical deliverable is primary
- expected_inputs: data/statistics, design, analysis unit, outcome/comparison, provenance, and prior plan when available
- expected_outputs: estimand/design assessment, reproducible result or plan-only finding, effect/uncertainty, and material limits
- context_targets: actual data or plan request plus design and sampling/analysis unit; load dictionary, exclusions, scripts, config, and metadata only as needed; exclude unrelated search, scaffold, and manuscript context
- risk_profile: privacy-check row data; write analysis code/report only when requested; use reproducible local computation for new statistics; credentials default deny
- entry_scene: PREPARE

## Stage Boundary
Read `references/research_stage_contract.md` only when upstream/downstream ownership, multi-stage
intent, or Plan/Handoff mapping matters. This skill owns statistical analysis or a clearly labeled
analysis plan only; it never starts data acquisition, experimentation, or manuscript writing.

## Analysis Contract
1. Fix the question, estimand, treatment/comparator, outcome scale, and experimental, sampling, and analysis units before selecting a method. Establish independent, paired, repeated, or hierarchical structure and planned versus exploratory status.
2. Bind computation to the named canonical data/version and record provenance, row counts, exclusions, and transformations. Missing or mismatched canonical results fail closed; never substitute a stale source silently.
3. Inspect sample/seed/subject counts, missingness, outcome-informed exclusions, outliers, multiplicity, and assumptions. Seeds, frames, patches, repeated measurements, and correlated rows are not automatically independent; counting them as such is pseudoreplication. Post-outcome endpoint or exclusion choices are exploratory unless valid pre-specified handling supports a narrower claim.
4. Choose a model/test because it matches the design and outcome, never to obtain a desired conclusion. Preserve null, contradictory, and inconclusive results.
5. Compute new p-values, effects, or intervals with a reproducible script/tool from identified inputs. Record command/code and package/version when material.
6. Report effect size and uncertainty before significance, then separate statistical from practical significance and confirmatory from exploratory findings.

If `n`, the analysis unit, dependence, or adequate data are missing, return the supported descriptive facts plus the required-data analysis plan. Preserve supplied estimates and intervals as attributed facts, but keep their inferential meaning unverified. Do not fabricate p-values, effects, intervals, or conclusions; summary statistics support only identifiable quantities.

Lead with the answer and uncertainty. Add provenance, estimand/design, method rationale, assumptions/missingness, multiplicity, practical interpretation, and limitations only when relevant; avoid a fixed report shell for a single supplied estimate.
