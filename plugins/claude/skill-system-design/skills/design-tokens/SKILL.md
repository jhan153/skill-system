---
name: design-tokens
description: "Normalize and audit design token sources for design-to-production — token JSON, CSS variables, Tailwind/theme config, Figma-exported tables, palette/typography/spacing/radius/shadow/motion/breakpoint tokens, token gaps/drift, platform mapping, and no-fabrication token evidence."
disable-model-invocation: true
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
    - `references/design_stage_contract.md` when this work is one node in a Design DAG or its ownership boundary is unclear
    - `references/design_evidence_contract.md` when classifying source authority, proof, or an unavailable condition
    - `references/product_family_design_contract.md` when the repository declares shared token governance or a product-family profile
    - `references/token-normalization.md` for multi-category normalization, alias/mode/naming normalization, platform export shape, or an explicit inventory/export artifact
    - `references/token-gap-policy.md` when names, values, aliases, modes, or source priority are incomplete
    - `references/visual_decision_contract.md` when a missing look tempts a factory palette or type stack
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

This is a token-evidence owner. It may create or edit a requested token artifact, but it never
owns production UI code or a later Design stage.

## Stage Boundary

Apply `references/design_stage_contract.md`. Close only the assigned token authority, mapping, or
gap condition. A result from this skill does not start component mapping, implementation, visual
review, or accessibility review. Use `references/design_evidence_contract.md` for evidence labels
and proof ceilings.

## Workflow
1. Pin source pointers and declared authority. When an applicable product-family profile exists,
   apply `references/product_family_design_contract.md`. Use a declared canonical source;
   otherwise keep the conflict unresolved without inventing precedence. Screenshot/rendered values
   remain inferred, and a canonical winner does not erase displaced live/legacy mismatches.
2. Answer narrow authority, conflict, gap, or same-system mappings directly. Load `references/token-normalization.md` only for multi-category, alias/mode/naming, platform-export, or explicit inventory/export work. Preserve repo naming, shape, typing, modes, and platform conventions; create no unrequested export.
3. For incomplete names, values, aliases, modes, or priority, load `references/token-gap-policy.md`. Keep gaps missing and inferences labeled; a required gap needs canonical evidence or an explicit scoped user decision before readiness.
4. For requested edits, read the resulting value, alias, and mode through the real consumer path. If it resolves another source, keep the condition open, correct selection in the owning module, and repeat the same-path readback. A parser inventory, mock, or generated file proves only its boundary.
5. Return the scoped mapping, decisive evidence, and unresolved items. Name the relevant owner only
   as a handoff hint; do not invoke it or claim UI completion from token readiness.

## Output
For a narrow question, return only the mapping, conflict, or gap in scope. For an explicit inventory/export artifact, use the shape in `references/token-normalization.md` and omit empty fields.

## Validation And Limits
- Never invent a missing value, semantic name, alias, hierarchy, or source priority. No source means `user-verification-needed` or `unverified`, not readiness.
- Never fill a token gap with indigo/violet, Inter/Space Grotesk, or a framework semantic rainbow. A sourced brand, including a purple identity, stays.
- Report parser failure with path/error. `scripts/inspect_tokens.py` is a read-only inventory aid, not correctness or design-system proof.
- Keep subjective palette critique separate from verified mismatch. Screenshot values and visual taste are not token authority.
- Do not broaden one surface into a redesign or exhaustive catalog. Accessibility contrast belongs to `design-a11y-audit`; visual, component-state, repo, and user-visible validation remain separate gates.
- An unavailable token source affects only the assigned token condition. It does not block an
  unrelated node or authorize a substitute palette, alias, or source.
