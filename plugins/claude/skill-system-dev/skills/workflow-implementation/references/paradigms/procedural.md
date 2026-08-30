# Procedural Implementation

Cross-stage selection authority lives in `references/programming-paradigms/procedural.md`. This file owns
concrete realization and actual-path verification; it may narrow implementation admission from
production evidence but never broadens the accepted trigger or scope.

Use a procedural boundary when the behavior is primarily an explicit sequence of transformations rather than a long-lived identity collaborating with other identities. The important question is not whether the language offers classes; it is whether the module's meaning is best expressed as `input -> ordered work -> output`.

## Selection Strength

Distinguish three reasons for choosing this model.

1. **Externally required**: C ABI, FFI, callbacks, shader/kernel entry points, interrupts, plugin entry points, or a framework-prescribed function signature determine the public shape.
2. **Strongly suitable**: numerical methods, geometry/mesh operations, codecs, parsers, image/signal processing, state machines, and real-time kernels are governed by data transformation and execution order.
3. **Sufficiently simple**: a bounded transaction, migration, converter, build tool, or one-shot automation has no domain value in a larger object model.

Do not treat the third category as permanent. A simple transaction that accumulates shared invariants and complex state transitions may need a stronger domain owner later.

## Decision Questions

- Are input, output, parameters, failure, and intermediate state enumerable?
- Is the meaningful behavior a finite transformation or ordered pipeline?
- Is there no identity that must survive across calls independently of its current value?
- Is the data schema relatively stable while new operations are likely to be added?
- Must allocation, blocking, loop bounds, or control flow remain explicit?
- Would a class contain little more than setters followed by one `run()` call?

Several positive answers favor a procedural module. Identity, resource ownership, or guarded invariants favor an object boundary instead.

## Observable Implementation Contract

### Make dataflow explicit

Prefer signatures that expose semantic inputs, mutable context, workspace, output, and failure:

```cpp
struct SimplifyOptions {
    double targetRatio;
    bool preserveBoundary;
};

struct SimplifyScratch {
    std::vector<int> heap;
    std::vector<double> errorMetrics;
};

SimplifyResult simplifyMesh(
    MeshView input,
    const SimplifyOptions& options,
    SimplifyScratch& scratch,
    MeshData& output);
```

Avoid hidden current-object pointers, ambient configuration, or an implicit last result when those values are part of the computation contract.

### Separate orchestration from kernels

The orchestration layer should reveal meaningful order, while each kernel should have a bounded responsibility:

```cpp
ImportResult importMesh(Path path, const ImportOptions& options) {
    MeshBytes bytes = readFile(path);
    MeshData mesh = parseMesh(bytes, options.format);
    transformCoordinateSystem(mesh, options.coordinates);
    validateIndices(mesh);
    weldVertices(mesh, options.weldTolerance);
    computeMissingNormals(mesh);
    return finalizeImport(std::move(mesh));
}
```

This is clearer than hiding the entire pipeline inside a stateful processor whose valid call sequence is undocumented. Lower kernels may use loops and in-place buffers while remaining independently testable.

### Make repeated state a context, not a global

```cpp
struct DecoderContext {
    BitReader reader;
    HuffmanTable table;
    DecoderScratch scratch;
};

DecodeStatus decodeFrame(
    DecoderContext& context,
    ByteSpan input,
    ImageBuffer& output);
```

A named context supports multiple instances, reentrancy, test isolation, and explicit concurrency. It does not need to expose its representation publicly; an opaque handle can preserve a procedural ABI and encapsulation simultaneously.

### Expose mutation, allocation, and failure policy

Use names or signatures that distinguish value-returning, in-place, and output-buffer operations:

```cpp
MeshData transformed(MeshView input, const Matrix4& matrix);
void transformInPlace(MeshData& mesh, const Matrix4& matrix);
void transformInto(MeshView input, const Matrix4& matrix, MeshData& output);
```

