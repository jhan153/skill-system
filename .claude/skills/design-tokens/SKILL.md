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
    - `references/token-normalization.md`
    - `references/token-gap-policy.md`
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
1. Identify and record source pointers. Prefer a declared canonical token/design-system source; otherwise use the precedence in `references/token-normalization.md`. Screenshot/rendered values are inferred candidates only.
2. Freeze source precedence before mapping. If authority is unresolved, keep both values and pointers in `conflicts`; never let a convenient source win. If a declared canonical source wins, still record any displaced live/legacy mismatch in `conflicts`.
3. Normalize requested categories, separating raw values from semantic aliases and preserving existing repo naming, shape, typing, modes, and platform conventions. Use `references/token-normalization.md` for detailed categories.
4. Map only to the requested CSS, Tailwind, theme-object, native, or token-JSON target. Do not create exports unless file changes were explicitly requested.
5. Keep missing values missing and inferred values labeled with their basis. For a required gap, request canonical evidence or an explicit scoped assumption/user decision; do not mark it ready. Use `references/token-gap-policy.md` when names, aliases, modes, priority, or values are incomplete.
6. For requested edits, inspect the real consumer path and read back the resulting token value/alias/mode from that path. If it resolves another source, keep the condition open, correct selection in the owning module, and repeat the same-path readback. A parser inventory, mock, or generated file presence proves only its own boundary.
7. Hand the scoped mapping and unresolved items to `design-frontend`, `design-component-mapper`, or visual review; do not claim UI completion from token readiness.

## Output
For a narrow question, return only the mapping, conflict, or gap in scope. For an explicit inventory/export artifact, omit empty fields from this shape:

```yaml
source_pointer: []
source_format: token-json | css-variables | tailwind-config | theme-object | figma-export | style-guide | screenshot-inferred | mixed
target_platform: css | tailwind | js-theme | native | unknown
normalized_tokens:
  color: []
  typography: []
  spacing: []
  radius: []
  shadow: []
  motion: []
  breakpoint: []
platform_mapping: []
aliases: []
inferred_values: []
missing_values: []
conflicts: []
do_not_generate: []
unverified: []
```

## Validation And Limits
- Every confirmed token cites a source pointer; every platform token maps to that source or remains `inferred`. Multiple modes report coverage separately.
- Never invent a missing value, semantic name, alias, hierarchy, or source priority. No source means `user-verification-needed` or `unverified`, not readiness.
- Report parser failure with path/error. `scripts/inspect_tokens.py` is a read-only inventory aid, not correctness or design-system proof.
- Keep subjective palette critique separate from verified mismatch. Screenshot values and visual taste are not token authority.
- Do not broaden one surface into a redesign or exhaustive catalog. Accessibility contrast belongs to `design-a11y-audit`; visual, component-state, repo, and user-visible validation remain separate gates.
