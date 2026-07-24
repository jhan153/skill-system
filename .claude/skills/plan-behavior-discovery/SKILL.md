---
name: plan-behavior-discovery
description: Run an explicitly requested, one-question behavior discovery turn for an existing implementation or user path, grounding each choice in underlying source/runtime anchors and stopping when the next human-operable slice is decision-ready. Use after a core capability exists but product interaction, failure, recovery, or adaptation remains unresolved; do not use for greenfield requirements, quizzes, explanation, or direct implementation.
disable-model-invocation: true
---

# Plan Behavior Discovery

## Routing Card
- role: primary
- intent_signature: post-implementation behavior discovery or next human-operable slice decision
- use_when:
  - the user explicitly asks to resolve product-facing behavior for a concrete existing capability/path one decision at a time.
- do_not_use_when:
  - greenfield elicitation belongs to `plan-requirements-discovery`; selected code work to `workflow-implementation`; explanation artifacts to `report-implementation-explainer`.
  - the user asks for recall testing, generic ideation, bug diagnosis, implementation verification, or an exhaustive release checklist.
- expected_inputs: concrete capability/path, underlying current-behavior anchors, actor/constraints, accepted decisions, and open behavior gaps
- expected_outputs: one evidence-grounded question, a ledger delta, and a bounded next-slice handoff
- context_targets:
  must_read:
    - explicit discovery request, target capability/actor/path, and smallest underlying source/runtime evidence
  read_if_needed:
    - narrow production path, trace/readback, accepted product decisions, or an explainer used only to locate its cited anchors
  do_not_load_by_default:
    - full repository/roadmap/release plan/history or every possible UX question
- risk_profile:
  reads: supplied decisions and narrow source/runtime evidence
  writes: none by default; persist a record only when explicitly requested
  tools: focused read-only inspection; no implementation or validation execution
  sensitive_resources: credentials/private data default deny; prefer anonymized states
- entry_scene: PREPARE

## Decision Contract

Own one `one_shot` decision turn within `core_capability_available -> next_vertical_slice_decision_ready`. The conversation may continue with another explicit turn, but no persisted plan state, implementation approval, operability, validation, or release completion follows automatically.

Ask only about what a person can do or observe. Open-book source, docs, and side-chat use is valid; progress is an observable product decision, not code recall or a claim of understanding.

An implementation explainer is a navigation aid, not current-behavior evidence. Re-open its cited production source/runtime/test anchors before using a claim. If the anchor is missing or stale, label current behavior `unverified`. Otherwise label it `runtime_observed`, `source_established`, or `inferred`; label missing desired behavior `open_product_decision` and preserve conflicts with accepted intent.

## Question Admission

Before asking, establish the exact operation/path, current evidence or `unverified` status, desired authority or open-decision status, representative initial state, observable differences among choices, and consequence for the next slice.

For irreversible/high-risk choices—persistent data, topology mutation, external side effects, security/safety, or hard compatibility boundaries—also require the transaction boundary and a falsifying observation. For reversible low-risk interaction choices, one discriminating observable is enough. If required context is missing, inspect the smallest source/readback first or ask for that fact; do not ask abstract “before or after mutation” questions without an operation and observable state.

## Interview Workflow

1. State the capability, actor, accepted decisions, current anchored behavior, assumptions, and gaps without calling the feature complete.
2. Rank only applicable gaps by next-path blocking impact, irreversibility, and interface cost: selection, preview/commit/cancel, undo/recovery, invalid input/atomicity, feedback, persistence/compatibility, accessibility.
3. Ask exactly one question using `scenario`, `current_behavior` (label + underlying anchor), `decision` (2–4 exclusive choices; recommendation first with tradeoff), and `observable_contract`.
4. Record only the delta: id, scenario, anchor, choice, `decided|assumed|delegated|open`, observable contract, affected scope, source, deferrals. A delegated default is an assumption, not comprehension evidence.
5. Re-rank and stop when one next human-operable slice has an exact user path, observable success, applicable cancel/failure/recovery behavior, named decision sources, and no unrecorded blocker. Do not continue toward total feature/release coverage.

## Output And Handoff

During the interview, return current evidence, the one question, and the latest delta when useful. At stop or explicit artifact request, return a compact `behavior_decision_record`: capability snapshot, next user path, decisions/open deferrals, observable acceptance/falsifiers where required, implementation handoff, and remaining productization gaps.

Hand selected code work to `workflow-implementation`; explanation needs to `report-implementation-explainer`; use `plan-requirements-discovery` when no concrete capability/path exists. Before returning, confirm one active decision, an underlying evidence anchor, risk-proportional admission, observable options, and the next-slice stop. Emit no quiz score, `understood` flag, implementation permission, or release claim.
