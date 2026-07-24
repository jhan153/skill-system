---
name: plan-requirements-discovery
description: Run an explicitly requested one-question requirements interview that records decision-bearing gaps and stops at a traceable handoff without implying approval or implementation permission.
disable-model-invocation: true
---

# Plan Requirements Discovery

## Routing Card
- role: primary
- intent_signature: guided requirements/scope interview before PRD, planning, or implementation
- use_when:
  - the user explicitly requests guided elicitation and material requirement gaps remain
- do_not_use_when:
  - requirements are stable, one clarification/direct answer is enough, or execution/artifact work is requested
- expected_inputs: rough goal, known constraints/non-goals, domain hints, notes, and willingness to answer
- expected_outputs: incremental decision ledger and discovery record ready for distillation
- context_targets:
  must_read:
    - discovery request and supplied goal/notes
  read_if_needed:
    - `references/interview-protocol.md` for complex interviews
    - `references/discovery-record-template.md` only for persistence/handoff
    - narrow repo evidence for an existing target surface
  do_not_load_by_default:
    - full repo/memory, plan packages, unrelated implementation
- risk_profile:
  reads:
    - supplied notes and scoped artifacts
  writes:
    - none by default; persist only when explicitly requested
  tools:
    - none by default
  sensitive_resources:
    - do not request secrets/private data without explicit necessity and scope
- entry_scene: PREPARE

## Exact Route
| Request | Owner |
| --- | --- |
| explicit one-question elicitation | `plan-requirements-discovery` |
| product behavior decision for a concrete existing capability/path | `plan-behavior-discovery` |
| supplied answers to requirements contract | `plan-requirements-brief` |
| stable requirements to implementation | `workflow-implementation` |
| active `docs/plan` synchronization | `plan-short-term-docs` |
| explicit multi-phase planning package | `plan-long-term-package` |
| formal SDLC artifact/traceability package | `report-lifecycle-artifacts` |
| one clarification or lightweight gap review | no skill; answer directly |

Use exact owners. Keyword mentions of requirements or plans do not start an interview.

## State Boundary
- Own `scratch -> discovery`. Ask only for gaps that can change scope, acceptance, edge/failure behavior, data ownership, constraints, or non-goals.
- Record an answer only when it resolves/narrows a gap. Discovery completion is not an accepted contract, active plan, implementation approval, or feasibility proof.

## Interview Workflow
1. Extract supplied facts, decisions, assumptions, and open gaps before asking.
2. Rank blocking/irreversible decisions first, then costly scope/interface decisions, then preferences.
3. Ask exactly one highest-impact question. State its consequence briefly; when useful, offer 2–4 exclusive options with the recommended choice first and its tradeoff.
4. Record only the ledger delta: id, question, answer, `decided|assumed|open`, affected scope/criterion, and source.
5. Re-rank after each answer. Skip questions safely resolved by admitted evidence; never repeat an answered decision or use a broad questionnaire.
6. Stop when readiness passes, the user stops, or a blocking decision belongs to an external stakeholder.

## Readiness Gate
Applicable dimensions must be decided or explicitly recorded with impact, owner, and blocking status:

- objective, actor, observable success
- scope, non-goals, deferrals
- domain rules/ownership and acceptance/edge/failure behavior
- data, privacy, permissions, credentials, external systems
- UI/API/runtime constraints and validation/launch expectations

Handoff is ready when no unrecorded unknown blocks a requirements contract.

## Output And Handoff
- During interview turns, return only the next decision-bearing question, short rationale/options, and latest ledger delta when needed; never replay the full record.
- At stop or explicit artifact request, load the record template and emit populated decisions, terms, constraints, non-goals, edges, acceptance signals, assumptions, open questions, and handoff.
- Hand a ready record to `plan-requirements-brief`; preserve unresolved stakeholder decisions as open/unverified rather than inventing them.
