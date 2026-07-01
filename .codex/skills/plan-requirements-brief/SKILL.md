---
name: plan-requirements-brief
description: Distill requirements discovery notes, stakeholder answers, or decision logs into a requirements contract or PRD/SRS-lite with goals, scope, non-goals, user stories, acceptance criteria, assumptions, risks, and handoff notes. Use only when explicitly requested.
---

# Plan Requirements Brief

## Routing Card
- role: primary
- intent_signature:
  - requirements brief
  - requirements contract
  - PRD
  - SRS-lite
  - 요구사항 계약
  - 요구사항 정리
- use_when:
  - the user explicitly asks to turn discovery notes, answers, or decisions into a requirements brief, PRD, or SRS-lite.
  - requirements must be stabilized before HLD, LLD, active planning, or implementation.
  - scope, non-goals, user stories, and acceptance criteria need a reusable contract.
- do_not_use_when:
  - requirements still need interactive elicitation; use `plan-requirements-discovery`.
  - the user wants active `docs/plan` synchronization; use `plan-short-term-docs`.
  - the user wants a heavy phase/package plan; use `plan-long-term-package`.
  - the user wants direct implementation, validation execution, lifecycle reporting, or critique-only review.
- expected_inputs:
  - discovery record, stakeholder answers, decision log, rough requirements, or product notes
  - target product/feature/workflow and known constraints
  - intended handoff target when available
- expected_outputs:
  - requirements-contract or feature-requirements-brief
  - goals, scope, non-goals, user stories, acceptance criteria, assumptions, risks, open questions, and handoff notes
- context_targets:
  must_read:
    - current brief request
    - provided discovery notes, decision logs, or rough requirements
  read_if_needed:
    - `references/requirements-contract-template.md`
    - `references/acceptance-criteria-template.md`
    - narrow repo docs only when the requirements contract must match an existing product surface
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated plan packages
    - validation logs unless the user asks to include evidence status
- risk_profile:
  reads:
    - user-provided requirements artifacts and narrow referenced docs
  writes:
    - none by default; write a requirements artifact only when explicitly requested
  tools:
    - none by default
  sensitive_resources:
    - credentials default deny; do not include secrets in requirements artifacts
- entry_scene:
  - PREPARE

## Purpose
- Convert raw discovery into a stable requirements contract.
- Preserve non-goals and assumptions so later planning does not expand scope silently.
- Hand off to HLD/LLD-style planning or implementation without pretending the brief is executable code work.

## Brief Rules
- Keep the brief decision-grounded, not aspirational.
- Include non-goals and deferred scope.
- Acceptance criteria must be observable.
- Mark unresolved questions explicitly instead of inventing product decisions.
- Separate product success criteria from implementation validation commands.

## Output Contract
Return only the sections needed:
- `problem`
- `goals`
- `target_users`
- `scope`
- `non_goals`
- `user_stories`
- `acceptance_criteria`
- `assumptions`
- `risks`
- `open_questions`
- `handoff_notes`

## Handoff
- Use `plan-long-term-package` for phase/package architecture planning after the requirements contract is accepted.
- Use `plan-short-term-docs` for current-horizon implementation design records.
- Use `workflow-plan-runner` only after an executable plan/spec slice exists.
- Use `report-lifecycle-artifacts` when the brief should be packaged into a formal SDLC artifact set.

## Known Limits
- A requirements brief is not an implementation plan.
- It does not validate feasibility without source inspection or implementation evidence.
- It should not replace user approval for product decisions.
