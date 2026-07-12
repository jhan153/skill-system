---
name: design-visual-regression
description: "Capture, verify, and compare rendered UI screenshots for design evidence — exact-target fidelity, product-family coherence against pinned component/surface baselines, desktop/mobile viewports, nonblank rendering, framing, overflow/clipping, and unavailable-evidence handling after UI work."
---

# design-visual-regression

## Routing Card
- role: design_evidence_gate
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
    - `references/viewport-policy.md`
    - `references/visual-diff-report-schema.md`
    - design token export
    - component contract mapping
    - accessibility evidence report
  do_not_load_by_default:
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

## Workflow
1. Determine the rendered target:
   - Use a local URL, Storybook story, static HTML, native preview, screenshot file, or simulator output.
   - If no target exists, report the missing target and stop visual proof.
2. Determine comparison lanes and viewport set:
   - Use `target_fidelity` for the exact selected frame/spec/screenshot.
   - Also use `family_coherence` when an applicable product-family profile declares pinned component-state or surface-archetype baselines.
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
6. Compare against family baselines when declared:
   - Pin each baseline source, state, viewport, theme mode, and version/digest.
   - Compare shared axes such as typography scale, token color use, spacing rhythm, radius/elevation, control height, icon family, density, shell/chrome, and recurring component states.
   - Compare like with like. Do not apply full-screen pixel thresholds between unrelated screens or use one sibling screenshot as the entire family standard.
7. Hand off unresolved gaps:
   - Token mismatches go to `design-tokens`.
   - Missing variants/states go to `design-component-mapper`.
   - Focus/keyboard/contrast/target-size issues go to `design-a11y-audit`.

## Output
For one screenshot or viewport question, lead with confirmed visual differences and the evidence path. Use the structured shape only for an explicit regression artifact or multi-viewport comparison; omit empty fields.

```yaml
target:
source_reference:
family_baselines: []
comparison_lanes: []
viewports: []
screenshots: []
capture_method:
nonblank_result:
framing_result:
visual_differences: []
family_coherence_findings: []
target_fidelity_verdict:
family_coherence_verdict:
overflow_or_clipping: []
responsive_findings: []
unavailable_evidence: []
unresolved_visual_gaps: []
unverified: []
```

## Validation
- Provide screenshot paths or explicit unavailable reasons.
- Use exact viewport dimensions when captured.
- Do not claim visual readiness from build success alone.
- Do not claim pixel-perfect equivalence without side-by-side evidence or image diff evidence.
- Do not collapse target fidelity and family coherence into one pass/fail verdict.
- A family-coherence verdict requires an applicable pinned baseline and like-for-like comparison axes; an unrelated screen or mutable path is insufficient.
- Do not invent a universal pixel threshold for coherence. Use project-declared thresholds when present and reasoned shared-axis findings otherwise.
- If a script is used, include the command and mark it as a nonblank/framing aid only.
- Do not turn a single clipping or blank-render check into a full fidelity review.

## Loop Contract Consumption
When invoked as a loop verifier:
- Read the accepted `loop_term` and verifier map.
- Verify only the visual success conditions assigned to `design-visual-regression`.
- Return status per success condition id: `pass`, `fail`, `unverified`, or `blocked`.
- Include screenshot paths, viewport dimensions, nonblank/framing result, visual gaps, and unavailable-evidence reasons.
- Treat unchanged screenshot failures as no-progress signals for `workflow-loop-runner`.
- Do not verify accessibility, source-code correctness, or build readiness from screenshots alone.

## Recovery
- If browser tooling is unavailable, use provided screenshots and mark capture unavailable.
- If source reference is unavailable, compare against user acceptance criteria and mark fidelity as `user-verification-needed`.
- If family baselines are absent, stale, or not applicable, omit that lane and mark any requested family-coherence claim `unverified`; do not synthesize a family style from one convenient screen.
- If an applicable family baseline exists but only the user can access or judge it, keep the family lane `user-verification-needed` rather than collapsing it into target fidelity or claiming it passed.
- If a screenshot is blank, first verify target URL, app server, route, loading state, viewport, and console/build errors.
- If mobile and desktop disagree, report separate viewport findings instead of averaging them.

## Known Limits
- Nonblank checks do not prove fidelity.
- Pixel diff thresholds are project-specific and should not be invented as universal pass/fail.
- Family coherence across different surface archetypes is a shared-axis judgment, not necessarily a whole-image pixel diff.
- Screenshots cannot prove keyboard accessibility or screen-reader semantics.
- Authenticated pages may require user-provided screenshots if session access is unavailable.

## Do not invent / Unverified policy
- Do not invent source reference details that are not visible.
- Mark missing source references, screenshots, fonts, assets, or viewports as `Unverified`.
- Mark missing or unpinned family baselines as `Unverified` and preserve the independent target-fidelity result.
- Keep subjective visual polish separate from confirmed visual mismatch.

## Optional resources
- Read `references/viewport-policy.md` before choosing viewports.
- Read `references/visual-diff-report-schema.md` before producing a visual diff report.
- Use `scripts/check_screenshot_nonblank.py` only as a read-only screenshot sanity helper.

## Completion Boundary
Do not mark design implementation complete from this gate alone. Visual evidence must be combined with token, component contract, accessibility, and repo validation gates.
