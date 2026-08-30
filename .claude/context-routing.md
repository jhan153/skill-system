# Context Routing

This file is the operational routing reference for the Claude harness. It preserves the 9.2.1 structured decision model independently from the compact Codex router.

## Custom Skill Scope
`.claude/skills/.system`, live home runtime directories, and plugin caches are app-managed or deployment state. Skill System repository changes apply to canonical `source/` assets first and use repository generators for targets. Do not audit, patch, migrate, deprecate, route-register, or smoke-test `.system` skills as repository work.

## Mode Separation
Development / Implementation Mode:
- Use for coding, refactoring, bug fixing, implementation plans, repo work, tests, scripts, APIs, build/lint/test tasks.
- Treat user-provided requirements, keywords, file names, APIs, metrics, and implementation constraints as task specifications unless they are ambiguous, impossible, unsafe, contradictory, or conflict with repo rules.
- Do not perform broad premise skepticism by default.
- Do not route to `research-hypothesis-planning` just because the user mentions "experiment", "approach", "model", "loss", or "metric" in a development context.
- Prefer concrete execution, verification, and repo validation.
- Direct implementation commands such as `구현해`, `작업해`, `플랜대로 구현`, `fix`, or
  `refactor` stay in Development / Implementation Mode even when an active plan document exists.
  Standalone `add tests` routes to `workflow-test-implementation` when its contract is already
  authoritative, or to `workflow-test-design` when material test choices remain; regression tests
  that are inseparable from an active production slice stay with that implementation owner.
- Active plans may be read as task input and updated as secondary status tracking, but they must not replace source, test, runtime config/build, or executable scaffold changes for implementation requests.
- Markdown-only, plan-only, spec-only, report-only, memory-only, or planning-manifest-only diffs are not implementation completion unless the user explicitly requested documentation/spec work only.
- If a requested implementation cannot produce a non-documentation implementation diff, report `blocked` or analysis-only with the exact blocker instead of claiming completion.

Research Hypothesis Planning Mode:
- Use only when the user explicitly asks for research plan, paper idea, novel method, experiment design, ablation design, loss design, training plan, hypothesis planning, or scientific claim development.
- Treat user-provided causal or field-state claims as hypotheses, not facts.
- Use premise triage, checkpoint-first baseline, one-claim core experiment, progressive ablation, and loss budget.

If the request is primarily about implementing an already chosen method, stay in Development / Implementation Mode. If the request is primarily about deciding whether a scientific claim/method is valid or publishable, use Research Hypothesis Planning Mode.

## Context Bundle Contract
For multi-step work, writes, broad scans, reports, automation changes, or memory mutation, compile a small internal context pack before acting. Start with the request, the selected owner, direct source, and validation evidence; expand only from `read_if_needed`, one layer at a time.

When delegation follows an already selected specialist, carry its exact canonical skill ID into the worker task. If no specialist was selected upstream, let the worker route normally rather than inventing one for the handoff.

The canonical pack shape, cache-friendly ordering, reference-admission limits, and token-cost interpretation live in `.claude/docs/context_pack_guidelines.md`. Do not duplicate that schema here or recover from missing context by loading all repo docs, memory, skills, or chat history.

## Skill Precedence
1. Explicit user invocation wins within the named skill's declared role and scope.
2. Explicit artifact intent wins over generic analysis.
3. Heavy artifact generators require explicit artifact, package, or report intent.
4. Primary skills own task execution.
5. Narrow routing gates may choose a primary skill but must not perform writes.
6. Apply `.claude/docs/execution_assurance_contract.md` to an active behavior-changing owner when maker/checker separation is material, or use `strict` for high-risk rollback/readback assurance. A semantic completion claim resting mainly on maker-authored code and checks is a concrete `standard` trigger; low-risk work uses the global evidence baseline without an assurance mode. Directness, mutation, Core cards, DAG transitions, and condition-matched validation remain with the active owner or named domain verifier.
7. Output modifiers attach only to final presentation.
8. Review gates attach only when critical review, QA, blocker, risk, or validation is requested.
9. Memory operations attach only when persistent memory mutation or inspection is explicit.
10. If two skills could apply, choose the narrower one and mark the broader one as excluded.

