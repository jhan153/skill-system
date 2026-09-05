---
name: workflow-prototype
description: Build the smallest throwaway runnable artifact that answers one explicit unresolved UI, interaction, state, or logic question before production implementation. Use when the user asks for a prototype, spike, side-by-side UI alternatives, or an executable state/logic model whose observation will select or reject a direction; do not use for vague ideation, an already-selected production change, bug diagnosis or repair, or proof of performance, security, accessibility, concurrency, or release readiness.
---

# Workflow Prototype

## Routing Card
- role: primary
- family: workflow
- intent_signature: one bounded product or engineering question answered by a runnable disposable artifact
- use_when:
  - the user explicitly requests a prototype or spike and can name, or safely delegate, the decision it must inform.
  - observing UI variants or exercising a small state/logic model is cheaper and more discriminating than more discussion.
- do_not_use_when:
  - the task is open-ended ideation, requirements discovery, ordinary production implementation, bug work, validation-only work, or a behavior-preserving refactor.
  - the desired claim requires representative load, production data, security review, accessibility audit, concurrency evidence, or real integration behavior.
- expected_inputs: one question, decision owner, discriminating observation, target project/runtime, budget/stop, write boundary, retention boundary, and excluded claims
- expected_outputs: isolated runnable prototype, one exact launch instruction, observation guide, bounded verdict or pending-decision state, proof ceiling, retention status, and production handoff
- context_targets:
  must_read:
    - current question and target decision
    - repository instructions and the smallest relevant route/module/runtime path
    - local run command, components/tooling, and data/state shape needed for a representative observation
  read_if_needed:
    - accepted behavior decisions, safe fixtures, nearby prototypes, or the exact external boundary being stubbed
  do_not_load_by_default:
    - full repository, broad plans, unrelated design system internals, production data, credentials, or live mutation paths
- risk_profile:
  reads: scoped target context and representative safe data/state shapes
  writes: isolated prototype files within the authorized boundary; optional branch/worktree only when repository policy permits it; no cleanup or deletion without explicit authorization
  tools: host runtime plus the narrowest build, preview, browser, terminal, file-open, or smoke operation needed to observe the question
  sensitive_resources: deny credentials and production data; stub external writes unless that boundary is the explicit question and separately authorized
- entry_scene: PREPARE

## Prototype Contract

Treat the artifact as decision evidence, not early production. Before writing, lock one `question`, `decision_owner`, discriminating `observation`, `decision_rule`, `budget_stop`, `proof_ceiling`, and `retention`/cleanup trigger. Infer only reversible fields that do not change the deliverable. If no observation can discriminate outcomes, return to behavior or requirements discovery; if UI and logic are both open, prototype only the one blocking the next decision unless two artifacts were explicitly requested.

## Select The Artifact Shape

- For layout, hierarchy, density, control placement, navigation, or interaction comparison, read [UI Prototype](references/ui-prototype.md) and build a UI comparison in the real host surface when safe.
- For state transitions, invariants, command semantics, reducer/state-machine shape, or domain feedback, read [Logic Prototype](references/logic-prototype.md) and expose a deterministic rule model through one browser-openable HTML evidence page.
- For a question that depends on performance, security, accessibility, concurrency, persistence durability, or production integration, use the specialist actual-path workflow instead. A throwaway harness may illustrate behavior but cannot close that claim.

## Workflow

1. Bind the contract, current evidence, non-goals, and resulting decision.
2. Inspect the smallest real host path. Reuse local runtime/components/fixtures for UI or authoritative rules and safe fixtures for logic.
3. Isolate and mark the artifact `PROTOTYPE`. Prefer a route/story/preview/nearby file; use a branch/worktree only when explicitly requested or required by repository policy. Never disturb unrelated work or push without authorization.
4. Build only the discriminator. Stub mutations/external systems, keep state in memory, and omit polish, generalized abstractions, migrations, persistence, analytics, and production hardening unless they are the question.
5. Provide one exact launch instruction and expose the decisive variants/actions/states without source inspection.
6. Observe and classify `selected`, `supported`, `contradicted`, or `inconclusive`. Human/private judgment stays `user-verification-needed` until the owner responds.
7. Keep comparison evidence runnable and outside production until observation. After explicit selection, hand off to the production owner; clean up only on request or the agreed trigger.

## Guardrails

Use structurally discriminating variants and representative safe fixtures without real external mutation. Add no framework, package, persistence, backend, or generic abstraction merely for the prototype. Builds, mocks, screenshots, and self-authored checks prove only their boundary; never claim production correctness, scalability, security, accessibility, reliability, integration, or release readiness. Do not silently merge or delete the evidence while its decision is pending; only a small validated pure core may be lifted after ownership and production checks are explicit.

## Validation And Output

Confirm the launch instruction, question/observation match, side-effect boundary, budget, proof ceiling, and runnable retention. Apply the selected UI/logic reference's additional checks.

Return only applicable fields:

- `prototype_question`
- `artifact_shape` and changed paths
- `launch_instruction`
- `observation_guide`
- `verdict` and decisive evidence
- `proof_ceiling`
- `production_handoff`
- `retention_or_cleanup`
