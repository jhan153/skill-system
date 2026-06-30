# Improvement Tracks

This document records active improvement tracks for the next version cut. It is a field-quality backlog, not a package gate.

## Active Tracks

| track | target files | current action | next evidence |
| --- | --- | --- | --- |
| Design field cases | `.codex/eval/design_usage_cases.yaml`, `.codex/docs/design_cluster_roadmap.md` | Track the 10-skill design cluster across primary, evidence gate, analysis, and explicit-only surface roles. | Real design-to-code, decomposition, layout translation, and surface-specific requests. |
| Research negative routing | `.codex/eval/negative_routing_cases.yaml`, `.codex/eval/research_regression_cases.yaml` | Add cases where research terms appear in ordinary development or lightweight text work. | Field examples where research cluster over-triggered or correctly stayed inactive. |
| Coordination over-trigger | `coordination-brief`, `coordination-multi-agent`, `handoff_cases.yaml`, `negative_routing_cases.yaml` | Narrow triggers to explicit DAG, handoff, lock-scope, or multi-session coordination. | Requests containing goal/목표 that should stay simple. |
| Context lifecycle drift | `plan-spec-curator`, `.codex/eval/runtime_usage_cases.yaml`, `.codex/eval/negative_routing_cases.yaml` | Observe whether stale plans, closed plans, and oversized instruction packets are pruned without taking over substantive task execution. | Field examples where old plans polluted context or were correctly excluded. |
| Heavy planning over-trigger | `plan-long-term-package`, `negative_routing_cases.yaml`, `skill_registry.md` | Require explicit package-style planning intent. | Requests containing phase, migration, rewrite, or handoff that should not create packages. |
| Maturity feedback | `skill_registry.md`, `skill_maturity.md`, `field_feedback_guidelines.md`, `FIELD_FEEDBACK.md` | Tie maturity changes to repeated real-use feedback. | Field entries with expected vs actual primary skill and output shape. |
| Eval result capture | `evaluation-harness`, `.codex/eval/usage_quality_report.template.md`, `.codex/eval/runtime_usage_cases.yaml` | Record observed primary/supporting skills, context overload, trigger misses, output shape mismatch, and friction. | Manual field review notes from representative runtime cases. |
| Context pack filtering | `memory-bank-harness`, `context_pack_guidelines.md`, `memory_usage_guidelines.md`, `memory_usage_cases.yaml` | Exclude stale plans, raw transcripts, scratch, poison-risk text, and unrelated field feedback from default context packs. | Cases where old plans or feedback polluted current instructions. |

## Non-Goals

- Do not use this backlog as a bundle validator.
- Do not calculate package readiness.
- Do not create deployment, signoff, rollback, or evidence-finality workflow from these tracks.
- Do not upgrade maturity from static document quality alone.

## Review Cadence

Review this file before the next version cut. Update the registry, eval cases, and skill text only when field feedback shows a recurring issue or a repeated success pattern.
