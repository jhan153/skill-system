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
- Direct implementation commands such as `구현해`, `작업해`, `플랜대로 구현`, `fix`, `add tests`, or `refactor` stay in Development / Implementation Mode even when an active plan document exists.
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
6. Attach `workflow-rigor` to an active behavior-changing owner when medium/high risk, rollback/readback, or maker/checker separation is material. A semantic completion claim resting mainly on maker-authored code and checks is a concrete `standard` trigger; simple edits, direct command-output requests, and explanation-only turns attach no rigor mode. Attach `workflow-minimal-implementation` only for explicit YAGNI/minimality requests or credible over-engineering pressure. Attach `workflow-validation` only when validation design or execution is itself in scope.
7. Output modifiers attach only to final presentation.
8. Review gates attach only when critical review, QA, blocker, risk, or validation is requested.
9. Memory operations attach only when persistent memory mutation or inspection is explicit.
10. If two skills could apply, choose the narrower one and mark the broader one as excluded.

For an explicit “what next / which flow” request, separate the questions instead of consulting another route matrix: `.claude/docs/work_horizon_model.md` owns persistence and artifact altitude, while `.claude/docs/planning_state_model.md` admits transitions only for persisted planning artifacts. Stable work with no such boundary stays with the current task owner. Neither reference invokes a chain.

Resolve a requested skill in this order: exact user-provided path, skill installed or exposed in the current session, repository-local skill root declared by project instructions or `project-context.yaml`, then `unresolved`. Do not scan unrelated home directories, plugin versions, adjacent projects, or guessed harness locations as fallback.

