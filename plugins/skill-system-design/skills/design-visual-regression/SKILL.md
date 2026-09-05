---
name: design-visual-regression
description: "Capture, verify, and compare rendered UI screenshots for design evidence — exact-target fidelity, product-family coherence against pinned component/surface baselines, desktop/mobile viewports, nonblank rendering, framing, overflow/clipping, and unavailable-evidence handling after UI work."
---

# design-visual-regression

## Routing Card
- role: design_evidence_gate
- family: design
- intent_signature:
  - visual regression
  - screenshot evidence
  - nonblank screenshot check
  - desktop and mobile viewport capture
  - visual diff report
  - product-family visual coherence
- use_when:
  - a design-to-production task needs screenshot, viewport, or visual diff evidence.
  - missing visual evidence must remain user-verification-needed instead of being treated as complete.
  - the user asks whether a rendered UI is blank, clipped, overflowing, poorly framed, or visually different from a reference.
- do_not_use_when:
  - the task only needs token normalization, component mapping, or accessibility checks.
  - there is no rendered target and no screenshot artifact to inspect.
  - the user asks for direct UI implementation; use `design-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - rendered implementation target, screenshot path, or preview URL
  - source visual reference when available
  - pinned product-family component-state or surface-archetype baselines when declared
  - desktop and mobile viewport requirements
- expected_outputs:
  - desktop/mobile screenshot evidence or unavailable reason
  - nonblank and framing result
  - visual difference report
  - separate target-fidelity and family-coherence verdicts when both lanes apply
  - unresolved visual gaps
- context_targets:
  must_read:
    - rendered target URL, artifact path, or screenshot path
    - source visual reference or acceptance criteria
  read_if_needed:
    - `references/design_stage_contract.md` when this check is a Design DAG node or its ownership boundary is unclear
    - `references/design_evidence_contract.md` for evidence labels, proof ceilings, and unavailable rendered evidence
    - `references/product_family_design_contract.md` when family coherence or a shared visual baseline is in scope
    - `references/viewport-policy.md` only when viewport dimensions, capture rules, or framing policy must be selected
    - `references/visual-diff-report-schema.md` only for an explicit regression artifact or multi-viewport comparison
    - `references/visual_decision_contract.md` when extras not in the source look like unchosen factory chrome
    - design token export
    - component contract mapping
    - accessibility evidence report
  do_not_load_by_default:
    - the visual-diff report schema for a single-view check or unavailable rendered result
    - unrelated routes
    - full repo history
    - live credentials
- risk_profile:
  reads:
    - rendered UI, screenshots, visual references
  writes:
    - screenshots, visual diff artifacts, and registry entries only when explicitly requested
  tools:
    - local browser, screenshot, and image comparison checks when available
  sensitive_resources:
    - credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

Use this skill for visual evidence, not for implementation ownership. It can support `design-frontend` after a UI is rendered.

## Stage Boundary

Apply `references/design_stage_contract.md`. This skill owns only the visual condition assigned by
the user or accepted Plan. It never edits the UI, starts another gate, triggers repair/retry, or
selects a successor. Use `references/design_evidence_contract.md` for evidence labels and proof
ceilings.

## Workflow
1. Determine the rendered target:
   - Use a local URL, Storybook story, static HTML, native preview, screenshot file, or simulator output.
   - If no target exists, report the missing target and stop visual proof.
2. Determine comparison lanes and viewport set:
   - Use `target_fidelity` for the exact selected frame/spec/screenshot.
   - Also use `family_coherence` when an applicable product-family profile declares pinned
     component-state or surface-archetype baselines. Apply
     `references/product_family_design_contract.md` to that lane.
   - Keep the verdicts separate: a target can match an off-family mockup, or fit the family while missing the target.
   - Prefer user-specified viewport, design frame size, or project breakpoints.
   - If no viewport is specified and the surface is responsive, check at least one mobile and one desktop viewport.
3. Capture or inspect screenshots:
   - Use available browser/simulator tooling.
   - If capture is unavailable, inspect provided screenshots and mark capture as unavailable.
4. Run nonblank and framing checks:
   - Confirm screenshot dimensions, non-empty content, and that primary UI content is inside frame.
   - Record blank, clipped, overflow, text-overlap, and off-canvas risks.
5. Compare against the exact target reference:
   - Compare hierarchy, layout regions, spacing, typography, color, imagery, icons, states, responsive order, and overflow.
   - Separate objective mismatches from subjective polish.
   - Extras that are not in the source — gradient headlines, restating kickers, decorative emoji, invented stat rows, unchosen Inter/indigo kits — are fidelity misses, not polish. Keep a sourced brand.
6. Compare against family baselines when declared:
   - Pin each baseline source, state, viewport, theme mode, and version/digest.
   - Compare shared axes such as typography scale, token color use, spacing rhythm, radius/elevation, control height, icon family, density, shell/chrome, and recurring component states.
   - Compare like with like. Do not apply full-screen pixel thresholds between unrelated screens or use one sibling screenshot as the entire family standard.
7. Return unresolved gaps with their current evidence label. Name token, component, accessibility,
   or implementation ownership only as a handoff hint; do not invoke another skill or convert a
   visual result into a repair decision.

## Output
Return single-view findings, evidence paths, and scoped status directly. Structured regression or multi-viewport artifacts follow the conditionally loaded schema; keep lane verdicts separate and missing evidence explicit.

## Validation
- Provide screenshot paths or explicit unavailable reasons.
- Use exact viewport dimensions when captured.
- Do not claim visual readiness from build success alone.
- Do not claim pixel-perfect equivalence without side-by-side evidence or image diff evidence.
- Do not collapse target fidelity and family coherence into one pass/fail verdict.
- A family-coherence verdict requires an applicable pinned baseline and like-for-like comparison axes; an unrelated screen or mutable path is insufficient.
- Do not invent a universal pixel threshold for coherence. Use project-declared thresholds when present and reasoned shared-axis findings otherwise.
- Missing source, screenshot, font, asset, viewport, or baseline evidence prevents a pass in the affected lane.
- If only the user can supply or judge it, use `user-verification-needed`; otherwise use `unverified`.
- Do not turn a single clipping or blank-render check into a full fidelity review.

## Plan/Handoff Condition Result

When the accepted Plan names this skill as an evidence owner:

- Verify only the assigned visual condition IDs.
- Return `pass`, `fail`, `unverified`, or `user-verification-needed` per condition with screenshot
  paths, viewport/state, decisive comparison evidence, and unavailable reason.
- An unchanged failure is only evidence for that condition. The Coordinator applies an existing
  Plan edge; this skill never creates a retry, repair node, or back-edge.
- Do not infer accessibility, source correctness, build readiness, Human Test, or overall Design
  completion from screenshots.

## Do Not Invent / Unverified Policy
- Do not invent source reference details that are not visible.
- Keep subjective visual polish separate from confirmed visual mismatch.

## Completion Boundary
Close only the assigned visual condition. Do not require token, component, accessibility, or repo
gates unless the user or accepted Plan separately names those conditions.
