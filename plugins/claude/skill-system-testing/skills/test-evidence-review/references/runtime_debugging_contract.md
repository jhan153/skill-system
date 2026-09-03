# Runtime Debugging Contract

This contract defines the shared scope, evidence, identity, safety, and ownership rules for one
concrete runtime correctness failure. It covers both an execution-ready debugging scope and direct
operation of a debugger session, crash artifact, dynamic diagnostic, or graphics capture. It is not
a universal debugging checklist, a test strategy, a repair workflow, or a performance-analysis
contract.

## Outcome

Define the smallest execution-ready debugging scope and, when operation is authorized, acquire the
smallest runtime observation that distinguishes a failure mechanism or credible cause while
preserving the original trigger, exact target/artifact identity, debugger perturbation, unavailable
state, safe session handback, and proof ceiling.

Use this model:

`runtime debugging = trigger identity × debugging scope × target/artifact identity × observed state/transition × discriminator × perturbation × session handoff × proof ceiling`

Source proximity, a familiar stack frame, a loaded symbol file, or a passing test never substitutes
for a discriminating runtime observation.

## Ownership

| Requested outcome | Owner | Boundary |
| --- | --- | --- |
| define an execution-ready debugging scope or directly investigate runtime correctness through a live debugger, dump, dynamic diagnostic, or graphics capture without repair | `workflow-runtime-debugging` | direct task-local or graph-mode Core `debugging_result`; no source write or successor selection |
| repair a bounded defect while preserving an already-implemented accepted production contract, including proportional diagnosis | `workflow-bug-fix` | one semantically admitted repair owner; may consume an existing `debugging_result` or apply this contract internally |
| first implement or explicitly replace an accepted production algorithm, model, backend, canonical flow, or other mechanism in response to a failure | `workflow-implementation` | production implementation owner; the failure is evidence, not Bug Fix authority |
| diagnose a progressing target's latency, throughput, utilization, CPU/GPU, memory, query, rendering-time, or resource-cost bottleneck | `analysis-performance` | comparable performance evidence, not no-progress/crash/corruption/device-loss causality |
| define test conditions and required diagnostic capture | `workflow-test-design` | capture contract and proof ceiling, not root cause |
| implement tests and preserve failure artifacts | `workflow-test-implementation` | test-only stimulation/capture, not production repair or causal verdict |
| review test artifact credibility | `test-evidence-review` | identity, provenance, completeness, perturbation, and proof-ceiling findings only |
| statically review diagnostic infrastructure | `workflow-code-review` | source-level safety/conformance only, never runtime artifact validity |
| implement crash capture, symbol publication, diagnostic hooks, markers, or observability | `workflow-implementation` | production infrastructure change, not diagnosis of a current failure |

A result never invokes the next owner automatically. A failing test, crash dump, validation message,
or graphics capture may trigger classification, but it does not authorize repair or establish a
cause by itself.

## Scope And Operation Modes

Runtime Debugging requires one concrete correctness trigger. Select one Workflow mode:

- `scope`: produce an execution-ready debugging contract without operating tools. A missing session,
  artifact, symbol set, permission, or reproduction is an input to the scope, not an admission failure.
- `operate`: consume a supplied or inline debugging scope and use one existing or approved evidence
  lane.

An operate-mode lane is one of:

- `existing_session`: inspect a user-provided debugger session;
- `launch_under_debugger`: start a named target under an approved debugger configuration;
- `attach`: attach to an identified live process under configured permission policy;
- `postmortem`: inspect a crash/core/minidump and matching build artifacts;
- `instrumented_run`: inspect an authorized dynamic diagnostic, trace, or record/replay run; or
- `graphics_capture`: inspect validation, frame/shader/resource state, live correlation, or
  device-loss evidence.

Every debugging scope names the target/trigger boundary, questions to decide, required signal layers,
selected lane and fallback, exact identity requirements, tools/artifacts, permissions and forbidden
effects, expected perturbation, sensitive-data controls, hypotheses or unknowns, stop conditions,
session handback, and downstream verification signal. Ordinary source/log explanation with no need
for such a scope stays with the current task owner. A bounded same-contract repair stays with
`workflow-bug-fix`; first implementation or explicit production-mechanism replacement stays with
`workflow-implementation`, and an unresolved approach stays with its decision owner.
An operation lane may change only when the new lane answers an unresolved discriminator and its
changed conditions are recorded.

