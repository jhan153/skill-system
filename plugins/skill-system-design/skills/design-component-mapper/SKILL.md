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
    - `references/component-contract-schema.md` for a mapping artifact, multi-component matrix, or persisted fallback/exception record
    - `references/state-coverage-matrix.md` for a broad state review
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

Use this skill to connect design roles to existing code components without redesigning their API. The gate distinguishes what a catalog offers, what a plan selects, and what the product actually uses.

## Contract
- Pin each applicable design source, repository surface, and approved catalog by path plus version or digest. Include the catalog's platform/surface scope and declared fallback policy.
- Map semantic role and required behavior before comparing names or appearance.
- An applicable approved match is required unless a scoped exception or declared fallback authorizes another path.
- Keep proposed API changes separate. `design-frontend` owns implementation and evidence-based UX choices when several approved components fit.

## Workflow
1. Establish the inspected scope. Record exact design pointers, target app-surface paths, catalog identity, and the fallback/exception policy. A missing, mutable, or out-of-scope catalog cannot support a conformance claim.
2. Inventory only relevant candidates. For each affected control, record its semantic role, required behavior, candidate path/export and available examples. If names differ, record an alias rather than renaming automatically.
3. Select or reject candidates by semantic role and behavior. Cite the selected catalog id/export/variant and nearest rejection. If none matches, keep the role `unmapped` and apply only a declared fallback; never invent a match or permission.
4. Compare only required contract dimensions: relevant variants, states, slots, events, responsive behavior, and accessibility expectations. Missing required dimensions remain gaps. Load `references/state-coverage-matrix.md` only for a broad state review.
5. Classify one mapping or reuse decision directly as `planned`, `reused`, `approved_exception`, `unmapped`, `conflict`, or `unverified`. Load the contract schema only for a mapping artifact, multi-component matrix, or persisted fallback/exception record. `reused` requires the actual app-surface file and import/use site; export inventory alone cannot pass reuse, and other availability artifacts support only `planned`. Record exceptions and conflicts with their exact rule, scope, and authorizing source.
6. Hand only unresolved mappings, missing states, conflicts, and scoped implementation gaps to the relevant implementation, visual, or accessibility owner.

## Evidence Rules
- Actual app-surface source outranks catalog inventory and generic scans. Scope violations to app-surface call sites; Semantic HTML/native primitives inside an approved component are its implementation detail.
- Apply only the pinned fallback outcome from its authorizing source; `unmapped` is not permission. Native fallback still needs inspected no-match evidence, the actual native call site, and its relevant accessibility contract.
- Missing required states stay gaps; never infer them from a default example or enumerate irrelevant theoretical states.
- Scripts and project checks prove only their documented scope. `scripts/scan_component_exports.py` inventories availability, not reuse.
- Do not invent variants, props, slots, events, approvals, exceptions, fallback policies, or behavior. Mark material missing evidence `unverified`.

## Output
For a narrow question, return the semantic role, selected or rejected mapping, status, decisive source pointers, and unresolved gaps directly. For an explicitly requested artifact or multi-component review, load `references/component-contract-schema.md` and emit only populated sections; add the state matrix only when state coverage is material.

## Recovery And Limits
- Without exports or stories, inspect nearby production routes or screens that use the component.
- Without a design source, map only user-provided requirements and mark the absent design evidence `unverified`.
- This gate does not prove rendered fidelity, keyboard or screen-reader behavior, token readiness, or repository validation. Use their owning checks when those conditions are material.
- Do not invoke this skill for backend data models merely because they are called components.

## Completion Boundary
Do not mark design implementation complete from this mapping alone. Close only the component-contract condition evidenced here; production use, visual fidelity, accessibility, and other material conditions retain their own status.
