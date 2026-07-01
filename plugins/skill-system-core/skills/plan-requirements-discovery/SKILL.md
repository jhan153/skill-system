---
name: plan-requirements-discovery
description: Run a human-in-loop requirements discovery interview before planning or implementation, eliciting goals, domain terms, constraints, edge cases, non-goals, assumptions, and unresolved questions one decision at a time. Use only when explicitly requested.
---

# Plan Requirements Discovery

## Routing Card
- role: primary
- intent_signature:
  - requirements discovery
  - guided requirements interview
  - 요구사항 인터뷰
  - 구현 전에 질문
  - scope discovery
- use_when:
  - the user explicitly asks to be questioned before PRD, HLD, LLD, planning, or implementation.
  - the request has a meaningful requirements gap and the user wants guided discovery rather than immediate execution.
  - domain terms, constraints, non-goals, edge cases, or acceptance boundaries must be elicited from the user.
- do_not_use_when:
  - the user already provided stable requirements or an approved spec.
  - the user asks for direct implementation, active `docs/plan` synchronization, phase package planning, validation execution, or lifecycle reporting.
  - a brief clarification question is enough for a small one-shot task.
- expected_inputs:
  - rough goal, idea, feature, bugfix intent, or product direction
  - known constraints, target user, domain, repo area, or non-goals when available
  - explicit user willingness to answer questions
- expected_outputs:
  - requirements-discovery-record with question/answer decisions
  - domain terms, goals, constraints, assumptions, risks, edge cases, non-goals, and open questions
  - handoff notes for `plan-requirements-brief`, `plan-long-term-package`, or `plan-short-term-docs`
- context_targets:
  must_read:
    - current discovery request
    - any provided rough goal, notes, screenshots, docs, or repo slice explicitly in scope
  read_if_needed:
    - `references/interview-protocol.md`
    - `references/discovery-record-template.md`
    - narrow repo docs only when the user asks to discover requirements against an existing codebase
  do_not_load_by_default:
    - full repo
    - full memory bank
    - plan packages
    - implementation files unrelated to the elicitation target
- risk_profile:
  reads:
    - user-provided notes and narrowly referenced artifacts
  writes:
    - none by default; write a discovery artifact only when explicitly requested
  tools:
    - none by default
  sensitive_resources:
    - credentials default deny; do not ask the user to reveal secrets or private data unless absolutely necessary and explicitly scoped
- entry_scene:
  - PREPARE

## Purpose
- Elicit requirements before they become a PRD, HLD, LLD, active plan, or implementation task.
- Force missing assumptions into explicit decisions.
- Produce a reusable discovery record without pretending it is an implementation plan.

## Interview Rules
1. Ask one decision-bearing question at a time.
2. Include 2-4 recommended answer options when that helps the user decide quickly.
3. Prefer questions that change scope, acceptance criteria, edge behavior, data ownership, constraints, or non-goals.
4. Do not ask trivia or questions whose answer can be safely inferred from provided context.
5. Stop when the remaining unknowns are minor enough to hand off as assumptions or open questions.

## Discovery Dimensions
- goal and success signal
- target user or actor
- domain terms and business rules
- scope, non-goals, and deferred work
- acceptance criteria and failure cases
- data, permissions, privacy, credentials, and external systems
- UI/API/runtime constraints when relevant
- validation and launch expectations

## Output Contract
Return only the sections needed:
- `discovery_scope`
- `decisions_made`
- `domain_terms`
- `constraints`
- `non_goals`
- `edge_cases`
- `acceptance_signals`
- `open_questions`
- `handoff_target`

## Handoff
- Use `plan-requirements-brief` when the discovery record should become a requirements contract or PRD/SRS-lite.
- Use `plan-long-term-package` only when the user explicitly wants a heavy phase/package architecture plan.
- Use `plan-short-term-docs` only when the user wants an active `docs/plan` implementation design record.
- Use implementation workflows only after requirements are stable enough for execution.

## Known Limits
- This skill discovers requirements; it does not write production code.
- It does not replace product judgment from the user or stakeholders.
- It should not block obvious small changes with an interview.
