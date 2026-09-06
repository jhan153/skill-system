---
name: plan-test-discovery
description: Resolve human-owned test-basis, oracle, tolerance, baseline, horizon, or accepted-uncertainty decisions when Test Design cannot proceed from authoritative evidence. Persist only the decided scope into an Execution Handoff input record when a package is bound; do not design or implement tests, edit Plan/Handoff, or replace Human Test.
---

# Plan Test Discovery

## Routing Card

- role: support
- family: testing
- intent_signature: human-in-loop test decision, oracle discussion, tolerance approval, baseline approval, test discovery
- use_when:
  - `workflow-test-design` identifies one named condition that needs a human-owned judgment before a test contract can be completed
  - the user explicitly asks to decide how an executable or accepted externally contracted behavior should be judged or what uncertainty is acceptable
- do_not_use_when:
  - a canonical requirement, mathematical property, accepted interface contract, or observation already accepted by a named authority decides the field
  - the open question is product requirements, user behavior, algorithm choice, test implementation, production repair, or Human Test
- expected_inputs:
  - target snapshot and representative actual path, or an accepted external-contract boundary and revision
  - blocked Test Design condition IDs
  - admitted evidence, unresolved judgment, options, consequences, and recommendation
  - authority owner and optional Execution Handoff package/plan identity
- expected_outputs:
  - decision ledger with authority and accepted uncertainty
  - inline result or package-local `inputs/test-decisions.md`
  - `decision_ready` or explicit open status plus the required continuation boundary
- context_targets:
  must_read:
    - discovery request, target/condition IDs, evidence, options, and decision owner
    - `references/testing_stage_contract.md`
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - `references/execution_handoff_input_contract.md` when a package or graph-mode node is bound
    - `references/test-decision-record.md` when persisting the result
    - `references/runtime_debugging_contract.md` when the human-owned decision changes debugger/dump/dynamic/graphics collection scope or cost, perturbation acceptance, sensitive-data handling, or the deliberately lowered proof ceiling; exact target/build/module/load-address/symbol identity match remains an evidence-validity rule and cannot be waived into a match
    - the smallest source, measurement, screenshot, recording, or artifact slice that distinguishes the options
  do_not_load_by_default:
    - full repository, full Plan/Handoff, unrelated requirements, raw production data, or credentials
- risk_profile:
  reads: bounded test basis, current observations, and decision-relevant artifacts
  writes: none by default; with explicit persistence or a bound package, only `inputs/test-decisions.md`
  tools: focused read-only observation and one human question at a time when decisions are dependent
  sensitive_resources: private data and external systems require their governing access and redaction boundary
- entry_scene: PREPARE

## Discovery Admission

For implicit support, require a complete Discovery request from an active `workflow-test-design`;
standalone Discovery requires an explicit user request.

Admit a decision only when all are true:

1. one or more exact Test Design condition IDs are blocked;
2. admitted source and existing evidence cannot answer the question;
3. at least two reasonable choices change the verdict, proof ceiling, false-positive/negative
   tradeoff, or accepted risk; and
4. the named answer owner has authority to choose.

Resolve discoverable facts before asking. An accepted external contract may supply the intended
boundary, observable signal, and normative authority before an executable SUT exists; Discovery may
then resolve a human-owned contractual oracle, tolerance, horizon, or accepted-risk choice. An
empirical choice about current variability, performance, rendering, or output distribution requires
representative observations, and an empirical baseline approval requires the compared artifact. If
neither an executable SUT nor accepted external-contract evidence can frame the options—or an
empirical choice lacks its required observations—return the exact evidence/testability gap to the
production, prototype, or contract owner instead of asking a person to invent it.

## Workflow

1. Bind target snapshot, actual path or accepted external-contract boundary/revision, blocked
   conditions, available evidence/observations, authority owner, and the decision consequence.
   Separate normative contract authority, observed current behavior, and accepted behavior.
2. Prepare 2–4 mutually exclusive options when a real choice exists. For each, state what it can
   detect, may miss, costs to run or maintain, and how it changes the proof ceiling. Put the
   recommended option first with its basis.
3. Ask exactly one decision question per turn. Preserve independent ready judgments for later
   turns instead of widening the active human-intervention point.
4. In a dispatched Worker, send one `question`, complete independent authorized work, and yield.
   Keep the session passively resumable; pending human response is Handoff lifecycle state, not an
   artifact status, failure, timeout, `worker_done`, or DAG-level `blocked`.
5. Record only decision deltas: ID, blocked condition IDs, question, evidence, selected option,
   authority/source, `decided|assumed|open`, accepted uncertainty, affected downstream scope, and
   rejected alternatives when their future reuse would be unsafe.
6. Mark the record `decision_ready` only when every decision required for its declared consumed
   scope is `decided`. Unrelated open items may remain visible but are not authoritative.
7. For an approved graph, send one `escalation` with the decision-record path/status, request and
   decision IDs, blocked condition IDs, source anchors, and requested continuation. Apply the Plan
   revision and resume rules in `references/testing_stage_contract.md`.

## Persistence

Apply `references/execution_handoff_input_contract.md`. Without durable intent, return the result
inline. With an exact package or associated plan, use only:

```text
<package-root>/inputs/test-decisions.md
```

Use `references/test-decision-record.md` to store decisions and evidence anchors. Only decided rows
with named authority may constrain their named downstream Test Design conditions.

## Output Contract

During discovery, return current evidence, the ready question, options/tradeoffs, and the latest
decision delta. At stop or handoff, return only applicable fields:

- `target_snapshot`
- `blocked_condition_ids`
- `observed_evidence`
- `decision_ledger`
- `accepted_uncertainty`
- `rejected_oracles_or_baselines`
- `ready_for_test_design`
- `continuation`: `resume_same_node | plan_revision | new_plan`
- `open_decisions`
- persisted path/status when applicable
