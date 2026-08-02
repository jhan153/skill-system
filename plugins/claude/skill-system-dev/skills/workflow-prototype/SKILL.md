---
name: workflow-prototype
description: Build the smallest throwaway runnable artifact that answers one explicit unresolved UI, interaction, state, or logic question before production implementation. Use when the user asks for a prototype, spike, side-by-side UI alternatives, or an executable state/logic model whose observation will select or reject a direction; do not use for vague ideation, an already-selected production change, bug diagnosis or repair, or proof of performance, security, accessibility, concurrency, or release readiness.
---

# Workflow Prototype

## Routing Card
- role: primary
- intent_signature: one bounded product or engineering question answered by a runnable disposable artifact
- use_when:
  - the user explicitly requests a prototype or spike and can name, or safely delegate, the decision it must inform.
  - observing UI variants or exercising a small state/logic model is cheaper and more discriminating than more discussion.
- do_not_use_when:
  - the task is open-ended ideation, requirements discovery, ordinary production implementation, bug work, validation-only work, or a behavior-preserving refactor.
  - the desired claim requires representative load, production data, security review, accessibility audit, concurrency evidence, or real integration behavior.
- expected_inputs: one question, decision owner, discriminating observation, target project/runtime, budget/stop, write boundary, retention boundary, and excluded claims
- expected_outputs: isolated runnable prototype, one run command, observation guide, bounded verdict or pending-decision state, proof ceiling, retention status, and production handoff
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
  tools: host runtime plus the narrowest build, preview, browser, terminal, or smoke command needed to observe the question
  sensitive_resources: deny credentials and production data; stub external writes unless that boundary is the explicit question and separately authorized
- entry_scene: PREPARE

## Prototype Contract

Treat the prototype as decision evidence, not an early production implementation. Before writing, lock:

- `question`: one sentence ending in a choice, hypothesis, or observable uncertainty.
- `decision_owner`: the person or accepted rule that can select the outcome.
- `observation`: what a human or direct run must reveal to distinguish outcomes.
- `decision_rule`: what selects, supports, contradicts, or leaves the question inconclusive.
- `budget_stop`: the smallest time/code/variant boundary after which to stop.
- `proof_ceiling`: qualities the prototype cannot establish.
- `retention`: where the runnable evidence remains until the decision owner observes it, plus any explicitly authorized cleanup trigger.

Infer a reversible field only when it does not change the deliverable; otherwise ask for the missing decision. If no observation can discriminate the options, return to behavior or requirements discovery instead of coding.

Keep one active question. When UI shape and logic shape are both open, prototype the one blocking the next decision and defer the other unless the user explicitly scopes two prototypes.

## Select The Artifact Shape

- For layout, hierarchy, density, control placement, navigation, or interaction comparison, read [UI Prototype](references/ui-prototype.md) and build a UI comparison in the real host surface when safe.
- For state transitions, invariants, command semantics, reducer/state-machine shape, or domain feedback, read [Logic Prototype](references/logic-prototype.md) and build a pure model with a thin runnable driver.
- For a question that depends on performance, security, accessibility, concurrency, persistence durability, or production integration, use the specialist actual-path workflow instead. A throwaway harness may illustrate behavior but cannot close that claim.

## Workflow

1. **Bind the question.** Record the contract fields, current evidence, non-goals, and the decision that becomes possible after observation.
2. **Inspect the host path.** Reuse the project's runtime, package manager, route/module conventions, components, fixtures, and one-command entrypoint. Avoid standalone scaffolding when the real surface can host the prototype safely.
3. **Isolate the evidence.** Mark the artifact `PROTOTYPE` and throwaway. Prefer an isolated route, story, preview, or nearby path inside the authorized workspace. Use a branch/worktree only when explicitly requested or repository policy makes it the accepted isolation mechanism. Never stash, reset, overwrite, or relocate unrelated work to obtain isolation, and never push without authorization.
4. **Build only the discriminator.** Implement the selected UI or logic shape. Stub mutations and external systems, keep state in memory by default, and omit polish, generalized abstractions, defensive completeness, migrations, persistence, analytics, and production error handling unless one is the explicit question.
5. **Make observation cheap.** Provide one exact command and working directory. Expose the relevant variants, actions, state, transitions, or failures without requiring source inspection. Keep the observation small enough to repeat while feedback is fresh.
6. **Observe and classify.** Run the narrow entrypoint when agent verification is allowed. Record `selected`, `supported`, `contradicted`, or `inconclusive`, the decisive observation, and counterevidence. Human taste or private interaction stays `user-verification-needed` until the decision owner responds; do not convert a pending human decision into `selected`.
7. **Close the boundary without destroying the evidence.** Keep the switcher, driver, fixtures, and alternatives runnable in the isolated prototype until the decision owner observes them. Keep those prototype-only pieces out of the production line. After an explicit selection, hand the accepted behavior to its normal implementation owner; delete or compact prototype evidence only when the user requests cleanup or the pre-agreed retention trigger fires.

## Guardrails

- Make variants structurally different; color, copy, spacing, or icon-only changes do not answer a layout question.
- Use representative real context or fixtures, but do not mutate real accounts, services, databases, files, or external systems by default.
- Add no new framework, package, persistence layer, backend endpoint, or generic abstraction merely to support the prototype.
- Do not use passing builds, typechecks, mocks, screenshots, or self-authored tests to claim the design question is answered. They prove only their covered boundary.
- Do not claim production correctness, maintainability, scalability, security, accessibility, reliability, or release readiness from prototype evidence.
- Do not silently merge prototype code into production. Lift only a small validated pure core when its ownership and production checks are explicit; rewrite the production surface under its normal workflow.
- Do not delete, collapse, or make the comparison unrunnable while its decision remains `user-verification-needed`.

## Validation And Output

Confirm the exact command starts the artifact, the observation matches the question, external side effects are absent or explicitly authorized, the budget remained bounded, the production/evidence boundary is visible, and pending evidence remains runnable at its declared retention location.

Return only applicable fields:

- `prototype_question`
- `artifact_shape` and changed paths
- `run_command`
- `observation_guide`
- `verdict` and decisive evidence
- `proof_ceiling`
- `production_handoff`
- `retention_or_cleanup`
