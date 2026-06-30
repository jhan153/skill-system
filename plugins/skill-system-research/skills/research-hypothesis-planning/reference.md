# research-hypothesis-planning Reference

## Purpose
Use this reference to keep research plans claim-first, checkpoint-first, and ablation-disciplined without weakening ordinary development execution.

## Mode Decision Table
| Request | Mode | Primary |
| --- | --- | --- |
| Paper idea, novel method, hypothesis, experiment, ablation, loss, training plan | Research Hypothesis Planning | `research-hypothesis-planning` |
| Implement chosen method, edit code, add tests, build pipeline | Development / Implementation | task-specific implementation skill |
| Generic algorithm recommendation | Algorithm Proposal | `analysis-algorithm` |
| Persist research plan under `docs/plan` | Research content + artifact writer | `research-hypothesis-planning` + `plan-short-term-docs` |
| Critique existing research plan | Review gate | `report-critical` with `review_goal=research_validation` |

## Premise Triage Labels
- `confirmed_fact`: supported by provided reliable evidence.
- `user_hypothesis`: user claim to test, not assume.
- `plausible_but_unverified`: reasonable but unproven in current context.
- `risky_overgeneralized`: too broad across datasets, models, papers, or metrics.
- `potentially_false`: conflicts with evidence or needs strong support.
- `needs_literature_check`: requires source verification.
- `not_needed_for_main_claim`: useful later but not core.

## Checkpoint-First Ladder
1. Existing checkpoint evaluation.
2. Pretrained baseline inference.
3. Re-score existing outputs.
4. Metric/error analysis.
5. Dataset or label audit.
6. Small controlled fine-tune only if evaluation-only is insufficient.
7. New training only after the gap is identified.

## Ablation Stage Template
```yaml
stage: A2
purpose: "test main intervention only"
changed_factor: "<one factor>"
frozen_factors:
  - dataset
  - checkpoint
  - architecture
  - training objective
expected_signal: "<metric or qualitative evidence>"
failure_interpretation: "<what this result would mean>"
```

## Loss Budget Template
```yaml
loss_budget:
  primary_objective: "<one objective>"
  auxiliary_loss: "none | one directly justified auxiliary"
  regularizer: "none by default"
  evaluation_metrics:
    - "<not training loss>"
  analysis_metrics:
    - "<diagnostic only>"
  risky_metric_proxy: "mark unverified if used"
```

## Output Skeleton
```markdown
## Mode Decision

## User Premise Triage

## Primary Research Claim

## What Not To Assume

## Checkpoint/Baseline Reuse Plan

## Minimal Core Experiment

## Progressive Ablation Ladder

## Loss Budget

## Metrics and Failure Criteria

## Ablation Backlog

## Deferred / Rejected Ideas
```

## Development Boundary Examples
- `이 loss 함수 구현하고 테스트까지 추가해줘` -> development; do not run premise triage.
- `이 모델 학습 파이프라인 구현 플랜을 짜줘` -> development plan if the pipeline is already chosen.
- `이 논문 아이디어에서 loss를 어떻게 설계할까?` -> research planning.
- `이 문제에는 어떤 알고리즘이 좋아?` -> generic algorithm proposal.

## Anti-Pattern Checks
- Does the plan assume the user's claim is true?
- Does it start with new training before checkpoint-only evaluation?
- Does the core experiment combine architecture, data, loss, and schedule changes?
- Are evaluation metrics confused with training losses?
- Is there more than one primary claim?
- Are secondary ideas hidden inside the main claim instead of the backlog?
