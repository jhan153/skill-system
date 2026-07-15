# Skill Quality Audit

Date: 2026-07-15
Bundle: 9.2.0 (local release cut)
Scope: the 66 current canonical `source/skills/*/SKILL.md` packages.

This is a maintenance record, not routing context. Do not load it during normal skill selection. App-managed system skills and seven pre-commit skills already removed by consolidation are outside scope. Historical 9.1.1 release-forward evidence and the unpublished 9.1.2 pre-diet baseline retain their original labels; neither is relabeled as 9.2.0 evidence.

## 9.2.0 Skill Diet Result

All 66 canonical skill bodies were reduced from 49,513 to 39,820 whitespace-delimited words (-9,693, -19.58%) and from 372,882 to 310,450 UTF-8 bytes (-62,432, -16.74%), excluding YAML frontmatter. The wider owned inventory, including existing references, fell from 132,280 to 122,482 words and from 1,196,415 to 1,133,065 bytes.

The T9 disposition pass resolved 38 merge/delete candidates as 32 merges and 6 deletions. No candidate was counted as reduced by moving text into a reference, and none remained `retained-unverified`. Generated-target agreement, core validation, focused behavior evidence, and recorded reviewer receipts remain scoped evidence: they do not establish universal output equivalence for every skill or unseen task.

The campaign figures use the frozen Git-object baseline at `7484956`. The earlier 9.1.2 audit measurement below predates the subsequent `analysis-router` depth-boundary clarification, so its 49,502-word/372,785-byte body total is retained as historical audit data rather than silently rewritten.

## 9.1.2 Pre-Diet Baseline

The 66 canonical `source/skills/*/SKILL.md` files are frozen for later 9.2.0 before/after comparison at:

- 52,199 whitespace-delimited words and 394,611 UTF-8 bytes across complete `SKILL.md` files;
- 49,502 words and 372,785 bytes after excluding YAML frontmatter;
- 15,220 body words in the 66 `Routing Card` sections;
- 18,389 characters and 2,367 whitespace-delimited words in frontmatter descriptions.

Words are counted as non-whitespace spans and bytes as UTF-8 encoded bytes. These are measured instruction surfaces, not tokenization or billing measurements. A smaller 9.2.0 result is acceptable only when the paired positive and negative/edge behavior contracts remain satisfied; moving content into eagerly admitted references does not count as a reduction.

The reproducible per-skill inventory and comparison rules are defined in `skill_diet_protocol.md` and `.codex/eval/baselines/skill-diet-9.1.2.yaml`. The initial coverage audit records 263 declared eval cases, 77 schema-v2 cases, structured primary contracts for 34 of 66 skills, observable structured-positive candidates for 3 skills, structured-negative candidates for 53 skills, explicit edge ownership for 0 skills, and zero fresh 9.1.2 observed runs. The evidence schema now supports source/oracle/run/output/verifier binding, but behavior and actual admitted context remain explicitly unverified until those missing contracts and receipts are populated.

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

`revised` means the current pass changed semantic instructions, runtime contracts, or context/output cost. `prior + revalidated` means an earlier evidence-complete revision was retained and included in focused/core validation through the 9.1.2 source baseline. `retained` means the file was read and no semantic change was justified; metadata may still have been corrected.

## Pre-Diet Per-Skill Decisions

The table below preserves the 9.1.2 ownership and behavior audit. The 9.2.0 size and merge/delete dispositions are recorded separately above and in the skill-diet protocol artifacts; this table is not retroactively rewritten into per-skill semantic-equivalence proof.

### Analysis

