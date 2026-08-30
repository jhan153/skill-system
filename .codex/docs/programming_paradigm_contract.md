# Programming Paradigm Decision Contract

This contract defines the shared meaning of programming-paradigm and adjacent implementation-model
choices across Architecture Design, atomic Boundary Design, and production Implementation. It is
not a repository-wide paradigm catalog, a code-style guide, a method-profile index, or a workflow
owner.

## Core Rule

Do not select one paradigm for an entire repository by default. Select and compose approaches at
the smallest boundary that owns the property they govern. A paradigm label is not a design:
record the observable property, owner, minimum complete application, maximum scope, interactions,
forbidden drift, and evidence ceiling.

Treat these as independent, composable axes:

| Governed axis | Typical approaches | Question owned |
| --- | --- | --- |
| runtime computation and state | procedural, object-oriented, functional | How are control flow, identity, state, mutation, and effects represented? |
| data representation and access | packed AoS, SoA/AoSoA, hot/cold split, ECS | Which data is processed together, in what layout and access order? |
| compile-time specialization | Concepts, `constexpr`, generic programming, TMP | Which types, invariants, layouts, or closed policies must be decided before runtime? |
| asynchronous progress and lifetime | structured async, readiness/event loops, completion queues | Where does waiting live, and how are operation lifetime, cancellation, backpressure, and result publication represented? |
| CPU execution architecture | Job System, task DAG, pipelines | How are CPU work, dependencies, completion, load balancing, and resource access represented? |
| shared-memory coordination | partitioned ownership, locks/atomics, reclamation | How are mutable invariants, visibility, ordering, lifetime, and forward progress preserved across execution contexts? |

`ECS` is not synonymous with data-oriented design. A Job System is not an alternative to
procedural, object-oriented, or functional computation. TMP does not own runtime extension or task
scheduling. `async` does not imply parallel execution, and a lock or atomic operation does not
define task scheduling, whole-invariant correctness, or performance.

An asynchronous contract permits caller progress before completion; concurrency permits overlap
and interleaving; parallelism means simultaneous execution. A task DAG expresses permitted order,
a Job System maps ready CPU work to execution carriers, and a pipeline overlaps distinct items or
frames. Threads, workers, and fibers are carriers rather than task or domain identity, so affinity
and TLS dependence must be explicit. None of these labels implies the others.

## Pattern-Application Specialization

`architecture_design_contract.md` exclusively owns the generic `pattern_application` shape,
including pattern, scope, owner, triggers/non-triggers, minimum closure, maximum scope,
interactions, costs, evidence, escalation, and retirement. A programming paradigm or adjacent
implementation model uses that shape and adds only these fields:

```yaml
pattern_application:
  kind: programming_paradigm | adjacent_implementation_model
  governed_axis:
  authority_ref:
  claimed_properties: []
  architecture_impact:
    status: local_implementation | architecture_material
    decision_owner: implementation | atomic_boundary | coupled_architecture
    changed_views: []
    delta_relation:
  forbidden_drift: []
  evidence:
    representative_path:
    falsifier:
    design_proof_ceiling:
    planned_implementation_readback:
```

Architecture Design stores only `decision_owner: coupled_architecture` inside
`architecture_design.pattern_applications`. Boundary Design stores `atomic_boundary` only inside
one `boundary_decision.paradigm_constraints`. Implementation may use the same specialization
internally only for `decision_owner: implementation`; these locations never duplicate one accepted
application.

## Progressive Profile Routing

Read this base contract first, then load only the profile selected by the task and actual path.
Load a second profile only when another material axis or pairwise conflict can change the decision.

| Signal | Default kind | Thin shared profile |
| --- | --- | --- |
| ordered transformation, pipeline, state machine, C ABI/FFI/callback | `programming_paradigm` | `programming-paradigms/procedural.md` |
| identity, invariant, lifecycle, resource owner, runtime substitution | `programming_paradigm` | `programming-paradigms/object-oriented.md` |
| deterministic value transformation, reducer, pure core, effect isolation | `programming_paradigm` | `programming-paradigms/functional.md` |
| bulk access/layout, SIMD/GPU transfer, ECS, representative hot path | `programming_paradigm` | `programming-paradigms/data-oriented.md` |
| compile-time type/layout/invariant, closed policies, TMP | `adjacent_implementation_model` | `programming-paradigms/template-metaprogramming.md` |
| readiness/completion, event loop, coroutine/task lifetime, cancellation/backpressure | `adjacent_implementation_model` | `programming-paradigms/structured-async.md` |
| task DAG, CPU dependency/completion scheduling, Job System | `adjacent_implementation_model` | `programming-paradigms/job-system.md` |
| shared mutable invariant, publication/visibility, locks/atomics, reclamation | `adjacent_implementation_model` | `programming-paradigms/shared-memory-concurrency.md` |