## Route Matrix
| Request type | Primary skill | Optional attachment | Must read | Default exclude |
| --- | --- | --- | --- | --- |
| bug diagnosis | `analysis-bug` | none by default | symptom, repro, relevant files, logs | full repo report |
| bug fix implementation | `workflow-bug-fix` | `analysis-bug` for unclear RCA; `workflow-recovery` for repeated same-signature failure; `workflow-validation` for check redesign when installed or explicitly requested; `workflow-rigor` for risky fixes | failure signal, expected behavior, repro or failing command, target files/tests | full repo report, plan package, broad redesign |
| algorithm proposal | `analysis-algorithm` | `report-qualitative` only for formal output | constraints, metrics, candidates | full repo or memory |
| domain modeling for development | `analysis-domain-modeling` | `workflow-refactor-safely` or `workflow-implementation` only after a model decision is selected | domain area, current terminology, source/schema/tests/docs with domain rules | persistent memory/docs mutation, pure product ideation, module-boundary-only design |
| performance analysis | `analysis-performance` | `workflow-implementation` only after a bottleneck and optimization are selected; `workflow-validation` for measurement plan when installed or explicitly requested | performance symptom, metric/workload, baseline or profile/log gap, hot path | correctness bug workflow, repo-wide report, research benchmark planning |
| research / scientific workflow | the narrow research owner matching the requested stage or supplied upstream artifact; ask for the missing stage distinction when it changes the deliverable | `plan-short-term-docs` only for an explicit persisted `docs/plan` artifact | research decision, stage/artifact hints, provided upstream artifact | full repo, full memory bank, `analysis-boundary-design`, `plan-long-term-package`, premature later stages |
| evidence search | the obvious lane directly; `search-deep-evidence` only when one claim needs independent lanes; lane-choice-only questions stay with the current owner | `search-paper-evidence`, `analysis-bug`, a design evidence gate, `management-memory-bank-harness`, `management-knowledge-base-read`, or explicit `analysis-llm-wiki-context` as applicable | evidence intent, domain hint, claim/topic, final task owner | speculative multi-lane fan-out, final synthesis, implementation, broad research lifecycle |
| durable multi-session map of unresolved decisions | `plan-decision-map` only on explicit map intent | evidence, discovery, domain-modeling, or prototype owner only for the selected decision item; normal plan owner after decision completion | target outcome, decision owner, scope boundary, artifact authority, known constraints | implementation backlog, direct execution, settled phase package, automatic remote issue creation |
| requirements discovery interview | `plan-requirements-discovery` | none by default; `plan-requirements-brief` only after discovery results are ready to distill | rough goal, idea, product direction, domain/scope hints, user willingness to answer questions | direct implementation, active docs/plan sync, lifecycle report package |
| one-recipient stakeholder question document | `plan-stakeholder-questionnaire` only on explicit artifact intent | none by default; returned answers may later feed discovery or a requirements brief | recipient and knowledge ownership, needed-back list, downstream use, response constraints | ordinary interactive discovery, many-respondent survey, external sending or upload |
| behavior discovery for an existing capability | `plan-behavior-discovery` | `report-implementation-explainer` only when an explanation artifact is explicitly requested | concrete capability/path, current source/runtime evidence, target actor, unresolved operability decision | greenfield requirements discovery, quiz, direct implementation, exhaustive release questionnaire |
| runnable prototype for one unresolved UI, interaction, state, or logic question | `workflow-prototype` | `plan-behavior-discovery` only when the question itself is not selected; normal implementation owner only after a decision | one question, decision owner, discriminating observation, target host path, budget/stop, proof ceiling, retention boundary | vague ideation, cleanup before decision-owner observation, production hardening, bug work, real data mutation, performance/security/accessibility/concurrency proof |
| repair immediately preceding explanation | current task owner | none | immediately preceding exchange and the user's confusion signal | new evidence gathering, repository context, file/tool action, task mutation |
| requirements contract / PRD brief | `plan-requirements-brief` | none by default; `plan-long-term-package` or `plan-short-term-docs` only after the brief is accepted for planning | discovery notes, stakeholder answers, decision log, rough requirements, intended handoff target | interactive elicitation, direct implementation, docs/plan status sync, lifecycle result reporting |
| loop readiness classification | `analysis-loop-readiness` | `plan-loop-term` only after `contract_needed` or `loop_worthy`; `workflow-loop-runner` only after accepted contract | prompt draft, target domain, verifier hints, side-effect, approval, durability, event-runtime, Wiki feedback, parallelism, and idempotency signals | direct execution, contract drafting, verifier execution, broad planning |
| loop verifier mapping | `plan-loop-term` in verifier-mapping mode | verifier skills only as named owners, not executors | loop contract or success conditions, verifier catalog, target domain, governance metrics | running checks, implementation, readiness classification |
| accepted loop contract execution | `workflow-loop-runner` | task-specific primary skill; `workflow-recovery` for repeated failures; `workflow-validation` for verifier strategy | accepted contract, verifier map, current checkpoint/budget; load only governance sections triggered by active risk/side-effect flags | contract creation, readiness classification, one-shot work, persistent Memory or Knowledge mutation |
| implementation | `workflow-implementation` | `workflow-minimal-implementation` only for explicit YAGNI/minimality requests or credible over-engineering pressure; `workflow-rigor` for medium/high-risk changes or material maker/checker separation; `workflow-validation` for check selection when installed or explicitly requested; `plan-short-term-docs` only as secondary status sync when an active plan is explicitly in scope | repo `CLAUDE.md`, relevant files, active plan as input when explicitly referenced, validation | unrelated docs, plan-only completion |
| dependency upgrade | `workflow-dependency-upgrade` | `workflow-rigor` for risky upgrades; `workflow-validation` for compatibility-matrix work; `workflow-recovery` for repeated upgrade failure | package/runtime manifests, lockfiles, target dependency/version, usage sites, validation | broad package churn, unrelated feature work, security verdict-only review |
| post-development source or comment maintenance | `workflow-source-maintenance` in `source_prune` or `comment_sync` mode | `workflow-validation` for check selection; `workflow-minimal-implementation` only as YAGNI pressure; `workflow-refactor-safely` only when cleanup uncovers live structural work | selected mode, target source/callers/tests or comments and described code, public exports/framework consumption, validation command | feature changes, concrete bug fixes, broad architecture redesign, dependency upgrades, README/wiki documentation writing |
| behavior-preserving refactor | `workflow-refactor-safely` | `analysis-boundary-design` before boundary changes; `workflow-minimal-implementation` for abstraction pressure; `workflow-validation` for characterization checks when installed or explicitly requested | refactor goal, behavior contract, target files/callers, tests or smoke command | feature changes, bug fixes, design-only analysis, broad rewrite |
| approved plan/spec execution | `workflow-plan-runner` | `workflow-rigor` for execution discipline when the risk/evidence trigger is material; `workflow-validation` for check selection; `plan-task-handoff` only for explicit handoff or multi-agent ownership | approved plan/spec/package slice, target phase or batch, execution-source sufficiency, source/test/config files, validation contract | plan/spec creation, plan-only completion, all plan packages |
| validation-only work | `workflow-validation` | `workflow-rigor` only when validation itself has medium/high risk or material checker-separation requirements | changed artifact or plan/spec slice, success criteria, risk tier, available checks | `evaluation-harness`, broad repo audit, critical verdicts |
| repeated failure recovery | `workflow-recovery` | `analysis-bug` for deeper RCA; `workflow-validation` for check redesign; `workflow-rigor` for risky fixes | repeated failure signature, failing command/log, latest attempted fix, narrowed repro, target files | broad redesign, plan package, simple rerun |
| plan document | `plan-short-term-docs` | `report-critical` only for QA/review | active plan, plan template | phase package |
| goal/loop contract | `plan-loop-term` | `analysis-loop-readiness` if readiness is unknown; `plan-short-term-docs` only when persisting into `docs/plan`; `plan-long-term-package` only when this is one artifact in a broad phase package | goal or loop intent, target plan/spec, success criteria, verifier evidence, governance coverage, budgets, stop/retry boundaries | implementation, loop execution, broad package ownership, generic validation-only work |
| context/spec lifecycle curation | `plan-short-term-docs` in `curation` mode | `report-critical` only for QA/review | current goal or task, candidate plan/spec slice, lifecycle state when available | full memory bank, all old plans, archived raw plans, full chat history |
| project context manifest init/bootstrap/doctor/update | `management-project-context` in the matching mode, only on explicit request | store initializers only for action IDs approved in the exact bootstrap transaction | repository root, nearest manifest/instructions, proposed exact paths or selected existing keys and storage intent | ordinary task auto-setup, home/adjacent scan, unapproved store creation |
| Knowledge Base context consumption | owning task primary | `management-knowledge-base-read` for the declared current slice and bounded typed why/history/scope/recurrence path | nearest `project-context.yaml`, Knowledge index, artifact anchors, selected records/relations/revisions/observations | full graph/store dump, raw chat, all plans, Knowledge mutation, recurrence scoring |
| named LLM Wiki context | `analysis-llm-wiki-context` only when a Wiki is explicitly named or an exact path is supplied | current task owner consumes the returned context | selected Wiki declaration/path, its own guide and navigation entrypoints | guessing a Wiki, loading every page, Wiki mutation |
| knowledge maintenance | `management-knowledge-base-record` for one new category identity, `management-knowledge-base-update` for an existing identity including accepted-plan admission, otherwise `management-knowledge-base-maintenance` | `workflow-rigor` for material write validation | declared Knowledge files, affected records and canonical artifact anchors | Memory Bank mutation, Wiki mutation, unrelated records |
| phase package | `plan-long-term-package` | none by default | prior reports, templates | lightweight plan only |
| codebase design / deep module analysis | `analysis-boundary-design` for one boundary decision or `analysis-architecture-deepening` for ranked candidates | `workflow-minimal-implementation` as abstraction pressure; `workflow-implementation` only after a candidate is selected | design pressure, user-named scope or bounded recent-change hot paths, target modules/call sites/tests, local patterns | full repo report, direct implementation before selection, history-only recommendations, domain glossary-only work |
| codebase architecture map | `analysis-codebase-map` | none by default | repo or named slice, representative path, state/flow question | one-boundary decision, ranked improvement scan, findings report |
| qualitative evaluation report | `report-qualitative` | `report-critical` only if blocker/QA verdict is also requested | artifact slice, evaluation goal, audience, criteria, evidence anchors, redaction boundary | readable changed-line diffs, artifact inventory, eval telemetry, implementation, debugging |
| implementation explanation, visualization, or changed-line comparison | `report-implementation-explainer` in `explain` or `compare` mode | `workflow-implementation` only when new production trace/readback instrumentation is separately requested | concrete snapshot or verified diff, production path, decision purpose, available runtime evidence | correctness verdict, pre-implementation algorithm choice, automatic post-implementation gate |
| lifecycle artifact package | `report-lifecycle-artifacts` | `report-critical` only for blocker-first QA; `workflow-validation` only when concrete validation planning/execution is separately requested | lifecycle source artifacts, evidence anchors, desired tier/scope, traceability needs | direct implementation, small task inventory, casual planning, validation-only work |
| critical review | `report-critical` | `report-qualitative` if formal report requested | artifact slice, goal, evidence anchors | full history |
| memory operation | `management-memory-bank-init`, `management-memory-bank-update` in `durable_item` or `candidate_mistake` mode, or `management-memory-bank-maintenance` | none by default | matching active memory cards and target memory files | unrelated memory |
| existing Skill System eval-case review | `evaluation-harness` | none by default | targeted existing eval cases and their owning contract | field-quality scoring, new scenario generation, usage telemetry, release verdicts |
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

