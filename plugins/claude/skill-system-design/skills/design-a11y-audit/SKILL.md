---
name: design-a11y-audit
description: "Accessibility evidence for implemented UI — keyboard reachability, focus visibility, selected-vs-focused distinction, roles, accessible names, labels, landmarks, status messages, color contrast, target size, responsive readability, and WCAG/APG-backed gaps."
disable-model-invocation: true
---

# design-a11y-audit

## Routing Card
- role: design_evidence_gate
- family: design
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
    - `references/design_stage_contract.md` when this audit is a Design DAG node or its ownership boundary is unclear
    - `references/design_evidence_contract.md` for evidence labels, proof ceilings, and unavailable runtime evidence
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

## Stage Boundary

Apply `references/design_stage_contract.md`. This skill owns only the accessibility condition
assigned by the user or accepted Plan. It never edits production UI, starts another gate, triggers
repair/retry, or selects a successor. Use `references/design_evidence_contract.md` for evidence
labels and proof ceilings.

## Workflow
1. Record the route/component/artifact, viewport, interaction states, and only the success conditions in scope. List relevant controls, landmarks, forms, status messages, and dynamic regions.
2. Match each condition to direct evidence: source/static checks are hints; DOM/tree verifies
   rendered roles, names, and associations; screenshots verify only visible pixels; browser
   interaction verifies keyboard/focus; rendered measurements verify quantitative criteria. Load
   only the matching procedure or checklist.
3. Report each condition from its direct evidence. A clean scan or passing lower-scope check cannot overrule conflicting rendered or interaction evidence and is never a full WCAG pass.
4. When a separate implementation owner changes the affected production path, repeat the same
   rendered interaction or measurement only if the user or accepted Plan still assigns this
   condition. This skill never applies the fix. Mock/source/test success alone leaves the
   condition open.
5. Return the assigned condition results and missing evidence. Name the visual, component, token,
   or implementation owner only as a handoff hint; do not invoke another skill or turn a finding
   into a repair decision.

## Output
Lead with confirmed high-impact gaps and the next missing evidence. For an audit artifact or several tracked conditions, use `references/audit-report-schema.md`.

## Plan/Handoff Condition Result

When the accepted Plan names this skill as an evidence owner:

- Verify only the assigned accessibility condition IDs.
- Return `pass`, `fail`, `unverified`, or `user-verification-needed` per ID with direct evidence.
  Missing rendered UI, absent measurement, or static-only evidence leaves only the affected
  condition unresolved.
- The Coordinator applies an existing Plan edge. This skill never creates a retry, repair node,
  back-edge, or global completion verdict.
- Do not weaken a finding for visual fidelity or let one accessibility condition imply another.

## Validation And Limits
- Cite direct evidence per result; unavailable evidence remains `unverified` or
  `user-verification-needed`. Never invent roles, labels, ratios, dimensions, or behavior, or
  conflate WCAG/APG criteria with polish.
- Keep conditions scoped. Without rendered UI, report source/static hints and manual checks, not compliance.
- This gate proves neither visual fidelity nor complete implementation; keep other user conditions separate.

## Completion Boundary

Close only the assigned accessibility condition. Do not require visual, token, component, or repo
gates unless the user or accepted Plan separately names those conditions.