For an explicit “what next / which flow” request, separate the questions instead of consulting another route matrix: `.claude/docs/work_horizon_model.md` owns persistence and artifact altitude, while `.claude/docs/planning_state_model.md` admits transitions only for persisted planning artifacts. Stable work with no such boundary stays with the current task owner. Neither reference invokes a chain.

Resolve a requested skill in this order: exact user-provided path, skill installed or exposed in the current session, repository-local skill root declared by project instructions or `project-context.yaml`, then `unresolved`. Do not scan unrelated home directories, plugin versions, adjacent projects, or guessed harness locations as fallback.

## Route Matrix
| Request type | Primary skill | Optional attachment | Must read | Default exclude |
| --- | --- | --- | --- | --- |
| diagnosis-only RCA with no repair requested | current task owner, read-only | none | concrete symptom, expected condition, repro, relevant files, logs | production writes, Bug Workflow activation, full repo report |
| concrete failure repair, including an unclear cause or a resumed same-problem attempt | `workflow-bug-fix` | its `causal-diagnosis.md` reference when a discriminator is needed; execution assurance for risky fixes | failure signal, expected behavior, repro or failing command, target files/tests, attempt history; DAG mode also requires node/round/source-review findings | a second workflow owner, multiple interventions inside one DAG node, full static review, Plan/Handoff mutation, broad redesign |
| algorithm proposal | `analysis-algorithm` | `report-qualitative` only for formal output | constraints, metrics, candidates | full repo or memory |
| domain modeling for development | `analysis-domain-modeling` | `workflow-refactor-safely` or `workflow-implementation` only after a model decision is selected | domain area, current terminology, source/schema/tests/docs with domain rules | persistent memory/docs mutation, pure product ideation, module-boundary-only design |
| performance analysis | `analysis-performance` | `workflow-implementation` only after a bottleneck and optimization are selected; the current task owner or named performance verifier owns a measurement plan | performance symptom, metric/workload, baseline or profile/log gap, hot path | correctness bug workflow, repo-wide report, research benchmark planning |
| research / scientific workflow | the narrow research owner matching the requested stage or supplied upstream artifact; ask for the missing stage distinction when it changes the deliverable | `plan-execution-handoff` only when durable execution state is explicitly requested | research decision, stage/artifact hints, provided upstream artifact | full repo, full memory bank, `analysis-boundary-design`, premature later stages |
| accepted Plan-assigned Research node | `workflow-research` plus exactly one Research stage skill already selected by the Plan | none; the Coordinator owns the next edge | node/scope identity, exact stage skill, upstream artifact refs, output/evidence ceiling, user checks | stage classification, multiple Research stages, search substitution, Handoff mutation, successor selection |
| evidence search | the obvious lane directly; `search-deep-evidence` only when one claim needs independent lanes; lane-choice-only and diagnosis-only bug questions stay with the current owner | `search-paper-evidence`, a design evidence gate, `management-memory-bank-harness`, `management-knowledge-base-read`, or explicit `analysis-llm-wiki-context` as applicable | evidence intent, domain hint, claim/topic, final task owner | speculative multi-lane fan-out, final synthesis, implementation, broad research lifecycle |
| durable multi-session map of unresolved decisions | `plan-decision-map` only on explicit map intent | evidence, discovery, domain-modeling, or prototype owner only for the selected decision item; normal plan owner after decision completion | target outcome, decision owner, scope boundary, artifact authority, known constraints | implementation backlog, direct execution, settled phase package, automatic remote issue creation |
| requirements discovery interview | `plan-requirements-discovery` | none by default; `plan-requirements-brief` only after discovery results are ready to distill | rough goal, idea, product direction, domain/scope hints, user willingness to answer questions | direct implementation, active docs/plan sync, lifecycle report package |
| one-recipient question document | `plan-question-document` only on explicit artifact intent | none by default; returned answers may later feed discovery or a requirements brief | recipient and answer ownership, needed-back list, downstream use, response constraints | ordinary interactive discovery, many-respondent survey, external sending or upload |
| behavior discovery for an existing capability | `plan-behavior-discovery` | `report-implementation-explainer` only when an explanation artifact is explicitly requested | concrete capability/path, current source/runtime evidence, target actor, unresolved operability decision | greenfield requirements discovery, quiz, direct implementation, exhaustive release questionnaire |
| human-owned test judgment surfaced during Test Design | `plan-test-discovery` only from a named blocked condition | no execution owner; `plan-execution-handoff` alone pins a decided package input through Scope Admission/revision | target/contract snapshot, blocked condition IDs, authority evidence, available observations (required when empirical), exclusive options/tradeoffs, recommendation, authority owner | generic requirements/product behavior discovery, test design/implementation, Human Test, Plan/Handoff mutation |
| software Test Design after an executable SUT or accepted external contract exists | `workflow-test-design` | only the material `test-*` specialists selected by its actual/contract scope, scenario, oracle, or evidence question; visual regression is explicit `design` mode | executable target/path or accepted external-contract boundary/revision, accepted test basis, failure risk, representative data/environment when empirical | test code, visual capture/verdict, production repair, automatic skill chain, exact output requirement when other authoritative oracle regimes exist |
| test-only implementation and scoped execution | `workflow-test-implementation` | Plan-selected replay/visual/statistical specialist only when the contract names that surface; visual regression is explicit `evidence` mode | Core `test_design_result` or complete authoritative inline contract, target snapshot, test-only lock scope, runner/environment | hidden Test Design/redesign, production writes, weakened oracle/baseline/tolerance, automatic repair from condition Fail |
| bounded test-evidence credibility review | `test-evidence-review` | none; repairs stay with the exact Test Design/Test Implementation/production owner | bounded test contract/assets/result, target path, authority, diagnostics, falsifier, claimed proof ceiling | broad quality gate, implementation, mutation infrastructure, automatic rerun or repair |
| runnable prototype for one unresolved UI, interaction, state, or logic question | `workflow-prototype` | `plan-behavior-discovery` only when the question itself is not selected; normal implementation owner only after a decision | one question, decision owner, discriminating observation, target host path, budget/stop, proof ceiling, retention boundary | vague ideation, cleanup before decision-owner observation, production hardening, bug work, real data mutation, performance/security/accessibility/concurrency proof |
| repair immediately preceding explanation | current task owner | none | immediately preceding exchange and the user's confusion signal | new evidence gathering, repository context, file/tool action, task mutation |
| requirements contract / PRD brief | `plan-requirements-brief` | `plan-execution-handoff` only after the brief is accepted and durable execution state is requested | discovery notes, returned question-document answers, decision log, rough requirements, intended handoff target | interactive elicitation, direct implementation, lifecycle result reporting |
| durable verifier-steered plan | `plan-execution-handoff` with its conditional repeated-work profile | verifier skills only as named owners, not executors | accepted durable outcome, conditions, verifier evidence paths, rewrite budget, and stop terms | suitability-only classification, direct execution, verifier execution, unrelated broad planning |
| accepted repeated-work execution | the Orchestrator follows the bounded acyclic DAG copied into the Plan/Handoff pair | task-specific Workflow nodes; each assigned `workflow-bug-fix` node owns one intervention/result, and the named review/verifier owner retains disposition | accepted terms, verifier map, graph budget, assigned repair node and attempt history | contract creation, one-shot work, persistent Memory or Knowledge mutation |
| implementation | `workflow-implementation` | execution assurance for medium/high-risk changes or material maker/checker separation; an existing Plan/Handoff remains input when explicitly referenced | repo `CLAUDE.md`, relevant files, accepted Plan node when applicable, validation | standalone test-only design/implementation owned by the Testing plugin, unrelated docs, plan-only completion, a second execution/status owner |
| dependency upgrade | `workflow-dependency-upgrade` | execution assurance for risky upgrades; named domain verifier for compatibility checks; `workflow-bug-fix` for a bounded concrete repair node | package/runtime manifests, lockfiles, target dependency/version, usage sites, validation, prior repair attempts | broad package churn, unrelated feature work, security verdict-only review, third same-problem repair |
| post-development source or comment maintenance | `workflow-source-maintenance` in `source_prune` or `comment_sync` mode | `workflow-refactor-safely` only when cleanup uncovers live structural work | selected mode, target source/callers/tests or comments and described code, public exports/framework consumption, validation command | feature changes, concrete bug fixes, broad architecture redesign, dependency upgrades, README/wiki documentation writing |
| behavior-preserving refactor | `workflow-refactor-safely` | `analysis-boundary-design` before boundary changes; the current owner or named domain verifier owns characterization checks | refactor goal, behavior contract, target files/callers, tests or smoke command | feature changes, bug fixes, design-only analysis, broad rewrite |
| static code review of a bound implementation or diff | `workflow-code-review` | `analysis-codebase-map` only as an optional map aid; fixes/runtime checks remain separate owners | exact snapshot/diff identity, intent and material changed effects, slice, activated risk paths, optional baseline, Known Bug exclusions, supplied node/round | mapping-only, style-only feedback, mutation, runtime tests or production test-oracle review, Plan/Handoff topology changes |
| approved plan/spec execution | current Orchestrator follows an existing canonical Plan/Handoff; without one, the task-specific Workflow owns one bounded approved slice | execution assurance only when its trigger is material; named domain verifiers own checks | approved Plan/Handoff or bounded approved slice, source/test/config files, validation contract | plan/spec creation, plan-only completion, a second execution-control skill |
| validation-only work | `workflow-test-design` or `workflow-test-implementation` when new software-test design/assets are the requested outcome; otherwise the current task owner or named domain verifier | execution assurance only when validation itself has medium/high risk or material checker-separation requirements | changed artifact or plan/spec slice, authoritative success criteria, test-contract readiness, risk tier, available checks | broad repo audit, critical verdicts, hidden oracle invention, new validation infrastructure without request |
| same problem after an attempted fix | `workflow-bug-fix` with preserved attempt history | its causal-diagnosis reference only when another discriminator is needed; `workflow-code-review` owns DAG review disposition | stable failure fingerprint, failing command/log, prior attempt rows; DAG mode also needs assigned node/round/source-review findings | resetting attempt count, automatic A2, multiple interventions in one DAG node, separate recovery owner, broad redesign |
| durable canonical Plan/Handoff pair | `plan-execution-handoff` only on explicit pair, long-running execution DAG, graph-method/ownership/lock routing, advisory timing, or cross-session continuation intent | select one typed acyclic archetype; validate typed timing once at `worker_done`; `phase_gate_delivery` terminates at `human_test_ready` and later Test results/worklist/design enter a fresh Waterfall | requested outcome, repository/plan identity, scope/approval, rough node timing, uncertainty/assurance/transition constraints, test transition/procedure, next worklist/design seeds, one-time baseline | direct implementation, strict deadlines, malformed timing acceptance, timing polling/retry, lightweight handoff, unbounded hybrid graphs, old-handoff resume |
| persisted execution plan | `plan-execution-handoff` | `report-critical` only when a separate QA verdict is explicitly requested | outcome, scope, graph constraints, execution owners, human boundary | direct implementation, casual plan prose |
| goal/repeated-work contract | `plan-execution-handoff` only when a durable verifier-steered pair is requested; otherwise the current task owner | named verifier owners only after conditions are accepted | durable outcome, target plan/spec, success criteria, verifier evidence, graph budget, stop boundaries | suitability-only artifact, implementation, direct verifier execution, generic validation-only work |
| named plan/spec file cleanup | current task owner, read-only until explicit mutation is requested | none by default | exact files, current goal, authoritative replacement if any | full memory bank, all old plans, full chat history, invented archive system |
| project context manifest init/bootstrap/doctor/update | `management-project-context` in the matching mode, only on explicit request | store initializers only for action IDs approved in the exact bootstrap transaction | repository root, nearest manifest/instructions, proposed exact paths or selected existing keys and storage intent | ordinary task auto-setup, home/adjacent scan, unapproved store creation |
| Knowledge Base context consumption | owning task primary | `management-knowledge-base-read` for the declared current slice and bounded typed why/history/scope/recurrence path | nearest `project-context.yaml`, Knowledge index, artifact anchors, selected records/relations/revisions/observations | full graph/store dump, raw chat, all plans, Knowledge mutation, recurrence scoring |
| named LLM Wiki context | `analysis-llm-wiki-context` only when a Wiki is explicitly named or an exact path is supplied | current task owner consumes the returned context | selected Wiki declaration/path, its own guide and navigation entrypoints | guessing a Wiki, loading every page, Wiki mutation |
| knowledge maintenance | `management-knowledge-base-record` for one new category identity, `management-knowledge-base-update` for an existing identity including accepted-plan admission, otherwise `management-knowledge-base-maintenance` | execution assurance for material write validation | declared Knowledge files, affected records and canonical artifact anchors | Memory Bank mutation, Wiki mutation, unrelated records |
| codebase design / deep module analysis | `analysis-boundary-design` for one standalone/explicitly assigned atomic boundary—including one architecture-material paradigm/model choice with `decision_owner: atomic_boundary`—or `analysis-architecture-deepening` for ranked candidates | accepted `architecture_design` only as binding context for its explicitly atomic target; shared paradigm base plus one thin profile when material; `workflow-implementation` only after a candidate is selected | design pressure, optional accepted architecture ref, user-named scope or bounded recent-change hot paths, target modules/call sites/tests, local patterns | coupled-view architecture redesign, local paradigm mechanics, full repo report, direct implementation before selection, history-only recommendations, domain glossary-only work |
| normative multi-view software architecture design | `workflow-architecture-design` | accepted domain/algorithm/boundary inputs and shared paradigm decision contract only when selected/material; implementation remains a later owner | accepted behavior and quality scenarios, decision authority, target scope, current owners/canonical sources and representative/edge path for brownfield work, non-goals; subsystem-wide paradigm composition only after the architecture-impact gate | current-state map only, one seam decision, candidate ranking, local function/class/layout/RAII/scheduler mechanics, full pattern catalog, production writes, Plan/ADR/Knowledge mutation |
| codebase architecture map | `analysis-codebase-map` | none by default | repo or named slice, representative path, state/flow question | one-boundary decision, ranked improvement scan, findings report |
| qualitative evaluation report | `report-qualitative` | none; a separately requested critical/QA report remains a separate deliverable | artifact slice, evaluation goal, audience, criteria, evidence anchors, redaction boundary | readable changed-line diffs, artifact inventory, eval telemetry, implementation, debugging |
| implementation explanation, visualization, or changed-line comparison | `report-implementation-explainer` in `explain` or `compare` mode | `workflow-implementation` only when new production trace/readback instrumentation is separately requested | concrete snapshot or verified diff, production path, decision purpose, available runtime evidence | correctness verdict, pre-implementation algorithm choice, automatic post-implementation gate |
| lifecycle artifact package | `report-lifecycle-artifacts` | none; critical/QA judgment and concrete validation remain separate explicit owners | selected existing lifecycle artifacts, evidence anchors, desired scope, traceability needs | empty planned shells, direct implementation, small task inventory, casual planning, validation-only work |
| explicit critical/blocker/risk/QA report | `report-critical` | none | artifact slice, report decision, material criteria, audience, evidence anchors | ordinary diagnosis, generic code review, implementation, full history |
| memory operation | `management-memory-bank-init`, `management-memory-bank-update` in `durable_item` or `candidate_mistake` mode, or `management-memory-bank-maintenance` | none by default | declared `memory.md`, matching records, source refs, and exact operation | unrelated Memory, legacy migration without explicit scope |
| Skill-System repository skill update | current implementation owner following repository canonical-source, generation, and validation instructions | none by default | requested behavior, target skill, concrete cases, implicated source/manifests | `.system`, live home runtime, plugin caches, full skill library |
| personal skill creation | system `skill-creator` only when explicitly named or the request clearly targets a personal new skill | none by default | authoring request, target location, concrete cases and resources | Skill-System repository integration, plugin caches, unrelated skills |
| Skill-System integration only | task-specific implementation owner following repository instructions | none | already-authored result or explicit runtime companion, affected `source/` paths and manifests | general/personal skill authoring, authoring decisions, generated-mirror hand edits |

