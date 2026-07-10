---
name: plan-requirements-discovery
description: Run a one-question-at-a-time requirements interview that converts goals, scope, constraints, edge cases, non-goals, and assumptions into explicit decisions before planning or implementation. Use only when the user explicitly requests guided discovery.
---

# Plan Requirements Discovery

## Routing Card
- role: primary
- intent_signature:
  - requirements/scope discovery interview
  - ask questions before PRD, plan, or implementation
- use_when:
  - the user explicitly asks for guided elicitation and meaningful requirements gaps remain.
- do_not_use_when:
  - requirements are stable, one clarification is enough, or the user requests direct implementation, plan synchronization, packaging, validation, or reporting.
- expected_inputs:
  - rough goal, known constraints/non-goals, domain hints, and willingness to answer
- expected_outputs:
  - decision ledger and a discovery record ready for requirements distillation
- context_targets:
  must_read:
    - current discovery request and provided goal/notes
  read_if_needed:
    - `references/interview-protocol.md` for a complex interview
    - `references/discovery-record-template.md` when persisting or handing off the record
    - narrow repo docs when discovery must match an existing surface
  do_not_load_by_default:
    - full repo, memory bank, plan packages, or unrelated implementation files
- risk_profile:
  reads:
    - user-provided notes and narrowly referenced artifacts
  writes:
    - none by default; persist a record only when explicitly requested
  tools:
    - none by default
  sensitive_resources:
    - do not request secrets or private data unless necessary and explicitly scoped
- entry_scene:
  - PREPARE

## State Boundary
- Own `scratch -> discovery` in the shared Planning State Model.
- Fire `ask_decision_question` only for a gap that can change scope, acceptance, edge behavior, data ownership, constraints, or non-goals.
- Fire `record_decision` only when an answer resolves or narrows that gap.
- Do not treat discovery completion as an approved requirements contract, active plan, or implementation permission.

## Interview Workflow
1. Extract known facts, explicit decisions, assumptions, and open gaps from the provided material before asking anything.
2. Rank gaps by downstream impact: blocking/irreversible decisions first, then costly scope or interface decisions, then preferences.
3. Ask exactly one highest-impact question. Explain its effect in one sentence; when useful, put the recommended choice first among 2-4 mutually exclusive options and state the tradeoff briefly.
4. Record a ledger delta: decision id, question, answer, status (`decided`, `assumed`, or `open`), affected scope/criterion, and source.
5. Re-rank remaining gaps after each answer. Skip questions whose answers are safely inferable from admitted context.
6. Stop when the Discovery Readiness Gate passes, the user stops, or one unresolved blocking decision requires an external stakeholder.

Do not ask broad questionnaires, trivia, implementation details with no product effect, or the same decision in different wording.

## Discovery Readiness Gate
Confirm applicable dimensions are either decided or explicitly recorded as assumptions/open questions:

- objective, target actor, and observable success signal
- scope, non-goals, and deferred work
- domain terms/business rules and ownership boundaries
- acceptance behavior, edge/failure cases, and excluded behavior
- data, privacy, permissions, credentials, and external-system constraints
- UI/API/runtime constraints and validation/launch expectations

Handoff is ready when no unrecorded unknown blocks a requirements contract. A known open question may remain only with its impact, owner, and blocking status.

## Token-Efficient Output
During the interview, return only:

- the next decision-bearing question;
- its short rationale/options when useful; and
- the latest ledger delta when continuity requires it.

Do not repeat the full discovery record every turn. At stop or explicit artifact request, use `references/discovery-record-template.md` and emit only populated sections: discovery scope, decisions, domain terms, constraints, non-goals, edge cases, acceptance signals, assumptions, open questions, and handoff target.

## Handoff
- Use `plan-requirements-brief` to distill an accepted discovery record into a requirements contract.
- Use `plan-short-term-docs` only for an explicitly requested active `docs/plan` artifact.
- Use `plan-long-term-package` only for explicit heavy package intent.
- Hand implementation to its workflow only after requirements are stable enough for execution.

Report unresolved blockers as `user-verification-needed` or `unverified`; never invent stakeholder decisions.
