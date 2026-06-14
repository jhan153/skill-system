# Skill Registry

Maturity values must be one of `skeleton`, `usable`, `field_tuned`, `experimental`, or `deprecated`.

## Registry

| skill | cluster | maturity | primary use | do_not_use_when | improvement_track |
| --- | --- | --- | --- | --- | --- |
| `accessibility-audit-harness` | design | `experimental` | Review keyboard, focus, semantic, contrast, target-size, and responsive readability evidence for implemented UI. | Backend-only work, token-only work, or requests without a concrete UI target. | Add concrete keyboard, focus, contrast, and responsive cases from real projects. |
| `agent-critical-review` | review_quality | `usable` | Evidence-first review, blocker diagnosis, QA-style critique. | The user wants implementation only and no review. | Add more negative cases for over-review and lightweight final checks. |
| `artifact-librarian` | coordination | `experimental` | Summarize task artifacts and verification notes. | A persistent registry, event log, or evidence workflow would be needed. | Keep it response-first; add examples for small handoff inventories. |
| `codebase-intel-report` | codebase_analysis | `experimental` | Build broad codebase reports when explicitly requested. | Single-bug, narrow implementation, or quick review tasks. | Tighten report trigger language and add smaller report modes only if field feedback supports it. |
| `component-contract-mapper` | design | `experimental` | Map design components, variants, states, slots, events, and responsive behavior to repo components. | Generic design critique, backend-only implementation, or full visual implementation ownership. | Add examples from Figma/spec-to-component mapping. |
| `create-skill-pack` | skill_lifecycle | `usable` | Create, harden, migrate, deprecate, or register custom skills. | The user is executing an existing skill rather than modifying skill assets. | Add more route registration and negative-routing examples. |
| `deep-algorithm-proposal` | analysis | `usable` | Compare technical approaches and choose a fit under constraints. | A concrete bug must be diagnosed first. | Add more examples separating algorithm choice from implementation. |
| `deep-analysis-workflow` | analysis_router | `usable` | Route deep analysis requests to bug or algorithm workflows. | Casual exploration or direct implementation with no analysis request. | Improve hybrid bug-plus-algorithm examples. |
| `deep-bug-analysis` | analysis | `usable` | Reproduce and diagnose recurring or high-risk failures. | The user only asks for a direct implementation with clear cause. | Add examples for repeated failure isolation and anti-fake-fix checks. |
| `dashboard-ui-implementation` | design | `experimental` | Apply dashboard surface constraints for KPI hierarchy, filters, charts, tables, density, async states, and operational accessibility. | Generic design-to-code, marketing pages, mobile-native screens, backend analytics, or evidence-only requests. | Keep explicit-only until field feedback proves it should trigger without direct invocation. |
| `design-to-frontend` | design | `usable` | Implement concrete visual designs as real frontend code. | Design critique, product ideation, backend-only work, or explanation-only tasks. | Add field cases for responsive behavior, assets, and browser verification. |
| `design-token-pipeline` | design | `experimental` | Normalize token sources, platform mappings, gaps, conflicts, and no-fabrication token evidence. | No token source or target platform exists, or the user expects invented token values. | Add token schema examples and repo integration cases. |
| `eval-harness` | usage_quality | `experimental` | Review `.codex/eval` runtime usage cases. | The user wants package approval, scoring, or readiness decisions. | Keep it case-review oriented; add schema consistency examples. |
| `goal-workflow-orchestrator` | coordination | `experimental` | Produce lightweight task DAG or handoff notes from an existing plan. | The word goal/목표 appears without explicit DAG, handoff, lock-scope, or coordination intent. | Track whether it still over-triggers; consider renaming if field feedback shows ambiguity. |
| `layout-constraint-translator` | design | `experimental` | Translate Auto Layout, flex/grid, sizing, overflow, and breakpoint constraints into implementation-ready layout rules. | Full UI implementation, screenshot-diff-only, component-state-only, or backend-only requests. | Keep implicit invocation disabled; add field cases for constraint translation attached to `design-to-frontend`. |
| `memory-bank-correction-capture` | memory | `usable` | Capture explicit user corrections as candidate memory. | The user did not ask for memory mutation. | Add examples for masking sensitive evidence. |
| `memory-bank-harness` | memory | `usable` | Compile task-specific context from accepted memory while filtering risky entries. | No memory context is needed or memory use is not explicit. | Add stale/conflict/poison-risk examples. |
| `memory-bank-init` | memory | `usable` | Initialize project-scoped memory when explicitly requested. | The user did not ask to start persistent memory. | Add safer initialization prompts and conflict handling examples. |
| `memory-bank-maintenance` | memory | `usable` | Inspect, validate, and consolidate memory state. | The request is ordinary implementation or analysis. | Add more conflict resolution and stale review cases. |
| `memory-bank-update` | memory | `usable` | Update persistent goals or rules with append-only history. | The user is only giving temporary task instructions. | Improve temporary-vs-persistent routing examples. |
| `mobile-screen-implementation` | design | `experimental` | Apply mobile/native screen constraints for safe areas, navigation, keyboard overlays, touch targets, scroll regions, states, and mobile accessibility. | Generic design-to-code, desktop-only dashboards, section-based web pages, or evidence-only requests. | Keep explicit-only until repeated mobile implementation field feedback is available. |
| `multi-agent-plan-executor` | coordination | `experimental` | Split explicit multi-agent work into handoff and lock-scope notes. | One agent can do the work directly or ownership is unclear. | Add real handoff examples without persistent workflow files. |
| `phase-subplan-workflow` | planning | `experimental` | Create large multi-document planning packages when explicitly requested. | A single plan doc, TODO list, summary, or direct implementation is enough. | Keep negative cases for keyword-only phase/migration/rewrite requests and prefer `plan-doc-workflow` for one-file plans. |
| `plan-doc-workflow` | planning | `usable` | Create or update persisted `docs/plan` artifacts. | The user only uses "plan" casually or asks for direct implementation. | Add more implementation-transition examples. |
| `readable-diff-report` | output | `usable` | Present actual changed lines in readable grouped diff form. | No diff or change snapshot exists. | Add examples for large but still scoped diffs. |
| `research-experiment-blueprint` | research | `usable` | Create experiment blueprints from selected hypotheses. | No selected hypothesis or research plan exists. | Add more checkpoint-first and falsification examples. |
| `research-experiment-scaffold` | research | `experimental` | Generate minimal experiment skeletons from approved blueprints. | No approved blueprint or write boundary exists. | Add no-download, no-training smoke-test cases. |
| `research-hypothesis-planning` | research | `usable` | Plan research hypotheses, ablations, loss design, and training plans. | The request is ordinary implementation of an already chosen method. | Add more premise-triage examples. |
| `research-literature-ideation` | research | `usable` | Generate candidate hypotheses from evidence and select one active hypothesis. | Evidence has not been acquired or the user only wants search. | Add examples separating gaps from claims. |
| `research-literature-synthesis` | research | `usable` | Turn evidence ledgers or papers into literature review synthesis. | The user wants experiment code or manuscript writing. | Add contradiction and limitation templates. |
| `research-manuscript-writing` | research | `usable` | Draft or revise manuscript sections from verified research artifacts. | Citations, results, or evidence are missing and cannot be marked. | Add more citation-status and unverified-claim patterns. |
| `research-paper-evidence-search` | research | `usable` | Search or plan searches and build evidence ledgers without fabricated citations. | The user wants code implementation or manuscript prose only. | Add current-source verification and citation-status examples. |
| `research-peer-review` | research | `usable` | Critique manuscripts, proposals, and research plans. | The user asks for implementation or literature search only. | Add more reproducibility and ethics/reporting examples. |
| `research-router` | research_router | `usable` | Route scientific research requests to narrow research skills. | Non-research development work. | Add negative cases for model/loss terms in ordinary implementation. |
| `research-statistical-analysis` | research | `usable` | Analyze result tables and metrics with statistical rationale. | No data exists and the user expects statistical conclusions. | Add planned-vs-exploratory examples. |
| `section-based-web-implementation` | design | `experimental` | Apply section-page constraints for hero, semantic sections, CTA flow, responsive order, media placement, first-viewport signal, and text fitting. | App/tool first screens, dense dashboards, mobile-native screens, or evidence-only requests. | Keep explicit-only until repeated section-page field feedback is available. |
| `spec-and-plan-curator` | coordination | `experimental` | Curate active context, close stale plans, and propose memory/archive load policy. | Substantive task execution, normal plan docs, direct memory mutation, or ordinary summaries. | Add field cases for stale-plan pruning, instruction-bloat reduction, and closeout distillation. |
| `strict-evidence-driven-reporting-workflow` | execution_control | `usable` | Control evidence-first implementation and split validation for risky changes. | The task is simple and no formal evidence mode is needed. | Add smaller mode examples to avoid heavy output. |
| `strict-response-quality` | output | `usable` | Produce formal evidence-first replies when explicitly requested. | The user did not ask for formal reporting. | Add examples for concise formal responses. |
| `ui-reference-decomposer` | design | `experimental` | Decompose UI references into hierarchy, layout regions, component candidates, token candidates, states, and validation needs. | Direct implementation, token-only, screenshot-diff-only, or product strategy requests. | Keep implicit invocation disabled; collect field cases before broader routing. |
| `visual-regression-harness` | design | `experimental` | Inspect rendered screenshots, nonblank/framing evidence, viewport behavior, and visual differences. | There is no rendered UI, screenshot target, or visual reference/acceptance criteria. | Add Playwright/browser examples and threshold guidance. |

## Cluster Notes

- Research cluster is preserved as a narrow multi-skill cluster with `research-router` as the routing entry.
- Design cluster is expected to grow like the research cluster, but only through narrow specialist skills.
- 7.0 coordination concepts remain only as lightweight support skills.
- `spec-and-plan-curator` is a context-governance support skill, not a task executor or memory mutator.
- Heavy artifact-producing skills require explicit artifact intent.

## Maturity Review Rules

- New specialist design skills start as `skeleton` only when they are documented candidates without an operational workflow; otherwise start as `experimental` with narrow routing.
- `design-to-frontend` remains `usable`.
- Broad orchestration or package-like skills should not be upgraded without field feedback.
- Maturity changes should be backed by `FIELD_FEEDBACK.md` entries or runtime usage eval updates.
- A maturity increase requires repeated successful field feedback, not just passing bundle hygiene.
- A maturity decrease is allowed after one severe over-trigger, unsafe context load, or repeated output-shape mismatch.
- Surface-specific implementation skills are active `experimental` skills, but remain explicit-only until field feedback proves implicit invocation is safe.
- Analysis skills with workflow/output/validation sections may be `experimental` even before field tuning, but must keep conservative routing until real-use feedback exists.
