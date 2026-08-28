---
name: plan-test-discovery
description: Resolve human-owned test-basis, oracle, tolerance, baseline, horizon, or accepted-uncertainty decisions when Test Design cannot proceed from authoritative evidence. Persist only the decided scope into an Execution Handoff input record when a package is bound; do not design or implement tests, edit Plan/Handoff, or replace Human Test.
disable-model-invocation: true
---

# Plan Test Discovery

## Routing Card

- role: support
- intent_signature: human-in-loop test decision, oracle discussion, tolerance approval, baseline approval, test discovery
- use_when:
  - `workflow-test-design` identifies one named condition that needs a human-owned judgment before a test contract can be completed
  - the user explicitly asks to decide how an executable behavior should be judged or what uncertainty is acceptable
- do_not_use_when:
  - a canonical requirement, mathematical property, accepted interface contract, or observation already accepted by a named authority decides the field
  - the open question is product requirements, user behavior, algorithm choice, test implementation, production repair, or Human Test
- expected_inputs:
  - target snapshot and representative actual path
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
    - the smallest source, measurement, screenshot, recording, or artifact slice that distinguishes the options
  do_not_load_by_default:
    - full repository, full Plan/Handoff, unrelated requirements, raw production data, or credentials
- risk_profile:
  reads: bounded test basis, current observations, and decision-relevant artifacts
  writes: none by default; with explicit persistence or a bound package, only `inputs/test-decisions.md`
  tools: focused read-only observation and one human question at a time when decisions are dependent
  sensitive_resources: private data and external systems require their governing access and redaction boundary
- entry_scene: PREPARE

## Boundary

Apply `references/testing_stage_contract.md`. This skill owns the missing judgment only. It does
not own the enclosing Test Design node, create an executable DAG node, choose a successor, edit
Plan/Handoff, implement a test, or claim that a human decision verifies the product.

Use exact neighboring owners:

| Open question | Owner |
|---|---|
| what the product must do | `plan-requirements-discovery` or accepted requirements owner |
| how a person uses or observes an existing capability | `plan-behavior-discovery` |
| which algorithm or technical approach fits | `analysis-algorithm` |
| how a named behavior will be judged, including tolerance or accepted uncertainty | `plan-test-discovery` |
| scenario/data/oracle/environment synthesis after decisions close | `workflow-test-design` |
| test-only code and execution | `workflow-test-implementation` |

## Discovery Admission

Admit a decision only when all are true:

1. one or more exact Test Design condition IDs are blocked;
2. admitted source and existing evidence cannot answer the question;
3. at least two reasonable choices change the verdict, proof ceiling, false-positive/negative
   tradeoff, or accepted risk; and
4. the named answer owner has authority to choose.

Resolve discoverable facts before asking. Do not ask a person to invent a numeric threshold without
showing representative observations or to approve a baseline without the compared artifact. If the
SUT is not executable or lacks necessary observability, return the testability gap to its production
or prototype owner instead of opening Discovery.

## Workflow

1. Bind target snapshot, actual path, blocked conditions, current observations, authority owner,
   and the decision consequence. Separate observed current behavior from accepted behavior.
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
7. When an approved graph is bound, do not resume Test Design from the file write alone. Send one
   `escalation` containing the decision-record path/status, request and decision IDs, blocked
   condition IDs, source anchors, and requested continuation. `plan-execution-handoff` must apply
   Scope Admission, pin the consumed decision IDs and source anchors through an explicit Plan
   revision, synchronize Handoff, and only then deliver the resume follow-up. A changed objective,
   owner/boundary, DAG, or completion oracle requires a sibling Plan. The Discovery owner emits no
   `worker_done` while the originating Test Design node remains in progress.

## Persistence

Apply `references/execution_handoff_input_contract.md`. Without durable intent, return the result
inline. With an exact package or associated plan, use only:

```text
<package-root>/inputs/test-decisions.md
```

Create no placeholder Plan/Handoff or other input files. Use
`references/test-decision-record.md`; the durable artifact contains decisions and evidence anchors,
not a transcript. Only decided rows with named authority may constrain their named downstream Test
Design conditions. Test Implementation consumes the completed Test Design contract or its own
complete authoritative inline contract, never this Discovery record as a design substitute.

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

Never report product Pass/Fail, test-design completion, implementation permission, or Human Test
completion from this artifact.
