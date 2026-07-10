---
name: plan-requirements-brief
description: Distill discovery notes or decisions into a concise requirements contract/PRD with bounded scope, non-goals, observable acceptance criteria, assumptions, risks, and handoff notes. Use only when explicitly requested.
---

# Plan Requirements Brief

## Routing Card
- role: primary
- intent_signature:
  - requirements contract, PRD, SRS-lite, or interview distillation
- use_when:
  - the user explicitly asks to stabilize supplied requirements before planning.
- do_not_use_when:
  - elicitation is still needed, or the request is active-plan sync, packaging, implementation, validation, or lifecycle reporting.
- expected_inputs:
  - discovery/decision evidence, constraints, and intended handoff
- expected_outputs:
  - traceable requirements contract with scope, criteria, risks, unknowns, and status
- context_targets:
  must_read:
    - current request and supplied requirements evidence
  read_if_needed:
    - `references/requirements-contract-template.md` for structured/persisted output
    - `references/acceptance-criteria-template.md` for vague or numerous criteria
    - narrow repo docs for required compatibility claims
  do_not_load_by_default:
    - full repo/memory, plan packages, represented raw transcripts, or unrelated logs
- risk_profile:
  reads:
    - supplied evidence and narrow referenced docs
  writes:
    - none by default; write only when requested
  tools:
    - none by default
  sensitive_resources:
    - omit credentials and secrets
- entry_scene:
  - PREPARE

## State Boundary
- Own `discovery -> requirements_contract` through `distill_requirements` only when goals, scope, non-goals, assumptions, and observable criteria need no invented decisions.
- Keep the result `proposed` until accepted or explicitly referenced downstream.
- Never report it as `active_plan`, `implementation_ready`, feasibility proof, or implementation approval.

## Distillation Workflow
1. Prefer the compact decision record over a raw transcript. Separate `decided`, `assumed`, `open`, and contradictory statements.
2. Normalize one problem, goals, actors, scope, non-goals, and deferred work; preserve source wording when meaning is sensitive.
3. Create only value-bearing user stories. Assign stable story/criterion ids and merge near-duplicates.
4. Link each material goal/story to an observable acceptance criterion or explicit deferral.
5. Move unresolved facts to assumptions, risks, or open questions with impact/blocking status; never decide speculatively.
6. Read narrow repo evidence only for compatibility claims; mark unsupported behavior or feasibility `Unverified`.
7. Select a downstream owner only after the Quality Gate passes.

Each criterion must name actor/context, condition, observable result, relevant boundary, and evidence/verification hint. Keep product acceptance separate from implementation commands. Replace vague qualities with a threshold or named reviewer check.

## Quality Gate
- Every product decision traces to supplied evidence; contradictions remain visible.
- Scope, non-goals, deferrals, and assumptions prevent silent expansion.
- Every material goal/story has acceptance coverage or explicit deferral.
- Each criterion has a decidable pass/fail outcome and evidence path/manual check.
- Terms, actors, ids, and criteria are consistent and non-duplicative.
- Blockers and required approval are explicit; downstream planning does not need the raw transcript.

If a missing product decision fails the gate, return only the blocking questions or route to `plan-requirements-discovery`.

## Output And Handoff
For structured output, read `references/requirements-contract-template.md` and populate only relevant problem, goals, users, scope/non-goals, stories, criteria, assumptions, risks, questions, handoff, and `proposed|accepted` status. Keep source pointers only for decisions or conflicts.

Route accepted current-horizon work to `plan-short-term-docs`, explicit phase/package work to `plan-long-term-package`, executable slices to `workflow-plan-runner`, and explicit formal SDLC packaging to `report-lifecycle-artifacts`. Report the state event, status, blockers, and one next owner.
