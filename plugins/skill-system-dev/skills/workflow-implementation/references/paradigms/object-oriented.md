# Object-Oriented Implementation

Cross-stage selection authority lives in `references/programming-paradigms/object-oriented.md`. This file owns
concrete realization and actual-path verification; it may narrow implementation admission from
production evidence but never broadens the accepted trigger or scope.

Use object boundaries where identity, protected state, lifetime, or behavioral substitution is the property the code must own. Object-oriented design is not “put functions in classes”; it assigns responsibility for state and valid behavior to stable owners.

## Core Model

An object is justified by one or more of these properties:

- **identity**: equal state does not make two instances the same entity;
- **invariants**: only some field combinations and transitions are valid;
- **lifecycle**: creation, use, cancellation, shutdown, and destruction have rules;
- **resource ownership**: acquisition and release must be paired;
- **behavioral substitution**: multiple real implementations satisfy one runtime contract;
- **event addressability**: events target a particular long-lived instance;
- **information hiding**: a volatile SDK, protocol, or storage choice must remain behind a stable boundary.

A struct with getters and setters is not automatically an object model. A module can expose a C API and still have object semantics internally.

## Construction Validity First

The default and most important object invariant is:

> After a constructor or factory succeeds, the public object is immediately valid for the semantic state named by its type.

`Valid` does not mean every long-running action has finished. It means the object is internally consistent, its allowed operations are defined, and callers do not need an undocumented setter sequence or hidden readiness transition before safe use.

Prefer:

```cpp
std::expected<FileHandle, FileError> openFile(Path path);
std::expected<ClosedCurve, CurveError> makeClosedCurve(PointSpan points);
```

Reject by default:

```cpp
File file;
file.setPath(path);
file.open();
if (file.ready()) { ... }
```

The rejected shape permits zombie handles, invalid setter orders, partially updated invariants, and methods whose meaning changes according to implicit state.

### Strong Explicit Exception: staged construction

Use a staged-construction exception only when final completion intrinsically cannot or should not occur atomically because it depends on:

- file, network, database, device, or other external events;
- asynchronous or streaming progress;
- a large array/buffer copy, decode, materialization, or parallel fill;
- GPU upload, DMA, fence, or multi-Job completion;
- explicit failure and cancellation that must be observed over time.

This exception does **not** permit an invalid final object. Introduce a different type whose semantic meaning is the in-progress operation:

```cpp
FileHandle file = TRY(openFile(path));
ReadRequest request = beginRead(file, range);

switch (request.state()) {
case ReadState::Pending:
case ReadState::Completed:
case ReadState::Failed:
case ReadState::Cancelled:
    break; // every state is valid for ReadRequest
}

std::expected<ByteBuffer, ReadError> result = finish(std::move(request));
```

Suitable names include `ReadRequest`, `ConnectionAttempt`, `DecodeSession`, `BufferBuilder`, `UploadTicket`, and `JobScope`. The staged type must itself be valid immediately after construction and must:

- expose its legal states and transitions;
- keep failure/cancellation as typed terminal outcomes;
- prevent final APIs from being called before successful completion;
- publish the final canonical value only through one `finish`, `commit`, or `freeze` boundary;
- avoid hidden fallback, default insertion, retry policy, or background state mutation that callers cannot observe;
- avoid exposing partially initialized final storage as though it were complete.

Do not create one of these types merely because the operation is asynchronous or large. First reuse the existing platform/runtime future, task, result, request, span, buffer builder, or completion primitive. A new public type is justified only when it owns a real additional invariant, legal state set, cancellation/cleanup rule, or lifetime that the existing primitive cannot express. A type that only renames or forwards an existing future/request is abstraction theater.

If the work is mainly a data transform, bulk fill, protocol parser, or dependency graph, route its implementation to procedural, data-oriented, or Job-style code. Object orientation may own the resource handle or staged-operation lifetime, but it should not absorb the whole process into a partially valid domain object.

## Decision Procedure

1. **Can the final public type be valid at construction/factory return?** Make that the default; do not design a setter/init protocol.
2. **Is staged construction intrinsically required?** If yes, reuse an existing runtime primitive first; add a separate operation/builder/request type only for a real additional invariant/state/lifetime, then name its sole final-value publication boundary.
3. **Does meaningful state survive across calls?** If not, begin with a function or algorithm module.
4. **Are some states or transitions invalid?** If yes, a concrete class can protect them; an interface is not yet required.
5. **Does identity or lifetime matter?** If the same entity must be tracked while its value changes, make that identity explicit.
6. **Are there simultaneously required runtime implementations with an identical semantic/state/failure/lifecycle contract?** Prefer direct concrete dispatch, composition, or a closed value/variant. Consider an interface/type erasure only when actual runtime substitution remains necessary and those simpler forms cannot satisfy it.
7. **Which axis changes most often?** Growing kinds with stable operations favor polymorphic implementations. Stable kinds with growing operations favor ADTs/variants and external functions.
8. **Is there a behavioral subtype contract?** A derived type must preserve the base preconditions, postconditions, and meaning. Otherwise prefer composition or delegation.
9. **Is this a bulk hot path?** Keep object ownership at the outer boundary and use values/arrays/kernels inside when per-element identity is not meaningful.

## Observable Implementation Contract

### Concrete invariant owner

