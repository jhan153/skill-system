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

Do not invoke a classifier for `/goal`, duration, automation, or repeated wording. The current owner uses `plan-execution-handoff` only when durable execution state is actually needed and attaches its repeated-work profile only when verifier evidence will steer later actions more than once. Otherwise select one specialist directly and stop routing; do not acquire evidence or attach validation, reporting, Memory, or Knowledge merely by topic.

### Technical analysis

| Dominant question | Direct owner |
| --- | --- |
| Why is a concrete failure occurring, with no repair requested? | current task owner, read-only causal diagnosis; no specialist skill |
| Which algorithm/model/retrieval/local approach fits concrete constraints? | `analysis-algorithm` |
| What one module/interface/seam/adapter/dependency boundary should be selected? | `analysis-boundary-design` |
| What coherent target/transition architecture should satisfy accepted quality scenarios across several interacting boundaries? | `workflow-architecture-design` |
| Which structural/deep-module improvement candidate should come next? | `analysis-architecture-deepening` |
| What concepts, identity, states, invariants, or business rules form the domain? | `analysis-domain-modeling` |
| What measured latency/throughput/CPU/memory/query/render/startup/bundle bottleneck dominates? | `analysis-performance` |

Choose by the requested decision, not incidental nouns. The word “architecture” alone does not
select target design: current maps, one-boundary decisions, candidate scans, and normative
multi-view design retain separate owners. Incorrect behavior beats performance unless the behavior
is correct and an SLO/resource target dominates; business meaning beats code boundary for domain
questions; one selected boundary beats candidate scanning. Use at most two stages serially only
when the second cannot be framed before the first resolves evidence.

An accepted `architecture_design` does not move every later boundary question back to Architecture
Design. Route one explicitly assigned atomic boundary to `analysis-boundary-design`, which preserves
the relevant accepted constraints. Route back to `workflow-architecture-design` only when the
decision changes coupled views/owners or an accepted architecture constraint.

Programming-paradigm wording alone does not select Architecture Design. Route subsystem-wide
composition or a choice that crosses the shared architecture-impact gate to
`workflow-architecture-design` when its decision owner is `coupled_architecture`; route one
architecture-material public/module/API/ABI boundary to `analysis-boundary-design`; keep
`local_implementation` function/class/layout/RAII/scheduling realization with
`workflow-implementation`.

## Evidence Lane Selection

Route an explicit, single-domain evidence request directly: papers/citations to `search-paper-evidence`, multi-angle verification of one claim to `search-deep-evidence`, diagnosis-only concrete failures to the current task owner under the read-only boundary, rendered UI evidence to the fitting design gate, declared Memory or Knowledge to its read harness, and an explicitly selected LLM Wiki to `analysis-llm-wiki-context`. Runtime/change evidence stays with the active task owner. If the user asks only which lane applies, the current owner returns that choice without loading a routing skill. Do not open several lanes speculatively; use `search-deep-evidence` only when the same claim genuinely requires independent lanes.

## Direct Owners

