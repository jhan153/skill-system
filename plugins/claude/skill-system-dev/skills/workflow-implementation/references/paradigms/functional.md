# Functional Implementation

Cross-stage selection authority lives in `references/programming-paradigms/functional.md`. This file owns
concrete realization and actual-path verification; it may narrow implementation admission from
production evidence but never broadens the accepted trigger or scope.

Use a functional boundary for deterministic calculations, value transformations, reducers, rules, and state transitions that benefit from explicit inputs, outputs, and isolated effects. The practical target is usually **observable purity at a useful boundary**, not ideological elimination of every local mutation.

## Core Model

A functional implementation makes these relationships easy to reason about:

- semantic inputs determine semantic outputs;
- hidden mutable globals are not undeclared inputs;
- effects are named and moved to an outer shell;
- state change is represented as a transition rather than scattered mutation;
- independent transformations can be composed, replayed, cached, tested, and scheduled.

```text
Functional core
    values -> calculation -> values

Imperative shell
    I/O -> snapshot -> core -> commit/upload/persist
```

The shell is not a failure of functional design. It is where unavoidable effects obtain an explicit owner.

## Strong Signals

- The same input and policy should produce the same result.
- The operation is naturally `input -> output`, `collection -> reduction`, or `old state + event -> new state`.
- Parallel execution benefits from eliminating hidden aliasing and shared writes.
- Replay, undo, memoization, deterministic tests, or caching need stable values.
- A domain value such as a transform, curve, matrix, query, or rule can be complete without identity.
- I/O, time, randomness, database, UI, or GPU effects can be injected or isolated.

## Observable Implementation Contract

### Pure query or transformation

```cpp
CurveJet evaluate(
    const NurbsCurve& curve,
    double parameter,
    int derivativeOrder);

std::expected<NurbsCurve, InsertKnotError> insertKnot(
    const NurbsCurve& source,
    double parameter,
    int multiplicity);
```

The call exposes its semantic input and returns its result or typed failure. It does not require the caller to set hidden fields in a particular order.

### Explicit state transition

```cpp
EditorState reduce(
    const EditorState& previous,
    const EditorEvent& event);
```

This makes transition inputs and outcomes inspectable. It is useful when replay, history, deterministic state tests, or snapshot isolation matters. A stateful object can still wrap the reducer when event addressing or lifecycle is the outer concern.

### Effect boundary

Keep external effects outside the calculation:

```cpp
MeshBytes bytes = fileSystem.read(path);          // effect
MeshData mesh = parseMesh(bytes, options);        // deterministic core
MeshData processed = simplify(mesh, policy);      // deterministic core
fileSystem.write(outputPath, encode(processed));  // effect
```

The core may accept explicit policies, random seeds, time values, or service results as data when those influence semantics.

### Typed approximation and partial results

Numerical or geometric operations often need more than a value:

```cpp
struct ApproximationReport {
    double maximumDeviation;
    double rmsDeviation;
    int iterations;
    bool converged;
};

struct CurveApproximation {
    NurbsCurve result;
    ApproximationReport report;
    ParameterMap parameterMap;
};
```

Returning the report keeps convergence, error, and mapping in the semantic contract rather than hidden in mutable processor state.

## Controlled Internal Mutation

An observationally pure API may use mutation internally for performance:

```cpp
std::expected<NurbsCurve, InsertKnotError> insertKnot(
    const NurbsCurve& source,
    double parameter,
    int multiplicity)
{
    MutableNurbsBuilder working = cloneToBuilder(source);
    working.insertKnotInPlace(parameter, multiplicity);
    working.recomputeAffectedControlPoints();
    return working.freeze();
}
```

The mutation is local, does not escape before a valid result exists, and does not change the source. This is often clearer and cheaper than forcing a persistent immutable collection for every intermediate array.

## NURBS And Editing Boundaries

A useful hybrid for geometry editing is:

- `NurbsCurve`/`NurbsSurface`: always-valid mathematical values;
- evaluation and exact edits: pure queries or value-to-value operations;
- fitting, reduction, removal, offset, or intersection: result plus error/convergence report;
- evaluation scratch: caller-owned or thread-local workspace that does not affect meaning;
- derived caches: external cache keyed by geometry revision and options;
- interactive CV drag: short-lived mutable edit session, committed to a new value;
- `MeshDocument`, B-rep topology identity, undo/redo, UI, files, and GPU: imperative or object-owning shell.

This separation prevents a logically const curve from hiding locks and mutable caches while allowing efficient editing and evaluation.

## Cache And Workspace Rules