Use a concrete type to make invalid state difficult or impossible:

```cpp
class ScanSession {
public:
    Result start(Device& device);
    Result submit(Frame frame);
    Result finish();
    void cancel() noexcept;

private:
    SessionState state_;
    FrameStore frames_;
    CancellationSource cancellation_;
};
```

The public API should expose valid operations, not arbitrary mutation of every field. Construction should produce a usable final object or typed failure; only the explicit staged-operation exception may defer final-value publication.

### RAII resource owner

Resources such as files, sockets, mappings, locks, GPU buffers, textures, and transactions benefit from lifetime-bound cleanup:

```cpp
class GpuBuffer {
public:
    GpuBuffer(Device& device, BufferDesc desc);
    ~GpuBuffer();
    GpuBuffer(GpuBuffer&&) noexcept;
    GpuBuffer& operator=(GpuBuffer&&) noexcept;

    GpuBuffer(const GpuBuffer&) = delete;
    GpuBuffer& operator=(const GpuBuffer&) = delete;

private:
    Device* device_;
    BufferHandle handle_;
};
```

Copy/move policy, shutdown order, and error behavior are part of the object contract.

### Rare exception: interface at a proven runtime substitution boundary

```cpp
class RenderBackend {
public:
    virtual ~RenderBackend() = default;
    virtual void resize(Size2D size) = 0;
    virtual UploadHandle upload(const MeshData&) = 0;
    virtual void render(const SceneView&) = 0;
};
```

This shape is exceptional, not the default for a boundary. Use it only when multiple implementations genuinely coexist now, callers must substitute them at runtime, every method has identical semantics/state/failure/lifecycle across implementations, and direct concrete dispatch, composition, a function table, or a closed variant cannot satisfy the requirement. Externality, testing, future platforms, file separation, or naming symmetry alone is not sufficient. Do not create `IMeshProcessor -> MeshProcessor` or normalize a single backend behind an interface.

### Event-owning instance

Interactive tools, UI controllers, sessions, and connections often own state across an event sequence:

```cpp
class TransformTool {
public:
    void pointerDown(const PointerEvent&);
    void pointerMove(const PointerEvent&);
    void pointerUp(const PointerEvent&);
    void cancel();

private:
    DragState drag_;
    TransformConstraint constraint_;
    UndoTransaction transaction_;
};
```

The value lies in one clear owner for capture, constraints, undo, and valid transitions—not in the class syntax itself.

## Expansion Axis

Use runtime polymorphism only when new kinds already need open runtime substitution while the operation set and full behavioral contract stay stable. Expected future kinds alone are not evidence.

Prefer a variant/ADT and external operations when the kinds are closed but operations keep growing:

```cpp
using Shape = std::variant<Sphere, Box, Capsule>;

double volume(const Shape&);
Bounds bounds(const Shape&);
Mesh tessellate(const Shape&);
```

If both kinds and operations are open, examine registration, capabilities, messages, or an ECS/data-driven architecture rather than forcing one inheritance tree.

## Typical Boundaries

- `MeshDocument`: identity, selection, undo/redo, dirty state, file association;
- `MeshAsset`: shared asset identity and loading state;
- `MeshInstance`: scene identity, transform, material, visibility;
- `Texture`, `Framebuffer`, `ShaderProgram`: GPU resource lifetime;
- `TransformTool`: event-driven interaction state;
- `CameraDevice`: vendor SDK and reconnect/lifetime policy;
- `ScanSession` or `NetworkSession`: state, cancellation, recovery, ownership.

Keep `TriangleMeshData`, vertices, triangles, pixels, residuals, and pure geometry queries as values or bulk data unless they have real independent identity.

## Composition Rules

- Use a **functional** or **procedural** core for deterministic calculations owned by an object shell.
- Use **data-oriented** storage for homogeneous hot data behind identity-rich document or scene owners.
- Select **TMP** for closed compile-time policies; for runtime choice prefer direct dispatch, composition, a value/variant, or a function table before the rare interface exception.
- Let a **Job System** schedule work on handles, immutable views, or ranges rather than exposing a deep shared mutable object graph to workers.

## Misapplications

- “It is a noun, therefore it is a class.”
- “It has temporary state, therefore it needs identity.”
- “Testing requires an interface.”
- “Future extensibility requires a base class now.”
- “Inheritance is the easiest way to reuse code.”
- “Every operation related to `Mesh` belongs as a `Mesh` method.”

These produce speculative interfaces, god objects, hidden call-order dependencies, and inheritance without substitutability.

## Implementation Verification

- Each object owns a specific identity, invariant, lifecycle, resource, or substitution contract.
- Ordinary final objects are valid immediately after constructor/factory success; no setter/init/readiness protocol remains.
- Every staged exception is justified by external/asynchronous/streaming/bulk/GPU progress, uses a separate valid type, and publishes its final value only through successful completion.
- Invalid transitions are rejected by the owner rather than every caller.
- Every interface satisfies the full rare-exception gate; no interface exists merely for externality, tests, future implementations, or symmetry.
- Inheritance preserves behavior; composition is used for implementation reuse.
- Value records and bulk elements were not objectified without identity.
- Hot kernels do not pay per-element allocation or virtual dispatch without evidence.
- The public API does not expose setters that bypass the claimed invariant.