| Request | Owner |
| --- | --- |
| direct implementation or refactor | current implementation owner or one clear specialist |
| ordinary single-stage Research artifact | the narrow `research-*` specialist matching the requested artifact; do not add a node manager |
| accepted Plan-assigned `RES-*` node | `workflow-research` plus exactly one stage skill already selected by the Plan; neither selects a successor |
| approved plan/spec execution | the current Orchestrator follows an existing canonical Plan/Handoff; without one, route one bounded approved slice to its task-specific workflow |
| concrete failure repair, including an unclear cause | `workflow-bug-fix`; DAG input owns one assigned intervention/result, while direct standalone repair may own at most two locally reviewed rounds |
| static code review of a bound implementation or diff | `workflow-code-review`; bind intent/material effects, run design-first risk selection, keep source-linked Mermaid evidence, and return a scoped standalone disposition or cross-owner Core result without selecting a successor |
| existing implementation explanation or verified changed-line comparison report | `report-implementation-explainer`, only on explicit explanation/compare artifact intent; Markdown is default and HTML is optional |
| product behavior discovery for an existing capability | `plan-behavior-discovery`, only on explicit one-question decision intent |
| human-owned test judgment surfaced by Test Design | `plan-test-discovery`, only from a named blocked test condition with evidence/options; it records decisions but never designs or implements the test |
| software Test Design after an executable SUT or accepted external contract exists | `workflow-test-design`; use only the material testing specialists selected by its actual/contract boundary, scenario, oracle, or evidence question; visual regression is explicit `design` mode |
| test-only implementation and scoped execution | `workflow-test-implementation`; direct mode requires a complete authoritative inline contract, otherwise consume Core `test_design_result`; visual regression is explicit `evidence` mode |
| bounded false-green or test-evidence credibility review | `test-evidence-review`; it reviews authority/path/oracle/falsifier/proof ceiling without repair or product-quality claims |
| unresolved decisions need a durable multi-session map | `plan-decision-map`, only on explicit decision-map intent; local Markdown unless a remote tracker is separately authorized |
| requirements discovery interview | `plan-requirements-discovery`, only on explicit interview intent; ask up to three mutually independent ready questions per round |
| one-recipient question document | `plan-question-document`, only on explicit question-document artifact intent; keep external delivery separate |
| runnable prototype for one unresolved UI, interaction, state, or logic question | `workflow-prototype`; use discovery only when the question itself is not selected |
| repair the immediately preceding explanation | current task owner; replace the explanation using admitted evidence only, with no inspection or mutation |
| goal/repeated-work terms or verifier map | `plan-execution-handoff` with its conditional repeated-work principles; author conditions and graph terms without executing checks |
| persisted execution plan | `plan-execution-handoff`; use `single_node_execution` for one durable executable node |
| durable canonical Plan/Handoff pair | `plan-execution-handoff`, only on explicit pair, long-running execution DAG, graph-method/ownership/lock routing, advisory timing, or cross-session continuation intent; typed timing is inspected once at `worker_done`, never enforced by polling; `phase_gate_delivery` terminates at `human_test_ready` and later Test results/worklist/design start a new Waterfall |
| accepted verifier-steered execution | let the Orchestrator follow the bounded DAG copied into the accepted `plan-execution-handoff` pair |
| Memory read | current task owner using `management-memory-bank-harness` only for a declared, task-relevant slice |
| persistent Memory write | the explicit Memory mutation skill matching the requested operation |
| Knowledge read | current task owner using `management-knowledge-base-read` for declared project knowledge |
| Knowledge write | `management-knowledge-base-record` for one new identity, including an approved-plan decision; otherwise `management-knowledge-base-update` or `management-knowledge-base-maintenance` |
| named LLM Wiki context | `analysis-llm-wiki-context`, explicitly selected and read-only |
| project context manifest init/bootstrap/doctor or location update | `management-project-context` in the matching explicit mode |
| repository skill update | current implementation owner following the repository's canonical-source, generation, and validation instructions |
| existing Skill System eval maintenance | current implementation owner; authored cases prove only their declared regression contract, never field quality |
| same problem after a reviewed repair attempt | preserve attempt history; a DAG repair runs only its explicitly assigned `BF1/A1` or `BF2/A2` node and returns evidence to Code Review/Coordinator, while standalone repair may use its remaining bounded round |
| explicit evidence-first completion control for active behavior-changing work | the current execution owner applies `docs/execution_assurance_contract.md`; assurance remains read-only and non-node while that owner retains mutation and final synthesis |
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
- Test Design and Test Implementation are explicit owners, not automatic post-implementation
  attachments. A failing test condition is evidence, not repair authority; the Coordinator or
  direct task owner applies the accepted repair/design/decision boundary.
- When delegation follows an already selected specialist, pass its exact canonical skill ID to the worker. With no upstream selection, let the worker resolve normally instead of inventing a recommendation.
- When a material semantic completion claim would rest mainly on code and checks produced by that same owner, apply `docs/execution_assurance_contract.md` in `standard` mode and use an independent pass on the most falsifying `Contract/Spec` or `Repository/Constraints` axis when available. High-risk behavior changes may use `strict` for separate axes plus rollback/readback. Low-risk work uses the global evidence baseline without an assurance mode. Assurance never owns writes, Core cards, or Plan successors.
- Invoke routine approved executables directly. Use a shell wrapper only when pipeline, redirection, globbing, or other shell semantics are required.
- Live home configuration, plugin caches, app-managed `.system` skills, and other sessions are deployment state. Modify them only on an explicit deployment or live-runtime request.
- Explicit `/goal`, automation, or Stop continuation does not itself select a workflow. Durable verifier-steered execution requires an accepted `plan-execution-handoff` pair; ordinary work stays with its direct owner.

## Heavy Artifacts And Evidence

- Plans, decision maps, recipient question documents, reports, lifecycle packages, synthetic eval suites, and other heavy artifacts require explicit artifact intent. Explicit decision-map/question-document intent grants one local artifact, not a remote tracker write or external delivery.
- An implementation explainer proves only that a source/runtime-anchored aid was generated. Do not claim human understanding; prefer an observable scenario comparison or product decision when the task continues.
- Scenario/replay files prove only their authored contracts; they are not field-quality evidence.
- Hooks, harness records, and verifier receipts do not prove user intent and do not authorize repair.
- Use the smallest existing verifier or actual-path observation that matches the material condition. Do not create fixtures or validation infrastructure merely to obtain a stronger result label.

## Registry Boundary

Current skill names, families, family aliases, and plugin membership belong to
`docs/skill_registry.md`, plugin manifests, and skill Routing Cards. This file does not duplicate
the inventory or group matrix. Unknown or stale skill IDs are `unresolved`; do not invent an
installed replacement.
