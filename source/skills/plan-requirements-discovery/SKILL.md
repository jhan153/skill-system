---
name: plan-requirements-discovery
description: Run an explicitly requested requirements interview that models decision dependencies, groups currently answerable independent decisions into bounded rounds, and stops at a traceable handoff without implying approval or implementation permission.
---

# Plan Requirements Discovery

## Routing Card
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
    - `references/task_working_state_contract.md` when material ambiguity, dependent state, or consequential freshness risk requires shared working-state semantics
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

### Resource Closure

```json
[
  {
    "source": "shared/docs/execution_handoff_input_contract.md",
    "target": "references/execution_handoff_input_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/task_working_state_contract.md",
    "target": "references/task_working_state_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "material ambiguity, dependent multi-turn state, or consequential freshness risk requires the shared working-state contract"
  }
]
```

## Exact Route
| Request | Owner |
| --- | --- |
| explicit requirements elicitation in dependency-aware question rounds | `plan-requirements-discovery` |
| product behavior decision for a concrete existing capability/path | `plan-behavior-discovery` |
| supplied answers to requirements contract | `plan-requirements-brief` |
| stable requirements to implementation | `workflow-implementation` |
| durable execution Plan/Handoff authoring or update | `plan-execution-handoff` |
| governed multi-session implementation Plan/Handoff pair | `plan-execution-handoff` |
| formal SDLC artifact/traceability package | `report-lifecycle-artifacts` |
| one clarification or lightweight gap review | no skill; answer directly |

Use exact owners. Keyword mentions of requirements or plans do not start an interview.

## State Boundary
- When the working-state condition applies, use the shared contract for sourced hard/soft constraints, evidence/authority, freshness, and selective correction. Keep question pacing and discovery persistence with this skill; no second state record is created.
- Own `scratch -> discovery`. Ask only for gaps that can change scope, acceptance, edge/failure behavior, data ownership, constraints, or non-goals.
- Record an answer only when it resolves/narrows a gap. Discovery completion is not an accepted contract, active plan, implementation approval, or feasibility proof.
- In package-bound mode, use `execution-handoff-inputs-v1` and update the one discovery record after each completed question round. `ready_for_distillation` authorizes Requirements Brief consumption only; it never authorizes execution.

## Interview Workflow
1. Extract supplied facts, decisions, assumptions, and open gaps before asking.
2. Build a **decision-dependency graph**: each open decision names the earlier decisions or fact checks required to make its wording and options valid. Rank blocking or irreversible decisions first, then costly scope/interface decisions, then preferences.
3. Resolve discoverable facts yourself through the narrowest admitted source or tool. A fact lookup is an unsettled prerequisite, so delay only its descendants. Delegate independent lookups only when the host supports it and current user/repository authority permits delegation; otherwise inspect locally.
4. Derive the **ready-question set**: open decisions whose decision and fact prerequisites are settled. Ask up to three mutually independent high-value questions in one numbered round. Give each a short consequence and, when useful, 2–4 exclusive options with the recommended choice first and its tradeoff.
5. Ask exactly one question when another candidate depends on its answer, the decision is irreversible or high-stakes enough to require focused steering, the user requests one-at-a-time pacing, or the host interaction surface admits only one.
6. Record only each ledger delta: id, prerequisite ids, question, answer, `decided|assumed|open`, affected scope/criterion, and source.
7. Recompute dependencies and the ready-question set after every round. Never carry a question forward unchanged when an answer altered its premise; never repeat a settled decision or ask the user for a fact that admitted evidence can resolve.
8. Stop when no ready or deferred in-scope decision remains, readiness passes, the user stops, or a blocking answer belongs to another answer owner. Use `plan-question-document` only on an explicit request for a local question document.

## Readiness Gate
Applicable dimensions must be decided or explicitly recorded with impact, owner, and blocking status:

- objective, actor, observable success
- scope, non-goals, deferrals
- domain rules/ownership and acceptance/edge/failure behavior
- data, privacy, permissions, credentials, external systems
- UI/API/runtime constraints and validation/launch expectations

Handoff is ready when no unrecorded unknown blocks a requirements contract.

## Output And Handoff
- During interview turns, return only the current ready-question round, short rationale/options, and latest ledger deltas when needed; never replay the full record.
- At stop or explicit artifact request, load the record template and emit populated decisions, terms, constraints, non-goals, edges, acceptance signals, assumptions, open questions, and handoff. In package-bound mode, return the record path and `active`, `ready_for_distillation`, or `stopped_with_open_questions` status.
- Hand a ready record to `plan-requirements-brief`; preserve unresolved answer-owner decisions as open/unverified rather than inventing them.
