---
name: test-visual-regression
description: Design or execute a rendered regression condition against an accepted, versioned baseline at named states and viewports. Own pixel, framing, clipping, overflow, and approved mask/tolerance evidence only; do not replace design-fidelity review, accessibility, interaction semantics, or business correctness.
---

# Test Visual Regression

## Routing Card

- role: testing_evidence_specialist
- intent_signature: screenshot regression test, rendered golden test, pixel diff, visual replay
- use_when:
  - an accepted test condition and rendered baseline require screenshot capture or comparison
  - Test Design needs a visual-regression contract for named states/viewports
- do_not_use_when:
  - visual direction, exact design-target fidelity, or product-family coherence is primary; use `design-visual-regression`
  - accessibility, interaction semantics, responsive completeness, or subjective acceptance is the only condition
  - no rendered target and no accepted baseline/reference exist
- expected_inputs:
  - rendered target, accepted baseline authority/version, named state/viewports, dynamic-region policy, tolerance/mask rule, and condition ID
- expected_outputs:
  - visual regression contract or condition-scoped screenshot/diff evidence
  - explicit baseline, environment, and proof-ceiling gaps
- context_targets:
  must_read:
    - condition, rendered target, baseline authority, state/viewports, and `references/testing_strategy_contract.md`
  read_if_needed:
    - font/assets/theme/renderer identity, animation/randomness controls, nearby capture tooling, or test-design handoff
  do_not_load_by_default:
    - unrelated routes/screens, mutable design sources, full visual history, private sessions, or credentials
- risk_profile:
  reads: rendered target, accepted baselines, and named capture state
  writes: screenshots and scoped diff artifacts only when explicitly requested; test code/baseline updates belong to `workflow-test-implementation`
  tools: browser/simulator/native capture and image comparison when available
  sensitive_resources: authenticated/private surfaces require explicit authority
- entry_scene: PREPARE

## Boundary

This skill answers whether rendered pixels/framing for a named state and viewport differ from an
accepted testing baseline. `design-visual-regression` answers whether an implementation matches an
exact design target or product-family visual language. One result never substitutes for the other.

## Workflow

1. Bind condition ID, target snapshot, baseline source/version/approval owner, state, viewport,
   theme, renderer, fonts/assets, and dynamic-region policy.
2. Reject unapproved current output as a baseline. A baseline update is a new authorized decision,
   not failure handling.
3. Control only comparison-breaking non-semantic variability: seed, simulation/frame time, asset
   loading, font/rendering environment, or specifically approved masks. If variability is material,
   design bounds/distributions instead of identical pixels.
4. Capture or inspect like-for-like images. Validate nonblank content, dimensions, target state,
   primary framing, clipping/overflow, and loading/auth redirects before diffing.
5. Apply only project/contract-declared pixel, perceptual, region, or structural comparison rules.
   Do not invent a universal threshold or mask a changed semantic region to obtain Green.
6. Preserve baseline/current/diff artifacts, exact viewport/state/environment, and unavailable
   reasons. Limit verdict to visible pixels/framing for that condition.

## Output Contract

Return condition, target/baseline identity, approval authority, state/viewports/environment,
dynamic controls/masks, capture paths, comparison rule, mismatches, scoped verdict, diagnostic
artifacts, proof ceiling, and unresolved baseline/target gaps.