## Debugging Signal Ladder

Keep the strongest applicable signal in each layer:

1. **Trigger signal:** exception, signal, assertion, crash, hang, corruption, invalid output, device
   loss, or failing condition that identifies the original failure.
2. **Localization signal:** stop reason, thread, program counter, module plus offset, fault address,
   wait owner, queue/event, resource, pipeline, or shader invocation.
3. **State signal:** registers, memory, locals with availability status, object/resource state,
   handles, descriptors, pipeline configuration, or relevant device state.
4. **Transition signal:** first bad write, prior recorded event, synchronization edge, queue/wait
   history, resource transition, submission order, or pixel/resource history.
5. **Causal signal:** an observation whose result differs across the retained hypotheses and rules
   out at least one credible alternative.
6. **Closure signal:** after a separately owned repair, the same original trigger is absent and the
   expected condition is directly observed on its representative path.

Logs and tests can supply trigger or transition context when they recorded it. They do not expose
unrecorded state, and they do not replace the debugger or capture lane when the unresolved question
is a machine/device state or first-invalid-transition question.

## Identity And Sufficiency

Validate identity before symbolizing or interpreting source:

- executable and loaded-module identities, load addresses, architecture, operating environment,
  build identifiers, and source revision when known;
- symbol identity plus coverage for functions, lines, types, locals, and unwind metadata; do not
  collapse coverage into one `symbols_loaded` boolean;
- dump/capture type, capture tool and version, included threads/streams/mappings/resources, filters
  and exclusions, and failure timestamp or sequence position;
- optimization, inlining, tail calls, omitted frame pointers, code generation, sanitizers,
  allocators, and other material build/runtime differences; and
- for graphics, API, device, driver, shader/pipeline identifier, resource identity, capture/replay
  compatibility, and enabled validation/instrumentation.

A build identifier is a lookup key, not binary-integrity proof. Filename equality, successful symbol
loading, or a plausible source line is insufficient when module identity or load address disagrees.
Missing dump memory, optimized-out values, unavailable locals, unsupported shader state, or absent
history remains unavailable; never infer zero, null, unused, or safe from absence.

In a compact Core result, `identity_and_artifact_status` retains one entry per material module or
capture identity/coverage decision plus missing/mismatched state. Never compress it into one global
`identity_match` or `symbols_loaded` boolean.

## Observation And Causal Rules

- Preserve raw program counters, module offsets, fault addresses, stop reasons, relevant registers,
  and capture event/resource identifiers beside symbolized or source-level interpretation.
- Mark unwind frames as physical, inline-virtual, tail-call-virtual, heuristic, ambiguous, or
  unavailable when the distinction matters. A stack is derived from machine state and unwind
  metadata, not a complete execution history.
- Retain only two or three credible hypotheses when a direct cause is unavailable. Give each a
  distinct predicted observation and use the cheapest safe discriminator.
- Record confirming and disconfirming observations with their exact stop, thread, frame, event,
  resource, replay, workload, and environment scope.
- Separate `postmortem_observed`, `historically_recorded`, `reproduced`, and
  `regression_guarded`. None implies another.
- A changed build, disabled optimization, sanitizer, debugger attachment, software breakpoint,
  watchpoint, single-step, replay, validation layer, or graphics capture may alter schedule, layout,
  allocator behavior, timing, device work, or watchdog exposure. Record it as perturbation and do
  not merge its result with the original condition silently.

## Causal Status

- `not_run`: scope mode produced an execution-ready contract without runtime operation.
- `failure_mechanism_established`: the observed failing instruction/state/transition is direct, but
  the earlier invalidating transition or owning root cause is not yet established.
- `root_cause_established`: direct evidence connects the trigger to the invalid transition or
  invariant breach and its owning mechanism while distinguishing credible alternatives.
