---
name: analysis-codebase-design
description: Decide one evidenced module, interface, seam, adapter, or dependency boundary before implementation, including when keeping the change local is best.
---

# Analysis Codebase Design

## Routing Card
- role: primary
- intent_signature:
  - one module/interface/seam/adapter/dependency/testability decision
- use_when:
  - one structural decision blocks a feature, fix, or refactor and current code evidence must select the boundary.
- do_not_use_when:
  - the request is a repo-wide report, ranked opportunity scan, domain model, bug RCA, direct implementation, or an obvious local edit with no boundary choice.
- expected_inputs:
  - one decision/pressure, target owner, common and edge callers, dependency/behavior evidence, constraints, and non-goals
- expected_outputs:
  - current owner, candidate moves including keep-local, gate result, one recommendation, and implementation/validation handoff
- context_targets:
  must_read:
    - design question, target owner/surface, common and material-edge callers, and one behavior path
  read_if_needed:
    - tests, contracts, side effects, canonical source, or readback that distinguishes candidates
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
1. Frame one decision and leverage: less caller knowledge, better change locality, real dependency isolation, or observable costly production behavior.
2. Inspect the owner, common and material-edge callers, and one disconfirming path. Map crossing knowledge/data/errors, side effects, canonical-source/fallback ownership, and dependency direction.
3. Compare at most three moves including `keep local`; deepen an existing owner before adding a wrapper or parallel source path.
4. Apply the gate and hand off the smallest evidenced move, preserved conditions, actual-path check/readback, and uncertainty.

## Abstraction Gate
Approve only when callers lose more knowledge than the surface adds, external volatility is contained, costly production behavior becomes observable, or policy returns to its owner. Defer pass-through layers, speculative reuse, duplicate patterns, test/mock-only interfaces, and separation that obscures cause and effect.

Adapters translate protocols, wire shapes, and representations. Canonical source, domain policy, fallback, migration truth, and failure policy stay at the production/domain owner on one authoritative path. A mock proves only its boundary.

## Evidence Budget and Stop Rule
- Treat names, directory shape, counts, and imports as leads, not proof.
- Evidence a seam by real behavior exposed, an adapter by translated volatility, and a deep module by caller decisions removed. Static shape, interfaces, and passing mocks do not establish production benefit.
- Expand only for a distinct caller contract, conflicting owner, hidden side effect, source conflict, or failed validation assumption.
- Stop when a representative path and material edge select a move or `keep local`, an implementation owner, and condition-matched validation. Inspect only a result-changing counterexample class; if still tied, return its discriminator as `Unverified`.

## Output Contract
Return only applicable fields: `design_pressure`, current owner/evidence, candidate moves including keep-local, gate result, recommendation, implementation/validation handoff, and material risks or `unverified_gaps`.

## Boundaries
- `analysis-architecture-deepening` ranks opportunities; `analysis-domain-modeling` owns business meaning; `analysis-codebase` owns repo-wide reports; `analysis-bug` owns uncertain cause. A known feature routes to `workflow-implementation` and a selected refactor to `workflow-refactor-safely`; those implementation owners may write when requested. Do not turn one decision into a cleanup backlog or completion claim.
