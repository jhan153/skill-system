---
name: design-a11y-audit
description: "Accessibility evidence for implemented UI — keyboard reachability, focus visibility, selected-vs-focused distinction, roles, accessible names, labels, landmarks, status messages, color contrast, target size, responsive readability, and WCAG/APG-backed gaps."
---

# design-a11y-audit

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - accessibility evidence for keyboard, focus, semantics, contrast, target size, or responsive readability
- use_when:
  - implemented UI needs scoped accessibility evidence beyond build/visual checks, or the user asks for one of these conditions.
- do_not_use_when:
  - the task is only token extraction, component mapping, or screenshot comparison.
  - the user asks for general accessibility advice without a concrete implementation or artifact target.
  - the user asks for direct UI implementation; use `design-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - implemented UI/artifact, acceptance criteria, and relevant viewport/interaction requirements
- expected_outputs:
  - condition-scoped results, evidence sources, unresolved gaps, and required manual checks
- context_targets:
  must_read:
    - target UI surface/artifact and scoped acceptance criteria
  read_if_needed:
    - `references/wcag-checklist.md`
    - `references/keyboard-focus-procedure.md`
    - component contract mapping
    - visual evidence manifest
    - accessibility test output
  do_not_load_by_default:
    - unrelated routes, repo history, or live credentials
- risk_profile:
  reads: rendered UI, source, and design evidence
  writes: evidence artifacts only when explicitly requested
  tools: browser interaction, accessibility tree/DOM inspection, measurements, screenshots, and static scans
  sensitive_resources: credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

This is an evidence gate. `design-frontend` owns requested UI fixes; this skill scopes findings and verifies the affected path.

## Workflow
1. Record the route/component/artifact, viewport, interaction states, and only the success conditions in scope. List relevant controls, landmarks, forms, status messages, and dynamic regions.
2. Choose evidence per condition:
   - Source and `scripts/a11y_static_scan.py` provide structural hints only. Runtime DOM/accessibility-tree readback can verify rendered roles, names, labels, associations, landmarks, and live regions.
   - Screenshots can show visible focus, clipping, or measurable pixels, but cannot prove keyboard reachability, tab order, accessible names, or dynamic behavior.
   - Browser interaction verifies reachability, order, focus movement/visibility, escape/close, activation, and selected-versus-focused behavior. Use `references/keyboard-focus-procedure.md` and APG for composite widgets.
   - Contrast, target size, reflow, and overflow require measured rendered values at the relevant viewport/zoom. Use the scoped criteria in `references/wcag-checklist.md`.
3. Report each condition from its direct evidence. A clean scan or passing lower-scope check cannot overrule conflicting rendered or interaction evidence and is never a full WCAG pass.
4. For requested fixes, identify the actual component/owner, then repeat the same rendered interaction or measurement after the production change. Mock/source/test success alone leaves the condition open.
5. Hand missing visual proof to `design-visual-regression`, state coverage to `design-component-mapper`, token values to `design-tokens`, and implementation to `design-frontend`.

## Output
Lead with confirmed high-impact gaps and the next missing evidence. Use this shape only for an audit artifact or several tracked conditions; omit empty fields.

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

## Loop Contract Consumption
When invoked as a loop verifier:
- Read the accepted `loop_term`/verifier map and verify only assigned accessibility condition IDs.
- Return `pass`, `fail`, `unverified`, or `blocked` per ID with direct evidence. Missing rendered UI is `blocked` when the assigned interaction cannot run; absent measurement or static-only evidence is `unverified` for an unmet evidence need.
- Do not weaken a finding for visual fidelity or let one accessibility condition imply another.

## Validation And Limits
- Every result cites its DOM/tree, source, screenshot, measurement, or interaction evidence; unavailable evidence remains `unverified`, `user-verification-needed`, or `blocked` as appropriate.
- Never invent roles, labels, ratios, dimensions, or keyboard behavior. Separate WCAG/APG criteria from heuristic polish.
- Keep a single focus, label, contrast, or overflow request scoped. No rendered UI means source/static hints plus explicit manual checks, not compliance.
- This gate cannot prove visual fidelity or complete design implementation; visual, token, component, repo, and other user conditions remain separate.
