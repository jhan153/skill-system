---
name: design-tokens
description: Normalize and audit design token sources for design-to-production work. Use when Codex must inspect token JSON, CSS variables, Tailwind/theme config, Figma-exported token tables, palette/typography/spacing/radius/shadow/motion/breakpoint tokens, token gaps, token drift, platform mapping, or no-fabrication token evidence before UI implementation or review.
---

# design-tokens

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - design token source
  - token normalization
  - platform token export
  - token gap and conflict audit
  - color typography spacing radius shadow motion breakpoint tokens
- use_when:
  - a design-to-production task needs token source handling before implementation or review.
  - token transformation evidence must be recorded for visual or component verification.
  - the user asks to compare design tokens with CSS variables, Tailwind config, theme files, or component styles.
- do_not_use_when:
  - the task only needs component state mapping, screenshot comparison, or accessibility checks.
  - no design source or token source is available and the user expects invented values.
  - the user asks for direct UI implementation from a concrete visual artifact; use `design-frontend` as primary and this skill only as a supporting gate.
- expected_inputs:
  - design token source, style guide, or design reference
  - target platform or repository styling conventions
  - expected token categories and output format when available
- expected_outputs:
  - token source pointer
  - normalized token inventory
  - platform token mapping
  - inferred values and unresolved token gaps
  - conflicts and do-not-generate notes
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
  reads:
    - design references, token files, style system files
  writes:
    - token artifacts and registry entries only when explicitly requested
  tools:
    - local read-only parsing and validation scripts
  sensitive_resources:
    - credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

Use this skill when a design-to-production task needs trustworthy token source handling. Keep it as an evidence gate: it can support implementation, but it does not own UI code changes unless the user explicitly asks for token artifact edits.

## Workflow
1. Identify the source of truth:
   - Prefer explicit token files, design-system theme files, exported token tables, or style-guide specs.
   - Treat screenshot-derived colors, spacing, and typography as inferred candidates, not confirmed tokens.
   - Record source paths, frame names, URLs, or artifact IDs as `source_pointer`.
2. Classify token categories:
   - Use color, typography, spacing, radius, border, shadow/elevation, opacity, motion, breakpoint, z-index, and semantic role categories.
   - Separate raw values from semantic aliases such as `color.action.primary` or `space.card.padding`.
3. Normalize names and values:
   - Preserve existing repo naming style when a platform target exists.
   - Keep role-based names where possible; avoid only raw-value names like `blue500` when the source clearly encodes intent.
   - Mark aliases, inherited values, and mode-specific values.
4. Map to the target platform:
   - CSS variables, Tailwind config, JS/TS theme objects, native constants, or design-token JSON may be targets.
   - Do not generate platform exports unless the user explicitly requests file changes.
5. Detect gaps and conflicts:
   - Missing values remain `missing_values`.
   - Conflicting definitions remain `conflicts`.
   - Inferred values remain `inferred_values` with the inference basis.
6. Hand off evidence:
   - Provide token mapping to `design-frontend`, `design-component-mapper`, or visual review when implementation continues.

## Output schema
Return or write a structured report with these fields:

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

## Validation
- Every confirmed token must cite a source pointer.
- Every platform token must map to a source token or be marked `inferred`.
- Missing values must stay gaps; do not silently invent colors, sizes, names, or aliases.
- If a script is used, include the command and state that it is an inventory aid, not a full design-system proof.
- If no token source exists, report `user-verification-needed` or `unverified`; do not claim token readiness.

## Recovery
- If token files cannot be parsed, inspect a smaller file or report parser failure with the path and error.
- If source and repo naming conflict, keep both names and list the proposed bridge mapping.
- If the repo has no token system, produce an inventory and recommend the smallest local constants needed for the requested UI surface.
- If multiple themes or modes exist, report mode coverage separately.

## Known Limits
- Screenshot-derived values are approximate and must remain inferred.
- NN/g or visual taste is not token evidence.
- This skill cannot certify full accessibility contrast alone; hand off contrast to `design-a11y-audit`.
- This skill should not broaden a UI task into full design-system redesign.

## Do not invent / Unverified policy
- Do not invent missing token values, semantic names, or design-system hierarchy.
- Mark unavailable sources, inferred measurements, and approximate values as `Unverified`.
- Keep subjective palette concerns separate from verified source-token mismatches.

## Optional resources
- Read `references/token-normalization.md` for category and naming guidance.
- Read `references/token-gap-policy.md` when values, names, aliases, or source priority are incomplete.
- Use `scripts/inspect_tokens.py` only as a read-only local inventory helper.

## Completion Boundary
Do not mark design implementation complete from this gate alone. This skill verifies token readiness; visual, accessibility, component-state, and repo validation remain separate gates.
