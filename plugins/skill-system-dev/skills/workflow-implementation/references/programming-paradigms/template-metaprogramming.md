# Template Metaprogramming Selection Profile

- **Trigger:** build-time-known inputs must create a type, layout, signature, static invariant, or
  small closed policy set, or remove an evidenced hot-loop runtime choice.
- **Non-trigger:** runtime configuration, user/device choice, runtime-loaded plugin, dynamic schema,
  session/I/O/recovery state, or virtual-call avoidance by taste.
- **Minimum closure:** bounded compile-time axes and supported instantiations, the material static
  invariant/selection, and a stable runtime/ABI crossing where required.
- **Maximum scope:** the bounded template core; runtime/open-world choices, public ABI, and runtime
  dependency scheduling remain outside.
- **Interactions:** DOD may justify static layout/SIMD; procedural/functional code owns runtime
  kernels; Job scheduling stays runtime-driven.
- **Proof ceiling:** compile success proves static representability only. Runtime semantics,
  performance, compile cost, diagnostics, and binary size need their matching observations.

Implementation details and actual-path verification remain with the matching
`workflow-implementation` method profile.
