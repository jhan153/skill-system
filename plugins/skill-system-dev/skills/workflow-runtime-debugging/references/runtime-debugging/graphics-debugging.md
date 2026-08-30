# Graphics Debugging

Use this reference for graphics correctness, visual corruption, shader/resource state, GPU hangs,
or device loss. Do not collapse graphics debugging into one generic GPU validation step; select the
evidence lane from the symptom.

A screenshot/layout/asset difference with no unresolved API, shader, resource, pipeline, queue, or
device-state question stays with Testing, Design, or the current UI owner. Runtime Debugging starts
only when graphics machine/device state or a transition is material.

## Evidence Lanes

| Symptom class | Primary evidence lane | Direct observations | Does not prove by itself |
| --- | --- | --- | --- |
| API, lifetime, synchronization, descriptor, or resource-state misuse | API/debug validation | configured validation messages on the exercised path | absence of all graphics defects or performance |
| wrong pixel, geometry, resource contents, draw/dispatch, or pipeline state | frame capture/replay plus event/resource/pixel history | recorded commands, bound state/resources, render targets, selected history | original live CPU pacing, frame-to-frame race, or broad correctness |
| shader calculation or invocation error | shader source/disassembly debugging for a selected invocation | supported variables, inputs/outputs, control flow, call stack | unobserved invocations, original optimized timing, unsupported stages |
| hitch, bubble, queue overlap, utilization, or frame-time regression | live CPU-GPU timeline and counters | named metric and queue/unit activity under recorded workload | graphics correctness or a different environment; routes to `analysis-performance` |
| device loss, timeout, page fault, or GPU hang | device-fault/crash dump, progress breadcrumbs, page-fault/resource correlation | captured last progress, fault data, markers, device/driver state | a unique application cause, driver innocence, or reproducibility |
| attribution across lanes | object names, command regions, queue labels, markers, build/shader IDs | correlation between messages/events/resources and source ownership | correctness, order, or timing without another lane |

Choose one primary lane. Add another only when it answers a distinct causal question; a clean
validation run cannot replace frame state, and a normal frame capture cannot replace device-fault
evidence.

## Identity Envelope

Before interpreting a capture or dump, record:

- target executable/build and loaded graphics/runtime modules;
- operating system, API, device, driver, and relevant runtime/layer versions;
- tool and capture/replay version, capture mode, frame/event range, and replay target;
- shader source/binary/debug identity, optimization, pipeline identifier, and specialization state;
- resource identifiers, dimensions/formats/usages, descriptor/binding state, queue ownership, and
  submission/fence context when material;
- enabled validation, instrumentation, counters, markers, and their known overhead; and
- unsupported features, dropped events, partial dump/capture status, and sensitive-data controls.

A capture that replays on a different device/driver/tool environment is a translated observation.
Record the difference and do not treat replay success as proof of the original live execution.

## Validation Lane

- Enable only the validation needed for the suspected API, synchronization, descriptor, resource,
  or shader-access class.
- Bind each message to target build, object/resource identity, command/event, queue/thread, and the
  exercised workload.
- Separate direct validator findings from application causal interpretation. One invalid use can be
  downstream of an earlier lifetime or ownership defect.
- A clean run means no configured message was emitted for that exercised path. Validation coverage
  can be incomplete, and heavy shader/device validation changes GPU work and timing.
- Keep validation and performance baselines separate.

## Frame And Resource Capture Lane

1. Identify the first visibly or numerically wrong frame/state and the corresponding event range.
2. Inspect event order, pipeline state, bound resources, actual bytes, render targets, and
   synchronization/resource transitions at the failing event.
3. Use pixel/resource history or event provenance to find the first wrong producer, not only the
   final draw that displays the bad value.
4. Compare a known-good capture only when target/build/content/device conditions are sufficiently
   matched; label all differences.
5. Record replay resets, wait-idle insertion, command reordering/optimization, unsupported calls, or
   resource reconstruction as perturbation.

A captured frame is a replay artifact for a bounded workload. It does not preserve the complete
live CPU schedule, presentation timing, previous-frame history, or external device state unless the
capture contract explicitly includes them.

## Shader Lane

- Pin one invocation or smallest invocation set whose inputs and outputs distinguish the hypothesis.
- Validate shader binary/debug identity and pipeline specialization before trusting source lines or
  locals.
- Preserve source/disassembly correspondence, inputs, outputs, control flow, supported variable
  availability, and resource accesses.
- Mark optimized-out, unsupported, divergent, derivative-dependent, or nondeterministic state
  explicitly.
- Shader replacement, disabled optimization, breakpoints, and stepping can change code generation,
  execution width, scheduling, and watchdog behavior; never use their timing as production evidence.

## Device-Loss And GPU-Hang Lane

- Preserve the device-loss/error reason, last known CPU submissions, queue/fence state, progress
  breadcrumbs, page-fault addresses/resources, faulting shader/warp information when available,
  markers, and partial/full dump status.
- Correlate raw addresses and opaque identifiers through exact driver/runtime/build/shader/resource
  metadata before source attribution.
- Distinguish invalid application commands/state, use-after-free/resource lifetime, infinite or very
  long shader work, synchronization failure, driver/runtime defect, and hardware instability as
  competing classes until evidence separates them.
- A breadcrumb names last observed progress, not necessarily the causal command. A page-fault
  correlation narrows the resource/lifetime question but may not identify the original freeing or
  overwrite transition.
- Missing or unsupported vendor/device evidence remains unavailable; do not substitute another
  platform's clean result.

## CPU-GPU Correlation And Performance Boundary

Markers, submission IDs, queue labels, fences, and synchronized clocks can connect CPU ownership to
GPU events. They improve attribution but do not create correctness or timing proof by themselves.

When the target is progressing and the dominant question is frame time, queue utilization, overlap,
throughput, or resource cost,
hand the identity-matched live timeline and workload to `analysis-performance`. Keep validation,
frame replay, and shader-debug overhead out of the performance baseline. When the question is wrong
state, invalid access/order, no progress under the bound horizon, watchdog/fault termination, or
device loss, Runtime Debugging retains the causal lane. A slow but progressing queue or shader is a
performance symptom even when users call it a “hang.”

## Proof Ceilings

- clean validation: only the configured validators on the exercised path;
- frame replay: the captured/reconstructed event and resource state, not the original full history;
- shader debug: the selected supported invocation under changed debug conditions;
- live timeline: the recorded workload/environment/metric, not correctness;
- device-fault dump: captured postmortem progress/fault state, not automatically a unique cause; and
- names/markers: correlation, not validation or ordering proof.

Return the symptom class, selected lane, identity envelope, direct and disconfirming observations,
perturbations, unsupported/missing evidence, causal status, next discriminator, and proof ceiling.
