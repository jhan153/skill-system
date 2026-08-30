# Core Execution Item Contract

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

## Item Kinds

### `design_result`

Producer: `workflow-ui-design`. Consumers: `design-frontend`, Code Review when it receives the
design as a conformance baseline, and the execution owner.

```yaml
payload:
  design_snapshot: <artifact set identity>
  target_surfaces: []
  requirements_refs: []
  viewports_and_states: []
  visual_decisions: []
  token_and_component_intent: []
  implementation_handoff: <bounded design-to-code contract>
  unresolved_decisions: []
```

The producer reports an inspectable design and implementation handoff. It does not claim
production UI code, component reuse, rendered fidelity, accessibility, Human Test, or successor
selection. Proposed token/component relationships remain intent until their owning evidence or
implementation path confirms them.

### `research_result`

Producer and consumer across Research DAG nodes: `workflow-research`. Recorder: the execution
owner. The accepted Plan or explicit user request selects one Research stage skill before work.

```yaml
payload:
  stage_skill: <one canonical skill-system-research:research-* id>
  input_refs: []
  result_summary: <bounded stage outcome>
  result_ceiling: <what this stage output does and does not establish>
  unresolved_inputs: []
  user_checks: []
```

The producer manages one node envelope and applies exactly one selected Research specialist. It
does not classify a vague request, run several stages, acquire a missing prerequisite, emit a card
for `not_produced` work, select a successor, or mutate Handoff. Downstream Research nodes consume
the item only as an artifact/evidence locator under an already accepted Plan edge.

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

### `test_design_result`

Producer: `workflow-test-design`. Consumers: `workflow-test-implementation`, Code Review when it
reviews test implementation against the contract, and the execution owner.

```yaml
payload:
  test_design_snapshot: <test-design artifact identity>
  test_design_scope: <bounded SUT and condition scope>
  target_snapshot: <SUT implementation/prototype/external-contract identity>
  test_profile: []
  test_basis_refs: []
  condition_ids: []
  actual_path: <representative executable or accepted external-contract path; mark unobserved when contract-only>
  oracle_contracts: []
  environment_and_horizon: []
  diagnostic_and_falsifier_contract: []
  implementation_handoff: <bounded test-only implementation contract>
  proof_ceiling: <what the designed test may and may not establish>
  human_decision_refs: []
  unresolved_decisions_or_testability_gaps: []
```

The producer reports an implementation-ready test contract. It does not claim test code, execution,
condition Pass/Fail, production repair, Human Test, or successor selection. An open material field
produces no card; a human-owned gap uses package-local Test Discovery and the required Plan revision.

### `test_implementation_result`

Producer: `workflow-test-implementation`. Consumers: Code Review and the execution owner.

```yaml
payload:
  implementation_scope: <bounded test-only write and condition scope>
  test_design_result_ref: <test_design_result item id or null for direct authoritative mode>
  inline_contract_refs: []
  target_snapshot: <tested SUT identity>
  test_asset_snapshot: <test implementation identity>
  changed_test_artifacts: []
  condition_results:
    - condition_id: <accepted condition id>
      status: pass | fail | inconclusive | unavailable | skipped_known_bug
      observation: <bounded observed result>
      evidence_refs: []
      known_bug_ref: <known_bug_record item id or null>
  execution_summary: <bounded observed result or unavailable reason>
  falsifier_result: <required challenge observation or unavailable reason>
  design_conformance: <contract conformance and deviations>
  proof_ceiling: <observed evidence ceiling>
  known_bug_exclusions: []
  review_slice: <bounded test files/flow>
  unresolved_design_testability_or_environment_gaps: []
```

The producer reports test-only implementation and honest condition-scoped observation. Workflow
completion is not product Pass. A failing condition does not authorize repair, and a direct-mode
result still requires a complete authoritative inline test contract. A material design,
authority, testability, environment, required-asset, or required-falsifier gap returns lifecycle
`not_produced` and emits no partial card.

### `code_review_result`

Producer: `workflow-code-review` or the named read-only review owner. Consumers: Coordinator and,
for concrete findings only, Bug Fix.

```yaml
payload:
  input_item_ref: <implementation_result, test_implementation_result, or bug_fix_result item id>
  design_baseline_ref: <design_result item id or null>
  test_design_baseline_ref: <test_design_result item id or null>
  review_round: <R0, R1, R2, or local review id>
  implementation_snapshot: <reviewed identity>
  review_slice: <bounded files/flow>
  review_coverage:
    covered_effect_ids: []
    activated_risk_axes: []
    material_unassessed: []
    conformance_scope: intrinsic_only | baseline_compared
  review_ceiling: <what this static review does and does not establish>
  review_disposition: pass | repair_required | complete_with_deferred_items
  findings: []
  advisories: []
  deferred_item_refs: []
  known_bug_exclusions: []
```

