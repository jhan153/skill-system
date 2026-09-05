# Planning Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `plan-behavior-discovery`

- role: primary
- family: planning
- intent_signature: post-implementation behavior discovery or next human-operable slice decision
- use_when:
  - the user explicitly asks to resolve product-facing behavior for a concrete existing capability/path one decision at a time.
- do_not_use_when:
  - greenfield elicitation belongs to `plan-requirements-discovery`; selected code work to `workflow-implementation`; explanation artifacts to `report-implementation-explainer`.
  - the user asks for recall testing, generic ideation, bug diagnosis, implementation verification, or an exhaustive release checklist.
- expected_inputs: concrete capability/path, underlying current-behavior anchors, actor/constraints, accepted decisions, open behavior gaps, and optional Execution Handoff package/plan id
- expected_outputs: one evidence-grounded question, a ledger delta, and a bounded next-slice handoff; when package-bound, `inputs/behavior-decisions.md`
- context_targets:
  must_read:
    - explicit discovery request, target capability/actor/path, and smallest underlying source/runtime evidence
  read_if_needed:
    - narrow production path, trace/readback, accepted product decisions, or an explainer used only to locate its cited anchors
    - `references/execution_handoff_input_contract.md` and `references/behavior-decision-record.md` when persisting into an associated package
  do_not_load_by_default:
    - full repository/roadmap/release plan/history or every possible UX question
- risk_profile:
  reads: supplied decisions and narrow source/runtime evidence
  writes: none by default; when an associated package or explicit persistence request is supplied, update only `<package-root>/inputs/behavior-decisions.md`
  tools: focused read-only inspection; no implementation or validation execution
  sensitive_resources: credentials/private data default deny; prefer anonymized states
- entry_scene: PREPARE

## `plan-decision-map`

- role: primary
- family: planning
- intent_signature: explicit durable map of unresolved decisions for a multi-session outcome
- use_when:
  - the user explicitly invokes `plan-decision-map` or requests a persistent decision map.
  - the target outcome is stable enough to name, while material prerequisites and choices are still unknown.
- do_not_use_when:
  - one discovery round, requirements brief, tactical plan, or implementation task can cover the work.
  - the requested artifact is a build backlog, phase package from settled decisions, status report, or execution queue.
- expected_inputs: target outcome, decision owner, scope boundary, known constraints, authorized workspace, optional Execution Handoff package/plan id, and optional existing map
- expected_outputs: one canonical package-local decision index, bounded decision items, prerequisite links, current ready set, unshaped unknowns, exclusions, and one next-owner recommendation when decision work closes
- context_targets:
  must_read:
    - current request or named decision index
    - repository instructions and the authorized artifact boundary
    - `references/execution_handoff_input_contract.md` before resolving a persistent artifact path
    - [Decision-map schema](references/decision-map-schema.md) before creating or changing artifacts
  read_if_needed:
    - the selected item, its prerequisites, linked resolutions, and evidence that can change its answer
    - existing requirements or domain contracts that constrain the target outcome
  do_not_load_by_default:
    - all item bodies, full repository history, unrelated plans, or every prior session
- risk_profile:
  reads: begin with the index and admit detail only for the selected item
  writes: local Markdown under the associated Execution Handoff `inputs/decision-map/`; a named external tracker still requires separate mutation authority
  tools: narrow evidence, prototype, or coordination tools only when their own routing and authority contracts are met
  sensitive_resources: credentials and production data denied; never store secrets in planning artifacts
- entry_scene: PREPARE

## `plan-execution-handoff`

- role: primary
- family: planning
- intent_signature: durable canonical Plan/Handoff pair with one typed graph archetype, bounded rewrites, and event-driven lifecycle coordination
- use_when: explicit pair, durable single-node execution, accepted repeated verifier-driven work, long-running DAG, phase-gated/risk-adaptive method selection, ownership/lock routing, or cross-session continuation
- do_not_use_when: direct implementation, status-only reporting, a small one-session short-term plan, lightweight one-off handoff, continuous polling, fixed/busy waits, or unrelated sibling scope
- expected_inputs: outcome, repository/plan identity, scope/approval, current baseline, graph-selection constraints, rough node timing, validation, and human boundary
- expected_outputs: validated canonical pair with one typed acyclic DAG, Core execution-item intake, implementation/review/repair gates, compact lifecycle state, and worker-done timing observations
- context_targets: request, repository rules, selected profile/reference, current source/callers, one disconfirming path, lifecycle capability, and resource stops
- risk_profile: writes only the requested planning pair; no production source, Git mutation, automatic coordinator polling, fixed/busy waits, external state, or invented model/skill substitutions
- entry_scene: PREPARE

## `plan-question-document`

- role: primary
- family: planning
- intent_signature: explicit local question document for one answer owner
- use_when:
  - the user explicitly requests a questionnaire or meeting-fill document for one person who owns a material knowledge gap.
- do_not_use_when:
  - the current user can resolve the questions through live discovery.
  - the requested work is audience-scale survey design, requirements distillation, interview facilitation without an artifact, or external delivery.