Development/implementation requests keep the existing implementation, bug, algorithm, or plan skills as primary and follow concrete user requirements as task specifications. Do not route to the research cluster merely because a development request mentions model, metric, experiment, loss, or training.

Router/support/context-cost guardrails:
- Do not read the full skill library to answer "which skill" or "reduce token cost" requests; read the registry, routing matrix, analyzer output, and selected skills only.
- Do not load every reference/template under a high-fanout skill. Use an index/catalog first, then admit selected references in small batches.
- Router skills stop after route selection unless the user asked for the specialist artifact.
- Evidence gates and support modifiers attach only when their trigger is explicit or the primary route needs their evidence to complete safely.

Knowledge or Wiki context consumption does not imply Memory Bank mutation. Persistent Memory and Knowledge writes require their explicit owning workflows; an LLM Wiki is read-only unless a separate mutation workflow is explicitly requested.

Aliases may remain in user-facing language, but routing docs should show actual skill IDs. Repository skill changes stay with the current implementation owner and follow repository source/generation/validation instructions. System `skill-creator` is reserved for explicit or clearly personal skill authoring. `.system` skills and plugin caches remain app-managed.

Unknown or stale skill IDs are unresolved. Host-resolved slash/plugin invocations and model-visible
requests must use a current installed ID; do not infer a replacement or pretend a removed alias is
installed.

