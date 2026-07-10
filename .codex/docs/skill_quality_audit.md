# Skill Quality Audit

Date: 2026-07-09
Bundle: 9.1.0
Scope: the 66 current canonical `source/skills/*/SKILL.md` packages.

This is a maintenance record, not routing context. Do not load it during normal skill selection. App-managed system skills and seven pre-commit skills already removed by consolidation are outside scope. Earlier evidence-complete revisions were credited and revalidated rather than rewritten.

## Audit Standard

Each current skill was checked for:

1. a distinct user outcome and execution owner;
2. positive and negative trigger boundaries;
3. minimum default context and conditional reference admission;
4. decision rules that discriminate behavior rather than reward static inventory;
5. proportional output rather than mandatory report sections;
6. evidence limits and anti-reward-hacking behavior;
7. positive, negative, or edge regression coverage;
8. repository metadata and generated-target consistency.

`revised` means the current pass changed semantic instructions, runtime contracts, or context/output cost. `prior + revalidated` means an earlier revision in the 9.1.0 pass was retained and included in focused/core validation. `retained` means the file was read and no semantic change was justified; metadata may still have been shortened.

## Per-Skill Decisions

### Analysis

| skill | decision | audit result |
| --- | --- | --- |
| `analysis-algorithm` | revised | Candidate count and report depth now follow genuine trade-offs; causal validation replaces fixed templates/metrics. |
| `analysis-architecture-deepening` | prior + revalidated | Narrow candidate-ranking owner remains distinct from targeted design and full reports. |
| `analysis-bug` | revised | Hypothesis depth and fix comparison are conditional; static leads cannot self-confirm runtime causes. |
| `analysis-codebase-design` | prior + revalidated | Targeted boundary/deep-module decisions remain separate from full report generation. |
| `analysis-codebase` | prior + revalidated | Semantic comparison requires runtime/contract evidence; framework-name differences do not count as logic differences. |
| `analysis-domain-modeling` | retained | Domain language, invariant, and state-model ownership is distinct and already proportional. |
| `analysis-performance` | retained | Measurement-first bottleneck selection is distinct; UI metadata was shortened. |
| `analysis-router` | prior + revalidated | Specialist and hybrid routing boundaries remain explicit. |

### Coordination And Design

| skill | decision | audit result |
| --- | --- | --- |
| `coordination-handoff` | prior + revalidated | Consolidated DAG/handoff/lock-scope owner remains support-only; metadata was shortened. |
| `design-a11y-audit` | revised | Narrow checks no longer force a full audit schema; interaction evidence remains separate from static hints. |
| `design-component-mapper` | revised | Output is scoped to relevant components/states instead of theoretical exhaustive matrices. |
| `design-frontend` | prior + revalidated | Mobile/dashboard/section profiles remain conditional inside one implementation owner. |
| `design-layout-translator` | revised | Removed internal routing-governance output and made the layout contract proportional. |
| `design-tokens` | revised | Single-surface gaps no longer expand into exhaustive token-system artifacts. |
| `design-ui-decomposer` | revised | Removed governance checklist leakage and made one-screen analysis compact. |
| `design-visual-regression` | revised | One screenshot/viewport check no longer forces a full fidelity report. |

### Evaluation, Kanboard, And Knowledge

| skill | decision | audit result |
| --- | --- | --- |
| `evaluation-harness` | prior + revalidated | Case-quality review remains separate from usage telemetry and release verdicts. |
| `evaluation-usage-tracker` | revised | Sanitized metadata, denominators, no-data behavior, and non-causal count interpretation are explicit. |
| `kanboard-plan-ops` | retained | Existing-board push/pull/validation ownership remains distinct; metadata was shortened. |
| `kanboard-plan-rollout` | retained | Onboarding/bulk-sync ownership remains distinct; metadata was shortened. |
| `knowledge-base-maintenance` | revised | Per-item decisions and post-write projection/store validation are required. |
| `knowledge-context-harness` | revised | Live task store replaces test fixtures; exact CLI inputs, actual mode, no-hit behavior, and measured pack size are explicit. |

### Loop And Memory

| skill | decision | audit result |
| --- | --- | --- |
| `loop-readiness-router` | prior + revalidated | One-shot/checkpoint/LoopRun readiness remains a routing decision, not an executor. |
| `loop-verifier-registry` | prior + revalidated | Verifier mapping remains fail-closed and cannot self-pass from artifact presence. |
| `memory-bank-correction-capture` | revised | Only recurring project mistakes are captured; stored goal/rule correction routes to update. |
| `memory-bank-harness` | revised | Global guides became conditional; inline/no-write default and measured context size are explicit. |
| `memory-bank-ingestion` | revised | Approved packets map all candidates to canonical entities through one all-or-no-write transaction. |
| `memory-bank-init` | revised | Fresh init is atomic; reinitialization cannot silently destroy accepted history. |
| `memory-bank-maintenance` | revised | Read-only modes and write-producing mistake consolidation are separated. |
| `memory-bank-update` | revised | Goal/rule mutation uses stable operation IDs, replay, and cross-file post-validation. |