Legacy skill-ID compatibility is narrowly model-level. When model-visible request text explicitly names an ID in `docs/skill_registry.md`'s Legacy Skill Alias Migration table, select exactly its current owner and mode/profile without loading or inventing a removed skill. Host-resolved direct slash/plugin invocations bypass this routing layer and must use the current installed ID; report an old slash ID as unavailable and name the replacement instead of pretending the alias was installed.

## Work Horizon Decision Table

Use `.claude/docs/work_horizon_model.md` as the detailed reference. The table below resolves plan/workflow ambiguity before selecting a primary skill.

Use `.claude/docs/planning_state_model.md` when a planning artifact changes state, when a plan is used as implementation input, or when old plan text may enter active context. Work horizon chooses the artifact altitude; planning state chooses whether the requested event is admitted.

| Horizon / intent | Primary route | Attachments | Exclude |
| --- | --- | --- | --- |
| direct one-shot edit/check | small direct execution or `workflow-implementation` when coding workflow is useful | none by default | `workflow-task-ledger`, `plan-short-term-docs`, `plan-loop-term`, `workflow-loop-runner` |
| task/ticket state across turns | task-specific primary such as `workflow-implementation` plus `workflow-task-ledger` | WorkItem only as lifecycle envelope when requested or already present | `plan-long-term-package`, `workflow-loop-runner` unless verifier feedback is required |
| durable multi-session decision map | `plan-decision-map` | selected decision-item owner only; normal plan handoff after decision completion | implementation backlog, direct execution, automatic tracker mutation |
| requirements discovery / interview | `plan-requirements-discovery` | none by default | direct implementation, phase package, lifecycle artifact report |
| stakeholder question document | `plan-stakeholder-questionnaire` | feed returned answers to discovery/brief only on a later explicit request | interactive interview as primary, external delivery |
| existing-capability behavior discovery | `plan-behavior-discovery` | none by default; consume an existing explainer only when relevant | greenfield discovery, direct implementation, exhaustive feature/release interview |
| bounded runnable prototype | `workflow-prototype` | question-selection discovery only when needed; production implementation only after verdict | vague ideation, cleanup before decision-owner observation, automatic production merge, release claims |
| requirements contract / PRD brief | `plan-requirements-brief` | hand off to `plan-long-term-package` or `plan-short-term-docs` after acceptance | interactive discovery, direct implementation |
| tactical design/current execution plan | `plan-short-term-docs` | `workflow-validation` or `report-critical` only when requested | `plan-long-term-package` |
| strategic phase/package plan | `plan-long-term-package` | `plan-short-term-docs` in `curation` mode for lifecycle cleanup | `plan-short-term-docs` as the planning primary |
| formal SDLC/lifecycle artifact pack | `report-lifecycle-artifacts` | `report-critical` only for QA verdicting | direct implementation, task-local artifact inventory |
| loop contract or verifier map | `plan-loop-term` | selected verifier owners only as contract fields | `workflow-loop-runner` before contract acceptance |
| approved plan execution | `workflow-plan-runner` | `workflow-task-ledger` only when batch state must survive turns; `workflow-validation` for checks | plan creation skills as primary |
| accepted loop execution | `workflow-loop-runner` | current owner applies the recovery protocol on repeated failure; `workflow-task-ledger` only for adjacent non-loop task state | one-shot execution, plan creation |
| plan/spec/context lifecycle cleanup | `plan-short-term-docs` in `curation` mode | memory/knowledge workflows only with explicit mutation/review intent | implementation owners, full history loading |

