# Debugging Signal And Causal Loop

Use this reference when the failure is real but the next useful observation or causal confidence is
unclear. It turns “inspect more state” into a bounded hypothesis-discrimination loop.

## Scope Before Operation

When no debugger/artifact is available or direct operation is not requested, produce an
execution-ready scope instead of a cause claim. Bind:

- original trigger, expected condition/authority, target/environment, reproduction and current gaps;
- the concrete question to decide and required trigger/localization/state/transition/causal signals;
- primary evidence lane plus one fallback, with exact target/build/symbol/dump/trace/device identity;
- tool/artifact prerequisites, permissions, allowed and forbidden target effects, expected
  perturbation, and sensitive-data controls;
- one or two initial hypotheses only when current evidence supports them, each with a predicted
  observation;
- stop conditions, session handback, next owner, and original-signal verification target.

Set `causal_status: not_run`. A scope is ready when another authorized agent can execute it without
inventing the target, evidence lane, identity test, permission, or stop rule.

## Signal Before Tool

Select the observation from the unresolved question, not from whichever tool is easiest to run.

| Signal layer | Question answered | Typical evidence | Common overclaim |
| --- | --- | --- | --- |
| trigger | What exact failure occurred? | exception/signal, assertion, crash, hang, invalid output, device loss, failing condition | nearby warning is the same failure |
| localization | Where was execution or device work when observed? | stop reason, thread, PC and module offset, fault address, queue/event/resource | nearest named frame caused it |
| state | What was true at that point? | registers, memory, locals with availability, object/resource/pipeline state | missing value was null or safe |
| transition | What first made the state invalid? | watchpoint, prior event, trace, wait edge, resource/pixel history | final crash instruction performed the corrupting write |
| causal | Which prediction rules out alternatives? | one discriminating query or replay observation | repeated correlation is causation |
| closure | Did a separately owned repair remove the same failure? | original trigger plus expected-state/output readback | another test pass closes the failure |

Keep the raw trigger stable throughout the investigation. A secondary crash, test assertion, or log
message may be easier to observe but must not silently replace the original condition.

## Bounded Causal Loop

1. State the original trigger, expected condition and authority, target/environment, reproduction
   status, and current evidence gaps.
2. Normalize the best available localization signal. Preserve raw address, module offset, thread,
   event, resource, and stop reason before source interpretation.
3. If a direct machine/device observation exposes the invalid transition and its owner, record it.
   Do not manufacture alternatives for an obvious cause.
4. Otherwise retain two or three credible hypotheses. Each hypothesis must predict a different
   observable state, transition, ordering, or artifact property.
5. Choose the cheapest safe observation that can falsify at least one hypothesis. Prefer a query,
   watchpoint, narrow trace slice, exact replay position, or resource history over broad new logging
   or test infrastructure.
6. Record confirming and disconfirming evidence with scope and perturbation. Remove a hypothesis
   only when its prediction is contradicted under a comparable condition.
7. Stop at `failure_mechanism_established`, `root_cause_established`, `leading_hypothesis`,
   `artifact_insufficient`, or `trigger_not_observed`. Return the next discriminator instead of an
   investigation backlog.

Use a compact working table only when more than one cause remains:

| hypothesis | predicted observation | discriminator | result | status |
| --- | --- | --- | --- | --- |
| one concrete mechanism | state/transition that must appear | cheapest safe query | direct observation | retained/refuted |

## Observation Authority

- A source path can establish reachability or a possible invariant violation. It cannot establish
  the runtime order, selected module/configuration, thread schedule, or actual state without matching
  observation.
- A log establishes only the fields emitted at recorded events. Missing log data is not missing
  runtime state, and log order may not equal cross-thread or device order without a clock/correlation
  contract.
- A test establishes its stimulus and oracle result. It may make a failure repeatable, but a failing
  assertion does not identify the cause and a passing test does not prove the defect absent elsewhere.
- A dump is a selected snapshot. A record/replay or trace is historical only for the events/state it
  actually recorded. Neither should be promoted into the other.
- A debugger stop establishes state at that stop under its target/artifact and perturbation limits.
  A call stack is a localization aid, not a complete causal history.

## Cheapest Useful Discriminators

- Wrong value with a reproducible write path: watch the smallest aligned location or owning field and
  stop at the first unexpected write.
- Suspected stale object or lifetime error: inspect allocation/lifetime metadata, ownership state,
  vtable/type identity when valid, and the transition that published or freed it.
- Suspected branch/configuration mismatch: compare actual loaded module/configuration and the machine
  branch condition; do not infer selection from source defaults.
- Suspected thread race: compare ordering/ownership evidence with and without intrusive stops; use a
  lower-perturbation trace or dynamic race detector when attachment changes the symptom.
- Suspected deadlock: build the observed wait-for edges from all relevant threads/tasks/queues and
  distinguish a cycle from a long but progressing wait.
- Suspected graphics state error: inspect validation/resource/pipeline history for the failing event;
  do not use live FPS or a clean screenshot as a correctness oracle.

## Stop Rules

Stop expanding when one observation distinguishes the cause, when the next step needs a new
permission or infrastructure owner, or when identity/capture gaps make the artifact insufficient.
Do not add logs, tests, captures, or hypotheses merely to appear thorough. Return one next
discriminator and the exact condition it would decide.

## Result Language

Use `Observed` for direct tool/artifact state, `Inferred` for interpretation tied to that state,
`Unverified` for a remaining causal claim, and `Unavailable` for state the selected artifact cannot
contain. A useful result can end with a leading hypothesis; a confident story without a
discriminator is not a stronger result.
