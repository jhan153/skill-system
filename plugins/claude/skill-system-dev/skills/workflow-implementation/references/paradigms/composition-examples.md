# Paradigm Composition Examples

Apply `references/programming_paradigm_contract.md` and the selected shared thin profiles before this file.
This file owns concrete realization examples and implementation readback, not cross-stage selection
or architecture acceptance.

Load this file only when two or more approaches must be combined, or when applying one approach could violate another material boundary. Load the individual method files too; this file does not replace their implementation rules.

The goal is not a stylistic blend. Each approach should own a different, named property of the system.

## Composition Procedure

1. List the user-selected approaches without reducing them to one favorite.
2. Identify the actual production owners and representative caller-to-effect path.
3. Map each approach to state ownership, data representation, effect boundary, compile/runtime variability, or execution dependency.
4. State where each approach stops.
5. Check pairwise conflicts against ABI, safety, compatibility, performance, lifecycle, and extension requirements.
6. Implement the smallest boundary-complete combination.
7. Read back the code shape and test one disconfirming case that could pass a shallow behavior test while violating the requested design.

Use a compact map:

| Boundary | Selected method | Observable rule | Forbidden drift |
| --- | --- | --- | --- |
| document/session/resource | object-oriented | one identity/lifecycle/invariant owner | computation state hidden in a god object |
| deterministic calculation | functional | explicit values, visible direct composition, and effect-free semantic boundary | hidden I/O, ambient mutable inputs, or abstraction-only pipeline layers |
| algorithm pipeline | procedural | visible order, context, output, failure | giant global-state procedure |
| bulk storage/kernel | data-oriented | layout/ranges follow measured access | automatic ECS/SoA without evidence |
| static specialization | TMP | bounded compile-time facts only | runtime choices encoded in types |
| external progress | Structured Async | scoped readiness/completion, cancellation, backpressure, publication | blocking work hidden behind `async` syntax or detached lifetime |
| CPU execution | Job System | DAG, grain, access, completion | thread-pool callback mislabeled as Job graph |
| shared mutable state | Shared-Memory Concurrency | invariant, visibility, reclamation, progress | atomics or locks without an owned invariant |

## Graphics, Mesh, CAD, Or Simulation

| Boundary | Suitable composition |
| --- | --- |
| `MeshDocument`, edit session, GPU/file resource | object-oriented identity, invariant, and lifetime owner |
| import, solve, or frame orchestration | procedural ordering and explicit failure |
| geometry query or deterministic edit | functional input/output contract |
| repeated vertex, particle, residual, or instance path | data-oriented layout selected from actual field access |
| static scalar, coordinate frame, fixed layout, bounded SIMD policy | Concepts/`constexpr` or narrowly bounded TMP |
| independent compute stages | Job DAG around sequentially callable kernels and explicit resource access |

This is coherent because each approach governs a different property. It does not justify converting the whole application to ECS, making every algorithm a method, templating runtime editor state, or hiding scheduling inside the calculation kernel.

### Example execution path

```text
MeshDocument (object owner)
  snapshot mesh revision
        |
        v
MeshComputeView (data-oriented arrays/views)
        |
        +-> face-normal kernel (functional contract, procedural loop)
        +-> adjacency build (procedural stages)
        +-> vertex reduction (functional partials + fixed reduction)
                scheduled as Job DAG
        |
        v
MeshPatch(revision, result)
        |
        v
MeshDocument commit (object invariant + stale-version policy)
```

The Job System does not own mesh semantics. The data layout does not own document identity. The pure kernel does not perform commit or GPU upload.

## NURBS Editing

```text
NurbsCurve / NurbsSurface
  immutable valid mathematical value

evaluate / split / insertKnot
  functional public contract
  mutable local workspace permitted

ControlPointEditSession
  short-lived imperative/object state for interactive drag

DerivedGeometryCache
  revision + options keyed execution cache

CAD Document / B-rep
  identity, topology ownership, undo/redo, transactions
```

This composition avoids two extremes: a giant mutable curve object containing UI, cache, rendering, and history; or whole-value copying on every pointer-move event. Commit converts the mutable draft back into a valid value and lets the document own identity/history.

## Explicit Staged-Construction Boundary

Construction-validity remains the default. When file/network/device progress or large bulk work prevents atomic final-value creation, split ownership by concern instead of weakening the final type:

Before adding any custom request/builder/ticket, reuse an existing future, task, result, scheduler handle, platform request, span, output iterator, or staging buffer when it already owns the required progress and lifetime. The table names semantic roles, not mandatory new classes; combine roles in one existing primitive when that is simpler and complete.

