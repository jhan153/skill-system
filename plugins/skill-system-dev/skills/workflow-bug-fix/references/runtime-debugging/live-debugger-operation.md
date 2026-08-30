# Live Debugger Operation

Use this reference for an existing debugger session or an approved target launch/attach. It is
debugger-neutral: adapt command syntax to the active tool while preserving the sequence, target
identity, and safety boundary.

## Session Handover

Before issuing commands, establish:

- whether the current prompt is a debugger, shell, remote monitor, or application console;
- debugger/tool version and target architecture;
- target executable, process ID, launch arguments, environment, working directory, and loaded
  modules;
- running, stopped, exited, detached, or core-file state;
- stop reason, selected thread/frame, breakpoint/watchpoint state, and prior user actions; and
- which controls are already approved: read-only inspection, interrupt, continue, step, breakpoint,
  watchpoint, launch, attach, capture, or detach.

Do not restart or replace an existing session merely to obtain a cleaner transcript. Preserve the
current stop and collect its identity and raw localization signal first.

When the host exposes an existing terminal or debugger-session handle, read its current output and
use that session's input channel. Do not spawn a duplicate debugger merely because starting a new
process is easier than taking over the active stop.

## First Stop Triage

Use this order unless the trigger itself supplies a more direct observation:

1. Record stop reason, exception/signal/assertion, program counter, raw module plus offset, fault
   address, and selected thread.
2. Summarize all threads/tasks before changing selection. For a hang, preserve every relevant wait,
   owner, and progress marker.
3. Focus the faulting or blocked thread and inspect a short backtrace with unwind quality. Keep raw
   frames beside symbolized frames.
4. Validate executable/module/build and symbol identity before trusting file/line, types, locals, or
   pretty-printers.
5. Inspect the minimum registers and nearby memory needed to interpret the faulting instruction,
   calling convention, object pointer, bounds, or branch condition.
6. Inspect nearby disassembly when source order, inlining, tail calls, optimization, or unavailable
   locals make the source view incomplete.
7. State the current cause hypothesis and one predicted observation before continuing or stepping.

Avoid unbounded “all threads, all frames, all locals, all memory” dumps. They consume context,
increase sensitive-data exposure, and often hide the decisive state.

## Breakpoints, Watchpoints, And Stepping

- Prefer a breakpoint on a concrete state transition, exception, allocation/lifetime boundary, or
  named invariant over a broad function-entry breakpoint.
- Prefer a watchpoint when the unresolved question is “which write first made this value invalid.”
  Bind the exact address/size/lifetime and distinguish hardware support from software emulation.
- Conditions and command lists are executable debugger logic. Keep them minimal, inspect their side
  effects, and do not call target functions to evaluate them without separate authority.
- Step at instruction level when source lines are reordered, coalesced, inlined, or optimized away.
  Step at source level only when line information and code generation make it meaningful.
- Before continue or step, state the expected next stop and what result would confirm or refute the
  hypothesis. After the stop, record the actual reason rather than assuming the breakpoint caused it.
- Remove or disable probes that no longer answer a live hypothesis, and record the resulting change
  in perturbation.

## Crash And Exception Stops

At a crash stop, prioritize:

- exact exception/signal and fault access type;
- faulting instruction and operands;
- program counter, stack/frame pointers where relevant, and architecture-specific status registers;
- fault address and whether its mapping, allocation, lifetime, permissions, or guard state is known;
- raw and symbolized top frames with unwind source; and
- other-thread state only when ownership, coordination, or corruption propagation is material.

The last instruction is often the manifestation, not the corrupting transition. Use a watchpoint,
recorded history, dynamic diagnostic, or lifecycle evidence when the fault consumes already-invalid
state.

## Hang And Deadlock Stops

- Confirm lack of progress under the named horizon; a single blocked thread is not a deadlock.
- Preserve all thread/task/queue summaries before resuming.
- For each relevant waiter, record wait object/condition, observed owner or producer, held resources,
  timeout/cancellation state, and last progress marker.
- Build only observed wait-for edges. A cycle supports deadlock; a missing owner or incomplete task
  state leaves a leading hypothesis.
- Distinguish debugger all-stop effects, suspended threads, scheduler pauses, device waits, I/O waits,
  and application locks.

## Optimized Targets

Treat the original optimized binary as authoritative for a release-only failure. Debug information
can map ranges and locations but cannot recreate state eliminated by optimization.

- Prefer raw PC/module offset, registers, memory, disassembly, unwind metadata, and calling convention
  over guessed locals.
- Mark values as optimized-out or unavailable; do not reconstruct them from a nearby source line
  unless machine state directly supports the computation.
- Distinguish physical frames from inline or tail-call virtual frames.
- A non-optimized comparison run can test a hypothesis, but it is a different layout/timing condition
  and never replaces the original observation.

## Control And Mutation Boundary

Within configured approval, attach/interrupt/continue/step and breakpoint/watchpoint insertion are
diagnostic controls, but they still affect execution. Record them. The following are not implied by
debugging authority and remain denied without a separate explicit grant:

- register or memory writes;
- forced return, skipped instruction, instruction patch, or changed control flow;
- target/inferior function calls or expression evaluation with side effects;
- injected signals/exceptions or modified exception handling;
- process termination; and
- untrusted debugger extensions, auto-load scripts, source-server commands, or pretty-printers.

Ordinary process-RAM/register reads are observational only when the target/debugger contract
guarantees no materialization or device effect. MMIO/device-register access, remote-stub reads,
managed-runtime property/expression evaluation, or another query that can execute target code or
acknowledge device state is an effect and requires approval plus perturbation recording.

If attachment or stopping removes the failure, preserve that as a perturbation observation and move
to a less intrusive dump, trace, record/replay, or dynamic-diagnostic lane.

## Safe Session Handback

Before returning, record final process/session/stop state; selected target, thread and frame;
pre-existing probes; probes inserted by this investigation; probes removed or intentionally retained;
captured artifacts; and the explicit detach/resume/continue decision. Never detach, resume,
continue, terminate, or remove a pre-existing user probe merely to clean up. When authority or intent
is unclear, preserve the current stop and hand control back with retained effects visible.

## Minimum Session Record

Preserve target and debugger identity, original trigger, mode, stop sequence, thread/frame selection,
breakpoint/watchpoint changes, decisive register/memory/disassembly observations, symbols and unwind
coverage, perturbations, causal status, safe session handback, and the next discriminator or repair
handoff. A transcript without interpreted evidence is not a debugging result.