## Work Horizon Decision Table

Use `.claude/docs/work_horizon_model.md` as the detailed reference. The table below resolves plan/workflow ambiguity before selecting a primary skill.

Use `.claude/docs/planning_state_model.md` when a planning artifact changes state, when a plan is used as implementation input, or when old plan text may enter active context. Work horizon chooses the artifact altitude; planning state chooses whether the requested event is admitted.

| Horizon / intent | Primary route | Attachments | Exclude |
| --- | --- | --- | --- |
| direct one-shot edit/check | small direct execution or `workflow-implementation` when coding workflow is useful | none by default | repeated-work principles, durable Plan/Handoff state |
| durable single task across turns | `plan-execution-handoff` with `single_node_execution` | one task-specific Workflow node | multi-node graph unless dependencies actually require it |
| durable multi-session decision map | `plan-decision-map` | selected decision-item owner only; normal plan handoff after decision completion | implementation backlog, direct execution, automatic tracker mutation |
| requirements discovery / interview | `plan-requirements-discovery` | none by default | direct implementation, phase package, lifecycle artifact report |
| recipient question document | `plan-question-document` | feed returned answers to discovery/brief only on a later explicit request | interactive interview as primary, external delivery |
| existing-capability behavior discovery | `plan-behavior-discovery` | none by default; consume an existing explainer only when relevant | greenfield discovery, direct implementation, exhaustive feature/release interview |
| conditional human test-decision discovery | `plan-test-discovery` only from an active Test Design blocked condition | package-local decision record and explicit Plan revision when graph-bound | standalone oracle invention, test design/implementation, Human Test |
| implementation-ready software Test Design | `workflow-test-design` | selected test specialists only for material subquestions | test-code writes, automatic successor, exact-output-only assumptions |
| test-only implementation and scoped execution | `workflow-test-implementation` | accepted `test_design_result` or complete inline contract | hidden design, production writes, automatic repair from condition Fail |
| bounded runnable prototype | `workflow-prototype` | question-selection discovery only when needed; production implementation only after verdict | vague ideation, cleanup before decision-owner observation, automatic production merge, release claims |
| requirements contract / PRD brief | `plan-requirements-brief` | hand off to `plan-execution-handoff` only when durable execution state is needed after acceptance | interactive discovery, direct implementation |
| persisted current execution plan | `plan-execution-handoff`; select `single_node_execution` for one durable executable node | `report-critical` only when requested | direct one-shot work, duplicate status artifact |
| durable execution Plan/Handoff pair | `plan-execution-handoff` | one selected archetype; typed advisory timing inspected at `worker_done`; phase work completes at `human_test_ready`; later Test results create a fresh pair | one-session short plan, strict timing enforcement, malformed timing acceptance, old-handoff resume, waiting agents, polling, fixed/busy waits, broad phase/package decomposition, direct execution |
| selected SDLC/lifecycle artifact package | `report-lifecycle-artifacts` | none; any QA verdict is a separate explicit report | empty shells, direct implementation, task-local artifact inventory |
| repeated-work terms or verifier map | `plan-execution-handoff` with conditional repeated-work principles | selected verifier owners only as contract fields | execution before contract acceptance |
| approved Plan/Handoff execution | current Orchestrator follows the copied pair | task-specific Workflow nodes and named verifiers only | a second plan runner or ledger |
| accepted verifier-steered execution | the Orchestrator follows the bounded DAG copied into the accepted Plan/Handoff pair | task-specific Workflow nodes and bounded Bug Fix/Known Bug protocol | one-shot execution, unbounded back-edges, retrying an excluded Known Bug |
| named plan/spec/context cleanup | current task owner | memory/knowledge workflows only with explicit mutation intent | implementation owners, full history loading, automatic archive state |

