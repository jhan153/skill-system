---
name: design-a11y-audit
description: "Accessibility evidence for implemented UI — keyboard reachability, focus visibility, selected-vs-focused distinction, roles, accessible names, labels, landmarks, status messages, color contrast, target size, responsive readability, and WCAG/APG-backed gaps."
disable-model-invocation: true
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
    - `references/wcag-checklist.md` for contrast, target size, reflow, or scoped WCAG checks
    - `references/keyboard-focus-procedure.md` for rendered keyboard/focus and APG widget interaction
    - `references/audit-report-schema.md` only for an audit artifact or several tracked conditions
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
2. Match each condition to direct evidence: source and `scripts/a11y_static_scan.py` are hints; DOM/tree verifies rendered roles, names, and associations; screenshots verify only visible pixels; browser interaction verifies keyboard/focus; rendered measurements verify quantitative criteria. Load only the matching procedure or checklist.
3. Report each condition from its direct evidence. A clean scan or passing lower-scope check cannot overrule conflicting rendered or interaction evidence and is never a full WCAG pass.
4. For requested fixes, identify the actual component/owner, then repeat the same rendered interaction or measurement after the production change. Mock/source/test success alone leaves the condition open.
5. Hand missing visual proof to `design-visual-regression`, state coverage to `design-component-mapper`, token values to `design-tokens`, and implementation to `design-frontend`.

## Output
Lead with confirmed high-impact gaps and the next missing evidence. For an audit artifact or several tracked conditions, use `references/audit-report-schema.md`.

## Loop Contract Consumption
When invoked as a loop verifier:
- Read the accepted `loop_term`/verifier map and verify only assigned accessibility condition IDs.
- Return `pass`, `fail`, `unverified`, or `blocked` per ID with direct evidence. Missing rendered UI is `blocked` when the assigned interaction cannot run; absent measurement or static-only evidence is `unverified` for an unmet evidence need.
- Do not weaken a finding for visual fidelity or let one accessibility condition imply another.

## Validation And Limits
- Cite direct evidence per result; unavailable evidence remains `unverified`, `user-verification-needed`, or `blocked`. Never invent roles, labels, ratios, dimensions, or behavior, or conflate WCAG/APG criteria with polish.
- Keep conditions scoped. Without rendered UI, report source/static hints and manual checks, not compliance.
- This gate proves neither visual fidelity nor complete implementation; keep other user conditions separate.