## Planning State Admission

- `plan-behavior-discovery` is a bounded, non-persisted decision surface around an existing capability unless the user explicitly requests a record. It does not reopen `scratch -> discovery`, synthesize a plan state, or authorize implementation; it stops when the next human-operable slice is decision-ready.
- `plan-decision-map` keeps unresolved decisions and their prerequisites in one durable map when one session cannot close them. It does not create a planning-state transition, implementation backlog, or execution approval.
- `plan-requirements-discovery` owns `scratch -> discovery`; it asks mutually independent ready questions in bounded rounds when requirements gaps affect scope, acceptance, edge behavior, data ownership, constraints, or non-goals.
- `plan-stakeholder-questionnaire` creates a stakeholder input document, not a discovery result or accepted requirements contract. Only returned answers can later enter those owners.
- `plan-requirements-brief` owns `discovery -> requirements_contract`; acceptance criteria must be observable before a brief can hand off to planning.
- `plan-short-term-docs` owns `active_plan -> implementation_ready` and, in `curation` mode, lifecycle cleanup; `approve_implementation` requires explicit active plan scope and current-task approval wording.
- Direct implementation commands such as `이 플랜대로 구현`, `플랜 작업해`, or a referenced active plan path plus `작업해줘` may be accepted as implementation transition when the plan scope is explicit.
- One-word replies such as `승인`, `작업해`, or `구현해` are invalid transition events when the active plan scope is not explicit in surrounding context.
- `plan-loop-term` creates only the `loop_contract_ready` overlay; execution waits for accepted success conditions, verifier evidence mapping, and `workflow-loop-runner`.
- `plan-long-term-package` creates the `package_planned` overlay; canonical state names, release gates, and source-of-truth ownership must not be redefined in derived docs.
- `plan-short-term-docs` curation owns `completed -> closed_out -> archived`; raw completed or archived plans are excluded by default unless explicitly requested or admitted as summary-only.

