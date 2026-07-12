---
name: design-component-mapper
description: "Map design components, semantic roles, variants, states, slots, events, responsive behavior, and accessibility contracts to existing repo components. Use approved component catalogs to prove app-surface reuse, identify raw/default/custom-control violations, and record authorized exceptions or unmapped gaps before UI completion."
---

# design-component-mapper

## Routing Card
- role: design_evidence_gate
- intent_signature:
  - component contract mapping
  - approved component catalog mapping
  - component reuse proof
  - design component inventory
  - repo component mapping
  - variant and state coverage
  - responsive and accessibility contract coverage
- use_when:
  - a design-to-production task needs proof that design components map to implemented repo components.
  - a product-family policy requires approved controls instead of raw, default, or custom app-surface controls.
  - missing UI states, variants, slots, events, or responsive behavior need to be recorded before implementation or completion.
  - the user asks to compare Figma/spec/Storybook/component variants or state names.
- do_not_use_when:
  - the task only needs token normalization, screenshot comparison, or accessibility checks.
  - no design source, component list, or implementation target is available.
  - the user asks for direct visual implementation; use `design-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - design component inventory or reference artifact
  - repository component paths, stories, exports, or examples
  - expected variants, states, slots, events, and breakpoints
  - approved component catalog and fallback/exception policy when declared
- expected_outputs:
  - design component inventory
  - repo component mapping
  - component reuse evidence or scoped exception
  - variant/state/responsive matrix
  - unresolved component contract gaps
- context_targets:
  must_read:
    - design source or component list
    - relevant repo component paths
    - applicable approved component catalog when declared, or the inspected-scope result that none was found
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

Use this skill when design-to-code work needs a clear contract between design components and existing code components. It maps planned controls and verifies actual import/use evidence; it does not redesign a component API unless the user asks for API design.

## Workflow
1. Identify and pin component sources:
   - Design components, variants, component sets, screenshots, specs, Storybook stories, exported props, existing repo components, and any approved catalog/fallback policy.
   - Record exact source pointers and implementation paths. When a catalog exists, record its version or digest and applicable platform/surface scope.
2. Build a component inventory:
   - Include component name, visual role, repo path/export, current usage, and available examples.
   - If repo components cannot be found, mark `unmapped_design_components`.
3. Map semantic roles to catalog candidates:
   - For every affected app-surface control, record semantic role, required behavior, selected catalog id/export/variant, and nearest rejected candidate.
   - If an approved match exists, mark it `required`; do not treat raw/default/custom implementation as an equivalent mapping.
   - If none exists, mark it `unmapped` and carry the declared native fallback or exception requirement forward.
4. Map variants and states:
   - Track size, tone, emphasis, density, platform, layout, and responsive variants.
   - Track default, hover, focus, active, selected, disabled, loading, empty, error, success, expanded, collapsed, validation, and destructive states when relevant.
5. Map slots, events, and composition:
   - Record required children, icons, labels, helper text, actions, menus, overlays, and event callbacks.
   - Separate page-specific copy from reusable component API requirements.
6. Map accessibility and responsive behavior:
   - Record labels, roles, focus expectations, keyboard behavior, target size, breakpoint behavior, and overflow expectations.
7. Verify actual reuse after implementation:
   - Cite the app-surface file and import/use site for each selected approved component. A catalog entry, export list, story, or similar appearance proves availability only.
   - Record status as `planned`, `reused`, `approved_exception`, `unmapped`, `conflict`, or `unverified`. A planned mapping cannot close the post-implementation reuse gate.
   - Scope raw/native primitive checks to app-surface call sites. Semantic HTML/native primitives used inside an approved design-system component are not violations.
8. Hand off gaps:
   - Feed missing states, unresolved mappings, raw-control conflicts, and exceptions into `design-frontend`, visual review, or accessibility review only when implementation continues.

## Output
For a narrow mapping question, return the mapping, missing contracts, and evidence pointers directly. Use the structured shape only for an explicit mapping artifact or multi-component review; omit empty matrices.

```yaml
component_inventory: []
catalog_identity: {}
repo_mapping: []
component_reuse_report: []
variant_matrix: []
state_matrix: []
slot_contracts: []
event_contracts: []
responsive_matrix: []
accessibility_contracts: []
unmapped_design_components: []
unimplemented_repo_states: []
conflicts: []
approved_exceptions: []
scope_boundary: []
unverified: []
```

## Validation
- Every mapped repo component must cite a file path, story path, export name, or concrete source pointer.
- Every `reused` verdict must cite the app-surface import/use evidence; export inventory alone cannot pass reuse.
- A `planned` mapping is implementation guidance, not reuse proof or a completion verdict.
- When an applicable approved match exists, raw/default/custom app-surface controls are `conflict`, even if visually similar.
- An `approved_exception` must cite the waived rule, exact scope, reason, and authorizing source. Do not infer approval from existing drift.
- An unmapped role stays `unmapped`; follow the product-family fallback policy and never invent a catalog match.
- Interpret `approved_match_required`, `native_when_unmapped`, and `explicit_exception_only` using `references/component-contract-schema.md`; do not treat every unmapped role as implicit native/custom permission.
- Do not report primitives internal to an approved component as app-surface violations.
- Treat project-specific lint/import checks as deterministic only for their documented scope; a generic text scan is inventory evidence, not reuse proof.
- Missing states remain gaps, not assumed complete.
- One-off page details must not become reusable component API requirements without justification.
- If design and repo names differ, report the alias mapping instead of renaming automatically.
- If a script is used, include the command and treat its output as inventory evidence, not complete contract proof.
- Do not enumerate every theoretical state when the target component cannot express or require it.

## Recovery
- If the repo lacks Storybook or component exports, inspect nearby routes/screens that use the component.
- If design source is unavailable, map from user-provided specs and mark missing design evidence as `Unverified`.
- If the catalog is missing, mutable without a version/digest, or out of scope for the target, do not claim catalog conformance.
- If a component has too many variants, split the matrix by component or state family.
- If implementation is requested after mapping, hand off only the scoped gaps to `design-frontend`.

## Known Limits
- This skill does not decide visual fidelity by itself.
- This skill does not decide which UX pattern is best when several approved components satisfy the role; `design-frontend` owns the evidence-based choice.
- This skill does not prove keyboard or screen-reader behavior; hand off to `design-a11y-audit`.
- This skill should not trigger for backend data models just because they are called components.

## Do not invent / Unverified policy
- Do not invent variants, props, slots, events, or state behavior not present in design, code, or user requirements.
- Do not invent a catalog, approval, exception, or native fallback policy.
- Mark inferred or missing state coverage as `Unverified`.
- Keep proposed API improvements separate from confirmed component contracts.

## Optional resources
- Read `references/component-contract-schema.md` for the contract report shape.
- Read `references/state-coverage-matrix.md` for state family coverage guidance.
- Use `scripts/scan_component_exports.py` only as a read-only source inventory helper.

## Completion Boundary
Do not mark design implementation complete from this gate alone. This skill verifies contract coverage; rendered visual proof, accessibility evidence, token readiness, and repo validation remain separate gates.
