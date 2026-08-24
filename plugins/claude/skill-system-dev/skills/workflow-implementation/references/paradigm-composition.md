# Implementation Paradigm Composition Index

Use this index only when the user names or supplies research about a programming paradigm or adjacent implementation model, asks to combine approaches, or when the implementation choice would materially change state ownership, data layout, side-effect boundaries, dispatch, specialization, or concurrency. It is not a reason to debate architecture during an already-shaped trivial edit.

## Progressive Loading

Read this index first, then load only the files implicated by the request and actual production path.

| Task signal | Load |
| --- | --- |
| ordered algorithm, explicit pipeline, state machine, C ABI/FFI/callback | `paradigms/procedural.md` |
| identity, invariant, lifecycle, resource owner, runtime substitution | `paradigms/object-oriented.md` |
| deterministic value transformation, reducer, pure core, effect isolation | `paradigms/functional.md` |
| bulk processing, memory layout, SIMD/GPU, ECS question, measured hot path | `paradigms/data-oriented.md` |
| compile-time types, static invariants, closed policy combinations, TMP | `paradigms/template-metaprogramming.md` |
| task DAG, CPU work decomposition, dependency scheduling, Job System | `paradigms/job-system.md` |
| file/network/GPU progress, streaming input, large parallel fill, or another staged-construction exception | start with `paradigms/composition-examples.md`, then load only the one method file that owns the unresolved state/data/execution decision; load object-oriented only when identity/lifetime/invariant ownership is material |
| two or more approaches must be combined, or their boundaries conflict | `paradigms/composition-examples.md` plus only the named approach files |

Do not load every paradigm file to make a routine implementation decision. If the user names one approach, start with that file. If production evidence introduces a second material axis, load that second file and the composition examples. Stop when the boundary map is decidable.

## Core Rule

An implementation does not need one repository-wide paradigm. Select and compose approaches at the smallest boundary that owns the property they govern.

Boundary-specific composition is not permission to narrow an explicit user scope. If the user selected an approach for a module, subsystem, or repository, map every materially affected boundary in that stated scope and preserve the selection wherever it is compatible.

Treat these as different, composable axes rather than one mutually exclusive list:

| Axis | Examples | Governing question |
| --- | --- | --- |
| Runtime computation and state | procedural, object-oriented, functional | How are control flow, identity, state, mutation, and effects represented? |
| Data representation and access | data-oriented layout, packed AoS, SoA/AoSoA, ECS | What data is processed together, how often, and in what memory/access order? |
| Compile-time specialization | generic programming, `constexpr`, Concepts, template metaprogramming | Which types, invariants, layouts, or closed policy combinations must be decided before runtime? |
| Execution architecture | Job System, task DAG, pipelines, actors | How are independent work, dependencies, scheduling, completion, and cancellation represented? |

`ECS` is one possible data/runtime architecture, not a synonym for data-oriented design. A Job System is an execution architecture, not another alternative to object-oriented or functional programming. Template metaprogramming operates at compile time and does not determine the whole runtime model.

Construction validity crosses these axes: a final domain/resource value is valid when created, while unavoidable external or bulk progress is modeled as a separate valid staged operation. Do not relax the final type's invariant merely because the work is better executed procedurally, over data-oriented buffers, or through a Job/event system.

## Authority And Conflict

1. Capture the user's exact words and any user-supplied paradigm material. Do not replace an explicit technique with a nearby alternative because the alternative is more familiar.
2. Inspect the actual production owner, representative caller-to-output path, and the local contracts that constrain the choice.
3. Translate the selected approach into observable code rules. A label alone is not an implementation contract.
4. If a hard safety/security, language, ABI, framework, canonical-data, compatibility, or measured performance constraint contradicts the requested shape, state the exact collision and ask for the decision when it would change the deliverable. Do not silently weaken either side.
5. If there is no conflict, user intent outranks agent taste. Existing patterns guide unspecified details but do not cancel an explicit user choice.
6. If the user did not choose an approach, preserve the coherent local model. Introduce a new paradigm only when the requested behavior or an evidenced production constraint requires it.

Do not silently reinterpret a broad request such as “make it object-oriented” as “add one manager class,” or “make it functional” as “ban every local mutation.” Determine which boundary and observable properties the user means from supplied context; ask only when materially different interpretations remain.

## Boundary Map

For a material choice, make this map internally before editing. Report it only when it helps the user verify the outcome.

| Boundary | Problem evidence | Selected approach | Observable implementation rules | Forbidden drift |
| --- | --- | --- | --- | --- |
| named production owner/path | identity, invariants, transformation, access pattern, static variability, dependency graph, or explicit user choice | one or more approaches | state owner; mutation/effect location; data layout; dispatch/specialization; execution dependencies | one realistic way the implementation could violate the choice while still compiling or passing a shallow test |

Answer only the dimensions material to the task:

- Who owns long-lived state and invariants?
- Is the core operation an ordered procedure, an object collaboration, or an input-to-output value transformation?
- Where may mutation and external side effects occur?
- Which data is read or written together on the representative path?
- Is variability open and runtime-driven, or small, closed, and compile-time-known?
- Does concurrency require a dependency graph and completion semantics, or merely one asynchronous call?
- Does construction produce a final valid value, or does an evidenced staged-operation exception own progress and the only final-value publication boundary?
- Where does each selected approach stop so it does not spread into unrelated code?