## Planning State Admission

- `plan-behavior-discovery` is a bounded, non-persisted decision surface around an existing capability unless the user explicitly requests a record. It does not reopen `scratch -> discovery`, synthesize a plan state, or authorize implementation; it stops when the next human-operable slice is decision-ready.
- `plan-decision-map` keeps unresolved decisions and their prerequisites in one durable map when one session cannot close them. It does not create a planning-state transition, implementation backlog, or execution approval.
- `plan-requirements-discovery` owns `scratch -> discovery`; it asks mutually independent ready questions in bounded rounds when requirements gaps affect scope, acceptance, edge behavior, data ownership, constraints, or non-goals.
- `plan-question-document` creates an answer-owner question document, not a discovery result or accepted requirements contract. Only returned answers can later enter those owners.
- `plan-requirements-brief` owns `discovery -> requirements_contract`; acceptance criteria must be observable before a brief can hand off to planning.
- Direct implementation commands such as `이 플랜대로 구현`, `플랜 작업해`, or a referenced active plan path plus `작업해줘` may be accepted as implementation transition when the plan scope is explicit.
- One-word replies such as `승인`, `작업해`, or `구현해` are invalid transition events when the active plan scope is not explicit in surrounding context.
- Repeated-work terms live inside `plan-execution-handoff`; accepted conditions, verifier ownership, budget, and stop semantics are compiled into the same bounded DAG before the Orchestrator starts.

