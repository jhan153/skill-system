---
name: design-a11y-audit
description: "Accessibility evidence for implemented UI — keyboard reachability, focus visibility, selected-vs-focused distinction, roles, accessible names, labels, landmarks, status messages, color contrast, target size, responsive readability, and WCAG/APG-backed gaps."
---

# design-a11y-audit

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - accessibility evidence
  - keyboard navigation check
  - focus visibility check
  - semantic roles and labels
  - contrast target size responsive readability
- use_when:
  - a design-to-production task needs accessibility proof beyond build or visual checks.
  - visual evidence exists or is being gathered and accessibility still needs a separate gate.
  - the user asks for keyboard, focus, semantic, contrast, target-size, or text-overflow evidence.
- do_not_use_when:
  - the task is only token extraction, component mapping, or screenshot comparison.
  - the user asks for general accessibility advice without a concrete implementation or artifact target.
  - the user asks for direct UI implementation; use `design-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - implemented UI target, source files, rendered artifact, or screenshot
  - design source or acceptance criteria when available
  - relevant viewport and interaction requirements
- expected_outputs:
  - keyboard navigation result
  - focus visibility result
  - semantic role and label result
  - contrast and target-size result
  - unresolved accessibility gaps
- context_targets:
  must_read:
    - target UI surface or artifact path
    - design acceptance criteria
  read_if_needed:
    - `references/wcag-checklist.md`
    - `references/keyboard-focus-procedure.md`
    - component contract mapping
    - visual evidence manifest
    - accessibility test output
  do_not_load_by_default:
    - unrelated app routes
    - full repo history
    - live credentials
- risk_profile:
  reads:
    - rendered UI, source files, design evidence
  writes:
    - accessibility evidence artifacts and registry entries only when explicitly requested
  tools:
    - local browser, screenshot, static scan, or accessibility checks when available
  sensitive_resources:
    - credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

Use this skill for accessibility evidence. It can support implementation, but it should not redesign the UI unless the user asks for fixes.

## Workflow
1. Identify target and interaction scope:
   - Record route, component, story, screenshot, source files, viewport, and interaction states.
   - List interactive elements, landmarks, status messages, and dynamic regions.
2. Check keyboard and focus:
   - Confirm reachability, logical tab order, visible focus, escape/close behavior, and selected-vs-focused distinction.
   - Use WAI-ARIA APG patterns when a composite widget is present.
3. Check semantics:
   - Inspect semantic elements, roles, accessible names, labels, headings, landmarks, form associations, icon-only buttons, and live/status messages.
4. Check measurable criteria:
   - Check contrast when colors are available.
   - Check target size when dimensions are measurable.
   - Check responsive readability, text overflow, and zoom/reflow risks when rendered evidence exists.
5. Separate evidence types:
   - Static scan hints are not a WCAG pass.
   - Manual/browser checks are stronger when interaction behavior matters.
6. Hand off unresolved gaps:
   - Missing visual proof goes to `design-visual-regression`.
   - Missing state coverage goes to `design-component-mapper`.
   - Missing token values go to `design-tokens`.

## Output schema
Return or write a structured report with these fields:

```yaml
target:
keyboard_result:
focus_result:
semantics_result:
contrast_result:
target_size_result:
responsive_readability_result:
manual_checks_needed: []
static_scan_hints: []
unresolved_gaps: []
unverified: []
```

## Validation
- Every pass/fail item must cite DOM/source/screenshot/tool evidence or be marked `Unverified`.
- WCAG/APG-backed checks must be separated from heuristic polish.
- Static scan output cannot claim full WCAG compliance.
- If contrast or target size cannot be measured, report the unavailable evidence.
- If a browser interaction check is unavailable, keep keyboard/focus behavior `user-verification-needed` or `unverified`.

## Loop Contract Consumption
When invoked as a loop verifier:
- Read the accepted `loop_term` and verifier map.
- Verify only the accessibility success conditions assigned to `design-a11y-audit`.
- Return status per success condition id: `pass`, `fail`, `unverified`, or `blocked`.
- Include the evidence source for keyboard, focus, semantics, labels, contrast, target size, and responsive readability.
- Treat missing rendered UI as `blocked` for interaction evidence and `unverified` for static-only evidence, depending on the requested condition.
- Do not weaken accessibility findings to satisfy visual fidelity.

## Recovery
- If rendered UI is unavailable, run source/static inspection only and mark manual checks needed.
- If color tokens are unavailable, report contrast as unverified and hand off token gaps if relevant.
- If custom controls lack clear semantics, identify the source files and required accessible-name/role/focus evidence.
- If mobile text overflow is the only request, keep the audit scoped to responsive readability.

## Known Limits
- This skill cannot prove visual fidelity.
- Static regex scans are incomplete and can miss framework-generated accessibility behavior.
- Screenshots alone cannot prove keyboard reachability or semantic names.
- WCAG/APG evidence is standards-backed; visual comfort and polish are not compliance claims.

## Do not invent / Unverified policy
- Do not invent roles, labels, contrast ratios, target dimensions, or keyboard behavior.
- Mark unmeasured criteria as `Unverified`.
- Do not weaken accessibility findings to match a screenshot exactly.

## Optional resources
- Read `references/wcag-checklist.md` for the scoped WCAG 2.2 evidence checklist.
- Read `references/keyboard-focus-procedure.md` for manual keyboard/focus checks.
- Use `scripts/a11y_static_scan.py` only for static hints.

## Completion Boundary
Do not mark design implementation complete from this gate alone. Accessibility evidence is one required design-to-production gate, not a substitute for visual, token, component, or repo validation.