Disposition precedence is `repair_required` over `complete_with_deferred_items` over `pass`.
A required current-scope implementation omission is `repair_required`, never deferred. Findings
use P0/P1/P2, tight code refs, current impact, a mandatory repair `required_condition`, and only an
optional non-normative solution. Advisories never change disposition or create repair/deferred
authority. `pass` requires empty findings, deferred refs, and material-unassessed coverage; it is
limited to the declared static review ceiling and is not runtime, test, merge, or product approval.
Every cross-owner `code_review_result` envelope includes at least one `artifact_refs` entry for the
source-linked Mermaid review artifact required by the static Code Review contract.

### `deferred_item`

Producer: the owner that identified a non-repair item. Consumer: Coordinator/Handoff and the
declared later human or Waterfall owner.

```yaml
payload:
  deferred_kind: design_decision | runtime_observation | out_of_scope_work |
                 static_evidence_gap | ambiguous_requirement
  description: <precise unresolved item>
  impact: <bounded consequence>
  code_refs: []
  baseline_refs: []
  carry_to: human_test | next_waterfall_design | next_waterfall_worklist
```

Create a deferred item only when it can materially change a later decision or outcome, is not a
current-scope repair, has a named later owner or observation point through `carry_to`, and would
otherwise lose a material risk or authority gap. Nice-to-have cleanup, generic questions,
speculative reuse, style preference, and ordinary advisories do not become durable deferred work.
Deferred means the producing node is complete for the current run. It never authorizes automatic
evidence acquisition, design work, re-review, repair, or waiting. The execution owner preserves it
and follows an existing Plan edge.

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

### `known_bug_candidate`

Producer: Bug Fix after bounded attempt evidence exists. Consumer: the execution owner.

```yaml
payload:
  bug_scope: <affected behavior>
  failure_fingerprint: <stable fingerprint>
  expected: <condition and authority>
  latest_observed: <latest unresolved observation>
  attempt_refs: [<one or two repair-attempt item ids>]
  latest_attempt_status: narrowed | moved | unchanged | unreproducible
  change_disposition: kept | rolled_back | retained_with_known_bug
  reopen_when: <new evidence or explicit future scope>
```

A candidate is evidence, not state. It cannot exclude a condition, skip a verifier, or choose a
successor before the execution owner combines it with the terminal review/verifier result.

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

## Coordinator Consumption

```text
design_result -> assigned UI implementation or existing Plan successor
research_result -> existing Plan successor
debugging_result -> existing Plan successor; scope/operate/repair routing follows only accepted edges
implementation_result -> assigned Code Review
test_design_result -> assigned Test Implementation or existing Plan successor
test_implementation_result -> assigned Code Review or existing Plan successor
code_review_result repair_required -> assigned BF1 or BF2
bug_fix_result changed_snapshot_ready_for_review -> assigned CR1 or CR2
code_review_result pass -> existing Plan successor
code_review_result complete_with_deferred_items -> preserve items -> existing Plan successor
terminal repair_required + bounded candidate -> final Known Bug -> existing Plan successor
```

Only an already accepted execution source may authorize these nodes. When no implementation node
remains, follow the existing terminal node; do not invent an early-close state. A real missing
external prerequisite is a Coordinator lifecycle result under the active work contract, not a
Workflow card disposition.

## Worker-Done Body

Send only item kind/ID, node/round, compact outcome, disposition, or attempt status,
finding/advisory/deferred summaries, artifact/evidence anchors, and required start/finish/elapsed
timing. Keep full diagrams, matrices, source analysis, and raw logs in their owning artifact or
worker context.

## Adoption

| Participant | Produces | Consumes |
| --- | --- | --- |
| `skill-system-design:workflow-ui-design` | `design_result` | none |
| `skill-system-research:workflow-research` | `research_result` | predecessor `research_result` items named by its assigned node |
| `skill-system-dev:workflow-runtime-debugging` | `debugging_result` | optional predecessor `debugging_result` named by its assigned node |
| `skill-system-design:design-frontend` | `implementation_result` | `design_result`, final review/repair evidence when it is the current execution owner |
| `skill-system-dev:workflow-implementation` | `implementation_result` | final review/repair evidence when it is the current execution owner |
| `skill-system-testing:workflow-test-design` | `test_design_result` | optional `implementation_result` target snapshot |
| `skill-system-testing:workflow-test-implementation` | `test_implementation_result` | optional `test_design_result`, `known_bug_record` exclusions |
| `skill-system-dev:workflow-code-review` | `code_review_result`, `deferred_item` | optional `design_result` or `test_design_result` baseline, `implementation_result`, `test_implementation_result`, `bug_fix_result`, `known_bug_record` exclusions |
| `skill-system-dev:workflow-bug-fix` | `bug_fix_result`, `known_bug_candidate`, and standalone-only `known_bug_record` | concrete repair findings from `code_review_result` and supplied `debugging_result` evidence |
| `skill-system-core:plan-execution-handoff` | `known_bug_record` and ledger transition | all graph-mode items |

Other skills adopt only the item kinds they actually exchange. Merely mentioning another skill or
Known Bug does not require this contract.

The canonical Plan/Handoff pair records durable graph-mode cards. A candidate, inline attempt list,
or self-declared exclusion cannot substitute for the final authorized `known_bug_record`.