- `leading_hypothesis`: evidence narrows the cause, but one material discriminator remains.
- `artifact_insufficient`: target/build/symbol/capture identity or required state is missing,
  mismatched, truncated, or unsupported.
- `trigger_not_observed`: the authorized run did not expose the original trigger.

`trigger_not_observed` is not `resolved`. `failure_mechanism_established` must not be inflated into a
root cause. `artifact_insufficient` is a valid termination state and must not be replaced by a
guessed call stack or generic logging recommendation.

## Safety And Trust Boundary

- Attach, interrupt, continue, step, breakpoint/watchpoint insertion, record/replay, validation, and
  graphics capture affect target execution and follow configured approvals.
- Prefer the least intrusive lane that can decide the question. Record target stop duration,
  all-stop versus non-stop behavior, inserted traps/watchpoints, instrumentation, replay changes,
  and other material effects.
- Ordinary process-RAM/register reads are observational only when the target/debugger contract
  guarantees no materialization or device effect. MMIO/device-register reads, remote-stub reads,
  managed-runtime evaluation, or another query that can execute target code or acknowledge device
  state are effects requiring approval and perturbation recording. Register or memory writes,
  inferior function calls, instruction patching, forced signals/exceptions, process termination, and
  unsafe evaluation require separate explicit authority; otherwise they are denied.
- Treat dumps, symbols, executables, source mappings, pretty-printers, extensions, auto-load scripts,
  and capture files as sensitive or untrusted inputs. Use trusted stores and allowlists; do not run
  artifact-provided code implicitly.
- Dumps and captures may contain secrets, personal data, source paths, executable contents, shader
  code, and user data. Apply access, minimization, redaction, retention, and transfer rules before
  preservation or sharing.
- In-process crash writers can encounter corrupted state, reentrancy, loader locks, exhausted stack,
  or unsafe allocation. Diagnostic-infrastructure implementation and static review must make those
  constraints explicit; a successful unit test is not crash-context proof.

## Session Handoff

Every live operate-mode result records final process/session/stop state; selected target, thread and
frame; pre-existing versus inserted breakpoints/watchpoints/probes; removed and retained probes;
captured artifact paths; and the explicit detach/resume/continue decision. Do not detach, resume,
continue, or terminate merely to make the session look clean. When authority or user intent is
unclear, preserve the current stop and return control with the remaining probes and effects visible.

## Testing Projection

Testing consumes only the capture and credibility subset of this contract:

- Test Design may require a dump, trace, target stop, build/symbol manifest, frame capture, device
  artifact, or other diagnostic handoff only when it helps localize a named failing condition.
- Test Implementation may mechanically reproduce the condition and execute only the trigger, probe,
  location/range, commands, and capture scope frozen by the accepted contract, preserving exact
  target, tool, environment, build/symbol/capture identity. If the observation must adapt the probe,
  watchpoint, stepping, or next query, return a Runtime Debugging handoff. Do not interpret the
  artifact into a root cause or change production code.
- Test Evidence Review checks identity match, capture completeness, provenance, perturbation,
  sensitive-data controls, and claim ceiling from existing artifacts/session metadata only. It does
  not issue debugger control or adaptive observation commands, rerun the suite, or authorize repair.
- A passing test establishes only its encoded condition/path/environment/horizon. A failing test
  establishes a condition observation, not the unique cause. A captured dump or trace is diagnostic
  evidence, not an oracle unless the test contract separately defines one.

When a test result warrants later runtime investigation, preserve a task-local handoff containing
the original condition and trigger, target/test snapshot, artifact references, identity and capture
scope, environment/horizon, perturbations, sensitive-data controls, and missing material fields.
Do not auto-invoke `workflow-runtime-debugging`.

## Debugging Result

Use only applicable fields. Direct mode may return the full envelope. Graph mode projects its compact
fields into the canonical Core `debugging_result` card.

