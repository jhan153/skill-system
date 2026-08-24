# Data-Oriented Implementation

Use data-oriented design when a representative bulk path processes many similar items and data movement, access order, branching, batching, SIMD/GPU transfer, or tail latency materially shapes the result. The design question is not “what object does this datum resemble?” but “which bytes does this operation need, in what order, at what frequency?”

## Distinguish The Concepts

| Concept | What it decides |
| --- | --- |
| Data-oriented design | representation and traversal from actual transformations and hardware cost |
| Packed pool/array | contiguous storage and fewer allocations/indirections |
| AoS | whole records stored together |
| SoA | fields stored separately for field-specific passes |
| AoSoA | small field blocks aligned to cache/SIMD processing width |
| Hot/cold split | frequently used fields separated from rare metadata |
| Bucketing/sorting | similar types, states, or work grouped before a hot loop |
| ECS | entity identity, component composition, query, and storage architecture |
| Job/dataflow graph | execution dependencies around data access; not the storage model itself |

DOD is not synonymous with SoA or ECS. A packed `std::vector<Record>` can be data-oriented if the representative pass consumes each record as a whole. An ECS can have poor locality if every component is separately heap allocated.

## Selection Evidence

### Workload structure

A useful first-order model is:

```text
work pressure
  ~= item count
   x update frequency
   x passes per update
   x bytes touched per pass
```

A thousand items processed thousands of times per second may matter more than a million items processed once. Record the representative count, frequency, traversal, fields read/written, and latency target before selecting a layout.

### Strong intrinsic signals

- the same operation runs across many vertices, particles, pixels, voxels, instances, constraints, residuals, or observations;
- a staged pipeline performs classify/transform/reduce/compact operations;
- SIMD, GPU, accelerator, or network transfer requires regular buffers;
- a real-time frame/tick path must bound allocations and irregular traversal;
- runtime polymorphism or pointer chasing occurs inside a large repeated loop.

### Measured optimization signals

- L1/L2/LLC or TLB misses;
- low IPC with backend memory stalls;
- high DRAM bandwidth pressure;
- branch and instruction-cache disruption from mixed types;
- many small allocations or pointer indirections;
- poor multicore scaling after memory bandwidth saturation;
- P95/P99 frame spikes linked to scattered access or structural mutation.

If the current algorithm is unnecessarily `O(N^2)`, change the algorithm before celebrating a layout improvement. If I/O or a lock dominates, DOD may not address the actual bottleneck.

## Layout Decision

| Access pattern | First candidate |
| --- | --- |
| most passes consume the whole record | packed AoS |
| different passes consume different field subsets | SoA |
| tight SIMD/cache-width blocks consume several fields | AoSoA |
| a few fields dominate every frame, metadata is rare | hot/cold split |
| mixed runtime types cause branch/dispatch disorder | sort or bucket by type/state/work |
| graph traversal is stable and index-based | CSR/adjacency/index graph |
| fixed schema, bulk computation | dedicated arrays; no ECS required |
| varying entity composition and recurring component queries | ECS candidate |

Do not decide from type aesthetics. Inspect the bytes each representative pass actually reads and writes, including alignment, prefetch behavior, update locality, and whether fields are consumed together.

## Observable Implementation Contract

### Define the data views used by kernels

```cpp
struct ParticleView {
    std::span<float> positionX;
    std::span<float> positionY;
    std::span<float> positionZ;
    std::span<float> velocityX;
    std::span<float> velocityY;
    std::span<float> velocityZ;
};

void integrate(ParticleView particles, float dt, IndexRange range);
```

The view exposes the batch and write range. Ownership may remain in a resource or simulation object; the kernel does not need a pointer-rich object graph.

### Separate build storage from the published final buffer

Large arrays, parallel copies, decode targets, and GPU staging buffers may need storage before every element is initialized. Treat that as an explicit builder/storage state, not as a partially valid final container:

```text
BufferBuilder(total range)
  -> reserve/allocate raw storage
  -> write validated disjoint ranges
  -> record coverage and failures
  -> commit/freeze
  -> ImmutableBuffer | typed failure
```

The builder is valid as a builder immediately after creation. It must define element lifetime, initialized-range coverage, cancellation, ownership, and what happens after a failed write. The final `ImmutableBuffer`, tensor, image, or mesh array is published only after complete required coverage and invariant validation.

Reuse an existing span, output iterator, platform staging buffer, allocator-owned storage, task result, or local builder before creating a new public builder type. Add a type only when it owns real coverage, element-lifetime, cancellation, cleanup, or publication invariants; a forwarding wrapper around ordinary storage is not a data-oriented design improvement.

Do not expose a final-type read view over uninitialized or partially copied storage, use a `ready_` bit to change method meaning, or silently fill missing ranges with defaults. If partial data is a legitimate product state, give it a distinct type and explicit semantics.

