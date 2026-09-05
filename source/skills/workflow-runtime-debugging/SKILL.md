---
name: workflow-runtime-debugging
description: Define an execution-ready debugging scope or directly investigate one concrete runtime correctness failure through an existing or approved debugger session, crash artifact, dynamic diagnostic, or graphics capture. Validate target, build, symbol, and capture identity before using stop, state, transition, or device evidence to establish the failure mechanism, root cause, or next discriminator. Do not repair source, design tests, or own performance-only diagnosis.
---

# Workflow Runtime Debugging

## Routing Card

- role: execution_primary
- family: analysis
- intent_signature:
  - debugging scope, live debugger operation, crash/core/minidump analysis, symbol and unwind validation, watchpoint or record/replay diagnosis, graphics/device-loss debugging, runtime root cause; 디버깅 범위, 디버거, 덤프, 심볼, 런타임 원인 규명
- use_when:
  - one concrete runtime correctness failure needs an execution-ready debugging scope even when no debugger or artifact is currently available
  - one concrete runtime correctness failure has an existing stopped debugger, approved launch/attach path, crash artifact, dynamic diagnostic report, record/replay trace, graphics frame capture, or device-loss artifact
  - the requested outcome is debugging-scope selection, causal localization, artifact sufficiency, or the next discriminating runtime observation without source repair
- do_not_use_when:
  - ordinary source/log reasoning already answers the question without a runtime evidence lane
  - the user requests a source/test write: use `workflow-bug-fix` only for a semantically admitted bounded repair of an already-implemented accepted contract, or `workflow-implementation` for first implementation or explicit production-mechanism replacement
  - the target is progressing correctly and the dominant question is latency, throughput, utilization, frame time, resource cost, or another performance metric; use `analysis-performance`
  - test design, test-only implementation, static code review, or production diagnostic infrastructure is the requested deliverable
- expected_inputs:
  - original trigger and expected condition, target/process/build or artifact identity when known, available or missing session/artifacts, environment, prior observations, permitted debugger effects, and optional Plan/node identity
- expected_outputs:
  - one direct task-local or graph-mode Core `debugging_result` containing an execution-ready debugging scope and, in operate mode, identity/sufficiency checks, observations, perturbations, causal status, session handoff, proof ceiling, next discriminator, and optional repair/performance handoff
- context_targets:
  must_read:
    - concrete runtime trigger, expected condition/authority, available or missing session/artifact state, repository/runtime instructions, and `references/runtime_debugging_contract.md`
    - supplied Plan/node identity and predecessor `debugging_result` when graph mode is assigned
  read_if_needed:
    - implicated source, loaded modules, build manifest, symbol manifest/store, capture metadata, prior attempts, and only the callers/state owners needed to interpret observed machine or device state
    - `references/execution_item_view.md` in graph mode or when a result crosses another Workflow/plugin
    - `references/runtime-debugging/debugging-signal-and-causal-loop.md` when competing causes or signal quality determine the next observation
    - `references/runtime-debugging/live-debugger-operation.md` for an existing session, launch, attach, stop, breakpoint, watchpoint, stepping, or hang inspection
    - `references/runtime-debugging/crash-dump-symbols-and-unwind.md` for core/minidump/crash artifacts, address symbolization, optimized code, or unreliable stacks
    - `references/runtime-debugging/dynamic-temporal-and-concurrency-debugging.md` for corruption, races, deadlocks, time-dependent failure, sanitizer output, trace, or record/replay
    - `references/runtime-debugging/graphics-debugging.md` for API validation, frame/resource/shader state, CPU-GPU correlation, device loss, or GPU crash artifacts
  do_not_load_by_default:
    - full repository/history, unrelated tests/logs, every reference, raw production data, credentials, or untrusted debugger extensions
- risk_profile:
  reads: target/source identity, live process state, dumps, symbols, traces, captures, registers, memory, disassembly, and directly relevant code
  writes: no production or test source; only approved debugger/session control and explicitly authorized diagnostic artifact capture
  tools: debugger prompt and process control, stack/register/memory/disassembly inspection, breakpoint/watchpoint, symbol/dump tools, dynamic diagnostics, trace/replay, and graphics capture tools
  sensitive_resources: attach/launch/continue/step changes execution; dumps and captures may contain secrets; target-state mutation and untrusted auto-load code are denied without separate authority