```yaml
debugging_result:
  target_and_trigger:
    symptom:
    expected_condition:
    authority_ref:
    environment:
    reproduction_status:
  mode: scope | operate
  debugging_scope:
    questions: []
    primary_lane:
    fallback_lane:
    required_signals: []
    required_tools_and_artifacts: []
    allowed_effects: []
    forbidden_effects: []
    stop_conditions: []
    downstream_verification_signal:
  session_or_artifact_identity:
    source_revision:
    tool_and_version:
    capture_time_or_sequence:
    target_os_arch_device_driver:
  per_module_identity_and_coverage:
    - module:
      binary_identity_evidence:
      symbol_identity_evidence:
      load_address_match:
      function_coverage:
      line_coverage:
      type_coverage:
      local_coverage:
      unwind_coverage:
      missing_or_mismatch: []
  dump_unwind_or_capture_sufficiency:
    included_state: []
    missing_or_unsupported_state: []
    unwind_or_replay_limits: []
  direct_observations: []
  disconfirming_observations: []
  hypotheses_and_discriminators: []
  debugger_or_instrumentation_perturbations: []
  causal_status: not_run | failure_mechanism_established | root_cause_established | leading_hypothesis | artifact_insufficient | trigger_not_observed
  failure_mechanism:
  root_cause:
  leading_hypothesis:
  next_discriminator:
  session_handoff:
    final_process_session_stop_state:
    selected_target_thread_frame:
    preexisting_probes: []
    inserted_probes: []
    removed_probes: []
    retained_probes: []
    detach_resume_continue_decision:
  proof_ceiling:
  repair_handoff:
    implicated_owner_or_path:
    repair_direction:
    original_signal_verification_target:
  performance_handoff:
  sensitive_artifact_controls:
  unresolved_conditions: []
```

This is a diagnostic envelope, not a test verdict, repair result, release verdict, or Plan
transition. In graph mode its canonical Core card crosses the Workflow/Coordinator boundary; the
card still never creates a node or selects a successor.

## Execution DAG Integration

Runtime Debugging may be selected as a durable DAG node only when an accepted Plan explicitly names
the node, mode, inputs, selected skill, lock/effect scope, output, validation owner, stop/escalation,
and typed edges.

- A `DBG0`-style `debugging_scope` node returns a Core `debugging_result` with `mode: scope` and
  `causal_status: not_run`. It operates no debugger/capture tool.
- A `DBG1`-style `runtime_debugging` node consumes a predecessor scope result or supplies the same
  scope inline, then returns one Core `debugging_result` with `mode: operate`.
- A scope node may `unblocks`/`depends_on` an operate node. An operate result may feed an already
  admitted Bug Fix node only through an accepted edge and never replaces that Workflow's independent
  review/round dispatch prerequisites. Performance, test, or human-decision needs remain explicit
  handoff context until their own accepted node/input contract admits them. Runtime Debugging does
  not create, choose, or execute a successor.
- Direct one-session work may use the same shape without Plan/Handoff or a Core envelope.

## Proof Ceilings

A scope-mode result establishes only that the named trigger has an execution-ready debugging
contract with explicit identity, evidence, effect, stop, and handback requirements. It establishes no
runtime observation or cause.

A debugger or postmortem observation may establish:

> At the named stop, dump, replay, trace, or capture, the verified target and available artifacts
> exposed the recorded machine/device state, which supports the stated causal status within the
> recorded identity, coverage, and perturbation limits.

It does not by itself establish:

- the unique history that produced the state;
- absence of unobserved thread schedules, races, undefined behavior, memory errors, or device faults;
- values optimized away or omitted from the dump/capture;
- complete stack, resource, or execution-history reconstruction;
- reproduction in the original production condition;
- correctness after a repair; or
- broad product, release, performance, security, or test quality.

## Discriminating Cases

- Matching dump/binary/symbol identities with a decisive faulting instruction can support a
  postmortem root cause without claiming reproduction.
- A symbol mismatch or required missing mapping yields `artifact_insufficient`, even when function
  names look plausible.
- A race that disappears after attach records debugger perturbation and moves to a less intrusive
  lane; disappearance is not closure.
- A clean graphics validation run supports only the configured validation scope. A frame replay is
  not the original live CPU/GPU history, and a device-loss breadcrumb is not automatically a unique
  cause.
