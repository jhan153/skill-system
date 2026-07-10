---
name: analysis-codebase-design
description: Targeted codebase design analysis for one module boundary, deep module, interface, seam, adapter, dependency direction, or testability decision before implementation. Use when current code evidence must decide a structural move; do not use for repo-wide reports, opportunity scans, or ordinary local implementation.
---

# Analysis Codebase Design

## Routing Card
- role: primary
- intent_signature:
  - one module, interface, seam, adapter, dependency, or testability decision
- use_when:
  - one concrete code-structure decision blocks a feature, fix, or refactor.
  - current coupling, caller knowledge, dependency leakage, or test pain may justify a boundary change.
- do_not_use_when:
  - the user wants a repo-wide report (`analysis-codebase`) or ranked structural candidates (`analysis-architecture-deepening`).
  - a local implementation is obvious, first-pass bug RCA is needed, or the question concerns domain meaning rather than code ownership.
- expected_inputs:
  - target decision and design pressure
  - target source, callers, dependencies, and relevant tests
  - constraints and non-goals when available
- expected_outputs:
  - evidence-backed boundary decision, abstraction-gate result, and smallest implementation/validation handoff
- context_targets:
  must_read:
    - current design question
    - target implementation and public surface
    - representative callers and directly relevant tests
  read_if_needed:
    - package manifests, nearby ADRs, dependency contracts, or failure evidence that distinguishes candidates
  do_not_load_by_default:
    - full repo, full memory, repo-wide reports, or unrelated domain docs
- risk_profile:
  reads:
    - targeted source, usage sites, tests, and dependency signals
  writes:
    - none; an implementation owner must apply a selected design
  tools:
    - focused search and targeted checks only
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Decision Principle
- Prefer a small stable interface that hides policy, data shape, side effects, or dependency volatility from callers.
- Require present leverage and compare every abstraction with keeping the change local.

## Progressive Workflow
1. Frame one decision and observable success: less caller knowledge, better change locality, dependency isolation, or testability.
2. Enumerate usages mechanically, but inspect only the target, a common caller, an edge caller, and the directly affected test path first.
3. Map caller policy, crossing data/errors, side effects, dependency direction, and ownership.
4. Compare at most three moves, including `keep local/no new abstraction`; deepen an existing module before creating one.
5. Apply the gate, recommend the smallest evidenced move, and hand off exact surfaces, preserved behavior, and checks.

## Abstraction Gate
Approve only when evidence shows at least one:
- callers lose duplicated policy or more knowledge than the new surface adds.
- an unstable external dependency is contained.
- costly/brittle behavior gains a meaningful test seam.
- policy moves to its owning concept/module.

Defer when the surface only delegates, serves speculative reuse, duplicates an existing local pattern, or makes the current change harder to validate.

## Evidence Budget and Stop Rule
- Treat names, directory shape, counts, and imports as leads, not proof.
- For a seam, evidence the behavior it makes observable; for an adapter, the volatility it contains; for a deep module, the caller decisions it removes.
- Expand one axis only for a distinct caller contract, conflicting ownership, hidden side effect, or failed validation assumption.
- Stop when one representative path supports the boundary, the gate selects a recommendation or `keep local`, and preserved behavior has a targeted check.
- If a counterexample changes the result, inspect only that usage class. If candidates remain tied, return the missing discriminator as `Unverified`.

## Output Contract
Return the shortest sufficient set:
- `design_pressure`: observed symptom and desired leverage
- `current_boundary`: ownership, crossing knowledge/effects, and evidence refs
- `candidate_moves`: at most three, including keep-local
- `abstraction_gate`: pass/defer reasons tied to evidence
- `recommended_design` and `implementation_handoff`: boundary, knowledge removed, files, behavior, and checks
- `validation_notes`, `risks`, or `unverified_gaps` only when material

## Boundaries
- `analysis-architecture-deepening` finds and ranks multiple opportunities; this skill decides one.
- `analysis-domain-modeling` owns business concepts, identities, invariants, and names.
- `analysis-codebase` owns explicit repo-wide evidence report artifacts.
- `workflow-implementation` or `workflow-refactor-safely` owns code changes.
- Do not turn one design decision into a broad cleanup backlog.