- expected_inputs: recipient role, knowledge ownership, decisions or facts needed back, downstream use, tone/language, effort or deadline constraints, optional output path, and optional Execution Handoff package/plan id
- expected_outputs: one recipient-ready Markdown file, a coverage readback, unresolved setup assumptions, and an explicit no-delivery statement; when package-bound, `inputs/question-documents/<topic>.md`
- context_targets:
  must_read:
    - current request and supplied recipient/outcome context
    - `references/execution_handoff_input_contract.md` before resolving a package-local path
    - [Question-document template](references/question-document.md) before authoring
  read_if_needed:
    - only supplied notes needed to give the recipient sufficient orientation
  do_not_load_by_default:
    - full repository, unrelated requirements, contact systems, private profiles, or unstated recipient data
- risk_profile:
  reads: current request and explicitly supplied supporting notes
  writes: one local Markdown artifact; prefer the associated package's `inputs/question-documents/` path when bound
  external_state: no sending, sharing, uploading, calendar creation, or messaging
  sensitive_resources: never request credentials, secrets, or personal/production data not required by the named decision
- entry_scene: PREPARE

## `plan-requirements-brief`

- role: primary
- family: planning
- intent_signature: requirements contract, PRD, SRS-lite, or interview distillation
- use_when: the user explicitly asks to stabilize supplied discovery/decisions before planning
- do_not_use_when: elicitation, active-plan sync, packaging, implementation, validation execution, or lifecycle reporting is primary
- expected_inputs: decision evidence, constraints, contradictions, intended handoff, and optional Execution Handoff package/plan id
- expected_outputs: traceable proposed/accepted contract with bounded scope, material criteria, unknowns, and one next owner; when package-bound, `inputs/requirements-contract.yaml`
- context_targets: read supplied decision evidence; load `references/execution_handoff_input_contract.md` when package-bound, the contract/criteria templates for structured output, and only narrow canonical docs needed for compatibility claims
- risk_profile: read-only by default; when an associated package or explicit persistence request is supplied, write only `<package-root>/inputs/requirements-contract.yaml`; exclude full repo/memory, raw transcript duplication, unrelated logs, credentials, and secrets
- entry_scene: PREPARE

## `plan-requirements-discovery`

- role: primary
- family: planning
- intent_signature: guided requirements/scope interview before PRD, planning, or implementation
- use_when:
  - the user explicitly requests guided elicitation and material requirement gaps remain
- do_not_use_when:
  - requirements are stable, one clarification/direct answer is enough, or execution/artifact work is requested
- expected_inputs: rough goal, known constraints/non-goals, domain hints, notes, willingness to answer, and optional Execution Handoff package/plan id
- expected_outputs: incremental decision-dependency graph, ready-question set, decision ledger, and discovery record ready for distillation; when package-bound, `inputs/requirements-discovery.yaml`
- context_targets:
  must_read:
    - discovery request and supplied goal/notes
  read_if_needed:
    - `references/interview-protocol.md` for complex interviews
    - `references/discovery-record-template.md` only for persistence/handoff
    - `references/execution_handoff_input_contract.md` when resolving an associated package path
    - narrow repo evidence for an existing target surface
  do_not_load_by_default:
    - full repo/memory, plan packages, unrelated implementation
- risk_profile:
  reads:
    - supplied notes and scoped artifacts
  writes:
    - none by default; when an associated package or explicit persistence request is supplied, update only `<package-root>/inputs/requirements-discovery.yaml`
  tools:
    - none by default
  sensitive_resources:
    - do not request secrets/private data without explicit necessity and scope
- entry_scene: PREPARE

## `plan-task-handoff`

- role: support
- family: planning
- intent_signature: explicit task DAG, handoff, ownership/lock split, or artifact/verification inventory
- use_when: the user explicitly requests coordination across agents, sessions, or workstreams, or a handoff/inventory
- do_not_use_when: direct implementation, ordinary goal/status summary, or persistent event, workflow, deployment, or completion state
- expected_inputs: request plus the minimum relevant plan slice, task list, diff, artifact set, and any canonical skill IDs already selected for delegated tasks
- expected_outputs: smallest requested response or explicitly requested document, preserving already selected skills at the worker boundary
- context_targets: task-local inputs; `references/handoff-schemas.md` when structure helps; repository team conventions only when needed
- risk_profile: task-local reads, no tools by default, no file write without an explicit document request, and secrets redacted
- entry_scene: PREPARE

Choose the smallest requested mode:
- `brief`: provide a short objective, non-goals, success signal, and continuation note. Add a 3-6 node task DAG only when the user requests decomposition or dependencies.
- `multi_agent`: add non-overlapping lock scopes, one owner per scope, serialization for shared files, and one validation owner per task.
- `artifact_inventory`: list changed/generated artifacts, labeled validation evidence, user checks, and stale follow-ups.

An explicit changed/generated-file or validation-evidence list is `artifact_inventory` even without the word handoff.
Combine modes only when both needs are explicit. An artifact list or short session handoff alone does not justify a task DAG.