| skill | decision | audit result |
| --- | --- | --- |
| `analysis-algorithm` | revised | Candidate count and report depth now follow genuine trade-offs; causal validation replaces fixed templates/metrics. |
| `analysis-architecture-deepening` | prior + revalidated | Narrow candidate-ranking owner remains distinct from targeted design and full reports. |
| `analysis-bug` | revised | Hypothesis depth and fix comparison are conditional; static leads cannot self-confirm runtime causes. |
| `analysis-codebase-design` | prior + revalidated | Targeted boundary/deep-module decisions remain separate from full report generation. |
| `analysis-codebase` | revised | Semantic comparison remains evidence-bound; C/C++ structure now records `Not evidenced` and fails closed until a compilation-aware symbol/class/call index exists. |
| `analysis-domain-modeling` | retained | Domain language, invariant, and state-model ownership is distinct and already proportional. |
| `analysis-performance` | retained | Measurement-first bottleneck selection is distinct; routing metadata is host-neutral. |
| `analysis-router` | prior + revalidated | Specialist and hybrid routing boundaries remain explicit. |

### Coordination And Design

| skill | decision | audit result |
| --- | --- | --- |
| `coordination-handoff` | prior + revalidated | Consolidated DAG/handoff/lock-scope owner remains support-only; metadata was shortened. |
| `design-a11y-audit` | revised | Narrow checks no longer force a full audit schema; interaction evidence remains separate from static hints. |
| `design-component-mapper` | revised | Output stays scoped while requiring app-surface import/use evidence for approved-catalog reuse and explicit exception boundaries. |
| `design-frontend` | revised | Surface profiles remain conditional; product-family, component-reuse, and open UX-decision gates now fail closed only when applicable. |
| `design-layout-translator` | revised | Removed internal routing-governance output and made the layout contract proportional. |
| `design-tokens` | revised | Single-surface gaps no longer expand into exhaustive token-system artifacts. |
| `design-ui-decomposer` | revised | Removed governance checklist leakage and made one-screen analysis compact. |
| `design-visual-regression` | revised | Narrow checks remain proportional while exact-target fidelity and pinned family-coherence claims use separate evidence lanes. |

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
| `plan-long-term-package` | revised | Final manifests default to a 20-artifact preflight cap, explicit reasoned escalation, canonical-first staged materialization, and no empty ingest artifact. |
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
| `workflow-bug-fix` | retained | Direct failure repair remains distinct from RCA-only and recovery; routing metadata is host-neutral. |
| `workflow-comment-maintenance` | retained | Comment/docstring-only behavior-preserving scope and public-contract guard are distinct. |
| `workflow-dependency-upgrade` | retained | Manifest/lockfile/migration scope and network/lifecycle boundaries are distinct; routing metadata is host-neutral. |
| `workflow-implementation` | retained | Direct implementation owner remains goal-first and proportionally validated; routing metadata is host-neutral. |
| `workflow-loop-runner` | prior + revalidated | Accepted LoopRun execution remains verifier/checkpoint/stop governed. |
| `workflow-minimal-implementation` | prior + revalidated | YAGNI pressure remains a conditional modifier, not a correctness owner. |
| `workflow-plan-runner` | prior + revalidated | Batch, phase, and plan completion remain separate and evidence-gated. |
| `workflow-recovery` | prior + revalidated | Repeated same-signature failure uses one active hypothesis and original success signal. |
| `workflow-refactor-safely` | retained | Behavior contract and characterization batches remain distinct; routing metadata is host-neutral. |
| `workflow-rigor` | prior + revalidated | Lite/standard/strict evidence depth remains a modifier and does not reimplement work. |
| `workflow-source-maintenance` | retained | Evidence-backed safe deletion remains distinct from structural refactor and feature work. |
| `workflow-task-ledger` | revised | Explicit resumption risk—not step count—now controls activation. |
| `workflow-validation` | revised | Support attaches only when validation selection is materially non-obvious. |

## Remaining Field Risks

- Static and replay tests cannot establish every model-output improvement; real forward runs remain the maturity signal.
- Memory Bank writers now share a transaction contract, but a dedicated executable Memory Bank transaction/validator runtime is still a future hardening opportunity.
- Research/search evidence schemas now resist confirmation-only convergence; legacy external ledgers require migration to schema v2.
- Context surface measurements are advisory characters/words/heuristics, not billed-token telemetry.