| Concern | Example owner/style |
| --- | --- |
| resource lifetime | valid `FileHandle`, socket handle, or GPU allocation owner |
| progress and state transition | procedural `ReadRequest`, `ConnectionAttempt`, `DecodeSession`, or `UploadTicket` |
| large writable storage/ranges | data-oriented `BufferBuilder` or staging buffer |
| external readiness/completion | Structured Async scope, event loop, completion runtime, or bounded blocking adapter |
| CPU dependency/completion | Job scope/handle with explicit access and completion semantics |
| shared publication/reclamation | Shared-Memory Concurrency contract only when state is actually shared |
| final publication | one validated `finish`/`commit`/`freeze` returning final value or typed failure |

```text
openFile -> FileHandle
              |
          beginRead
              v
ReadRequest(Pending/Failed/Cancelled/Completed)
              |
       fill BufferBuilder ranges
              |
      finish + coverage validation
              v
          ByteBuffer
```

`FileHandle`, `ReadRequest`, and `BufferBuilder` are each valid for the state named by their type. `ByteBuffer` does not exist as a public final value until the operation succeeds. The same separation applies to `ConnectionAttempt -> Connection`, `DecodeSession -> Image`, and `UploadTicket -> ReadyGpuResource`.

This exception is invalid when it only avoids constructor validation, preserves a setter/init protocol, or hides defaulting/fallback behind a background task.

## Data-Oriented Work With A Job System

The two approaches complement but do not imply one another.

1. DOD identifies arrays, access patterns, batch/range boundaries, and partial-result buffers.
2. The Job System schedules those ranges using explicit prerequisites and read/write declarations.
3. Functional/procedural kernels define the computation inside each range.
4. An object/session owner controls snapshots, cancellation, and commit.
5. Shared-Memory Concurrency is added only when partitions still overlap, publish across workers, or
   coordinate reclamation; a Job dependency alone is not a memory-visibility proof.

```text
Position[] + Velocity[] -> Integrate chunks
CellId[]                 -> Sort/bin chunks
Bins                     -> Neighbor-force chunks
PartialForce[]           -> deterministic reduction
```

Reject the combination when the work is too small, sequential, dominated by I/O, or unpartitionable. DOD may still be useful without scheduling; a Job System may schedule coarse object-owned operations without changing their internal layout.

## Static Versus Runtime Extension

- A fixed vertex layout or small build-time SIMD policy set can use compile-time specialization.
- A runtime-loaded plugin, user-selected backend, or data-defined schema remains a runtime problem. Prefer an ordinary value, direct dispatch, function table, composition, or closed variant; use interface/type erasure/registry only for actual current open substitution with an identical full contract and no direct alternative.
- A non-template ABI facade may call a small explicitly instantiated template core.
- Do not replace runtime openness with a closed template list without acknowledging deployment, code-size, and ABI consequences.

```text
direct selector / function table / variant   runtime choice
        |
        v
Backend implementation
  Kernel<float, SoA, AVX2>              bounded static specialization
```

Exceptional object polymorphism and TMP can coexist when they solve different extension times, but an external boundary alone does not justify either extra layer.

## Ordered Pipeline With Functional Kernels

An import, processing, or frame path often benefits from procedural orchestration plus functional calculation:

```cpp
Result processAsset(const Request& request, Services& services) {
    Bytes bytes = services.files.read(request.path);       // effect
    Asset parsed = parse(bytes, request.format);            // functional
    Asset normalized = normalize(parsed, request.policy);   // functional
    Validation report = validate(normalized);               // functional
    if (!report.ok()) return report.error();
    return services.store.write(request.output, normalized); // effect
}
```

The procedure makes order and early failure obvious. The kernels remain reusable and deterministic. The service object owns external effects and lifetime.

## Conflict Handling Examples

### Object-oriented request versus packed hot path

Determine whether “object-oriented” means:

- encapsulate the buffer/resource owner;
- provide a stable domain API;
- introduce runtime strategy substitution; or
- allocate one polymorphic object per element.

The first three can preserve a packed kernel. The last may contradict an accepted memory/latency contract. Do not silently move the user's request to another boundary; show the conflict and ask when those interpretations lead to different deliverables.

### Functional request versus interactive editing

Keep committed geometry values and calculations functional, but use a short-lived mutable draft for high-frequency drag updates. If the user explicitly requires persistent immutable editing data structures, that is a separate concrete constraint and must not be silently replaced by the draft design.

### DOD request versus ECS

For a fixed particle schema, choose layout from the update passes. ECS is justified only if independent entity identity, variable composition, and recurring component queries are also required.

### Job System request versus one callback

If the task has one independent background operation, use the existing asynchronous executor or
thread pool unless the user explicitly wants Job System infrastructure. If the operation owns
readiness/completion, cancellation, queue pressure, or a child lifetime, apply Structured Async;
otherwise do not manufacture either model. A dependency-aware DAG, completion scope, and
resource-access model should correspond to a graph-shaped CPU requirement.

### Async request versus CPU parallelism

