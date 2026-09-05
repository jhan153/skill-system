# Implementation Paradigm Method Index

Apply `programming_paradigm_contract.md` first whenever paradigm selection, scope, composition, or
architecture impact is material. That shared contract owns the cross-stage meanings, application
record, architecture-impact gate, thin selection profiles, authority, and proof ceilings.

This file owns only progressive loading of Implementation's detailed method profiles. Those
profiles define concrete code rules, language/runtime mechanics, examples, misapplications, and
actual-path verification after the paradigm boundary is selected.

Where a method profile repeats selection language, the shared contract is authoritative for
cross-stage trigger, non-trigger, minimum closure, maximum scope, architecture impact, and proof
ceiling. A method profile may narrow implementation admission from actual-path evidence but cannot
broaden the accepted application.

## Progressive Loading

Read only the files implicated by the accepted paradigm application, a user- or agent-selected
local choice, and the actual production path.

| Task signal | Shared selection profile | Implementation method |
| --- | --- | --- |
| ordered algorithm, explicit pipeline, state machine, C ABI/FFI/callback | `programming-paradigms/procedural.md` | `paradigms/procedural.md` |
| identity, invariant, lifecycle, resource owner, runtime substitution | `programming-paradigms/object-oriented.md` | `paradigms/object-oriented.md` |
| deterministic value transformation, reducer, pure core, effect isolation | `programming-paradigms/functional.md` | `paradigms/functional.md` |
| bulk processing, memory layout, SIMD/GPU, ECS question, measured hot path | `programming-paradigms/data-oriented.md` | `paradigms/data-oriented.md` |
| compile-time types, static invariants, closed policy combinations, TMP | `programming-paradigms/template-metaprogramming.md` | `paradigms/template-metaprogramming.md` |
| file/network/device/timer/process progress, readiness/completion, structured task lifetime | `programming-paradigms/structured-async.md` | `paradigms/structured-async.md` |
| task DAG, CPU work decomposition, dependency scheduling, Job System | `programming-paradigms/job-system.md` | `paradigms/job-system.md` |
| shared mutable invariant, publication/visibility, locks/atomics, reclamation | `programming-paradigms/shared-memory-concurrency.md` | `paradigms/shared-memory-concurrency.md` |
| GPU progress, streaming input plus CPU transform, large parallel fill, or another staged-construction exception | selected state/data/execution profiles | start with `paradigms/composition-examples.md`, then load only the method files that own the unresolved decision |
| two or more approaches must be combined, or their boundaries conflict | only the material axis profiles | `paradigms/composition-examples.md` plus only the named method files |

Do not load every profile for a routine implementation. If the user names one approach, start with
that file. If production evidence introduces a second material axis, load that second file and the
composition examples. Stop when the code realization and one disconfirming case are decidable.

## Implementation Handoff

- Treat an accepted architecture `pattern_application` with either
  `kind: programming_paradigm` or `kind: adjacent_implementation_model` as a binding
  owner/axis/scope/interaction contract. Do not reselect, mutate, or broaden it while coding.
- Treat accepted `boundary_decision.paradigm_constraints` as the equivalent binding source for an
  `atomic_boundary` choice; cite that boundary decision as `application_ref` in the downstream
  `paradigm_conformance` observation.
- Apply the shared impact/decision-owner gate to every new or changed material choice, whether
  user-explicit or agent-selected, before loading method details. Keep only
  `decision_owner: implementation`; route `atomic_boundary` to `analysis-boundary-design` and
  `coupled_architecture` to `workflow-architecture-design`.
- Without an explicit or accepted choice, preserve the coherent local model. Do not create a
  paradigm discussion for an already-shaped trivial edit.
- If concrete evidence conflicts with an accepted axis, owner, maximum scope, cross-view
  interaction, or architecture delta, stop only the dependent implementation and return the
  conflict to the accepted decision owner. Do not manufacture or rewrite an architecture/boundary
  artifact inside Implementation.
- Translate the selected application into observable code rules for state/identity ownership,
  inputs/outputs/failures, mutation/effects, construction/publication, data layout,
  dispatch/specialization, and execution dependencies only where material.

## Method-Profile Proof Boundary

The detailed profiles may close concrete source shape and actual-path behavior for the implemented
slice. They never modify an accepted application or silently upgrade its planned fitness. Return a
separate `paradigm_conformance` observation with only the matching test, trace, benchmark, or
readback and preserve every profile-specific proof ceiling from the shared contract.

Return the accepted application reference or task-local application, loaded method profiles,
observable code rules, forbidden drift, `paradigm_conformance`, and unresolved owner conflict only
inside the owning Implementation output. This index creates no separate architecture artifact or
workflow transition.

## Direct And Core Result Projection

Direct work can return `paradigm_conformance` in the ordinary Implementation output. For a
graph/cross-owner `implementation_result`, keep the Core payload unchanged and project the same
facts into its existing fields:

| Observation | Existing Core location |
| --- | --- |
| Accepted application and implemented scope | `artifact_refs` for an existing accepted design/boundary artifact; `scope_ref` and bounded condition text identify the applied scope. |
| Implemented/source-read shape | `implemented_conditions`, with its exact source/evidence refs and proof limit. |
| Required behavior not observed or an unresolved conflict | `unresolved_conditions`; never list it as verified because the source shape matches. |
| Detailed conformance readback, when already present | `evidence_refs` to the existing artifact's exact section; otherwise keep the necessary facts inline in the condition entries. |

The following illustrative mapping assumes the named design and source exist in the receiving
task; it is not evidence that this repository contains or executed that example. Replace every
identity/ref with actual task data. It preserves a source-shape observation while leaving the
independent-scratch result condition unverified:

```json
{
  "contract_id": "core-execution-items-v1",
  "item_id": "EI-normalize-C0",
  "kind": "implementation_result",
  "producer": "skill-system-dev:workflow-implementation",
  "plan_ref": "normalize-plan@1",
  "node_id": "C0",
  "scope_ref": "PA-1 normalization slice",
  "artifact_refs": ["design.md#PA-1", "src/normalize.cpp"],
  "evidence_refs": ["src/normalize.cpp#normalize"],
  "payload": {
    "implementation_snapshot": "current reviewed worktree diff",
    "changed_artifacts": ["src/normalize.cpp"],
    "implemented_conditions": ["PA-1/P-SHAPE: inputs and policy are explicit; source readback only"],
    "review_slice": "normalize entry and workspace path",
    "unresolved_conditions": ["PA-1/P-RESULT: equivalent output with fresh and reused scratch is unverified; no matching execution observation"]
  }
}
```

Do not add unsupported payload fields, invent a conformance artifact to fit the example, or copy
the accepted application's status into an observed-result claim. A detailed observation remains
subordinate to its accepted application; this projection adds no Plan transition or new record type.
