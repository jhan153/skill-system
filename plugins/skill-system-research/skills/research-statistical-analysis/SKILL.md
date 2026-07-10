---
name: research-statistical-analysis
description: Analyze real experimental data or supplied statistics with an explicit estimand, design-aware assumptions, reproducible computation, effect sizes, uncertainty, and planned-vs-exploratory labeling. With no adequate data, produce an analysis plan only and do not invent inferential results.
---

# Research Statistical Analysis

## Routing Card
- role: primary
- intent_signature:
  - statistical analysis, significance, effect size, interval, result table interpretation, 통계 분석
- use_when:
  - the user provides data/statistics and asks for inference, or explicitly wants a statistical analysis plan.
- do_not_use_when:
  - data are absent but the user expects conclusions, the test is being chosen to obtain a desired result, or manuscript prose is the primary task.
- expected_inputs:
  - data/statistics, experimental design, analysis unit, outcome, comparison, and planned tests when available
- expected_outputs:
  - provenance, estimand, design/assumption assessment, reproducible analysis or no-data plan, effect/uncertainty, and limitations
- context_targets:
  must_read:
    - actual data or explicit plan-only request
    - experimental design and sampling/analysis unit
  read_if_needed:
    - blueprint, data dictionary, exclusion policy, scripts, config, and result metadata
  do_not_load_by_default:
    - manuscript templates, unrelated paper search, or experiment scaffold
- risk_profile:
  reads:
    - data, design, metadata, and prior analysis plan
  writes:
    - analysis code/report only when requested
  tools:
    - reproducible local computation when new statistics are calculated
  sensitive_resources:
    - credentials default deny; review privacy before reading row-level data
- entry_scene:
  - PREPARE

## Analysis Gate
Before selecting a test, establish:

- research question and estimand
- experimental, sampling, and analysis units
- independent vs paired/repeated/hierarchical structure
- treatment/comparator and outcome scale
- planned vs exploratory status
- sample/seed/subject counts, missingness, exclusions, outliers, and multiplicity

Seeds, frames, patches, repeated measurements, and correlated rows are not automatically independent samples. Treating them as independent is pseudoreplication. If the design or `n` is unavailable, do not manufacture inferential precision.

## Workflow
1. Record data provenance, row counts, exclusions, and transformations.
2. State the estimand and design-derived assumptions.
3. Choose a model/test because it matches the design and outcome—not the desired conclusion.
4. Check or qualify assumptions and missing-data handling.
5. Calculate with a reproducible script/tool when new p-values, effects, or intervals are needed; record command/code, package/version when material, and exact inputs.
6. Report effect size and uncertainty before interpreting significance.
7. Separate statistical from practical significance and planned from exploratory findings.
8. Preserve null, contradictory, and inconclusive results.

If only supplied summary statistics are adequate, interpret only what they support. If no adequate data exist, return the analysis plan and required data; no p-values, effects, intervals, or conclusions.

## Output
Lead with the answer to the analysis question and its uncertainty. Add provenance, estimand/design, method rationale, assumption/missingness checks, results, multiplicity, practical interpretation, and limitations only as relevant. Avoid a fixed ten-section report for a single supplied estimate.

## Behavior Cases
- Positive: “paired per-seed results와 설계 정보를 사용해 effect size와 interval을 계산해줘.”
- Negative: “데이터는 없지만 유의하다고 증명해줘.” → analysis plan/no-data response only.
- Edge: mean±SD is supplied without `n` or sampling unit → decline inferential testing and name the missing information.

## Validation
- New statistics are reproducible from identified inputs.
- Analysis unit and dependence structure are explicit.
- Effect size/uncertainty and exclusions are reported with the test result.
- Exploratory findings are not presented as confirmatory.
- No-data and insufficient-data cases contain no fabricated inference.