## Design Cluster Routing

`design-frontend` owns concrete visual implementation and selects one conditional surface profile. Evidence gates and analysis skills should not take over code changes unless the user explicitly asks for their artifact.

| Request type | Primary skill | Supporting skill(s) | Must not trigger as primary |
| --- | --- | --- | --- |
| concrete visual artifact to repo UI code | `design-frontend` | token/component/visual/a11y gates when evidence exists | `design-ui-decomposer`, `design-layout-translator` |
| visual reference breakdown without code | `design-ui-decomposer` | `design-layout-translator` if constraints dominate | `design-frontend` |
| Auto Layout/flex/grid/sizing/overflow/breakpoint translation | `design-layout-translator` | `design-visual-regression` only after rendered evidence exists | `design-frontend` |
| mobile/native screen implementation | `design-frontend` with `mobile` profile | `design-visual-regression`, `design-a11y-audit` when evidence is requested | other surface profiles by default |
| dashboard/admin/analytics implementation | `design-frontend` with `dashboard` profile | `design-component-mapper`, `design-visual-regression`, `design-a11y-audit` when relevant | other surface profiles by default |
| section-based web implementation | `design-frontend` with `section-web` profile | `design-visual-regression`, `design-a11y-audit` when evidence is requested | other surface profiles by default |
| token source normalization or token gaps | `design-tokens` | `design-component-mapper` if component styles are involved | `design-frontend` |
| design component to repo component/state mapping | `design-component-mapper` | `design-tokens`, `design-a11y-audit` when relevant | `design-visual-regression` |
| rendered screenshot, nonblank, viewport, or visual diff evidence | `design-visual-regression` | `design-a11y-audit` for focus/contrast/readability | `design-frontend` |
| keyboard/focus/semantic/contrast/target-size/readability evidence | `design-a11y-audit` | `design-visual-regression` for rendered screenshot evidence | `design-frontend` |