The thin profile owns cross-stage trigger, non-trigger, minimum closure, maximum scope,
interactions, and proof ceiling. Implementation's local method profile may narrow admission from
actual-path evidence and owns concrete code rules, but it cannot broaden the shared application.

## Architecture-Impact And Decision-Owner Gate

Set `status: local_implementation` and `decision_owner: implementation` when the choice changes
private control flow, types, layout, dispatch, effects, or scheduling inside one existing owner
without changing a public contract, canonical state/data owner, accepted architecture delta,
runtime integration, deployment, ABI, or trust boundary.

Set `status: architecture_material`, then select exactly one decision owner:

- `atomic_boundary` when one public/module/API/ABI boundary is the whole decision and its result can
  be expressed as one `boundary_decision` without coordinating another view or owner;
- `coupled_architecture` when the choice coordinates several module/API or owner boundaries,
  changes canonical state/data/effect ownership or a shared representation/publication contract,
  introduces a cross-owner executor/queue/scheduler/dependency/completion/cancellation model,
  changes a cross-owner shared-memory visibility/publication contract or canonical
  lifetime/reclamation contract, changes runtime extension, protocol, process/deployment, or trust
  topology, or changes an accepted application's cross-view interaction;
- `coupled_architecture` for an explicit subsystem/repository scope whose materially affected
  boundaries must be mapped together, even when the implementation language remains unchanged.

Implementation owns `local_implementation`. `analysis-boundary-design` owns `atomic_boundary`.
`workflow-architecture-design` owns `coupled_architecture`. A consumer must not skip this gate
because the paradigm/model was selected implicitly by the agent rather than explicitly by the
user.

## Composition And Authority

- Map each selected approach to one named property/owner and state where it stops. Combining
  approaches is not permission to duplicate state, policy, fallback, or publication ownership.
- Record pairwise conflicts across ABI, safety, compatibility, performance, lifecycle, extension,
  and deployment. Do not silently replace an explicit user selection with a nearby technique.
- Syntax is not evidence: functions do not prove procedural/functional meaning, classes do not
  prove object ownership, arrays do not prove DOD, templates do not prove appropriate static
  closure, `async` syntax does not prove non-blocking progress or structured lifetime, locks and
  atomics do not prove a protected invariant, and queues do not prove a Job System.
- Explicit user scope and supplied paradigm material are authoritative unless they conflict with a
  hard safety/security, language, ABI, framework, canonical-data, compatibility, or measured
  production constraint. Expose a material conflict instead of weakening either side.
- Without an explicit selection, preserve the coherent local model and introduce a new paradigm
  only when the requested behavior or evidenced constraint requires it.

## Evidence And Immutable Handoff

Architecture Design or Boundary Design may establish selection, owner, scope, interactions,
forbidden drift, and planned fitness from accepted requirements, intrinsic constraints, and
representative scenarios. An accepted application remains immutable authority; Implementation
never changes its evidence or status in place.

Implementation returns a downstream observation instead:

```yaml
paradigm_conformance:
  application_ref: <accepted architecture pattern application, atomic boundary decision, or task-local application id>
  implemented_slice:
  status: conformed | conflict | unverified
  actual_path:
  evidence_refs: []
  proof_ceiling:
```

Only the Architecture/Boundary owner may revise and re-accept its source decision. A matching test,
trace, benchmark, or readback may support `paradigm_conformance`, but it does not mutate the
accepted application or prove a broader runtime property than its thin profile allows.

## Consumer Responsibilities

- `workflow-architecture-design` consumes this contract only for
  `decision_owner: coupled_architecture`. It records the application in
  `architecture_design.pattern_applications`, loads only selected thin profiles, and leaves local
  code mechanics and detailed method profiles to Implementation.
- `analysis-boundary-design` owns `decision_owner: atomic_boundary` and may also consume a
  target-relevant accepted application as an immutable architecture constraint. It returns exactly
  one boundary decision, stores the selected profile/axis/property owner/scope/interactions,
  forbidden drift, and proof ceiling in its optional `paradigm_constraints`, and defers any
  axis/owner/scope/interaction/delta expansion to Architecture Design.
- `workflow-implementation` owns `decision_owner: implementation`, consumes accepted applications,
  or consumes accepted atomic `boundary_decision.paradigm_constraints`, and uses its local
  index/method profiles for concrete realization. Every new or changed material paradigm/model
  choice—explicit or agent-selected—passes through this gate. It returns `paradigm_conformance`
  against the accepted architecture or boundary reference rather than rewriting either decision.

## Stop Rule

Stop at the smallest application whose kind, owner, axis, minimum closure, maximum scope,
interactions, forbidden drift, decision owner, and proof ceiling are explicit. Do not load another
profile unless a second material axis or conflict can change the decision.
