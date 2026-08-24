---
name: analysis-boundary-design
description: Decide one evidenced module, interface, seam, adapter, or dependency boundary before implementation, including when keeping the change local is best.
---

# Analysis Boundary Design

## Routing Card
- role: primary
- intent_signature:
  - one module/interface/seam/adapter/dependency/testability decision
- use_when:
  - one structural decision blocks a feature, fix, or refactor and current code evidence must select the boundary.
- do_not_use_when:
  - the request is an architecture map, ranked opportunity scan, domain model, bug RCA, direct implementation, or an obvious local edit with no boundary choice.
- expected_inputs:
  - one decision/pressure, target owner, common and edge callers, dependency/behavior evidence, constraints, and non-goals
- expected_outputs:
  - current owner, candidate moves including keep-local, gate result, one recommendation, and implementation/validation handoff
- context_targets:
  must_read:
    - design question, `references/boundary_decision_contract.md`, target owner/surface, common and material-edge callers, and one behavior path
  read_if_needed:
    - tests, contracts, side effects, canonical source, or readback that distinguishes candidates
    - `references/database_persistence_transparency_contract.md` when the selected boundary concerns database ownership, domain/persistence separation, or an ORM/ODM/data-access seam
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated domain docs, raw production data, or credentials
- risk_profile:
  reads: target, callers, tests, dependency and actual-path signals
  writes: none; implementation owns changes
  tools: focused search and safe observations
  sensitive_resources: deny credentials
- entry_scene:
  - PREPARE

## Decision Workflow
1. Use `references/boundary_decision_contract.md` to frame the target, design pressure, cohesion/separation basis, owned invariant, and representative scenario. Initial implementation may be grounded in requirements and invariants; existing-system work also inspects the actual path.
2. Inspect the owner, common and material-edge callers, and one falsifying path. Map the minimum crossing contract, knowledge/data/errors, side effects, canonical-source/fallback ownership, dependency direction, and smallest sufficient enforcement.
3. Compare at most three moves including `keep_local`; deepen an existing owner before adding a wrapper or parallel source path. Include translation, coordination, testing, failure, latency, and operating costs that the selected enforcement creates.
4. Apply the gate and return the completed `boundary_decision`, smallest evidenced move, preserved conditions, actual-path check/readback, and uncertainty.

When `references/database_persistence_transparency_contract.md` is active, this skill owns only
`boundary_owner`, `caller_contract`, and `automation_boundary`, while preserving accepted
`source_of_truth` and domain requirements. It hands the concrete database model, access effects,
lifecycle, cost visibility, and readback to the matching execution owner.

## Abstraction Gate
Approve only when callers lose more knowledge than the surface adds, an invariant or external volatility is contained, independently evolving work is materially separated, costly production behavior becomes observable, or policy returns to its owner. The independence gained must outweigh the boundary cost recorded by the shared contract. Defer pass-through layers, speculative reuse, duplicate patterns, test/mock-only interfaces, and separation that obscures cause and effect.

Adapters translate protocols, wire shapes, and representations. Canonical source, domain policy, fallback, migration truth, and failure policy stay at the production/domain owner on one authoritative path. A mock proves only its boundary.

## Evidence Budget and Stop Rule
- Treat names, directory shape, counts, and imports as leads, not proof.
- Evidence a seam by real behavior exposed, an adapter by translated volatility, and a deep module by caller decisions removed. Static shape, interfaces, and passing mocks do not establish production benefit.
- Expand only for a distinct caller contract, conflicting owner, hidden side effect, source conflict, or failed validation assumption.
- Stop when a representative path and material edge select a move or `keep_local`, an implementation owner, and condition-matched validation. Inspect only a result-changing counterexample class; if still tied, return its discriminator as `Unverified`.

## Output Contract
Return only applicable fields: `boundary_decision`, current owner/evidence, candidate moves including `keep_local`, gate result, recommendation, implementation/validation handoff, and material risks or `unverified_gaps`.

## Boundaries
- `analysis-architecture-deepening` ranks opportunities; `analysis-domain-modeling` owns business meaning and may supply the semantic fields of the shared `boundary_decision`; preserve established meaning and surface conflicts rather than silently redefining it. `analysis-codebase-map` owns Mermaid HLD/LLD maps. An uncertain failure cause stays with the current task owner when diagnosis-only and with `workflow-bug-fix` when repair is requested. A known feature routes to `workflow-implementation` and a selected refactor to `workflow-refactor-safely`; those implementation owners may write when requested. Do not turn one decision into a cleanup backlog or completion claim.
