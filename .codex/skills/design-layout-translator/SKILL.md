---
name: design-layout-translator
description: Translate design layout constraints into implementable layout rules without owning full UI implementation. Use when Codex must convert Figma Auto Layout, flex/grid decisions, fill/hug/intrinsic sizing, fixed vs flexible regions, min/max constraints, padding/gap, scroll and overflow behavior, breakpoint behavior, responsive order, or CSS/native layout mapping into code-ready guidance.
---

# design-layout-translator

## Routing Card
- role: primary_analysis_or_modifier
- intent_signature:
  - Auto Layout to implementation mapping
  - flex/grid constraint translation
  - intrinsic fill hug fixed sizing
  - responsive breakpoint behavior
  - scroll overflow text fitting rules
- use_when:
  - the user asks to translate layout constraints, Auto Layout, flex/grid, sizing, overflow, or breakpoints.
  - an implementation task needs layout rules before code changes.
  - a layout bug or design mismatch depends on constraint interpretation rather than full visual implementation.
- do_not_use_when:
  - the user asks for full UI implementation; use `design-frontend` with this as a reference/modifier.
  - the user asks only for visual screenshot comparison; use `design-visual-regression`.
  - the user asks only for component variant/state mapping; use `design-component-mapper`.
  - the request is backend-only or data-model-only.
- expected_inputs:
  - design constraint description, Figma Auto Layout notes, screenshot, CSS/native layout code, or target platform
  - container hierarchy and responsive requirements when available
  - target implementation technology when known
- expected_outputs:
  - layout rule map
  - fixed/flexible region decisions
  - spacing and sizing constraints
  - overflow and scroll behavior
  - breakpoint and responsive order rules
  - unverified constraint gaps
- context_targets:
  must_read:
    - provided layout reference, design spec, or relevant layout code
  read_if_needed:
    - `references/layout-translation-map.md`
    - design-frontend surface references
    - visual evidence report
  do_not_load_by_default:
    - unrelated app routes
    - full repo history
    - live credentials
- risk_profile:
  reads:
    - design references and layout source files
  writes:
    - analysis artifacts only unless attached to implementation
  tools:
    - local source inspection and rendered screenshot inspection when available
  sensitive_resources:
    - authenticated design sessions default deny
- entry_scene:
  - PREPARE

Use this skill to produce code-ready layout constraints. It can attach to `design-frontend`, but it should not take over full implementation.

## Workflow
1. Identify layout context:
   - Record platform, target surface, parent/child hierarchy, viewport, and source evidence.
2. Classify axes and regions:
   - One-axis arrangement usually maps to flex/stack.
   - Two-axis region layout usually maps to grid.
   - Fixed-format controls, boards, and tiles need stable dimensions.
3. Translate sizing:
   - Map hug/intrinsic to content-sized with max constraints.
   - Map fill to flexible tracks, flex grow, or bounded percentage sizing.
   - Map fixed sizing only when stability is required.
4. Translate spacing and alignment:
   - Record padding, gap, alignment, distribution, gutters, and nested spacing.
   - Keep token names if known; otherwise mark inferred.
5. Translate overflow and responsive behavior:
   - Decide wrap, scroll, truncate, clamp, hide, stack, reflow, or reorder.
   - Define breakpoint-specific changes and text-fitting risks.
6. Hand off:
   - For code changes, hand off layout rules to `design-frontend`.
   - For rendered proof, hand off viewport checks to `design-visual-regression`.

## Output schema
```yaml
source_reference:
target_platform:
layout_hierarchy: []
axis_model:
fixed_regions: []
flexible_regions: []
sizing_rules: []
spacing_rules: []
alignment_rules: []
overflow_rules: []
breakpoint_rules: []
text_fitting_risks: []
implementation_mapping: []
unverified: []
```

## Validation
- Each layout rule must cite source evidence or be marked inferred.
- Do not scale font size with viewport width.
- Do not claim responsive correctness without breakpoint rules or screenshot evidence.
- Include at least three negative route checks before promoting implicit invocation:
  - not full implementation
  - not screenshot-diff-only
  - not component-state-only

## Recovery
- If Figma metadata is unavailable, infer from visible hierarchy and mark exact sizes `Unverified`.
- If the repo uses a specific layout system, translate into that system instead of generic CSS.
- If text overflow is likely, require min/max/wrap/truncate rules before handoff.

## Known Limits
- This skill does not inspect full visual fidelity by itself.
- This skill does not create a component API.
- This skill does not choose product hierarchy; use `design-ui-decomposer` first when hierarchy is unclear.

## Optional resources
- Read `references/layout-translation-map.md` for common design-to-code mappings.
