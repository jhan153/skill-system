# Template Metaprogramming Implementation

Cross-stage selection authority lives in `references/programming-paradigms/template-metaprogramming.md`. This
file owns concrete realization and actual-path verification; it may narrow implementation admission
from production evidence but never broadens the accepted trigger or scope.

Use template metaprogramming (TMP) only when compile-time-known inputs must produce types, signatures, layouts, overload sets, static invariants, or a small closed set of specialized policy combinations. TMP solves a compile-time problem; it is not a general replacement for runtime control flow or object interfaces.

## Distinguish The Mechanisms

```text
runtime behavior or state           -> ordinary functions and values
compile-time value                  -> constexpr / consteval
template parameter requirements     -> Concepts / requires
bounded implementation selection    -> if constexpr / aliases / traits
new type or compile-time type graph  -> TMP
```

Generic programming and TMP overlap but are not identical. A templated `max(T, T)` is generic programming. A trait that computes a storage type, transforms a type list, or constructs an expression-tree type is metaprogramming.

## Strong Application Cases

### Type computation

Use TMP when the answer itself must be a type:

- result types and common scalar types;
- matrix/tensor dimensions;
- storage policy types;
- transformed function signatures;
- filtered or deduplicated `tuple`/`variant` type lists;
- generated interfaces from fixed type metadata.

```cpp
template<class L, class R>
struct matrix_product_result;

template<class T, std::size_t M, std::size_t K, std::size_t N>
struct matrix_product_result<Matrix<T, M, K>, Matrix<T, K, N>> {
    using type = Matrix<T, M, N>;
};
```

### Fixed heterogeneous schemas

A compile-time vertex layout, serialization schema, RPC signature, or tuple-like record can derive offsets, formats, visitors, and validation from a fixed type list. Use runtime descriptors instead when files, plugins, devices, or users determine the schema after launch.

### Static invariants

Physical units, dimensions, coordinate frames, address spaces, ownership states, and fixed resource transitions can make invalid combinations fail to compile:

```cpp
template<class Frame>
struct Point3;

Point3<WorldFrame> transform(
    const Transform<CameraFrame, WorldFrame>&,
    Point3<CameraFrame>);
```

The type-level distinction must prevent a material class of error. Do not lift ordinary runtime validation into types without a clear benefit.

### Expression templates and static DSLs

Expression templates can represent a mathematical or query expression as a type-level AST and fuse evaluation:

```text
a + b * c
 -> AddExpr<Vector, MulExpr<Vector, Vector>>
 -> one fused evaluation loop
```

Use this only when expression construction and optimized evaluation are the module's core purpose, such as a matrix/tensor/SIMD library, automatic differentiation, or a bounded query DSL. A few temporary objects in application code do not justify building a new expression system.

### Closed policy specialization

Static policies may select scalar precision, storage layout, robustness, SIMD implementation, or a bounded algorithm variant when:

- supported combinations are known at build time;
- the set is small enough to instantiate intentionally;
- the choice changes type/layout or removes a measured inner-loop branch;
- runtime extension is not required.

## Least-Powerful-Sufficient Ladder

1. Ordinary function for runtime work.
2. `constexpr`/`consteval` for compile-time values and tables.
3. Concepts/`requires` for readable constraints.
4. `if constexpr`, aliases, and standard traits for local selection.
5. Type lists, partial specialization, tag dispatch, or expression templates only when the preceding tools cannot express the required type computation.

Stop at the first level that closes the contract. This improves diagnostics and limits compile-time cost.

## Runtime And ABI Boundary

The following are runtime problems unless the product explicitly closes the set at build time:

- user-selected algorithms or backends;
- configuration-file options;
- runtime-loaded plugins;
- dynamic message/file schemas;
- device capabilities discovered at startup;
- editor state, scene topology, sessions, I/O, and recovery.

Use an ordinary value, direct dispatch, function table, or closed variant first. Interface, type erasure, or registry is a rare exception requiring actual current open runtime substitution with one identical semantic/state/failure/lifecycle contract and evidence that the direct forms cannot satisfy it. Keep long-lived DLL/shared-library/plugin boundaries non-template when ABI stability matters, but do not create a facade merely because the boundary is external; a concrete C API or exported function may be sufficient. Place bounded templates behind the simplest stable boundary or explicitly instantiated core.

```text
stable public API
    non-template facade / C API / PImpl
              |
      bounded template internals
              |
    explicit instantiation set
```

## Cost And Complexity Control

TMP shifts work into compilation. Track:

- front-end time and compiler memory;
- template instantiation count and duplication;
- binary/code size across policy combinations;
- header propagation and rebuild surface;
- diagnostic depth and usability;
- debugability, symbol size, and tooling support.

A template with seven independent three-way policies has a theoretical 2,187 combinations. Even if only a subset is used, uncontrolled call sites can instantiate many variants. Restrict template axes to properties that change types/layouts, enforce static invariants, or remove measured hot-loop costs. Keep ordinary user options as runtime values.

Use named Concepts, aliases, intermediate types, `static_assert` messages, and explicit instantiations. Avoid one-line nested type expressions whose failures surface deep inside library internals.

## Recommended Module Shape

```text
Public API
  Concepts and clear value types
  non-template facade where ABI matters

Meta layer
  traits, aliases, type transformations
  bounded policy selection

Algorithm core
  ordinary loops and functions
  explicit data and mutation

Instantiation layer
  supported combinations only
```

The algorithm does not need to become a metaprogram merely because its scalar or layout is static.

## Composition Rules

- Use **procedural/functional** runtime kernels inside the statically selected implementation.
- Use **data-oriented** evidence to decide whether a static layout/SIMD specialization is valuable.
- Use direct runtime dispatch, composition, a function table, or a value/variant before the rare object-interface exception; use TMP only for a closed build-time set.
- Keep **Job System** scheduling runtime-driven unless task structure itself is truly fixed and generated without causing combinatorial complexity.

## Misapplications

- Recursive template factorials when `constexpr` is clearer.
- Encoding runtime plugin sets or user state in template arguments.
- Templating a public ABI that must remain stable across compilers or releases.
- Adding policies for every conceivable option and causing combination explosion.
- Replacing an ordinary branch without measuring its cost.
- Using TMP because it looks advanced or avoids a virtual call with no runtime requirement analysis.
- Confusing compile success with correct runtime semantics.

## Implementation Verification

- Every template axis is compile-time-known and changes a type, static invariant, layout, signature, or measured specialization.
- The least-powerful-sufficient ladder was followed.
- Runtime/open-world inputs remain runtime values/direct dispatch, with interface/type erasure only after the rare-exception gate.
- ABI and plugin boundaries have an explicit non-template strategy where required.
- Supported combinations are bounded and intentionally instantiated.
- Compile time, diagnostics, and binary size are measured or explicitly accepted when material.
- A negative task such as runtime-loaded plugin selection does not get silently converted into a closed template set.