Prefer meaningful result/error types over a bare `bool` when callers must branch on failure. In bounded real-time paths, expose scratch capacity, allocation policy, blocking restrictions, and partial-success rules.

### Represent a real state machine explicitly

When transitions are the problem, name states, inputs, guards, and effects rather than spreading flags across callers:

```cpp
TransitionResult handleEvent(
    InteractionState& state,
    const PointerEvent& event,
    InteractionEffects& effects);
```

An explicit procedural state machine can be preferable to a class when transition completeness and order are more important than instance polymorphism. A class may still own the state when identity or event addressing is material.

### Route staged construction through an explicit procedure/context

File/network reads, streaming decode, large materialization, and similar work should not force a final object to exist before its data is ready. Model the operation and its final publication separately:

```cpp
ReadRequest beginRead(FileHandle& file, ByteRange range);
ReadProgress poll(ReadRequest& request);
std::expected<ByteBuffer, ReadError> finish(ReadRequest&& request);
```

The request/context is a valid procedural state machine. The `ByteBuffer` final value does not exist until `finish` succeeds. Apply the same shape to `ConnectionAttempt -> Connection`, `DecodeSession -> Image`, or `BufferBuilder -> ImmutableBuffer`.

These names describe roles, not mandatory new classes. Reuse the existing future, task, result, platform request, decoder context, span/output iterator, or scheduler handle when it already expresses the required states and lifetime. Add a new type only for a real invariant, legal-state set, cancellation/cleanup rule, or publication boundary that the existing primitive cannot express.

The procedure must expose pending/completed/failed/cancelled states, prevent final publication after incomplete coverage, and keep retry/default/fallback policy out of incidental helpers. A staged context is not permission to pass a partially initialized final object through several functions.

## Typical Boundaries

- numerical kernels: decomposition, solvers, fitting, residual/Jacobian evaluation;
- geometry: normals, smoothing, subdivision, intersection tests, resampling, voxelization;
- images/signals: convolution, filtering, histograms, encoders and decoders;
- parsers and protocol state machines;
- shaders, GPU kernels, C ABI adapters, and callbacks;
- import/export and asset-processing pipelines;
- explicit file/network/streaming/bulk staged operations that publish a final value only at completion;
- deterministic command-line transformations and migrations.

## Composition Rules

- Pair with **functional** when the public contract should be deterministic and value-oriented while the kernel mutates local buffers efficiently.
- Pair with **data-oriented** when the procedure repeatedly traverses bulk data and layout affects cost.
- Place behind an **object-oriented** owner when the surrounding resource, session, or document has identity and lifecycle.
- Wrap kernels in a **Job System** only after independent ranges, dependencies, and grain are identified.
- Pair with a **data-oriented** builder for large disjoint-range fills and publish the final buffer only after coverage/commit succeeds.
- Use **TMP** only for genuinely static types or policies inside the kernel, not to encode runtime pipeline state.

## Misapplications

Procedural does not mean global variables, a giant function, `goto`, missing encapsulation, or unrestricted mutation. A C-style public API does not force the internal core to use the same paradigm. A stateful utility class with only static methods is still effectively procedural and should not be treated as object-oriented evidence.

Stop treating the module as primarily procedural when:

- invalid states and shared invariants dominate many operations;
- resource acquisition/release or identity across events is central;
- runtime substitution among growing implementation kinds is required;
- transaction scripts duplicate the same business rules across entry points.

## Implementation Verification

- The meaningful order is visible at the orchestration boundary.
- Inputs, outputs, mutation, scratch, allocation, and failure are not hidden.
- No new global mutable state was introduced.
- Kernels are bounded and can be called without manufacturing a lifecycle object.
- External procedural constraints do not leak unnecessarily into unrelated internals.
- Staged procedures reuse an existing primitive when sufficient; any new request/context owns real state/lifetime semantics and cannot expose the final value before successful finish/commit.
- The negative case—identity/invariant/lifecycle dominance—was checked before choosing this model.
