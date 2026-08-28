---
name: test-visual-regression
description: "Work in exactly one explicit mode for a rendered regression condition: `design` authors an implementation-ready visual-regression contract without capture or verdict, while `evidence` consumes an accepted contract to capture and compare named states/viewports. Never switch modes automatically or replace design-fidelity review, accessibility, interaction semantics, or business correctness."
---

# Test Visual Regression

## Routing Card

- role: testing_design_or_evidence_specialist
- intent_signature: visual regression design, screenshot regression evidence, rendered golden test, pixel diff, visual replay
- use_when:
  - the caller or assigned node explicitly selects `design` to author a visual-regression contract for named states/viewports
  - the caller or assigned node explicitly selects `evidence` to capture/compare an accepted visual-regression contract
- do_not_use_when:
  - neither `design` nor `evidence` is explicitly selected
  - visual direction, exact design-target fidelity, or product-family coherence is primary; use `design-visual-regression`
  - accessibility, interaction semantics, responsive completeness, or subjective acceptance is the only condition
  - `evidence` lacks a rendered target, accepted contract, or accepted baseline identity
- expected_inputs:
  - selected mode and condition ID
  - for `design`: target snapshot or accepted external rendered-state contract, baseline authority/version, named states/viewports, and environment constraints
  - for `evidence`: accepted visual-regression contract ref, rendered target/current snapshot, and matching baseline identity
- expected_outputs:
  - `design`: visual-regression contract and implementation handoff, with no capture/diff/verdict
  - `evidence`: condition-scoped screenshot/diff evidence and verdict, with no redesign
  - explicit baseline, environment, and proof-ceiling gaps
- context_targets:
  must_read:
    - selected mode, condition, baseline/contract authority, state/viewports, and `references/testing_strategy_contract.md`
  read_if_needed:
    - font/assets/theme/renderer identity, animation/randomness controls, nearby capture tooling, or test-design handoff
  do_not_load_by_default:
    - unrelated routes/screens, mutable design sources, full visual history, private sessions, or credentials
- risk_profile:
  reads: rendered target or accepted external rendered-state contract, accepted baselines, and named capture state
  writes: `design` none; `evidence` screenshots and scoped diff artifacts only when explicitly requested; test code/baseline updates belong to `workflow-test-implementation`
  tools: `design` bounded read-only contract inspection; `evidence` browser/simulator/native capture and image comparison when available
  sensitive_resources: authenticated/private surfaces require explicit authority
- entry_scene: PREPARE

## Boundary

This skill answers whether rendered pixels/framing for a named state and viewport differ from an
accepted testing baseline. `design-visual-regression` answers whether an implementation matches an
exact design target or product-family visual language. One result never substitutes for the other.

## Mode Admission

Lock exactly one mode from the explicit caller or assigned-node outcome before mode-specific work.
If neither mode is selected or the request mixes them, return an unresolved mode-selection gap.
Do not infer mode from tool availability, the presence of a rendered target, or the current stage.

- `design` produces input for a later separately invoked implementation/evidence owner. It never
  captures, compares, writes screenshots/diffs, or returns a condition verdict.
- `evidence` consumes an already accepted visual-regression contract. A missing or mismatched
  contract returns the exact design/authority gap; it never falls back to `design` or changes the
  baseline, threshold, mask, state, viewport, or environment contract.
- Completion in either mode never starts the other mode or another DAG node.

## Design Mode Workflow

1. Bind condition ID, target snapshot or accepted external rendered-state contract, baseline
   source/version/approval owner, states, viewports, themes, renderer, fonts/assets, and environment.
2. Reject unapproved current output as baseline authority. Specify who may approve/update the
   baseline and what evidence a future update requires.
3. Define the capture matrix and comparison-breaking non-semantic controls: seed,
   simulation/frame time, asset loading, font/rendering environment, and specifically authorized
   dynamic masks. If variability is material, design bounds/distributions instead of identical
   pixels.
4. Define the contract-authorized pixel, perceptual, region, or structural comparison rule,
   tolerance/mask authority, and pre-diff validity checks for nonblank content, dimensions, target
   state, framing, clipping/overflow, loading, and auth redirects.
5. Define required baseline/current/diff artifacts, diagnostics, falsifier, unavailable behavior,
   implementation handoff, and proof ceiling. Do not capture, compare, write evidence artifacts, or
   return a verdict in this mode.

## Evidence Mode Workflow

1. Pin the accepted visual-regression contract, condition, target/current snapshot, baseline
   identity, states/viewports/environment, controls, comparison rule, and artifact destinations.
2. Refuse a missing, stale, unauthorized, or identity-mismatched contract/baseline before capture.
   Return the exact design or authority gap without switching modes.
3. Capture or inspect only the contract-declared like-for-like images. Validate the prescribed
   nonblank, dimensions, target-state, framing, clipping/overflow, loading, and auth conditions.
4. Apply only the frozen comparison rule, tolerance, regions, and masks. Do not invent a universal
   threshold, mask a changed semantic region, update the baseline, or redesign the contract to
   obtain Green.
5. Preserve baseline/current/diff artifacts, exact state/viewport/environment, comparison result,
   diagnostics, and unavailable reasons. Limit verdict to visible pixels/framing for the named
   condition and contract.

## Output Contract

Return `mode` plus only the matching shape:

- `design`: condition, target/external-contract identity, baseline/update authority,
  states/viewports/environment, capture matrix, controls/masks, comparison rule, pre-diff checks,
  diagnostics/falsifier, implementation handoff, proof ceiling, and unresolved design gaps.
- `evidence`: condition, accepted contract ref, target/baseline identity, state/viewports/environment,
  capture paths, comparison rule, mismatches, scoped verdict, diagnostic artifacts, proof ceiling,
  and unresolved evidence gaps.