## Design Cluster Routing

`workflow-ui-design` owns concrete visual design creation from accepted requirements;
`design-frontend` owns production UI implementation and selects one conditional surface profile.
Evidence gates and analysis skills own neither production code nor automatic stage transitions.

| Request type | Primary skill | Supporting skill(s) | Must not trigger as primary |
| --- | --- | --- | --- |
| accepted requirements/product behavior to a new concrete UI design artifact | `workflow-ui-design` | decomposer/layout/token/component context only when material | production UI code, product research, automatic implementation |
| concrete visual artifact to repo UI code | `design-frontend` | only evidence conditions explicitly requested or named by an accepted Plan | `design-ui-decomposer`, `design-layout-translator` |
| visual reference breakdown without code | `design-ui-decomposer` | layout translation only when separately requested or named by a Plan | `design-frontend` |
| Auto Layout/flex/grid/sizing/overflow/breakpoint translation | `design-layout-translator` | visual evidence only when separately requested or named by a Plan | `design-frontend` |
| mobile/native screen implementation | `design-frontend` with `mobile` profile | named visual/a11y conditions only | other surface profiles by default |
| dashboard/admin/analytics implementation | `design-frontend` with `dashboard` profile | named component/visual/a11y conditions only | other surface profiles by default |
| section-based web implementation | `design-frontend` with `section-web` profile | named visual/a11y conditions only | other surface profiles by default |
| token source normalization or token gaps | `design-tokens` | component mapping only when separately requested or named by a Plan | `design-frontend` |
| design component to repo component/state mapping | `design-component-mapper` | token/a11y conditions only when separately requested or named by a Plan | `design-visual-regression` |
| rendered screenshot, nonblank, viewport, or visual diff evidence | `design-visual-regression` | a11y conditions only when separately requested or named by a Plan | `design-frontend` |
| keyboard/focus/semantic/contrast/target-size/readability evidence | `design-a11y-audit` | visual conditions only when separately requested or named by a Plan | `design-frontend` |

