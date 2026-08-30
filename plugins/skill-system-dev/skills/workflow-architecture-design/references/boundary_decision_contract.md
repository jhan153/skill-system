# Boundary Decision Contract

This contract defines the shared meaning and decision fields used when software knowledge,
state, behavior, ownership, or dependencies may need a boundary. It applies both to initial
implementation and to changes in an existing system. It is a decision contract, not a third
workflow owner.

## Principle

Keep knowledge, state, and behavior that must remain consistent inside one boundary. Separate
things that need to evolve independently behind the smallest sufficient contract. Strengthen a
boundary only when the independence it creates outweighs its translation, coordination, testing,
and operating cost.

## Decision Record

Use only the fields needed by the current decision. Mark material claims `established`, `inferred`,
or `unverified` according to the consuming skill's evidence rules.

```yaml
boundary_decision:
  target:
  design_pressure:
  cohesion_basis:
  separation_basis:
  inside_invariant:
  outside_contract:
  dependency_direction:
  enforcement:
  boundary_cost:
  representative_scenario:
  falsifier:
  paradigm_constraints:
    profile_ref:
    kind: programming_paradigm | adjacent_implementation_model
    governed_axis:
    owner:
    authority_ref:
    claimed_properties: []
    minimum_closure: []
    maximum_scope:
    interactions: []
    forbidden_drift: []
    design_proof_ceiling:
    delta_relation:
  decision: keep_local | create | merge | split | move | defer
```

- `target`: the knowledge, state, behavior, policy, dependency, or operating unit under decision.
- `design_pressure`: the initial use case, required invariant, external volatility, independent
  ownership/deployment need, or observed change/failure that makes the decision material.
- `cohesion_basis`: what must be understood, validated, or changed together.
- `separation_basis`: what must remain independently understandable, replaceable, testable,
  deployable, or operable.
- `inside_invariant`: the consistency rule that the boundary owns.
- `outside_contract`: the minimum knowledge and behavior allowed to cross the boundary.
- `dependency_direction`: which side may know or depend on the other, including policy ownership.
- `enforcement`: the smallest sufficient mechanism, such as a function, object/type, module/API,
  adapter, process, or deployment boundary.
- `boundary_cost`: added translation, coordination, lifecycle, testing, latency, failure, or
  operational cost.
- `representative_scenario`: one actual or required path that exercises the proposed boundary.
- `falsifier`: a concrete scenario that would show the grouping, separation, contract, direction,
  or strength to be wrong.
- `paradigm_constraints`: optional only when `programming_paradigm_contract.md` selects
  `decision_owner: atomic_boundary`. It preserves the selected thin profile and cross-stage
  property owner/paradigm-model meaning inside this one boundary record; it is not a second
  architecture artifact.
- `decision`: the smallest evidenced move. `keep_local` is a first-class result.

## Evidence Rules

- Initial implementation does not require historical change evidence. Explicit requirements,
  invariants, known external volatility, ownership, and a representative use case may establish the
  pressure.
- Existing-system decisions use the actual owner and one representative path. Change history,
  failures, and caller friction allocate attention but do not establish a boundary by themselves.
- Names, directory shape, class counts, reuse hopes, and test convenience are leads only.
- Prefer one current owner and contract. Do not create a wrapper, duplicate source of truth, or
  parallel policy path merely to make a boundary visible.
- A test or mock proves only the behavior it observes. It neither creates domain meaning nor proves
  the production boundary independently.
- Compare the proposed move with `keep_local`. If the contract surface and boundary cost remove no
  material knowledge, volatility, invalid state, or coordination burden, keep the behavior local.

## Consumer Responsibilities

- `analysis-domain-modeling` uses this contract when concept, invariant, lifecycle, or policy
  ownership requires grouping or separation. It owns domain meaning and may leave structural
  enforcement `defer` when that decision needs code-boundary evidence.
- `analysis-boundary-design` uses this contract for every standalone or explicitly assigned atomic
  structural boundary decision. It owns the minimum contract, dependency direction, enforcement
  strength, cost comparison, and `keep_local | create | merge | split | move | defer`
  recommendation for that one decision. When an accepted `architecture_design` explicitly
  constrains the target, it preserves the relevant architecture fields including accepted
  architecture-delta scope and returns the design reference plus one decision; a delta expansion,
  coupled-view move, or accepted-constraint conflict is `defer` and returns to the architecture
  owner. When the shared paradigm gate selects `atomic_boundary`, this owner writes the selected
  profile/scope/proof ceiling only into `paradigm_constraints` on that same decision.
- `workflow-architecture-design` uses the same record fields for coupled boundaries that must be
  selected together inside one multi-view target and transition architecture. It owns their
  cross-view coherence without invoking a second owner for each boundary; a request whose whole
  outcome is one contested structural boundary stays with `analysis-boundary-design`.
