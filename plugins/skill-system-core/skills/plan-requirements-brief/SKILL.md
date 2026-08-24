---
name: plan-requirements-brief
description: Distill discovery notes or decisions into a concise requirements contract/PRD with bounded scope, non-goals, observable acceptance criteria, assumptions, risks, and handoff notes. Use only when explicitly requested.
---

# Plan Requirements Brief

## Routing Card
- role: primary
- intent_signature: requirements contract, PRD, SRS-lite, or interview distillation
- use_when: the user explicitly asks to stabilize supplied discovery/decisions before planning
- do_not_use_when: elicitation, active-plan sync, packaging, implementation, validation execution, or lifecycle reporting is primary
- expected_inputs: decision evidence, constraints, contradictions, intended handoff, and optional Execution Handoff package/plan id
- expected_outputs: traceable proposed/accepted contract with bounded scope, material criteria, unknowns, and one next owner; when package-bound, `inputs/requirements-contract.yaml`
- context_targets: read supplied decision evidence; load `references/execution_handoff_input_contract.md` when package-bound, the contract/criteria templates for structured output, and only narrow canonical docs needed for compatibility claims
- risk_profile: read-only by default; when an associated package or explicit persistence request is supplied, write only `<package-root>/inputs/requirements-contract.yaml`; exclude full repo/memory, raw transcript duplication, unrelated logs, credentials, and secrets
- entry_scene: PREPARE

## Contract Boundary
Own `discovery -> requirements_contract` only when goals, scope, non-goals, assumptions, and observable criteria need no invented product decision. Keep it `proposed` until accepted or explicitly adopted downstream; never relabel it as an active plan, feasibility proof, implementation readiness, or approval.

In package-bound mode, use `execution-handoff-inputs-v1`. `proposed` is review input only;
`plan-execution-handoff` may treat the contract as scope/acceptance authority only after the named
owner records `accepted` with source references.

## Distillation Workflow
1. Prefer decision records over raw transcripts. Separate `decided`, `assumed`, `open`, and contradictory statements with source pointers for material decisions/conflicts.
2. Normalize one problem, goals, actors, scope, non-goals, and deferred work; preserve source wording when meaning is sensitive. When supplied intent speaks to execution, also preserve verification owner, attended/unattended mode, interaction availability, local-block continuation, and stop terms so downstream skills cannot silently reset them.
3. Create only value-bearing stories and stable IDs; link each material goal/story to an observable criterion or explicit deferral.
4. Move unresolved facts to assumptions, risks, or blocking questions; preserve contradictions rather than selecting a convenient answer.
5. Read narrow repo evidence only for compatibility claims; mark unsupported behavior or feasibility `Unverified`.
6. Select a downstream owner only after the gate passes.

Each criterion must trace to supplied intent and name actor/context, condition, observable result, boundary/exclusion, and evidence or user check. Replace vague qualities with a supplied threshold or an open decision; do not invent one. An agent-authored test or implementation command may be a verification hint, but it cannot define or independently prove a semantic/user-only product condition.

## Quality Gate
Pass only when every decision is sourced, contradictions stay visible, scope/non-goals prevent expansion, every material goal has criterion coverage or deferral, and each criterion has a decidable outcome plus a fitting evidence path/user check. Keep blockers and required approval explicit. Otherwise return only blocking questions or route to `plan-requirements-discovery`.

## Output And Handoff
For structured output use `references/requirements-contract-template.md`, admitting only relevant fields and source pointers for material decisions/conflicts. In package-bound mode, write the one canonical contract path and return its status/authority. Route one non-persisted executable slice to its task-specific Workflow, durable execution planning to `plan-execution-handoff`, and formal SDLC packaging to `report-lifecycle-artifacts`. Report status, blockers, and one next owner.