- entry_scene:
  - PREPARE

### Resource Closure

```json
[
  {
    "source": "shared/contracts/core-execution-items-v1/cards/debugging_result.md",
    "target": "references/core-execution-items-v1/cards/debugging_result.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/schemas/execution/execution-item.schema.json",
    "target": "references/execution-item.schema.json",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "matching Core result crosses the declared workflow boundary"
  },
  {
    "source": "shared/docs/execution_item_contract.md",
    "target": "references/execution_item_view.md",
    "projection": "execution-item-view",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/runtime-debugging",
    "target": "references/runtime-debugging",
    "projection": "tree",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/runtime_debugging_contract.md",
    "target": "references/runtime_debugging_contract.md",
    "projection": "verbatim",
    "load": "must_read",
    "condition": "selected skill's mandatory read contract applies"
  }
]
```

## Core Cards

- produces: `references/core-execution-items-v1/cards/debugging_result.md`
- consumes: `references/core-execution-items-v1/cards/debugging_result.md`

## Scope And Operation Modes

Apply `references/runtime_debugging_contract.md`. Admit this Workflow only for one concrete runtime
correctness trigger. Select one Workflow mode:

- `scope`: define an execution-ready debugging contract without operating a debugger or capture
  tool. The current absence of a session, artifact, symbol set, permission, or reproduction is an
  input to the scope, not an admission failure.
- `operate`: consume a supplied or inline debugging scope and directly use one existing or approved
  evidence lane.

An operate-mode lane is exactly one of:

- `existing_session`: take over a user-provided debugger already stopped or running;
- `launch_under_debugger`: start the named target under an approved debugger configuration;
- `attach`: attach to an identified live process under the configured permission policy;
- `postmortem`: inspect a crash/core/minidump with its exact build and symbol artifacts;
- `instrumented_run`: inspect an authorized dynamic diagnostic, trace, or record/replay run; or
- `graphics_capture`: inspect API validation, frame/shader/resource state, live CPU-GPU correlation,
  or device-loss artifacts.

Do not silently switch binaries, build modes, targets, dumps, symbol sets, devices, drivers, or
capture modes to obtain easier evidence. A comparison build or instrumented run is a distinct
condition and never replaces the original optimized or production artifact.

## Ownership And Result Boundary

This Workflow owns the debugging scope and, in operate mode, runtime evidence acquisition and causal
localization. It may operate the approved observation surface, but it does not edit source,
implement instrumentation, create tests, repair the failure, edit Plan/Handoff, select a successor,
or declare the repaired system correct. A supplied test failure is a trigger, not a root-cause
verdict. A supplied stack is an interpretation candidate, not a complete causal history.

In direct mode, return one task-local `debugging_result`. In graph mode, return the canonical Core
`debugging_result` and stop; the Coordinator records it and follows only an existing Plan edge. A
scope node may precede an operate node, and an operate result may be consumed by an already admitted
Bug Fix node only when that node independently satisfies its review/round dispatch prerequisites and
the typed edge already exists. Other next-owner handoffs remain recorded context for the Coordinator
or direct owner rather than undeclared Core consumers. This Workflow never creates or selects a
successor.
When a semantically admitted bounded same-contract repair is primary from the start,
`workflow-bug-fix` retains ownership and may apply the shared contract and selected detailed
references inside its diagnosis. First implementation or explicit replacement of an accepted
production mechanism remains with `workflow-implementation` even when this failure motivated it.

## Workflow

1. Bind Workflow mode, original trigger, expected condition and authority, environment,
   reproducibility, target identity when known, existing observations, permission boundary, optional
   node/predecessor identity, and material non-goals. Preserve the original signal even when a test,
   log, or secondary crash first exposed it.
