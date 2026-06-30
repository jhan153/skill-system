---
name: research-experiment-blueprint
description: Creates experiment blueprint artifacts from one selected hypothesis or research plan, with checkpoint-first evaluation, matched datasets/metrics, ablation ladder, loss budget, and falsification criteria.
---

# Research Experiment Blueprint

## Routing Card
- role: primary
- intent_signature:
  - experiment blueprint
  - experiment_blueprint.json
  - 실험 설계
  - benchmark design
  - dataset baseline metric ablation
  - selected hypothesis experiment
- use_when:
  - the user asks for an experiment blueprint from a selected hypothesis or research plan.
  - datasets, baselines, metrics, ablations, compute, reproducibility, and stop/go criteria need structured planning.
- do_not_use_when:
  - code scaffold generation; use research-experiment-scaffold.
  - literature review or hypothesis ideation.
  - raw user claim planning without selected hypothesis; use research-hypothesis-planning.
- expected_inputs:
  - selected hypothesis
  - research plan
  - evidence references
  - baseline/checkpoint availability
  - dataset and metric constraints
- expected_outputs:
  - selected hypothesis
  - evidence references
  - checkpoint-first plan
  - datasets with license/access notes
  - baselines with references
  - metrics
  - minimal core experiment
  - ablation ladder
  - loss budget
  - compute/timeline
  - stop/go criteria
  - falsification conditions
  - reproducibility plan
- context_targets:
  must_read:
    - one selected hypothesis or research plan
    - constraints and target metrics
  read_if_needed:
    - evidence_ledger.json
    - ideation_output.json
    - research_plan.json
    - speech-enhancement-research for speech/audio research
  do_not_load_by_default:
    - code scaffold
    - statistical claims
    - manuscript writing
- risk_profile:
  reads:
    - research plan
    - ideation output
    - evidence ledger
    - domain references
  writes:
    - `papers/experiment_blueprint.json` only when requested
  tools:
    - none by default
  network:
    - none by default
  credentials:
    - none
  generated_artifacts:
    - experiment blueprint only if requested
  destructive_actions:
    - none
- entry_scene:
  - PREPARE

## Purpose
Creates experiment blueprint artifacts from one selected hypothesis or research plan, with checkpoint-first evaluation, matched datasets/metrics, ablation ladder, loss budget, and falsification criteria.

## When To Apply
- the user asks for an experiment blueprint from a selected hypothesis or research plan.
- datasets, baselines, metrics, ablations, compute, reproducibility, and stop/go criteria need structured planning.

## When Not To Apply
- code scaffold generation; use research-experiment-scaffold.
- literature review or hypothesis ideation.
- raw user claim planning without selected hypothesis; use research-hypothesis-planning.

## Workflow
1. PREPARE - confirm exactly one selected hypothesis.
2. CHECKPOINT-FIRST - identify checkpoint, pretrained, baseline inference, metric-only, or label audit options before training.
3. DATASET/METRIC - select only datasets and metrics that match the hypothesis.
4. BASELINES - include a simple baseline and a strong baseline when possible.
5. CORE - define the smallest discriminating experiment.
6. ABLATION - add one factor at a time.
7. STOP/GO - define support, refute, inconclusive, and stop criteria.

## Resource and Risk Boundary
Summary:
- Reads research plans, ideation output, evidence ledgers, and targeted domain references.
- Writes `papers/experiment_blueprint.json` only when explicitly requested.
- Uses no tools or network by default.
- Performs no code writes, dataset downloads, dependency installs, or training.
- Required checkpoints: one selected hypothesis, checkpoint-first plan, matched datasets/metrics, ablation ladder, and artifact intent.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Selected hypothesis
2. Evidence references
3. Checkpoint-first plan
4. Dataset plan
5. Baseline plan
6. Metric plan
7. Minimal core experiment
8. Ablation ladder
9. Loss budget
10. Compute/timeline
11. Stop/go and falsification
12. Reproducibility plan

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
- A blueprint does not guarantee experimental success.
- Dataset licenses and availability must be verified before use.
- Metric selection can still miss human or deployment relevance.