Design cluster conservative defaults:
- Design specialists follow their canonical invocation bit; implicit selection still requires the concrete intent and inputs declared in the skill description.
- `workflow-ui-design` may enter implicitly only for concrete UI visual-design creation from accepted product behavior and a declared artifact boundary; it never starts implementation.
- `design-frontend` is the bounded exception: it may enter implicitly only for concrete UI/design implementation in repository code. Critique, ideation, reuse or visual audits, layout-only translation, and small CSS/text edits remain outside it.
- `design-ui-decomposer` and `design-layout-translator` may enter implicitly for a supplied UI reference or concrete layout-constraint translation, but never from a bare design topic.
- Mobile, dashboard, and section-web guidance is conditionally loaded from `design-frontend/references/`; select one primary profile instead of attaching surface skills.
- Evidence owners run only for an explicit request or accepted Plan condition. Their result is
  condition-local and never starts a gate, repair, retry, implementation, or Plan transition.
- Do not infer broader implicit routing from scenario counts or advisory quality labels.

## Routing Card Audit Shape
Each Skill System source `SKILL.md` Routing Card should keep these Markdown fields in this order unless a local reason exists: `role`, `intent_signature`, `use_when`, `do_not_use_when`, `expected_inputs`, `expected_outputs`, `context_targets` with `must_read`, `read_if_needed`, `do_not_load_by_default`, `risk_profile` with `reads`, `writes`, `tools`, `sensitive_resources`, and `entry_scene`.