2. Build the smallest execution-ready `debugging_scope`: target and failure boundary; questions to
   decide; required trigger, localization, state, transition, and causal signals; selected primary
   evidence lane and fallback; exact build/symbol/dump/trace/graphics identity requirements;
   required tools/artifacts; allowed and forbidden effects; expected perturbation; sensitive-data
   controls; hypotheses or unknowns; stop conditions; session handback; and downstream verification
   signal. In `scope` mode, return this result with `causal_status: not_run` and do not operate tools.
3. In `operate` mode, select the least intrusive admitted lane that can answer the causal question.
   Prefer an existing stopped session or adequate postmortem artifact over a new launch/attach;
   prefer a targeted watchpoint, trace, or capture over broad instrumentation. Record expected
   perturbation before running it.
4. Establish session or artifact identity before interpreting source names: executable and loaded
   modules, load addresses, build identifiers, source revision when known, symbol coverage, capture
   tool/version, dump streams or mappings, optimization, target OS/architecture, and graphics
   device/driver/shader identity when applicable. On mismatch or missing material state, return
   `artifact_insufficient` instead of a plausible stack story.
5. Normalize the trigger into the strongest available localization signal: stop reason, exception or
   signal, assertion, failing thread, program counter plus module offset, fault address, wait owner,
   invalid state transition, resource/pipeline event, or device-fault marker. Keep raw addresses and
   machine/device state beside symbolized interpretation.
6. Inspect the smallest decisive state. Start with thread summary, faulting thread, stack/unwind
   quality, registers, nearby memory and disassembly, object/resource state, and relevant history.
   Expand only for a distinct cause prediction, hidden owner, cross-thread dependency, missing dump
   region, or failed interpretation assumption.
7. If the cause is not direct, retain two or three credible hypotheses whose predicted observations
   differ. Choose the cheapest safe query, watchpoint, breakpoint, step, replay position, sanitizer
   check, trace slice, resource history, shader invocation, or wait-for edge that can falsify at
   least one. Record both confirming and disconfirming observations and any debugger-induced timing,
   scheduling, allocation, layout, or replay change.
8. Stop when evidence establishes the observed failure mechanism, establishes one root cause against
   credible alternatives, leaves one leading hypothesis and next discriminator, or reaches an
   artifact/session limit. Do not fill optimized-out values, missing dump memory, ambiguous unwind
   frames, absent thread history, or unsupported graphics state with inference presented as
   observation.
9. Before return, preserve a `session_handoff`: final process/session/stop state; selected target,
   thread and frame; pre-existing versus inserted breakpoints/watchpoints/probes; removed and retained
   probes; artifact paths; and the explicit detach/resume/continue decision. When authority or intent
   is unclear, preserve the current stop and do not detach, resume, or terminate.
10. Return the bounded `debugging_result`. When repair is later requested, hand off the failure
    mechanism or causal statement, decisive evidence, implicated owner/path, original-signal
    verification target, and proof ceiling. When investigation instead establishes a progressing
    cost/SLO bottleneck, return a performance handoff. Neither handoff invokes its owner.

## Live-Control Safety

- Confirm debugger prompt, target/process identity, stop state, and selected thread before issuing
  commands. Never type shell commands into an uncertain debugger prompt or debugger commands into an
  uncertain shell.
- Attach, interrupt, continue, step, breakpoint insertion, watchpoints, record/replay, and graphics
  capture can alter execution or timing. Follow configured approvals and record the effects used.
- Ordinary process-RAM/register reads and disassembly inspection are observational only when the
  target/debugger contract guarantees no materialization or device effect. MMIO/device-register
  reads, remote-stub reads, managed-runtime evaluation, and any query that can execute target code or
  acknowledge device state are effects requiring approval and perturbation recording. Register or
  memory writes, inferior function calls, instruction patching, forced signals/exceptions, process
  termination, and debugger-script/pretty-printer auto-load require separate explicit authority;
  otherwise do not perform them.
- Treat dumps, symbols, source-server mappings, capture files, extensions, and auto-load scripts as
  sensitive or untrusted inputs. Use trusted stores/allowlists and preserve access, redaction, and
  retention boundaries.

## Causal Status And Proof Ceiling

Use exactly one applicable causal status:

