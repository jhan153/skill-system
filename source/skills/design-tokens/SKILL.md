---
name: design-tokens
description: "Normalize and audit design token sources for design-to-production — token JSON, CSS variables, Tailwind/theme config, Figma-exported tables, palette/typography/spacing/radius/shadow/motion/breakpoint tokens, token gaps/drift, platform mapping, and no-fabrication token evidence."
---

# design-tokens

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - design-token source normalization, platform mapping, or gap/conflict audit
- use_when:
  - design-to-production work needs token evidence before implementation/review, or the user asks to compare tokens with CSS variables, Tailwind/theme config, or component styles.
- do_not_use_when:
  - the task only needs component state mapping, screenshot comparison, or accessibility checks.
  - the user asks for direct UI implementation from a concrete visual artifact; use `design-frontend` as primary and this skill only as a supporting gate.
- expected_inputs:
  - token/style source, target platform or repo styling conventions, and requested categories/output
- expected_outputs:
  - source-grounded token inventory/mapping plus inferences, gaps, conflicts, and do-not-generate notes
- context_targets:
  must_read:
    - token source or design reference
    - target styling conventions
  read_if_needed:
    - `references/token-normalization.md` for source precedence, category normalization, platform mapping, or an inventory/export artifact
    - `references/token-gap-policy.md` when names, values, aliases, modes, or source priority are incomplete
    - component contract mapping
    - visual evidence manifest
    - repo theme or design-system files
  do_not_load_by_default:
    - unrelated design files
    - full repo history
    - live credentials
- risk_profile:
  reads: design references, token files, and style-system files
  writes: token artifacts and registry entries only when explicitly requested
  tools: local parsing and focused validation
  sensitive_resources: credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

This is a token-evidence gate. It supports implementation but does not own UI code changes unless token artifact edits are explicitly requested.

## Workflow
1. Pin source pointers and authority. Use a declared canonical source; otherwise load `references/token-normalization.md` and apply its precedence. Retain every conflicting candidate and pointer. Screenshot/rendered values remain inferred; a canonical winner does not erase a displaced live/legacy mismatch.
2. Load that reference for requested category and target mapping, preserving repo naming, shape, typing, modes, and platform conventions. Create no export unless file changes were requested.
3. For incomplete names, values, aliases, modes, or priority, load `references/token-gap-policy.md`. Keep gaps missing and inferences labeled; a required gap needs canonical evidence or an explicit scoped user decision before readiness.
4. For requested edits, read the resulting value, alias, and mode through the real consumer path. If it resolves another source, keep the condition open, correct selection in the owning module, and repeat the same-path readback. A parser inventory, mock, or generated file proves only its boundary.
5. Hand the scoped mapping and unresolved items to `design-frontend`, `design-component-mapper`, or visual review; do not claim UI completion from token readiness.

## Output
For a narrow question, return only the mapping, conflict, or gap in scope. For an explicit inventory/export artifact, use the shape in `references/token-normalization.md` and omit empty fields.

## Validation And Limits
- Never invent a missing value, semantic name, alias, hierarchy, or source priority. No source means `user-verification-needed` or `unverified`, not readiness.
- Report parser failure with path/error. `scripts/inspect_tokens.py` is a read-only inventory aid, not correctness or design-system proof.
- Keep subjective palette critique separate from verified mismatch. Screenshot values and visual taste are not token authority.
- Do not broaden one surface into a redesign or exhaustive catalog. Accessibility contrast belongs to `design-a11y-audit`; visual, component-state, repo, and user-visible validation remain separate gates.