Design cluster conservative defaults:
- Design specialists follow their canonical invocation bit; implicit selection still requires the concrete intent and inputs declared in the skill description.
- `design-frontend` is the bounded exception: it may enter implicitly only for concrete UI/design implementation in repository code. Critique, ideation, reuse or visual audits, layout-only translation, and small CSS/text edits remain outside it.
- `design-ui-decomposer` and `design-layout-translator` may enter implicitly for a supplied UI reference or concrete layout-constraint translation, but never from a bare design topic.
- Mobile, dashboard, and section-web guidance is conditionally loaded from `design-frontend/references/`; select one primary profile instead of attaching surface skills.
- Do not infer broader implicit routing from scenario counts or advisory quality labels.

## Routing Card Audit Shape
Each Skill System source `SKILL.md` Routing Card should keep these Markdown fields in this order unless a local reason exists: `role`, `intent_signature`, `use_when`, `do_not_use_when`, `expected_inputs`, `expected_outputs`, `context_targets` with `must_read`, `read_if_needed`, `do_not_load_by_default`, `risk_profile` with `reads`, `writes`, `tools`, `sensitive_resources`, and `entry_scene`.

## Routing Behavior Evals

Historical positive and negative routing cases live in `.claude/eval/`. Do not copy case payloads into this operational document; duplicated examples drift and inflate every routing read.

Those cases may support an explicit structural review, but they are not a release gate or evidence of field quality. Do not create new scenario suites merely to justify a routing change.

## Agent Metadata Tradeoff
`allow_implicit_invocation` controls model discoverability, not authorization. Clear intent-matched workflow owners, bounded design interpreters, coordination handoff, and repository integration support may be implicit while their Routing Cards continue to enforce scope and side effects. A router-local recommendation does not disable a target that normal routing may select implicitly. Persistent Memory/Knowledge writes, project-context mutation, Kanboard, LoopRun, lifecycle gates, and explicitly selected context remain explicit-only.


## Group Alias Routing

User-facing skill families, aliases, display strings, and Phase A entry mapping are defined in `docs/skill_registry.md` (the `family` column and Group Alias Map). This section defines only *when* group-selection mode is used and the platform guardrails around that selection.

Trigger guard:
- Enter group-selection mode only when the request carries an explicit family-framing token (`스킬군`, `그룹`, `계열`, `group`, `family`) or an explicit family name.
- Do not enter group-selection mode for bare domain words like `분석`, `검토`, `보고`, `계획`; those route by the normal Route Matrix.

When the trigger guard admits group-selection mode, resolve the family and its entry owner from the registry Group Alias Map. Do not maintain a second family-entry table here. A named Wiki remains an explicit `analysis-llm-wiki-context` operation within the `analysis` family; its evidence domain does not create another skill family.

Evidence vs research boundary (mirrored rule; `research-routing.md` is Codex-only, so this boundary lives here so both Codex and Claude apply it):
- Cross-domain evidence search (papers, code, runtime, visual, memory) belongs to the `search` family; the `search` entry opens an evidence lane and `search-paper-evidence` provides paper evidence as support.
- The whole task routes to the narrow matching `research` specialist only when the user develops a scientific claim, hypothesis, experiment, ablation, manuscript, or publishability decision.
- Implementation/plan/algorithm requests that merely mention paper/loss/model/experiment keep their implementation/planning/analysis primary; research attaches only as a support evidence lane.

Phase B note:
- Clear technical-analysis and research stages route directly to their narrow owners. When a missing distinction would change the deliverable, ask for that distinction instead of invoking a router surface. Clear evidence lanes, workflow owners, and bounded design/support specialists may also be selected directly from natural-language intent; hooks retain lifecycle gates.
- Persistent Memory and Knowledge writes, LLM Wiki reads, and evaluation review remain explicit operations.
- Loop engineering skills remain explicit/routing-controlled: readiness classification, verifier mapping, and loop execution are separate to avoid accidental long-running loops.