## Agent Metadata Tradeoff
`allow_implicit_invocation` controls model discoverability, not authorization. Clear intent-matched workflow owners, bounded design interpreters, coordination handoff, and repository integration support may be implicit while their Routing Cards continue to enforce scope and side effects. A router-local recommendation does not disable a target that normal routing may select implicitly. Persistent Memory/Knowledge writes, project-context mutation, lifecycle gates, and explicitly selected context remain explicit-only.


## Group Alias Routing

User-facing skill families, family aliases, display strings, and entry owners are defined in
`docs/skill_registry.md` (the `family` column and Group Alias Map). This section defines only
*when* group-selection mode is used and the provider guardrails around that selection.

Trigger guard:
- Enter group-selection mode only when the request carries an explicit family-framing token (`스킬군`, `그룹`, `계열`, `group`, `family`) or an explicit family name.
- Do not enter group-selection mode for bare domain words like `분석`, `검토`, `보고`, `계획`; those route by the normal Route Matrix.

When the trigger guard admits group-selection mode, resolve the family and its entry owner from the registry Group Alias Map. Do not maintain a second family-entry table here. A named Wiki remains an explicit `analysis-llm-wiki-context` operation within the `analysis` family; its evidence domain does not create another skill family.

Evidence vs research boundary:
- Cross-domain evidence search (papers, code, runtime, visual, memory) belongs to the `search` family; the `search` entry opens an evidence lane and `search-paper-evidence` provides paper evidence as support.
- The whole task routes to the narrow matching `research` specialist only when the user develops a scientific claim, hypothesis, experiment, ablation, manuscript, or publishability decision.
- Implementation/plan/algorithm requests that merely mention paper/loss/model/experiment keep their implementation/planning/analysis primary; research attaches only as a support evidence lane.

Phase B note:
- Clear technical-analysis and research stages route directly to their narrow owners. When a missing distinction would change the deliverable, ask for that distinction instead of invoking a router surface. Clear evidence lanes, workflow owners, and bounded design/support specialists may also be selected directly from natural-language intent; hooks retain lifecycle gates.
- Persistent Memory and Knowledge writes, LLM Wiki reads, and evaluation review remain explicit operations.
- Repeated-work admission and contract authoring stay conditional inside `plan-execution-handoff`; verifier execution remains with named owners and runtime continuation remains with the Orchestrator.
