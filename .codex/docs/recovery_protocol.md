# Repeated Failure Recovery Protocol

Use this protocol inside the current implementation, repair, validation, refactor, dependency, plan, or loop owner when the same material failure fingerprint survives an intervention. It changes strategy; it does not create another workflow owner.

## Entry

Fingerprint the command or user path, failing phase/test/symbol, and first stable causal error, assertion, exit class, or observed mismatch. Ignore timestamps, temporary paths, random IDs, ordering noise, and wrapper frames. A changed causal error is `moved`, not the same fingerprint.

Freeze the original material success condition, oracle/evidence scope, latest intervention, and observed effect. Keep exactly one falsifiable hypothesis and one evidence-changing action; state the predicted observation first. Do not stack fixes, broaden scope, weaken criteria, or replace the original signal with an easier proxy.

## Protocol

1. Find the smallest reproducer preserving the fingerprint and original success signal.
2. State one hypothesis, its basis, and predicted observation.
3. Run the cheapest discriminating diagnostic, or one targeted production fix only when evidence isolates the cause.
4. Re-run the reproducer and original success check, then read back the material path when feasible.
5. Classify the result and keep the change only when the movement is explained.

| status | meaning | next action |
| --- | --- | --- |
| `resolved` | original material signal passes with no contradiction | close with decisive evidence |
| `narrowed` | evidence eliminates a causal alternative on the failing path | record it and choose one new hypothesis |
| `moved` | stable causal signature changed | keep only when the movement is explained, then fingerprint again |
| `unchanged` | same fingerprint and no new information | isolate/revert speculative change and mark the hypothesis unsupported |
| `unreproducible` | decisive signal cannot be observed | request/capture the missing evidence; do not patch |

A lower-scope pass alone is not `narrowed`. After two `unchanged` recovery actions, stop modifying and return `blocked` with one missing-evidence/access/decision action. Missing oracle, environment, permission, capability, or user judgment also stops the owning workflow without another retry.

## Output Slice

Within the owning workflow report `failure_fingerprint`, `active_hypothesis`, `diagnostic_or_fix`, `validation_result`, `keep_or_rollback`, `remaining_blocker`, and one `next_recovery_action`. Use `agent-verified` only when the original material signal is resolved and all required conditions are met.
