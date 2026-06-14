---
name: research-statistical-analysis
description: Analyzes experiment result tables and metrics into statistical reports with provenance, planned-vs-exploratory separation, test rationale, effect sizes, intervals, and limitations.
---

# Research Statistical Analysis

## Routing Card
- role: primary
- intent_signature:
  - statistical analysis
  - significance
  - effect size
  - confidence interval
  - metric results
  - analysis/statistical_report.md
  - 통계 분석
- use_when:
  - the user provides result tables, metric CSV/JSON, experiment configs, or design descriptions and asks for statistical interpretation.
- do_not_use_when:
  - simulate conclusions when data are missing.
  - choose tests based on desired result.
  - write manuscript prose as the primary task.
- expected_inputs:
  - metric tables
  - result CSV/JSON
  - experiment configs
  - design description
  - planned tests
- expected_outputs:
  - data provenance
  - planned vs exploratory tests
  - test selection rationale
  - assumption checks
  - effect sizes
  - confidence/credible intervals
  - multiple comparison handling
  - practical vs statistical significance
  - missing data/exclusions/outliers
  - limitations
- context_targets:
  must_read:
    - actual result data or explicit analysis-plan request
    - experiment design context
  read_if_needed:
    - experiment_blueprint.json
    - analysis scripts
    - result metadata
  do_not_load_by_default:
    - manuscript writing
    - paper search
    - experiment scaffold
- risk_profile:
  reads:
    - result tables
    - metric outputs
    - configs
    - design description
  writes:
    - `analysis/statistical_report.md` only when requested
  tools:
    - none by default
  network:
    - none
  credentials:
    - none
  generated_artifacts:
    - statistical report only if requested
  destructive_actions:
    - none
  forbidden_by_default:
    - fabricated data
    - fabricated conclusions
- entry_scene:
  - PREPARE

## Purpose
Analyzes experiment result tables and metrics into statistical reports with provenance, planned-vs-exploratory separation, test rationale, effect sizes, intervals, and limitations.

## When To Apply
- the user provides result tables, metric CSV/JSON, experiment configs, or design descriptions and asks for statistical interpretation.

## When Not To Apply
- simulate conclusions when data are missing.
- choose tests based on desired result.
- write manuscript prose as the primary task.

## Workflow
1. PREPARE - identify data provenance and analysis question.
2. ACQUIRE - read only provided result tables/configs.
3. SELECT TEST - choose tests from design and data type, not desired outcome.
4. CHECK ASSUMPTIONS - independence, pairing, distribution, missingness, multiple comparisons.
5. REPORT - include effect sizes, intervals, practical significance, and limitations.
6. ABSTAIN - if data are missing, produce analysis plan only.

## Resource and Risk Boundary
Summary:
- Reads result tables, metric outputs, configs, and design descriptions.
- Writes `analysis/statistical_report.md` only when explicitly requested.
- Uses no tools, network, or credentials by default.
- Does not fabricate data, p-values, effect sizes, intervals, or conclusions.
- Required checkpoints: real data availability, planned vs exploratory status, test rationale, assumption checks, and artifact intent.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Data provenance or explicit no-data status
2. Analysis question
3. Planned vs exploratory status
4. Test selection rationale
5. Assumption checks
6. Results and effect sizes only when real data are provided
7. Intervals only when real data support them
8. Multiple-comparison handling
9. Practical significance
10. Limitations

## No-Data Guard
If no real result data are provided, produce an analysis plan only. Do not produce p-values, effect sizes, confidence intervals, credible intervals, statistical conclusions, or practical-significance claims.

## Validation
- Confirm `.codex/skills/.system` was not touched.
- Confirm user intent matches this skill, not ordinary development.
- Confirm required evidence or artifact inputs are present or explicitly marked missing.
- Confirm no secrets, credentials, hardcoded single-host paths, fabricated citations, or fabricated results are introduced.
- Confirm artifact writes happen only when explicitly requested.

## Anti-Patterns
- Installing or invoking monolithic `codex-research-lifecycle`.
- Treating search keywords as conclusions.
- Collapsing evidence search, ideation, blueprint, scaffold, analysis, writing, and review into one step.
- Creating custom transcribe/speech skills from research source material.
- Weakening development/implementation routing because a request mentions model, metric, loss, experiment, or training.

## Known Limits
- Statistical validity depends on design and data quality.
- Missing raw data limits what can be checked.
- This skill cannot turn exploratory results into confirmatory evidence.