An `async` API does not make a CPU-bound loop parallel. Keep external progress and request lifetime
under Structured Async, then hand ready bulk computation to DOD/Job kernels only when the workload
and dependency graph require them. Do not block event-loop callbacks on CPU jobs or occupy CPU Job
workers with file/network waits.

### Disjoint ranges versus shared-memory safety

Disjoint logical indexes can still share an invariant, reclamation protocol, reduction order, or
cache line. Load Shared-Memory Concurrency only for those remaining properties. Do not add locks to
immutable snapshots or owner-exclusive ranges that already commit through one canonical owner.

### TMP request versus runtime plugin

Explain that compile-time closed combinations cannot provide arbitrary runtime-loaded implementations. A stable concrete C API, function table, or—only under the rare gate—plugin interface can call templated internals, but discovery/substitution remains runtime.

## Regression Cases

### Positive: Requested Composition

Task: implement bulk mesh processing using data-oriented storage, functional kernels, and a Job System while retaining resource owners as objects.

Expected behavior:

- load only the four implicated method references plus this composition file;
- map each approach to its boundary before coding;
- retain object ownership for document and resource lifetime;
- expose deterministic kernels with explicit inputs and outputs;
- select layout from fields used by the representative bulk pass;
- schedule chunks and dependencies around sequentially callable kernels;
- define versioned snapshot/commit and shared-write/reduction behavior;
- validate both the result and requested boundary shape.

### Edge: Explicit Approach Meets A Production Constraint

Task: make a measured packed vertex hot path object-oriented.

Expected behavior:

- identify the exact requested object property;
- inspect the accepted workload and memory/latency contract;
- preserve the explicit request wherever compatible;
- show the exact conflict if per-element identity/virtual dispatch violates the contract;
- obtain the decision rather than silently retaining the old design or silently weakening the requested paradigm.

### Negative: Trivial Local Edit

Task: change one label literal while preserving its handler and ownership.

Expected behavior: follow the existing local shape and make the bounded edit. Do not load the paradigm index, create a boundary map, or add abstractions.

### Negative: Category Substitution

Task: use data-oriented design for a fixed particle update.

Expected behavior: load only the DOD file; choose a layout from update access; do not introduce ECS automatically.

Task: make runtime-loadable plugins use template metaprogramming.

Expected behavior: load TMP and this composition file; expose the compile-time/open-runtime mismatch and ABI consequence.

Task: introduce a Job System for one independent background callback.

Expected behavior: load the Job file; distinguish a simple executor from dependency-aware jobs and do not manufacture a graph requirement.

Task: mark a blocking file call `async` while leaving it on the event-loop thread.

Expected behavior: load Structured Async; expose the actual blocking carrier and move it behind an
existing bounded adapter or keep the call synchronous. Syntax alone cannot satisfy the profile.

Task: protect independent immutable snapshots with a global mutex.

Expected behavior: do not load or apply Shared-Memory Concurrency merely because several threads
read the values; preserve the simpler immutable ownership contract.

### Positive: Explicit Staged Construction

Task: asynchronously read and decode a large file into a buffer using disjoint worker ranges.

Expected behavior:

- create a valid file/resource handle or typed open failure;
- represent read/decode progress with an explicit request/session state machine;
- fill a separately typed builder/staging buffer with explicit range coverage;
- expose failure and cancellation as terminal outcomes;
- publish the final buffer only after completion, coverage, and invariant validation;
- avoid a default-constructed final buffer whose method legality changes behind `ready_`.

### Negative: Functional Abstraction Theater

Task: implement a small deterministic mesh-coordinate normalization functionally.

Expected behavior:

- expose explicit input, policy, valid result, and typed failure where material;
- keep the representative `validate -> transform -> result` flow directly visible;
- use a plain function, value type, and direct loop/local builder where sufficient;
- do not introduce `IStage`, stage factories, registries, wrapper objects, a generic pipeline framework, or one-line forwarding functions;
- extract a stage only when it owns a real domain transformation, invariant, policy, or failure boundary;
- do not apply DRY across coordinate rules that are only syntactically similar but semantically distinct;
- check that functional syntax did not add avoidable intermediate allocation, copying, capture, or dispatch.

## Composition Verification

- Every selected method owns a named boundary and observable property.
- No method is used merely as a repository-wide label.
- Overlap and conflict decisions are explicit.
- The implementation preserves the user's stated scope rather than narrowing it for convenience.
- Non-applicable methods remain absent from unrelated paths.
- Tests/readback cover code shape as well as functional output when shape is a material requirement.
- Functional composition keeps the representative value flow visible and contains no abstraction-only stage, wrapper, interface, or combinator without a current semantic reason.
- Final domain/resource values are valid at construction; every staged exception has a separate valid operation type and a single verified publication boundary.
- Existing runtime primitives are reused before any staged type is added, and every interface/type-erasure/registry satisfies the rare current-substitution gate.
- One disconfirming case checks for a shallow pass that violates the requested composition.
