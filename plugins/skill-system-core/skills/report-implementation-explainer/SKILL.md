---
name: report-implementation-explainer
description: Produce an explicitly requested source/runtime explanation of an existing implementation or a verified changed-lines comparison. Use explain for causal understanding and compare for authoritative diff/before-after presentation. Deliver content-first Markdown by default and optional matching trace/compare/spatial HTML on explicit html/both or spatial intent. Do not use for quality verdicts, pre-implementation choice, local one-line explanation, implementation, or automatic post-task reporting.
---

# Report Implementation Explainer

## Routing Card
- role: report_primary
- family: report
- intent_signature: explicit implementation explanation report or verified changed-lines/before-after report
- use_when:
  - the user requests a durable causal implementation explanation or readable verified comparison
- do_not_use_when:
  - a direct local answer is sufficient, no concrete target exists, or the artifact would be automatic after implementation
  - quality/readiness judgment, approach selection, or production changes are primary
- expected_inputs: selected mode, concrete snapshot, decision purpose, audience, production path or authoritative diff pair, and delivery mode
- expected_outputs: content-first Markdown explanation/comparison; optional matching trace, compare, or spatial HTML
- context_targets:
  must_read:
    - target snapshot, requested mode, audience/decision purpose, and canonical caller-to-output path or diff pair
    - `references/report_delivery_contract.md`
  read_if_needed:
    - focused tests, runtime readback, accepted intent, rationale history, and one material counterexample
    - `references/compare-mode.md` for compare mode
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when inspectable spatial evidence is material
  do_not_load_by_default:
    - full repository/history, unrelated plans, generated mirrors, broad logs, or another worker transcript
- risk_profile:
  reads: bounded source, config, tests, traces, accepted decisions, or authoritative diff
  writes: one Markdown report and only the explicitly selected optional HTML projection; never production code or instrumentation
  tools: focused read-only inspection and optional local rendering
  sensitive_resources: credentials denied; redact sensitive runtime data
- entry_scene: PREPARE

## Delivery And Ownership

Apply `references/report_delivery_contract.md`. Markdown is the explanatory source. HTML only
projects the same path, states, evidence, and comparison. It cannot add a behavior claim or imply
reader understanding. A missing renderer leaves the Markdown explanation complete.

This skill explains existing evidence. It never changes production, runs automatically after an
implementation, edits Plan/Handoff, selects another node, or treats its artifact as correctness
evidence.

## Modes

- `explain`: causal source/runtime path, state/identity transitions, failure boundaries, and one
  representative scenario.
- `compare`: read `references/compare-mode.md`; preserve verified changed lines or authoritative
  before/after facts without requiring a causal walkthrough or verdict.

## Evidence Contract

Pin a commit, diff, branch, release, or clearly labeled current-worktree snapshot. Treat the report
as a derived index:

1. accepted intent states desired behavior;
2. production source/config/schema establishes the implemented path;
3. runtime readback establishes only its observed state;
4. tests establish only their named contract;
5. rationale/history explains why but does not override current evidence.

Label claims `intent_stated`, `source_established`, `runtime_observed`, `inferred`, `hypothetical`,
or `unverified`. When relevant, keep `core_capability`, `integration`, `operability`, and `release`
status separate. Never emit `understood: true` or infer comprehension from opening/scrolling.

## Explain Workflow

1. Name the target snapshot and the decision the reader should be able to make.
2. Trace the smallest production caller-to-output path, including policy ownership, state/identity
   transitions, and material failure boundaries.
3. Use one representative scenario. Add a counterexample only when it changes the decision.
4. Require runtime readback for mutation, source-selection, adapter, transform, or failure-atomicity
   claims; otherwise label the limit.
5. Produce Markdown with only useful sections: outcome, intuition, causal path, representative
   state change, invariants/failures, source map, evidence, and productization gaps.
6. If HTML is selected, render the same content as `trace` or `compare`. Use `spatial` only when
   geometry is the material evidence and an authoritative asset/sample exists.

## Output Contract

Return the Markdown link first, then optional HTML. Keep excerpts small and navigational. End with
one recommendation or `none`; naming another owner never invokes it or changes the current Plan.

Artifact creation proves only that the explanation was produced. `scenario_exercised`,
`behavior_compared`, `decision_confirmed`, or `assumption_delegated` require actual observation.
