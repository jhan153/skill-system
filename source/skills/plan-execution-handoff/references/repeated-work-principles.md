# Repeated Work Principles

Read this only for an admitted Plan/Handoff whose verifier evidence is expected to change a later
action more than once. Most plans—including ordinary `phase_gate_delivery`, its static review, and
its bounded repair path—do not use this profile. These are authoring rules, not a separate skill,
runtime, evaluator, state artifact, or continuation engine.

## Verifier-Steering Admission

- Use this profile only when a fresh condition-matched verifier result can select, reject, or
  reshape a later action. One final check, task length, expense, agent count, or high governance
  risk does not make work repeated.
- Approval, rollback, idempotency, and runtime support remain their existing Plan/Handoff gates;
  they never substitute for verifier-steering value.
- Missing success authority or verifier ownership remains an unresolved Plan decision. Do not
  create repeated execution to discover its own contract.

## Condition And Verifier Contract

For admitted repeated work, replace the ordinary table under the existing Plan
`Validation and Termination` section with this table. It is the actual authoring shape; do not
create a second contract file.

| Condition ID | Observable condition | Required / dependencies | Deciding verifier | Evidence scope / target | Pass / fail / freshness | Unavailable result | Intent key | Optional quality evidence |
|---|---|---|---|---|---|---|---|---|
| `RC-001` | `<observable statement>` | `<required; dependencies>` | `<owner>` | `<structural/runtime/semantic/user-only; target>` | `<signals; freshness>` | `<open result>` | `<stable purpose>` | `<separate evidence or none>` |

- Keep one stable condition ID and intent key when the same purpose could be attempted through
  several tools.
- A command exit proves only its command contract; artifact existence proves only exact presence.
  Maker self-report, a generated report, or lower-scope evidence never closes a broader semantic or
  user-owned condition.
- An unavailable deciding verifier leaves the condition open. Optional quality evidence informs
  the named authority but never replaces it.
- Record condition state and evidence in the canonical Plan/Handoff pair. Do not add a LoopRun,
  Python evaluator, receipt engine, or parallel checkpoint store.

## Evidence-Delta Expansion And Stop

- Progress is a condition-status or accepted-evidence delta, not tool calls, edits, elapsed time,
  agent count, or repeated identical output.
- Before execution, bound graph expansions, unchanged-evidence observations, strategy oscillation,
  and optional wall-time/token/cost use in the Plan's generic graph rewrite budget.
- Request another work/verifier node only when new evidence can change the next action. Apply the
  append-only acyclic rewrite rules from `graph-method-profiles.md`; do not restate them here.
- Stop expanding when every required condition has deciding evidence, only the declared human
  oracle remains, no required condition is runnable, the accepted budget is exhausted, or the next
  action would violate an existing approval/integrity boundary. Use the active Work Contract and
  Plan node stop fields; do not invent repeated-work-only result labels.
