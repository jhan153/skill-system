---
name: component-contract-mapper
description: Map design components, variants, states, slots, events, responsive behavior, and accessibility contracts to existing repository components. Use when Codex must audit Figma/spec components against code components, state coverage, Storybook variants, design-system contracts, unmapped UI states, or component implementation gaps before UI implementation or review.
---

# component-contract-mapper

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - component contract mapping
  - design component inventory
  - repo component mapping
  - variant and state coverage
  - responsive and accessibility contract coverage
- use_when:
  - a design-to-production task needs proof that design components map to implemented repo components.
  - missing UI states, variants, slots, events, or responsive behavior need to be recorded before implementation or completion.
  - the user asks to compare Figma/spec/Storybook/component variants or state names.
- do_not_use_when:
  - the task only needs token normalization, screenshot comparison, or accessibility checks.
  - no design source, component list, or implementation target is available.
  - the user asks for direct visual implementation; use `design-to-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - design component inventory or reference artifact
  - repository component paths, stories, exports, or examples
  - expected variants, states, slots, events, and breakpoints
- expected_outputs:
  - design component inventory
  - repo component mapping
  - variant/state/responsive matrix
  - unresolved component contract gaps
- context_targets:
  must_read:
    - design source or component list
    - relevant repo component paths
  read_if_needed:
    - `references/component-contract-schema.md`
    - `references/state-coverage-matrix.md`
    - design token export
    - visual evidence manifest
    - accessibility evidence report
  do_not_load_by_default:
    - unrelated routes
    - full repo history
    - live credentials
- risk_profile:
  reads:
    - design references and component source files
  writes:
    - component contract artifacts and registry entries only when explicitly requested
  tools:
    - local read-only component inventory scripts
  sensitive_resources:
    - credentials and authenticated live sessions default deny
- entry_scene:
  - PREPARE

Use this skill when design-to-code work needs a clear contract between design components and existing code components. It maps and reports gaps; it does not redesign a component API unless the user asks for API design.

## Workflow
1. Identify component sources:
   - Design components, variants, component sets, screenshots, specs, Storybook stories, exported props, or existing repo components.
   - Record exact source pointers and implementation paths.
2. Build a component inventory:
   - Include component name, visual role, repo path/export, current usage, and available examples.
   - If repo components cannot be found, mark `unmapped_design_components`.
3. Map variants and states:
   - Track size, tone, emphasis, density, platform, layout, and responsive variants.
   - Track default, hover, focus, active, selected, disabled, loading, empty, error, success, expanded, collapsed, validation, and destructive states when relevant.
4. Map slots, events, and composition:
   - Record required children, icons, labels, helper text, actions, menus, overlays, and event callbacks.
   - Separate page-specific copy from reusable component API requirements.
5. Map accessibility and responsive behavior:
   - Record labels, roles, focus expectations, keyboard behavior, target size, breakpoint behavior, and overflow expectations.
6. Hand off gaps:
   - Feed missing state/variant evidence into `design-to-frontend`, visual review, or accessibility review only when implementation continues.

## Output schema
Return or write a structured report with these fields:

```yaml
component_inventory: []
repo_mapping: []
variant_matrix: []
state_matrix: []
slot_contracts: []
event_contracts: []
responsive_matrix: []
accessibility_contracts: []
unmapped_design_components: []
unimplemented_repo_states: []
conflicts: []
scope_boundary: []
unverified: []
```

## Validation
- Every mapped repo component must cite a file path, story path, export name, or concrete source pointer.
- Missing states remain gaps, not assumed complete.
- One-off page details must not become reusable component API requirements without justification.
- If design and repo names differ, report the alias mapping instead of renaming automatically.
- If a script is used, include the command and treat its output as inventory evidence, not complete contract proof.

## Recovery
- If the repo lacks Storybook or component exports, inspect nearby routes/screens that use the component.
- If design source is unavailable, map from user-provided specs and mark missing design evidence as `Unverified`.
- If a component has too many variants, split the matrix by component or state family.
- If implementation is requested after mapping, hand off only the scoped gaps to `design-to-frontend`.

## Known Limits
- This skill does not decide visual fidelity by itself.
- This skill does not prove keyboard or screen-reader behavior; hand off to `accessibility-audit-harness`.
- This skill should not trigger for backend data models just because they are called components.

## Do not invent / Unverified policy
- Do not invent variants, props, slots, events, or state behavior not present in design, code, or user requirements.
- Mark inferred or missing state coverage as `Unverified`.
- Keep proposed API improvements separate from confirmed component contracts.

## Optional resources
- Read `references/component-contract-schema.md` for the contract report shape.
- Read `references/state-coverage-matrix.md` for state family coverage guidance.
- Use `scripts/scan_component_exports.py` only as a read-only source inventory helper.

## Completion Boundary
Do not mark design implementation complete from this gate alone. This skill verifies contract coverage; rendered visual proof, accessibility evidence, token readiness, and repo validation remain separate gates.