Separate semantic state from execution resources:

```cpp
struct CurveEvaluationWorkspace {
    std::vector<double> basis;
    std::vector<double> derivatives;
    int lastSpan = -1;
};
```

If changing a workspace changes the mathematical result, it is not merely workspace and must become a semantic input. Cache keys should include every value that affects the derived result: geometry revision, tolerance, tessellation options, coordinate system, and similar policies.

## Direct Composition, Not Abstraction Layers

Function composition means connecting semantic value transformations so the dataflow remains visible. It does not mean maximizing the number of functions, combinators, wrappers, or pipeline objects.

Prefer a direct flow:

```cpp
std::expected<Asset, ProcessError> processAsset(
    ByteSpan bytes,
    const ProcessPolicy& policy)
{
    Asset parsed = TRY(parse(bytes));
    TRY(validate(parsed, policy.validation));
    Asset normalized = normalize(std::move(parsed), policy.coordinates);
    return optimize(std::move(normalized), policy.optimization);
}
```

The stages are justified because parsing, validation, coordinate normalization, and optimization have distinct semantic inputs, failures, or policies. Their order is still visible in one representative caller.

Reject abstraction theater such as an `IStage` implementation, factory, registry, wrapper object, or generic pipeline builder for every one-line transformation when no current substitution or repeated semantic structure exists. A plain function, value type, local struct, loop, or direct branch is the default.

Admit a functional abstraction only when it satisfies a present condition:

- it names a real domain transformation, invariant, effect, or failure boundary;
- the same semantic operation is currently reused and changes for the same reasons;
- a generic combinator represents a recurring algebra/effect model rather than hiding ordinary control flow;
- it reduces the total number of states, branches, ownership rules, or duplicated semantic policies;
- its allocation, capture, temporary-materialization, dispatch, and debugging costs are understood and acceptable.

Do not apply DRY to textual similarity alone. Two short functions that look alike but encode different domain rules should remain separate; one abstraction that requires flags or callbacks to recover those differences is usually less functional because it obscures meaning.

Do not split a coherent calculation merely to satisfy “one function does one thing” or a preferred line count. A direct loop may be the clearest functional kernel when its semantic input/output boundary is pure. Avoid intermediate collections and copy-heavy chains when one bounded pass expresses the same transformation more directly.

## Composition Rules

- Put a **procedural** loop or mutable builder behind a pure public boundary.
- Put the functional core inside an **object-oriented** document, session, or resource shell.
- Use **data-oriented** arrays and SIMD internally when a value transformation runs over bulk data.
- Let a **Job System** schedule pure/range-disjoint kernels and combine partial results deterministically where required.
- Use **TMP** for static dimensions, coordinate frames, scalar types, or expression composition only when those are compile-time facts.

## Misapplications

- Copying an entire large graph for every tiny edit without a measured or semantic reason.
- Building an `IStage`/factory/registry/pipeline hierarchy around a fixed sequence of direct value transformations.
- Splitting a coherent calculation into one-line forwarding functions until control flow is scattered across files.
- Introducing generic combinators, wrapper result types, or DSL syntax without a recurring present semantic/effect model.
- Applying DRY to syntactically similar but semantically different rules and recovering the differences through flags or callbacks.
- Hiding allocations, captures, intermediate collections, or repeated copies behind fluent functional syntax.
- Treating recursion, `map`, or immutable syntax as proof of purity while effects remain hidden.
- Hiding I/O inside a function that appears deterministic.
- Using mutable global caches whose keys omit semantic inputs.
- Forcing resource lifetime, UI event capture, or runtime plugin identity into value transformations.
- Assuming floating-point parallel reduction is deterministic without fixing partition and reduction order.

## Implementation Verification

- Semantic inputs and outputs are explicit.
- The representative value flow is visible without traversing abstraction-only wrappers; each extracted stage owns a domain transformation, policy, invariant, or failure boundary.
- Every interface, pipeline object, or generic combinator has a current semantic reuse/effect reason and reduces total conceptual machinery rather than only moving code.
- Effects, randomness, time, I/O, and external services have named boundaries.
- Local mutation cannot leak an invalid or partially committed result.
- Workspace and caches do not change meaning unless represented in the contract.
- Error, approximation, convergence, and parameter mapping are returned when material.
- The negative case—identity/lifecycle/effect ownership—remains in an appropriate shell.
- A representative repeated call with the same semantic input has the promised determinism, including reduction-order constraints where applicable.
- A direct function/loop alternative was considered, and no avoidable intermediate allocation, copy, dispatch, or indirection remains on the representative path.
