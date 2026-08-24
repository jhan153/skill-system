# Core Execution Item Role View

Generated from the canonical Core execution-item contract for `workflow-implementation`. Do not edit this projection.

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
| production implementation result | the assigned implementation Workflow |
| read-only static disposition and review findings | `workflow-code-review` or the named review owner |
| one assigned repair intervention and attempt observation | `workflow-bug-fix` |
| Human Test observation and product/design judgment | user or explicitly declared human owner |

One producer owns each item. Consumers may record or route it, but they never reinterpret its
kind into authority they do not own. An execution item never creates a Plan node, rewrites an
edge, selects a successor ID, closes a graph, or waits/polls.

## Common Envelope

Use the smallest applicable fields. `plan_ref` and `node_id` are required only in graph mode.

```yaml
execution_item:
  contract_id: core-execution-items-v1
  item_id: <stable task-local id>
  kind: design_result | research_result | implementation_result | code_review_result | deferred_item |
        bug_fix_result | known_bug_candidate | known_bug_record
  producer: <canonical plugin:skill id or current owner>
  plan_ref: <plan id/revision or null>
  node_id: <Plan node id or null>
  scope_ref: <bounded design/research/behavior/review/repair scope>
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

- produces: `references/core-execution-items-v1/cards/implementation_result.md`
- consumes: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Selected Item Kinds

### `implementation_result`

Producer: assigned implementation Workflow. Consumers: Code Review and the execution owner.

```yaml
payload:
  implementation_snapshot: <commit/diff/worktree identity>
  design_result_ref: <design_result item id or null>
  changed_artifacts: []
  implemented_conditions: []
  review_slice: <bounded files/flow>
  unresolved_conditions: []
```

The producer reports the implemented scope and snapshot. It does not mark a review pass or choose
the review/next node.

### `code_review_result`

Producer: `workflow-code-review` or the named read-only review owner. Consumers: Coordinator and,
for concrete findings only, Bug Fix.

```yaml
payload:
  input_item_ref: <implementation_result or bug_fix_result item id>
  design_baseline_ref: <design_result item id or null>
  review_round: <R0, R1, R2, or local review id>
  implementation_snapshot: <reviewed identity>
  review_slice: <bounded files/flow>
  review_disposition: pass | repair_required | complete_with_deferred_items
  findings: []
  deferred_item_refs: []
  known_bug_exclusions: []
  transition_intent: continue | repair
```

Disposition precedence is `repair_required` over `complete_with_deferred_items` over `pass`.
A required current-scope implementation omission is `repair_required`, never deferred. A runtime
unknown alone does not invalidate a completed static review.

### `bug_fix_result`

Producer: `workflow-bug-fix`. Consumers: Code Review and the execution owner.

```yaml
payload:
  round: A1 | A2
  source_review_item_ref: <repair_required code_review_result item id>
  source_findings: []
  bug_scope: <affected behavior>
  failure_fingerprint: <stable fingerprint>
  hypothesis: <one causal claim>
  changed_artifacts: []
  changed_snapshot: <identity or null>
  original_signal_observation: <one bounded observation or unavailable reason>
  attempt_status: resolved | narrowed | moved | unchanged | unreproducible
  change_disposition: kept | rolled_back | retained_with_known_bug
  review_anchor: <identity or null>
  postcondition: changed_snapshot_ready_for_review | no_change_unresolved
  known_bug_candidate_ref: <item id or null>
```

In graph mode, one BF node owns exactly its assigned intervention and returns. `A2` requires an
existing assigned node plus concrete `CR1 repair_required` findings. Attempt status is an
observation, not a review disposition or permission to continue. A no-change result does not
create an empty review or retry cycle.

### `known_bug_record`

Producer: Coordinator/Handoff in graph mode; in standalone mode, the bounded Bug Fix owner may
produce it after its own final local review. Consumers: current review/test/validation owners and
the next Waterfall.

```yaml
payload:
  known_bug_id: <stable local id>
  candidate_ref: <known_bug_candidate item id>
  bug_scope: <affected behavior>
  failure_fingerprint: <stable fingerprint>
  expected: <condition and authority>
  observed: <terminal unresolved observation>
  attempt_refs: [<one or two repair-attempt item ids>]
  terminal_review_ref: <review/verifier item id>
  latest_attempt_status: narrowed | moved | unchanged | unreproducible
  change_disposition: kept | rolled_back | retained_with_known_bug
  condition_status: excluded_known_bug
  reopen_when: <new evidence or explicit future scope>
```

The record is unresolved and locally terminal for the current run. It is neither a pass nor a
global blocker. Current-run review/test/validation emits `SKIP — excluded Known Bug <id>` and does
not reopen it or expand validation. The Coordinator follows the existing Plan, including its
normal terminal node such as `human_test_ready`; there is no `partial_handoff` fallback.

## Worker-Done Body

Send only item kind/ID, node/round, compact outcome, disposition, or attempt status, finding/deferred
summaries, artifact/evidence anchors, and required start/finish/elapsed timing. Keep full diagrams,
matrices, source analysis, and raw logs in their owning artifact or worker context.
