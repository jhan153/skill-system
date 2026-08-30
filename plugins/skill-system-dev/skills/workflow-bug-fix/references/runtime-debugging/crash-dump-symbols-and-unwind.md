# Crash Dumps, Symbols, And Unwind

Use this reference for postmortem crash/core/minidump analysis, address symbolization, optimized-code
inspection, or a stack whose trustworthiness is material.

## Artifact Intake

Treat the crash artifact as a selected snapshot, not a recording of the execution that produced it.
Before analysis, record:

- capture tool/version, time or sequence, target environment and architecture;
- dump type and configured filters;
- included threads, registers, exception/signal record, memory mappings or ranges, modules, handles,
  unloaded modules, device data, and custom streams when present;
- excluded or truncated state, capture failure notes, and whether the writer ran in-process or out of
  process; and
- access, redaction, retention, and transfer controls.

Absence from the artifact means `unavailable`. It does not mean the value was zero, null, unused,
unmapped, unowned, or safe.

## Exact-Build Identity

Resolve identity in this order:

1. extract raw module names, load addresses, sizes, architectures, and embedded build identifiers
   from the dump or crash record;
2. match the exact executable and every material loaded module by platform identity, not filename;
3. match separate symbol artifacts to those binaries and record public/private, function/line,
   type/local, and unwind coverage independently;
4. bind source revision and generated-source mapping only when the binary/symbol metadata supports it;
5. retain raw addresses and module offsets beside every symbolized frame; and
6. fail closed when the binary, module, load address, or symbol identity conflicts.

A build identifier assists lookup but is not content-integrity proof. A symbol loader reporting
success proves only that it accepted an artifact; it does not prove full line/type/local coverage or
that every module in the stack matched.

## Symbolization And Source Mapping

- Symbolize module-relative addresses, not bare virtual addresses detached from load information.
- Preserve inlining, code folding, thunks, veneers, generated code, and tail calls when they affect
  attribution.
- Distinguish source line mapping from causal ownership. One instruction range can map to several
  source constructs, and the closest source line need not own the invalid state transition.
- Treat source-server and remapping commands as untrusted execution boundaries. Use pinned trusted
  source and explicit mappings.
- Do not invent parameter/local values from declarations when location coverage says unavailable.

## Unwind Quality

An unwind is a derived interpretation of registers, stack/memory, calling convention, and unwind
metadata. For material frames, record the mechanism:

- canonical frame/unwind metadata;
- frame-pointer chain;
- platform function/unwind table;
- debugger heuristic or stack scan; or
- unavailable/ambiguous.

Classify frames when useful as `physical`, `inline_virtual`, `tailcall_virtual`, `heuristic`, or
`unavailable`. Validate stack bounds, return-address plausibility, module mapping, instruction
boundary, and unwind progress. Stop trusting the chain after a material inconsistency; do not turn a
heuristic scan into a normal backtrace.

Corrupted stacks, missing memory, omitted unwind data, hand-written assembly, foreign runtimes,
signal/exception frames, context switches, and optimized tail calls can shorten or distort the
trace. One clean top frame does not validate the rest.

## Optimized And Partial State

- Record optimization and code-generation context for the exact failing binary.
- Prefer registers, memory, disassembly, raw frame state, and verified location ranges over source
  locals.
- Mark variables `optimized_out`, `out_of_scope`, `not_captured`, or `unavailable` distinctly.
- A rebuilt debug binary may aid comparison but is a separate timing/layout/code-generation
  condition; never use it to overwrite the original artifact identity.
- A small dump can be sufficient for an exception/register/stack cause and insufficient for a heap,
  handle, unloaded-module, or cross-thread cause. Scope sufficiency by the active hypothesis.

## Postmortem Causal Loop

1. Bind the original crash trigger and capture scope.
2. Establish exact binaries, modules, load addresses, symbols, source mapping, and unwind coverage.
3. Record exception/signal, fault instruction, operands, fault address, raw/symbolized frames, and
   directly captured relevant thread state.
4. Decide whether the invalid transition is present in the snapshot. If not, retain only hypotheses
   whose predicted residual state differs in the artifact.
5. Use allocation/lifetime metadata, guard pages, handles, thread ownership, breadcrumbs, or custom
   streams only when captured and identity-matched.
6. Return `failure_mechanism_established`, `root_cause_established`, `leading_hypothesis`, or
   `artifact_insufficient`. A decisive faulting access can establish the failure mechanism without
   establishing the earlier invalidating transition. Never label postmortem evidence `reproduced`
   unless a separate run observed the trigger.

## Capture Infrastructure Review Handoff

When the artifact is systematically inadequate, report the missing capture field to the production
infrastructure owner. Useful static questions include:

- can the crash writer run without unsafe allocation, locks, loader activity, recursion, or damaged
  calling-thread stack dependence;
- is out-of-process or dedicated-context capture required;
- are module/build/symbol manifests emitted and archived together;
- are required mappings/streams included without excessive sensitive data; and
- are capture failures and partial artifacts themselves observable.

Do not implement the improvement inside Runtime Debugging.

## Trust And Privacy

Dumps, binaries, symbols, source mappings, and extensions can expose code, paths, memory, secrets,
and personal data or execute helper logic. Use trusted stores and explicit allowlists, disable
untrusted auto-load behavior, minimize collection, and preserve access/retention rules. Copying a
full-memory artifact to a new location is an external data action, not a routine read.
