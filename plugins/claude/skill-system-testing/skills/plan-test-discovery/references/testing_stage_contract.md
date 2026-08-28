# Testing Stage Contract

This contract defines ownership and transition rules for human test-decision discovery, test
design, test-only implementation, execution evidence, and specialist testing methods. It is not a
universal test pipeline, an automatic post-implementation gate, or permission to repair production
code.

Use `testing_strategy_contract.md` for method selection, evidence meaning, and proof ceilings. This
contract owns only stage boundaries and cross-owner handoff.

## Role Ownership

| Requested outcome | Owner | Output ceiling |
|---|---|---|
| human decision needed for a test basis, oracle, tolerance, baseline, horizon, or accepted uncertainty | `plan-test-discovery` | decided or open test-decision record, not a test design or Plan transition |
| complete test contract from an executable SUT or accepted external contract and basis | `workflow-test-design` | Core `test_design_result`, not test code or a product verdict |
| test-only code, fixtures, runners, baselines, and scoped execution | `workflow-test-implementation` | Core `test_implementation_result`, not production repair or global quality |
| SUT and test-level/profile selection | `test-scope-selection` | selected test boundary/profile, not production-boundary redesign |
| positive, negative, edge, state, sequence, and horizon scenarios | `test-scenario-design` | scenario set, not semantic truth or implementation |
| exact, invariant, metamorphic, differential, golden, statistical, or human oracle choice | `test-oracle-design` | oracle contract and authority gaps, not an invented requirement |
| capture, recording, replay, and reality-corpus design | `test-replay-corpus` | provenance and replay contract, not correctness by replay alone |
| visual-regression contract for accepted states/viewports/baseline authority | `test-visual-regression` in explicit `design` mode | implementation-ready visual-regression contract, not capture, diff, or verdict |
| rendered regression evidence against an accepted visual-regression contract | `test-visual-regression` in explicit `evidence` mode | named pixel/framing condition evidence, not redesign, design fidelity, or accessibility |
| ensemble, distributional, tolerance, and chaotic-system oracle design | `test-statistical-oracle` | estimand and decision rule, not product acceptance or fabricated statistics |
| false-green, circular-oracle, surrogate-path, and proof-ceiling review | `test-evidence-review` | test-evidence findings, not implementation or repair |

## Stage Selection

Select the smallest sufficient path. A stage result never starts its successor automatically.

```text
authoritative implementation-ready test contract
    -> workflow-test-implementation

test meaning is settled but scenario/oracle/environment synthesis is material
    -> workflow-test-design -> workflow-test-implementation

workflow-test-design reaches a human-owned unresolved judgment
    -> plan-test-discovery -> explicit Plan consumption/revision when needed
    -> resume workflow-test-design -> workflow-test-implementation
```

Direct Test Implementation still requires an oracle. It may skip Test Design only when the SUT
boundary, test basis, inputs, expected property or result, environment, horizon, diagnostics, and
proof ceiling are already authoritative and no material choice remains.

`test-visual-regression` always locks one explicit `design|evidence` mode. Design never captures or
returns a condition verdict; Evidence never fills a missing contract, changes baseline/tolerance/
mask authority, or falls back to Design. A completed mode never starts the other.

## Test Discovery Interrupt

`plan-test-discovery` is a conditional Planning owner used by Test Design, not a hidden execution
node or a Human Test phase.

Test Design may request Discovery only when:

1. one named test condition cannot be completed without a decision;
2. admitted source or observation cannot resolve it;
3. two or more reasonable choices would change the verdict or proof ceiling; and
4. the decision belongs to a human or other declared authority.

Before asking, Test Design supplies the blocked condition IDs, target snapshot, authority/source
evidence, available observations, options, consequences, recommendation, and independent design
work that can continue. Representative observations are required when the choice claims empirical
current behavior; an accepted external contract may support a normative choice before an executable
SUT exists. Discovery
records the decision in the package-local `inputs/test-decisions.md` artifact owned by
`execution-handoff-inputs-v1`.

- `awaiting_human_event` is Worker/Handoff lifecycle state, never artifact status.
- Send one decision question, finish independent authorized work, and yield without polling.
- A decided row is authority only for its named scope and source. Current implementation output is
  observation until an authorized owner accepts it.
