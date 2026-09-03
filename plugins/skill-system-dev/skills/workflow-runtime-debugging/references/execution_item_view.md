# Core Execution Item Role View

Generated from the canonical Core execution-item contract for `workflow-runtime-debugging`. Do not edit this projection.

Contract ID: `core-execution-items-v1`
Semantic owner: `skill-system-core`

Machine shape: runtime `schemas/execution/execution-item.schema.json`; installed skill-local
projection `references/execution-item.schema.json`

Use this contract only when a result crosses Workflow, Coordinator, Plan/Handoff, or plugin
boundaries. A direct single-owner task may use its ordinary compact output.

## Authority

| Concern | Owner |
| --- | --- |
| accepted topology, dependencies, typed edges, and available node IDs | Plan or accepted execution source |
| current Task State, deferred-item carry, and exact successor | Coordinator/Handoff or the current execution owner when no Coordinator exists |
| final Known Bug record | Coordinator/Handoff in graph mode; bounded Bug Fix after final local review in standalone mode |
| concrete UI design artifact and implementation handoff | `workflow-ui-design` |
| one explicitly assigned Research-stage node result | `workflow-research` using one selected Research specialist |
| one assigned debugging-scope or runtime-debugging node result | `workflow-runtime-debugging` |
| production implementation result | the assigned implementation Workflow |
| implementation-ready software test contract | `workflow-test-design` |
| test-only implementation and scoped execution result | `workflow-test-implementation` |
| read-only static disposition and review findings | `workflow-code-review` or the named review owner |
| one semantically admitted contract-preserving repair intervention and attempt observation | `workflow-bug-fix` |
| Human Test observation and product/design judgment | user or explicitly declared human owner |

One producer owns each item. Consumers may record or route it, but they never reinterpret its
kind into authority they do not own. An execution item never creates a Plan node, rewrites an
edge, selects a successor ID, closes a graph, or waits/polls.

The Plan/Coordinator classifies the required positive production output before consuming a review
disposition. First implementation or explicit replacement of an accepted production mechanism is
Implementation work; Bug Fix owns only a bounded intervention that preserves an already-implemented
accepted contract. A failure signal, `repair_required`, attempt history, or BF label alone is not
workflow or successor authority.

## Common Envelope

Use the smallest applicable fields. `plan_ref` and `node_id` are required only in graph mode.

```yaml
execution_item:
  contract_id: core-execution-items-v1
  item_id: <stable task-local id>
  kind: design_result | research_result | debugging_result | implementation_result | test_design_result |
        test_implementation_result | code_review_result | deferred_item | bug_fix_result |
        known_bug_candidate | known_bug_record
  producer: <canonical plugin:skill id or current owner>
  plan_ref: <plan id/revision or null>
  node_id: <Plan node id or null>
  scope_ref: <bounded design/research/debugging/behavior/review/repair scope>
  artifact_refs: []
  evidence_refs: []
  payload: {}
```

Forbidden envelope or payload fields:

- `next_node`, `next_node_id`, or another successor selection;
- `graph_transition`, Plan edits, or an invented node;
- `partial_handoff` or renamed waiting/early-exit states;
- graph-level `blocked` from a Workflow result;
- worker transcript, raw source analysis, or repeated terminal/diff/Plan content.

A missing required artifact or lost access produces a lifecycle `question` or `escalation` with
the result marked `not_produced`; it does not manufacture a result card or review verdict.

## Core Markdown Cards

The actual Handoff-ready templates live under the installed skill-local path
`references/core-execution-items-v1/cards/`. A Workflow's `## Core Cards` section names only the
templates it produces or consumes; an execution owner additionally names the cards it records.
Generation projects each named card from the canonical
`source/shared/contracts/core-execution-items-v1/cards/` directory.

Use the Markdown card as the compact row written into the existing Handoff ledger section named by
the card and this contract's machine schema as its field authority. The Coordinator model performs
the write; there is no separate card writer or storage layer. Do not create a skill-owned wrapper
or copy a Core template into a local reference. Adding or removing a card type requires the
canonical Markdown file and every affected producer, consumer, and recorder binding to change
together.

## Role Cards

- produces: `references/core-execution-items-v1/cards/debugging_result.md`
- consumes: `references/core-execution-items-v1/cards/debugging_result.md`

## Selected Item Kinds

### `debugging_result`

Producer: `workflow-runtime-debugging`. Consumers: a later assigned Runtime Debugging node, Bug Fix,
and the execution owner. Recorder: the execution owner.

```yaml
payload:
  mode: scope | operate
  target_and_trigger: <concrete failure and expected condition>
  debugging_scope: []
  identity_and_artifact_status: []
  direct_observations: []
  perturbations: []
  causal_status: not_run | failure_mechanism_established | root_cause_established |
                 leading_hypothesis | artifact_insufficient | trigger_not_observed
  cause_summary: <observed mechanism, root cause, leading hypothesis, or none for scope mode>
  next_discriminator: <one next observation or none>
  session_handoff: <final process/session/probe/detach-resume state or not_applicable>
  proof_ceiling: <what this scope or observation does and does not establish>
  repair_handoff: <bounded repair direction and original signal, or none>
  performance_handoff: <bounded metric/workload handoff, or none>
  unresolved_conditions: []
```

`mode: scope` produces an execution-ready contract with `causal_status: not_run`; it performs no
debugger or capture operation. `mode: operate` consumes a predecessor scope result or supplies the
same scope inline and records exact identity, observations, perturbations, causal status, and safe
session handback. `failure_mechanism_established` is not a root-cause claim. A missing material
trigger, scope, permission boundary, target identity requirement, or graph input returns lifecycle
`not_produced`, not a partial card. The result never authorizes target-state mutation, source repair,
performance work, another debugging node, or successor selection outside an existing Plan edge.

## Worker-Done Body

Send only item kind/ID, node/round, compact outcome, disposition, or attempt status,
finding/advisory/deferred summaries, artifact/evidence anchors, and required start/finish/elapsed
timing. Keep full diagrams, matrices, source analysis, and raw logs in their owning artifact or
worker context.
