---
name: design-component-mapper
description: "Map design components, semantic roles, variants, states, slots, events, responsive behavior, and accessibility contracts to existing repo components. Use approved component catalogs to prove app-surface reuse, identify raw/default/custom-control violations, and record authorized exceptions or unmapped gaps before UI completion."
disable-model-invocation: true
---

# design-component-mapper

## Routing Card
- role: design_evidence_gate
- intent_signature: design-to-repo component contract mapping, catalog reuse proof, or required variant/state coverage
- use_when:
  - a design source must map to repo components or a declared catalog before implementation/completion.
  - required variants, states, slots, events, responsive behavior, reuse, exceptions, or gaps need evidence.
- do_not_use_when:
  - the task only needs token normalization, screenshot comparison, or accessibility checks.
  - no design source, component list, or implementation target is available.
  - the user asks for direct visual implementation; use `design-frontend` as primary and this skill as a supporting gate.
- expected_inputs:
  - design/reference inventory, target repo component paths/examples, required contract dimensions, and any approved catalog/fallback policy
- expected_outputs:
  - semantic mapping, reuse/exception evidence, required coverage, and unresolved contract gaps
- context_targets:
  must_read:
    - design source or component list
    - relevant repo component paths
    - applicable approved component catalog when declared, or the inspected-scope result that none was found
  read_if_needed:
    - `references/design_stage_contract.md` when this work is one node in a Design DAG or its ownership boundary is unclear
    - `references/design_evidence_contract.md` when classifying mapping/reuse proof or unavailable evidence
    - `references/product_family_design_contract.md` when an approved catalog, fallback policy, or family rule is declared
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

Connect design roles to existing code components without redesigning their API; keep catalog availability, planned selection, and actual app-surface reuse distinct.

## Stage Boundary

Apply `references/design_stage_contract.md`. This skill owns component/catalog mapping and reuse
evidence only. It never writes production UI, redesigns a component API, starts implementation,
or selects a later evidence owner. Use `references/design_evidence_contract.md` for proof ceilings.

## Contract
- Pin each applicable design source, repository surface, and approved catalog by path plus version or digest. Include the catalog's platform/surface scope and declared fallback policy.
- Map semantic role and required behavior before comparing names or appearance.
- An applicable approved match is required unless a scoped exception or declared fallback authorizes another path.
- Keep proposed API changes separate. `design-frontend` owns implementation and evidence-based UX choices when several approved components fit.

## Workflow
1. Establish the inspected scope. Record exact design pointers, target app-surface paths, catalog
   identity, and the fallback/exception policy. When a product-family profile declares these,
   apply `references/product_family_design_contract.md`. A missing, mutable, or out-of-scope
   catalog cannot support a conformance claim.
2. Inventory only relevant candidates. For each affected control, record its semantic role, required behavior, candidate path/export and available examples. If names differ, record an alias rather than renaming automatically.
3. Select or reject candidates by semantic role and behavior. Cite the selected catalog id/export/variant and nearest rejection. If none matches, keep the role `unmapped` and apply only a declared fallback; never invent a match or permission.
4. Compare only required contract dimensions: relevant variants, states, slots, events, responsive behavior, and accessibility expectations. Missing required dimensions remain gaps. Load `references/state-coverage-matrix.md` only for a broad state review.
5. Classify one mapping or reuse decision directly as `planned`, `reused`, `approved_exception`, `unmapped`, `conflict`, or `unverified`. Load the contract schema only for a mapping artifact, multi-component matrix, or persisted fallback/exception record. `reused` requires the actual app-surface file and import/use site; export inventory alone cannot pass reuse, and other availability artifacts support only `planned`. Record exceptions and conflicts with their exact rule, scope, and authorizing source.
6. Return only the assigned mapping/reuse result, decisive evidence, unresolved mappings, missing
   states, conflicts, and scoped implementation gaps. Name a relevant owner as a handoff hint only;
   do not invoke it.

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
Do not mark design implementation complete from this mapping alone. Close only the assigned
component-contract condition evidenced here; unavailable mapping evidence remains local to that
condition and never blocks unrelated Plan work.
