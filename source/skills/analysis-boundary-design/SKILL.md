---
name: analysis-boundary-design
description: Decide one evidenced module, interface, seam, adapter, or dependency boundary before implementation, standalone or as an explicitly assigned atomic decision inside an accepted architecture design. Preserve the design's relevant constraints; not for coupled multi-view architecture or implementation.
---

# Analysis Boundary Design

## Routing Card
- role: primary
- intent_signature:
  - one module/interface/seam/adapter/dependency/testability decision
- use_when:
  - one structural decision blocks a feature, fix, or refactor and current code evidence must select the boundary.
- do_not_use_when:
  - the request is a multi-view target/transition architecture (`workflow-architecture-design`),
    architecture map, ranked opportunity scan, domain model, bug RCA, direct implementation, or an
    obvious local edit with no boundary choice.
- expected_inputs:
  - one decision/pressure, target owner, common and edge callers, dependency/behavior evidence, constraints, and non-goals
  - optional accepted `architecture_design` reference that explicitly contains or constrains this
    one atomic boundary
- expected_outputs:
  - optional architecture reference/conformance, current owner, candidate moves including
    keep-local, exactly one boundary decision, and implementation/validation or architecture handoff
- context_targets:
  must_read:
    - design question, `references/boundary_decision_contract.md`, target owner/surface, common and material-edge callers, and one behavior path
  read_if_needed:
    - tests, contracts, side effects, canonical source, or readback that distinguishes candidates
    - `references/architecture_design_contract.md` when an accepted architecture design explicitly
      contains or constrains the assigned atomic boundary
    - `references/programming_paradigm_contract.md` when that accepted design contains a
      target-relevant `kind: programming_paradigm | adjacent_implementation_model` application or
      the one boundary question materially selects a paradigm/model
    - after that base contract, only the selected files under
      `references/programming-paradigms/`; load a second profile only for another material axis or
      conflict that can change this atomic decision
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
1. Bind exactly one atomic target and use `references/boundary_decision_contract.md` to frame its
   design pressure, cohesion/separation basis, owned invariant, and representative scenario. When
   an accepted architecture design is supplied, project only this target's applicable constraints
   under the consumption rules below. Initial implementation may be grounded in requirements and
   invariants; existing-system work also inspects the actual path.
2. Inspect the owner, common and material-edge callers, and one falsifying path. Map the minimum crossing contract, knowledge/data/errors, side effects, canonical-source/fallback ownership, dependency direction, and smallest sufficient enforcement.
3. Compare at most three moves including `keep_local`; deepen an existing owner before adding a
   wrapper or parallel source path. Include translation, coordination, testing, failure, latency,
   and operating costs. Reject a move that escapes an accepted pattern scope, canonical authority,
   target-relevant paradigm/model axis/owner/scope/interaction, dependency direction,
   architecture-delta class/changed-contract scope, transition constraint, approval, or fitness
   ceiling.
4. Apply the gate. When one move preserves the accepted architecture, return its reference,
   conformance, completed `boundary_decision`, smallest evidenced move, actual-path check/readback,
   and uncertainty. When every viable move changes coupled views or an accepted constraint, return
   `decision: defer`, the exact conflict, and a `workflow-architecture-design` re-design/re-acceptance
   handoff instead of selecting a local recommendation.

## Accepted Architecture Consumption

Activate this path only when the request is still one standalone or explicitly assigned atomic
boundary and the supplied `architecture_design` has `decision_status: accepted`. A proposed design
may inform hypotheses but is not binding authority and cannot yield architecture conformance.

- Preserve only the target-relevant drivers and quality scenarios, canonical authorities, pattern
  minimum closure and maximum scope, paradigm/model applications and their governed
  axes/owners/interactions/forbidden drift/proof ceilings, dependency direction,
  `architecture_delta.change_class` and `changed_contracts` with their approval state,
  transition/compatibility/rollback constraints, approvals, and fitness conditions as immutable
  inputs.
- Do not rewrite, re-accept, widen, or return the architecture record. Own exactly one nested or
  referenced `boundary_decision` and cite `architecture_design_ref`.
- If the evidence falsifies an accepted constraint, changes a paradigm axis/owner/scope or its
  cross-view interaction, expands the accepted architecture delta, or moves another view/owner,
  surface the conflict. The multi-view coherence and acceptance decision remain with
  `workflow-architecture-design`.
- Hand implementation only an atomic decision that preserves the accepted architecture. A deferred
  conflict returns to Architecture Design and never becomes implementation authority.

## Paradigm Decision Routing

When a paradigm/model choice is material to the one target, apply
`references/programming_paradigm_contract.md` before deciding:

- `decision_owner: implementation` is not a boundary decision and returns to
  `workflow-implementation` without creating an architecture artifact.
- `decision_owner: atomic_boundary` stays here. Load only the selected thin profile, map its kind,
  governed axis, property owner, claimed properties, minimum closure, maximum scope, interactions,
  forbidden drift, proof ceiling, and architecture-delta relation into that decision's optional
  `paradigm_constraints`, and keep implementation details out.
- `decision_owner: coupled_architecture` returns to `workflow-architecture-design`; do not compress
  several view/owner decisions into one nominal boundary.

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
Return only applicable fields: `architecture_design_ref` and `architecture_conformance`
(`preserved | conflict`) when an accepted design was consumed; exactly one `boundary_decision`
whose optional `paradigm_constraints` is the sole paradigm/model authority for an
`atomic_boundary`; current owner/evidence; candidate moves including `keep_local`; gate result;
recommendation; implementation/validation or architecture handoff; and material risks or
`unverified_gaps`. Never return a rewritten `architecture_design` or parallel paradigm record.

## Boundaries
- `workflow-architecture-design` owns a normative design when several module, data/state,
  runtime/failure, integration, deployment, or trust boundaries must be selected coherently. This
  skill may supply one architecture-conforming `boundary_decision` for an explicitly atomic target
  but never widens a one-boundary request into a whole-system architecture exercise or changes
  accepted multi-view coherence.
- `analysis-architecture-deepening` ranks opportunities; `analysis-domain-modeling` owns business meaning and may supply the semantic fields of the shared `boundary_decision`; preserve established meaning and surface conflicts rather than silently redefining it. `analysis-codebase-map` owns descriptive Mermaid HLD/LLD maps. An uncertain failure cause routes to `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane; simple source/log-only diagnosis stays with the current task owner, and requested repair stays with `workflow-bug-fix`. A known feature routes to `workflow-implementation` and a selected refactor to `workflow-refactor-safely`; those implementation owners may write when requested. Do not turn one decision into a cleanup backlog or completion claim.