### Planning And Reporting

| skill | decision | audit result |
| --- | --- | --- |
| `plan-long-term-package` | prior + revalidated | Explicit package intent, claim ledger, behavior oracles, and conditional archetype loading remain required. |
| `plan-loop-term` | prior + revalidated | Loop completion terms remain distinct from broad planning and execution. |
| `plan-requirements-brief` | prior + revalidated | Requirements contract remains distinct from discovery and implementation. |
| `plan-requirements-discovery` | prior + revalidated | Human-in-loop elicitation remains conditional on real requirement uncertainty. |
| `plan-short-term-docs` | prior + revalidated | Small plan artifact ownership and behavior evidence remain scoped. |
| `plan-spec-curator` | prior + revalidated | Context governance remains support-only and does not execute plans or mutate memory. |
| `report-critical` | prior + revalidated | Findings-first critical review remains separate from implementation and qualitative scoring. |
| `report-diff` | prior + revalidated | Readable semantic diff reporting remains support-only. |
| `report-lifecycle-artifacts` | prior + revalidated | Heavy lifecycle packages remain explicit-only and do not claim implementation. |
| `report-qualitative` | prior + revalidated | Compact evidence-first default remains separate from full/scored mode and static-presence rewards. |

### Research And Search

| skill | decision | audit result |
| --- | --- | --- |
| `research-experiment-blueprint` | revised | Selected claims become identifiable protocols with experimental units, controls, leakage, matched metrics, and falsifiers. |
| `research-experiment-scaffold` | revised | Approved equivalent specs become repo-native minimal runnable code with synthetic smoke evidence. |
| `research-hypothesis-planning` | revised | Raw premises become falsifiable decision targets and cheap Stage-0 discriminators before blueprints. |
| `research-literature-ideation` | revised | Observed gaps, corpus coverage gaps, and speculation are distinct; selection is conditional. |
| `research-literature-synthesis` | revised | Evidence directness/design/independence replace paper-count consensus. |
| `research-manuscript-writing` | revised | Claim-to-evidence prose separates planned methods, observed results, and citation gaps. |
| `research-peer-review` | revised | Anchored findings ordered by scientific consequence replace fixed review-section boilerplate. |
| `research-router` | prior + revalidated | Search, research stage, and ordinary development boundaries remain explicit. |
| `research-statistical-analysis` | revised | Estimand, analysis unit, dependence, reproducible computation, and no-data abstention are required. |
| `search-deep-evidence` | revised | Claim matrices preserve contradiction and source dependence; majority voting and confirmation-only convergence were removed. |
| `search-paper-evidence` | revised | Acquisition, source identity, evidence basis, provenance, and claim relation are separate. |
| `search-router` | prior + revalidated | Cross-domain evidence routing remains a router and does not own synthesis. |

### Repository And Execution Workflows

| skill | decision | audit result |
| --- | --- | --- |
| `skill-system-repo-adapter` | prior + revalidated | Repository projection remains support-only; semantic authoring stays with the primary owner. |
| `workflow-bug-fix` | retained | Direct failure repair remains distinct from RCA-only and recovery; metadata was shortened. |
| `workflow-comment-maintenance` | retained | Comment/docstring-only behavior-preserving scope and public-contract guard are distinct. |
| `workflow-dependency-upgrade` | retained | Manifest/lockfile/migration scope and network/lifecycle boundaries are distinct; metadata was shortened. |
| `workflow-implementation` | retained | Direct implementation owner remains goal-first and proportionally validated. |
| `workflow-loop-runner` | prior + revalidated | Accepted LoopRun execution remains verifier/checkpoint/stop governed. |
| `workflow-minimal-implementation` | prior + revalidated | YAGNI pressure remains a conditional modifier, not a correctness owner. |
| `workflow-plan-runner` | prior + revalidated | Batch, phase, and plan completion remain separate and evidence-gated. |
| `workflow-recovery` | prior + revalidated | Repeated same-signature failure uses one active hypothesis and original success signal. |
| `workflow-refactor-safely` | retained | Behavior contract and characterization batches remain distinct; metadata was shortened. |
| `workflow-rigor` | prior + revalidated | Lite/standard/strict evidence depth remains a modifier and does not reimplement work. |
| `workflow-source-maintenance` | retained | Evidence-backed safe deletion remains distinct from structural refactor and feature work. |
| `workflow-task-ledger` | revised | Explicit resumption risk—not step count—now controls activation. |
| `workflow-validation` | revised | Support attaches only when validation selection is materially non-obvious. |

## Remaining Field Risks

- Static and replay tests cannot establish every model-output improvement; real forward runs remain the maturity signal.
- Memory Bank writers now share a transaction contract, but a dedicated executable Memory Bank transaction/validator runtime is still a future hardening opportunity.
- Research/search evidence schemas now resist confirmation-only convergence; legacy external ledgers require migration to schema v2.
- Context surface measurements are advisory characters/words/heuristics, not billed-token telemetry.
