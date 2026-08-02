# Logic Prototype

Use this branch when the question concerns state transitions, invariants, action semantics, reducer/state-machine shape, or whether a domain interaction model behaves coherently.

## Build Shape

1. Use the host project's language, runtime, dependency set, and run tooling. Avoid a new framework or package unless the question is specifically about that dependency.
2. Put the behavior in a small pure, portable core: functions, reducer, state machine, or class with explicit inputs, outputs, state, and invalid transitions.
3. Add the thinnest runnable driver that makes the question observable: a script, command loop, plain CLI, or compact TUI. A full-screen TUI is unnecessary when a sequence of commands and state snapshots is clearer.
4. Keep state in memory and use deterministic representative fixtures. Do not add a database, migration, cache, network service, auth flow, or filesystem persistence unless that mechanism is the explicit question and separately authorized.
5. After every action, show the complete relevant state, transition/result, rejected action and reason, and any invariant affected. Keep the output within one screen or a short replay so the decision owner can compare sequences without reading code.
6. Provide one exact command plus a short action/replay guide. Include the representative happy sequence and one material edge or counterexample that can reverse the decision.

## Observation

- Judge the stated transition or interaction question, not production robustness.
- Record the action sequence, starting state, resulting state, invariant outcome, and the observation that selected, supported, contradicted, or failed to distinguish the candidate.
- Do not build a broad test suite or generalized framework around the prototype. A focused assertion is appropriate only when the explicit question is a deterministic invariant; it still does not prove integration behavior.

## Closure

Keep the CLI/TUI, fixtures, and replay runnable as isolated throwaway evidence until the decision owner observes them. Lift only a genuinely reusable pure core after its production owner, API, failure policy, and actual-path validation are selected; otherwise reimplement the accepted behavior through the normal production workflow. Clean up the prototype only on request or at its pre-agreed retention trigger.
