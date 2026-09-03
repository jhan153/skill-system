---
name: analysis-domain-modeling
description: Clarify domain language, identity, state transitions, invariants, and ownership from actual software paths before implementation or refactoring; not for generic architecture or glossary work.
---

# Analysis Domain Modeling

## Routing Card
- role: primary
- intent_signature:
  - domain modeling, ubiquitous language, identity/value/state boundary, invariant, business rule, or naming decision
- use_when:
  - a development decision depends on clarifying concepts, terminology, lifecycle, invalid states, or domain-policy ownership.
- do_not_use_when:
  - clear-term implementation (`workflow-implementation`), module/seam architecture (`analysis-boundary-design`), broad analysis, current failure RCA, persistent glossary/ADR/docs writing (documentation owner), memory/accepted-knowledge mutation, or product ideation.
- expected_inputs:
  - decision area, material use case, current terms, relevant production owner/callers/schema/API, and explicit write scope if any
- expected_outputs:
  - evidence-backed vocabulary, concept/state/invariant decision, rejected alternatives, smallest owner-mapped handoff, and unresolved rules
- context_targets:
  must_read:
    - request, actual domain owner, representative caller or transition path, and existing terms
  read_if_needed:
    - persisted/API schemas, errors, tests/fixtures, and explicitly referenced policy/docs
    - `references/boundary_decision_contract.md` when concept, invariant, lifecycle, or policy ownership requires grouping or separation
  do_not_load_by_default:
    - full repo/memory, unrelated product docs, production data, or generated reports
- risk_profile:
  reads: scoped production source, callers, schemas, tests, docs, and examples
  writes: none by default; code/docs only when explicitly requested
  tools: focused search and the smallest readback or counterexample that discriminates a rule
  sensitive_resources: deny credentials and production data
- entry_scene:
  - PREPARE

## Evidence And Modeling Rules
- Ground each rule in an explicit user decision, canonical policy/schema, current production owner/path, or observed behavior; name the source. Tests and fixtures show what they encode but are not independent business oracles, especially when agent-authored.
- When code, schema, docs, tests, and user language conflict, keep the conflict visible. Do not turn a current implementation accident into an invariant; reject a silent fallback as the candidate model when canonical input is required. Mark unresolved material rules `Unverified` and request the exact decision/evidence needed.
- An entity needs identity across change; a value object uses value equality; a state is a lifecycle condition; commands express intent; events record facts; policies/invariants constrain transitions. Do not add wrappers or type hierarchies unless they prevent a concrete invalid state or clarify an owning boundary.
- For every transition, state trigger, precondition, owning module, state/effect, invalid alternative, and evidence. Check one representative caller plus persistence/API readback or explain why unavailable.
- Adapters own translation, not canonical-source, eligibility, domain-policy, or fallback choice. Keep those decisions at the production/domain owner.
- When domain meaning requires a boundary decision, use `references/boundary_decision_contract.md`. Initial requirements and invariants are valid design pressure; do not require existing change history or invent structural enforcement without code-boundary evidence.

## Workflow
1. Define the material decision, observable implementation benefit, and non-goals.
2. Trace current language and behavior through the owning source, one representative caller, schema/API boundary, and only the tests/docs that carry relevant evidence.
3. Separate same-name/different-concept, synonym, raw data shape, lifecycle state, command, event, and policy candidates. Record conflicts and provenance.
4. Write the smallest concept and transition model, its invariants/invalid states, and one counterexample that would disprove it.
5. When grouping or separation is material, fill the semantic fields of the shared `boundary_decision`: design pressure, cohesion/separation basis, owned invariant, representative scenario, falsifier, and supported ownership decision. Preserve `defer` for unresolved structural enforcement.
6. Compare status quo with at most the material alternatives. Select names and ownership only where evidence supports them; leave unresolved business choices explicit.
7. Map the decision to concrete owner/call-site/schema changes and behavior readback. Hand unresolved structural enforcement to `analysis-boundary-design`, implementation to `workflow-implementation`, or behavior-preserving rename/extraction to `workflow-refactor-safely`.

## Output Contract
Return only needed sections: decision scope, current evidence/language, concept and transition model, invariants/invalid states, applicable `boundary_decision`, naming/ownership decision, rejected alternatives, implementation/readback handoff, and unverified questions. Label each material rule established, inferred, or unresolved.

## Cross-Skill Boundaries
- `analysis-boundary-design` owns module boundaries, deep modules, seams, and adapters. Preserve the shared `boundary_decision` and established domain meaning when handing off unresolved structural enforcement.
- `workflow-implementation` owns direct code changes from a selected model.
- `workflow-refactor-safely` owns behavior-preserving renames/extractions after the model is selected.
- An explicitly requested execution-ready debugging scope or runtime diagnosis through a debugger, crash artifact, dynamic diagnostic, concurrency trace, or graphics capture belongs to `workflow-runtime-debugging`; simple source/log-only diagnosis stays with the current task owner, and only a semantically admitted bounded repair under an already-implemented accepted contract belongs to `workflow-bug-fix`. A selected model's first production implementation or explicit replacement belongs to `workflow-implementation`.
- The documentation owner handles an explicitly requested ordinary glossary/ADR/docs artifact. Memory or knowledge skills own explicit persistent memory or Wiki/accepted-knowledge mutation.
