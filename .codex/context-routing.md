# Context Routing

This file defines only the exceptions that need routing. The current task owner remains responsible for understanding the request, implementation, validation, and final judgment.

## Default Resolution

```text
explicit user skill/path   -> direct use
clear specialist match     -> direct use
competing specialists      -> current owner selects from the narrow table
no skill needed            -> current task owner
```

Do not pre-classify every request. Do not attach skills merely because their names are related to the topic.

Implicit invocation selects an owner from a clear natural-language intent; it does not grant write, side-effect, persistence, or external-state authority beyond the user's request and the selected skill's guardrails.

When the user explicitly asks which workflow comes next, separate the questions instead of consulting a second routing table: `docs/work_horizon_model.md` owns persistence and artifact altitude, while `docs/planning_state_model.md` admits transitions only for persisted planning artifacts. Stable work with no such boundary stays with the current task owner. Neither reference invokes a chain.

Resolve a requested skill in this order:

1. exact path supplied by the user;
2. skill exposed or installed in the current session;
3. repository-local skill root explicitly declared by the nearest project instructions or `project-context.yaml`;
4. `unresolved`.

An exact path is authoritative for discovery but does not broaden the skill's declared scope. Do not declare a skill missing from the visible list before checking an exact supplied path. Do not scan unrelated home directories, plugin versions, adjacent repositories, or guessed local harnesses as fallback.

## Narrow Routing Gate

Use `analysis-loop-readiness` only for explicit durable, repeated, event-driven, or Stop-driven execution whose readiness is not established. Otherwise the current owner selects one specialist directly and stops routing; it does not acquire evidence or attach validation, reporting, Memory, or Knowledge merely by topic.

### Technical analysis

| Dominant question | Direct owner |
| --- | --- |
| Why is behavior broken, incorrect, or recurring? | `analysis-bug` |
| Which algorithm/model/retrieval/local approach fits concrete constraints? | `analysis-algorithm` |
| What one module/interface/seam/adapter/dependency boundary should be selected? | `analysis-codebase-design` |
| Which structural/deep-module improvement candidate should come next? | `analysis-architecture-deepening` |
| What concepts, identity, states, invariants, or business rules form the domain? | `analysis-domain-modeling` |
| What measured latency/throughput/CPU/memory/query/render/startup/bundle bottleneck dominates? | `analysis-performance` |

Choose by the requested decision, not incidental nouns. Incorrect behavior beats performance unless the behavior is correct and an SLO/resource target dominates; business meaning beats code boundary for domain questions; one selected boundary beats candidate scanning. Use at most two stages serially only when the second cannot be framed before the first resolves evidence.

## Evidence Lane Selection

Route an explicit, single-domain evidence request directly: papers/citations to `search-paper-evidence`, multi-angle verification of one claim to `search-deep-evidence`, a concrete failure to `analysis-bug`, rendered UI evidence to the fitting design gate, declared Memory or Knowledge to its read harness, and an explicitly selected LLM Wiki to `analysis-llm-wiki-context`. Runtime/change evidence stays with the active task owner. If the user asks only which lane applies, the current owner returns that choice without loading a routing skill. Do not open several lanes speculatively; use `search-deep-evidence` only when the same claim genuinely requires independent lanes.

## Direct Owners

| Request | Owner |
| --- | --- |
| direct implementation or refactor | current implementation owner or one clear specialist |
| approved plan/spec execution | `workflow-plan-runner` |
| bug fix with an unclear cause | `workflow-bug-fix`; use `analysis-bug` only for the unresolved cause |
| existing implementation explanation or verified changed-line compare HTML | `report-implementation-explainer`, only on explicit explanation/compare artifact intent |
| product behavior discovery for an existing capability | `plan-behavior-discovery`, only on explicit one-question decision intent |
| unresolved decisions need a durable multi-session map | `plan-decision-map`, only on explicit decision-map intent; local Markdown unless a remote tracker is separately authorized |
| requirements discovery interview | `plan-requirements-discovery`, only on explicit interview intent; ask up to three mutually independent ready questions per round |
| one-recipient stakeholder question document | `plan-stakeholder-questionnaire`, only on explicit questionnaire artifact intent; keep external delivery separate |
| runnable prototype for one unresolved UI, interaction, state, or logic question | `workflow-prototype`; use discovery only when the question itself is not selected |
| repair the immediately preceding explanation | current task owner; replace the explanation using admitted evidence only, with no inspection or mutation |
| goal/loop contract or verifier map | `plan-loop-term`; use verifier-mapping mode for an existing `SC-NNN` slice and do not execute checks |
| short persisted plan | `plan-short-term-docs` |
| accepted loop execution | `workflow-loop-runner` after a valid loop contract |
| Memory read | current task owner using `memory-bank-harness` only for a declared, task-relevant slice |
| persistent Memory write | the explicit Memory mutation skill matching the requested operation |
| Knowledge read | current task owner using `knowledge-base-read` for declared project knowledge |
| Knowledge write | `knowledge-base-record` for one new identity, including an approved-plan decision; otherwise `knowledge-base-update` or `knowledge-base-maintenance` |
| named LLM Wiki context | `analysis-llm-wiki-context`, explicitly selected and read-only |
| project context manifest init/bootstrap/doctor or location update | `workflow-project-context` in the matching explicit mode |
| repository skill update | current implementation owner following the repository's canonical-source, generation, and validation instructions |
| existing Skill System eval maintenance | `evaluation-harness`; authored cases prove only their declared regression contract, never field quality |
| repeated failure after an attempted fix | `workflow-recovery`; do not keep stacking patches in the previous execution owner |
| explicit YAGNI, smallest-correct, or over-engineering check | attach `workflow-minimal-implementation` to the current implementation or refactor owner |
| explicit evidence-first completion control for active behavior-changing work | `workflow-rigor` as a read-only execution modifier; the current execution owner retains mutation and final synthesis |
| personal skill creation | system `skill-creator` when explicitly named or clearly requested |