### Separate identity-rich authoring from compute snapshots

```text
Document / scene / entity owners
    identity, undo, hierarchy, metadata
            |
        build snapshot
            v
Packed compute data
    arrays, handles, versions, ranges
            |
       compute kernels
            v
Patch / result + source version
            |
          commit
```

This hybrid is often appropriate for CAD, editors, graphics, and simulation. It keeps editing invariants and lifecycle out of the hot loop while preserving identity at commit.

### Move runtime dispatch outside the hot loop

Instead of mixing thousands of unrelated virtual calls:

```cpp
for (Object* object : objects) {
    object->update(dt);
}
```

classify first and execute homogeneous batches:

```cpp
updateRigidBodies(rigidBodies, dt);
updateParticles(particles, dt);
updateSplineFollowers(splineFollowers, dt);
```

This does not ban polymorphism. It moves dispatch to a coarser boundary and makes data access regular.

### Make stages and temporary buffers visible

```text
input
 -> validate/classify
 -> transform
 -> local accumulation
 -> reduction
 -> compaction
 -> output
```

Named stages make allocation reuse, double buffering, incremental recomputation, profiling, GPU transfer, and Job dependencies explicit.

## When ECS Is Actually Required

Use ECS when most of these conditions hold:

1. many independently identified entities exist;
2. entity capability/component combinations vary materially;
3. multiple systems repeatedly query different component sets;
4. iteration is much more frequent than structural composition changes;
5. component read/write sets can express useful scheduling dependencies.

A fixed particle schema, one mesh's normal calculation, an image filter, residual evaluation, or matrix operation usually needs dedicated storage—not entity IDs, component registration, archetype migration, and query machinery.

### Archetype/table storage

Favor it when query iteration and joint component locality dominate and composition is relatively stable. Account for entity moves, archetype proliferation, fragmentation, and pointer instability when adding/removing components.

### Sparse-set storage

Favor it when component add/remove and entity-to-component lookup are relatively frequent. Account for extra lookup and weaker joint-iteration locality across multiple component pools.

Neither variant is universally superior. The composition-change/query ratio and actual access pattern decide.

## Graphics, Geometry, And Simulation Examples

- rendering/culling: transforms, bounds, visibility, LOD, mesh/material IDs, sort keys;
- particles/SPH/boids: positions, velocities, forces, lifetime, spatial cell IDs;
- mesh kernels: positions, indices, adjacency, face/vertex outputs, local accumulators;
- skinning/animation: pose arrays, parent indices, matrix/dual-quaternion palettes;
- point clouds/voxels/images: packed samples, tiles, grids, masks, compaction outputs;
- optimization: observations, residual/Jacobian batches, thread-local block contributions;
- BVH/spatial data: packed nodes, index ranges, bounds, traversal stacks.

For each, choose layout from the specific pass. A shader that always consumes `xyz` together may prefer `float4` AoS/AoSoA; a culling pass that only reads position and radius may prefer separated hot fields.

## Composition Rules

- Use an **object-oriented** shell for documents, resources, sessions, and entity identity.
- Expose **functional** or **procedural** kernels over views/ranges.
- Use a **Job System** when ranges and read/write sets support a dependency graph; DOD alone does not schedule work.
- Use **TMP** only for bounded static layouts, SIMD widths, coordinate-frame types, or kernels where compile-time specialization has evidence.

## Misapplications

- Selecting SoA without checking whether passes consume fields together.
- Introducing ECS merely because the task mentions entities or performance.
- Claiming cache improvement without a representative workload or measurement.
- Optimizing cold authoring/UI paths while a different algorithm or I/O dominates.
- Giving every datum independent identity, allocation, or virtual behavior inside a bulk path.
- Ignoring structural-change cost, stable handles, determinism, or commit conflicts.
- Publishing a final buffer/container before all required ranges have valid element lifetime and coverage.
- Assuming DOD automatically provides thread safety or deterministic floating-point reduction.

## Implementation Verification

- The workload, count, frequency, passes, and accessed fields are identified.
- The chosen layout follows a representative read/write traversal.
- AoS/SoA/AoSoA/ECS alternatives were rejected for concrete reasons.
- Ownership, identity, and structural mutation remain at a clear boundary.
- Kernel ranges, temporary buffers, and allocation behavior are explicit.
- Large staged fills reuse an existing primitive when sufficient; any new builder owns real coverage/lifetime/publication invariants, and only successful commit publishes the final canonical buffer.
- Performance claims use the same representative workload and metric before and after.
- Tail latency and memory traffic are checked when they motivated the design.
- The negative case—small, irregular, identity-heavy, or non-memory-bound work—does not receive a speculative data architecture.