- In graph mode, the active Workflow never edits Plan/Handoff or consumes a new decision silently.
  `plan-execution-handoff` applies Scope Admission and an explicit revision before the same node
  resumes. After recording a decided answer, Discovery sends one `escalation` with the exact
  artifact/request/decision/condition refs; it emits no `worker_done` while Test Design remains in
  progress. A changed objective, owner/boundary, DAG, or completion oracle requires a sibling Plan.
- Discovery never selects a successor, implements a test, or turns a human answer into product
  verification.

## Test Design

Test Design starts only after a minimum executable SUT or accepted external contract exposes a
representative actual or contract path and observable signal. It may design from an authoritative specification or
from partial invariant, metamorphic, differential, statistical, or explicitly accepted
characterization authority. It never promotes current behavior into truth by observation alone.

A complete design names:

- target snapshot and SUT/test boundary;
- test basis and authority for every condition;
- positive plus material negative, edge, or falsifying scenarios;
- data provenance and representative actual or accepted external-contract path;
- oracle regime, tolerances or decision rule, and independence limits;
- environment, seed/clock/viewport/load, sequence, and execution horizon;
- required diagnostics and proof ceiling;
- bounded test-only implementation handoff; and
- unresolved decisions or testability gaps.

If a material field remains open, no `test_design_result` is produced. A human decision request
uses Test Discovery. A missing production observation or hook is a current gap only when the
selected condition or decision is empirical; contract-only design records it as a later Test
Implementation prerequisite and never claims runtime evidence.

## Test Implementation

Test Implementation owns only requested test assets and their scoped execution. Production source
is read-only unless a separately assigned production Workflow owns a change.

It may create or change test code, fixtures, generators, corpus metadata, capture/replay tooling,
approved baselines, test-only configuration, runners, and diagnostic artifacts. It must not change
the SUT contract, oracle, tolerance, baseline authority, scenario meaning, environment, horizon, or
proof ceiling to obtain Green. An infeasible or conflicting contract returns the exact design or
testability gap.

Implementation may consume either a Core `test_design_result` or a complete inline authoritative
test contract. It records the target and test-asset snapshots, condition results, diagnostic
artifacts, design conformance, falsifier observation, proof ceiling, and unresolved conditions.
It emits no Core result when a material design/authority/testability/environment gap, required test
asset, or required falsifier prevents completion of the assigned test contract. That lifecycle is
`not_produced`, not a partial test result or a condition Fail.

## Evidence And Completion

Workflow completion and test verdict are different:

- Test Design completes when an implementation-ready test contract is produced.
- Test Implementation completes when the accepted contract is implemented and honestly observed.
- A condition may pass, fail, remain inconclusive, be unavailable, or be skipped as an excluded
  Known Bug without changing whether the Workflow completed its assigned work.

A test failure never authorizes repair. The Coordinator or direct task owner classifies the result
under the accepted contract and assigns any production repair, test-contract revision, or later
observation separately. Passing evidence closes only the exercised condition, path, environment,
state, and horizon.

## Execution Handoff Integration

- `workflow-test-design` produces Core `test_design_result` in graph mode.
- `workflow-test-implementation` consumes an optional `test_design_result`, produces Core
  `test_implementation_result`, and observes current-run `known_bug_record` exclusions.
- `workflow-code-review` may review a test implementation against its Test Design baseline.
- `plan-execution-handoff` records both Core cards and applies only existing Plan edges.
- Test specialist skills return task-local artifacts or condition evidence; they do not emit Core
  cards, select successors, or manufacture a Test phase.
- Human Test and qualitative product acceptance remain with the user or declared human owner.

## Discriminating Cases

- **Positive:** A chaotic simulation exposes state and diagnostics. Test Design selects invariant,
  metamorphic, and ensemble candidates; a human decides the acceptable tail-risk threshold through
  Test Discovery; Test Implementation realizes the frozen contract without changing it.
- **Direct edge:** A pure conversion has an authoritative input/output table and an existing test
  runner. Test Implementation proceeds without Test Design while preserving the table as oracle.
- **Negative:** A rendered or numeric result differs, so Test Implementation replaces the baseline,
  widens tolerance, reduces repetitions, or swaps in a mock-derived input until Green. This is a
  test-contract violation, not successful implementation.