Requested brevity, a status question, a correction, or a complaint does not change the task owner. A report of harm or undesired behavior is not permission to inspect or mutate external state.

## Project Context Locations

The nearest `project-context.yaml` declares project-local skill roots, Memory Bank, Knowledge Base, plans, and named LLM Wikis. Follow `.codex/docs/project_context_manifest.md` or the Claude mirror for the locator contract.

- An exact user path overrides the manifest.
- The nearest manifest wins; do not merge it with parent manifests.
- A missing declaration or missing target is `unavailable`; do not fallback-scan or auto-initialize.
- Memory, Knowledge, plans, and Wiki content are context. Current instructions and verified source evidence outrank them.
- Context admission never grants write permission or replaces the task owner.

## Memory, Knowledge, And Wiki Boundary

- Memory Bank stores cross-session working rules, recurring interaction mistakes, useful practices, and compact current state. Read only relevant active material; do not load full archives or event ledgers by default.
- Knowledge Base stores durable current project/domain/design/algorithm/architecture/code-review knowledge with direct artifact anchors, typed relations, semantic revisions, and source-traced observations. It derives recurrence dimensions without scores and is not an intermediate LLM Wiki projection or separate claim graph.
- An LLM Wiki is a separate, explicitly selected context source. Read its own guide and navigation contract; do not assume a shared schema or merge multiple Wikis.
- Persistent writes require the owning workflow. General session completion, hook events, complaints, or inferred usefulness do not authorize collection or storage.

## Execution And Runtime Boundary

- Development requests execute source work; an active plan is input, not a substitute for implementation.
- Use one `change -> validation` owner. A verifier does not become a second workflow owner.
- When delegation follows an already selected specialist, pass its exact canonical skill ID to the worker. With no upstream selection, let the worker resolve normally instead of inventing a recommendation.
- When a material semantic completion claim would rest mainly on code and checks produced by that same owner, attach `workflow-rigor` in `standard` mode and use an independent pass on the most falsifying `Contract/Spec` or `Repository/Constraints` axis when available. Medium/high-risk behavior changes may also attach it for proof depth, rollback, or readback; `strict` keeps both axes separate. Low-risk work with direct decisive observation stays self-reviewed, and harmless text/formatting or explanation-only work attaches no rigor mode.
- Invoke routine approved executables directly. Use a shell wrapper only when pipeline, redirection, globbing, or other shell semantics are required.
- Live home configuration, plugin caches, app-managed `.system` skills, and other sessions are deployment state. Modify them only on an explicit deployment or live-runtime request.
- Explicit `/goal`, automation, durable repeated execution, or Stop continuation requires loop readiness and an accepted contract before execution.

## Heavy Artifacts And Evidence

- Plans, decision maps, stakeholder questionnaires, reports, lifecycle packages, synthetic eval suites, and other heavy artifacts require explicit artifact intent. Explicit decision-map/questionnaire intent grants one local artifact, not a remote tracker write or external delivery.
- An implementation explainer proves only that a source/runtime-anchored aid was generated. Do not claim human understanding; prefer an observable scenario comparison or product decision when the task continues.
- Scenario/replay files prove only their authored contracts; they are not field-quality evidence.
- Hooks, harness records, and verifier receipts do not prove user intent and do not authorize repair.
- Use the smallest existing verifier or actual-path observation that matches the material condition. Do not create fixtures or validation infrastructure merely to obtain a stronger result label.

## Registry Boundary

Skill names, families, aliases, plugin membership, and legacy replacements belong to `docs/skill_registry.md` and skill Routing Cards. This file does not duplicate the full inventory or group matrix. Unknown or stale explicit aliases are `unresolved`; do not invent an installed skill.