- `not_run`: scope mode produced an execution-ready contract without runtime operation;
- `failure_mechanism_established`: the observed failing instruction/state/transition is direct, but
  the earlier invalidating transition or owning root cause is not yet established;
- `root_cause_established`: direct evidence connects the trigger to the invalid transition or
  invariant breach and its owning mechanism while distinguishing credible alternatives;
- `leading_hypothesis`: evidence narrows the cause but one material discriminator remains;
- `artifact_insufficient`: target/build/symbol/capture identity or required state is missing or
  mismatched; or
- `trigger_not_observed`: the authorized run did not reproduce or expose the original signal.

A debugger observation establishes only the target state seen at a named stop, dump, replay, trace,
or capture under verified artifact coverage. It does not by itself establish the unique history,
absence of unobserved races or memory defects, completeness of an unwind, production reproducibility,
or correctness after a future repair.

## Output Contract

Return only applicable fields from `references/runtime_debugging_contract.md`, including:

- `target_and_trigger`
- `mode_and_debugging_scope`
- `session_or_artifact_identity`
- `per_module_identity_and_coverage`
- `dump_unwind_or_capture_sufficiency`
- `direct_observations`
- `disconfirming_observations`
- `hypotheses_and_discriminators`
- `debugger_or_instrumentation_perturbations`
- `causal_status`
- `failure_mechanism`, `root_cause`, or `leading_hypothesis` as supported
- `next_discriminator`
- `session_handoff`
- `proof_ceiling`
- `repair_handoff`
- `performance_handoff`
- `sensitive_artifact_controls`
- Core `debugging_result` when graph-mode identity is supplied

Graph mode compacts the applicable fields into the canonical card payload and keeps per-module
identity, full observations, session transcripts, and large capture details in artifact/evidence
refs. Do not add undeclared payload fields or replace the compact identity array with one global
symbol-match boolean.

## Cross-Skill Boundaries

- Simple source/log-only explanation stays with the current task owner. The presence of an error
  message alone does not activate this Workflow.
- `workflow-bug-fix` owns every semantically admitted bounded source repair and same-original-signal
  closure attempt under the same accepted repair contract. It may consume a supplied
  `debugging_result`; no second diagnosis owner is inserted into a repair round. First implementation
  or explicit production-mechanism replacement belongs to `workflow-implementation` instead.
- `analysis-performance` owns a progressing target whose dominant question is frame time, latency,
  throughput, CPU/GPU utilization, memory bandwidth, or resource cost. No-progress under the bound
  horizon, OOM/allocation failure, watchdog termination, corruption, invalid ordering/access,
  graphics correctness, and device-loss causality stay here even when resource pressure is a cause
  candidate; hand off only after evidence reclassifies the symptom as a progressing cost/SLO issue.
- Testing owns test meaning, reproducible stimulation, test-only capture tooling, artifact
  preservation, and test-evidence credibility. It does not turn a dump, stack, or failing test into
  a root-cause verdict.
- `workflow-code-review` may statically review diagnostic infrastructure; runtime artifact validity
  remains outside static disposition. `workflow-implementation` owns requested production crash
  capture, symbol publication, diagnostic hook, marker, or observability infrastructure.

## Discriminating Cases

- **Positive:** An existing stopped session shows a corrupted field. Validate the target and symbols,
  set the narrowest safe watchpoint, and identify the first bad write rather than adding logs.
- **Scope:** No debugger or dump is available. Return the target/trigger boundary, selected evidence
  lane, exact artifact and symbol requirements, approval/perturbation limits, stop rules, and handback
  contract without pretending the cause was investigated.
- **Postmortem:** A matching dump, binary, and symbol set exists without a reproduction. Return the
  observed crash state and established or leading cause; do not label it reproduced.
- **Graphics:** Device loss routes to device-fault/crash evidence; a frame-time regression routes to
  `analysis-performance` even when the same graphics tools can display both.
- **Negative:** A failing test needs a new fixture or assertion. That is Test Design/Implementation,
  not Runtime Debugging.
- **Edge:** Attach makes an intermittent race disappear. Record perturbation and change to a less
  intrusive dump, trace, record/replay, or dynamic-diagnostic lane; do not report resolution.
