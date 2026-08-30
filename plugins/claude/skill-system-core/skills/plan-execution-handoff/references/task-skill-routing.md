# DAG Node Skill Routing

Use this table as examples, not as a reason to attach every skill. Select one primary
workflow for the node and only the support skills that its actual question requires.
Copy canonical IDs exactly. If a skill is not exposed in the current session, mark the
routing unresolved instead of inventing an alias.

Workflow-family roles are explicit: `execution_primary` skills may own executable DAG nodes.
Execution assurance is a contract attached to an owning node, not a skill, node, or successor
selector; load `references/execution_assurance_contract.md` only on its risk trigger.

Select the graph archetype first from `graph-method-profiles.md`; then route each compiled node.
The node code is not a role or an agent identity.

| Node kind | Default role | Primary or supporting skill examples | Routing rule |
|---|---|---|---|
| `R0` baseline and ownership | Coordinator | none; copied Plan/Handoff contract | Read the compact baseline once before dispatch; the canonical pair is the execution state and no planning or external runner skill is attached. |
| `MAP-HLD` product/repository map | Architect or read-only map owner | `skill-system-dev:analysis-codebase-map` | Request `hld` explicitly, bind it to the named product/repository slice, and return only a compact result plus artifact anchor to the Coordinator. |
| `MAP-LLD` module/actual-path map | Architect or reviewer | `skill-system-dev:analysis-codebase-map` | Use LLD for a named module, path, runtime flow, or changed caller path. |
| `D-BOUNDARY` module/seam decision | Architect | `skill-system-dev:analysis-boundary-design` | Compare keep-local and at most two moves; return one evidenced boundary. |
| `D-DOMAIN` identity/state decision | Architect | `skill-system-dev:analysis-domain-modeling` | Use when domain language, identity, state transitions, invariants, or ownership are open. |
| `D-ALGORITHM` technical approach | Architect | `skill-system-dev:analysis-algorithm` | Compare concrete candidates and define falsifiable selection evidence. |
| `D-PERF` performance approach | Architect | `skill-system-dev:analysis-performance` | Diagnose the representative latency/CPU/memory path before choosing optimization. |
| `DBG0` debugging scope | Runtime Debugging owner | `skill-system-dev:workflow-runtime-debugging` in `scope` mode | Bind one concrete trigger and return Core `debugging_result` with an execution-ready evidence lane, identity/artifact requirements, permissions/effects, perturbation, stop rules, session handback, and `causal_status: not_run`. Operate no debugger/capture tool and select no successor. |
| `DBG1` runtime debugging operation | Runtime Debugging owner | `skill-system-dev:workflow-runtime-debugging` in `operate` mode | Consume a predecessor scope result or equivalent inline scope, operate only the approved debugger/dump/dynamic/graphics lane, and return Core `debugging_result` with safe session handback and bounded causal status. Follow only existing edges; never auto-repair. |
| `D-BUG` source/log-only failure cause | Architect | no additional skill by default | Keep simple source/log-only diagnosis with the current owner. If repair is the node outcome, route a separate `BF1` node to `skill-system-dev:workflow-bug-fix`. |
| `D-UI` concrete UI design artifact | Design owner | `skill-system-design:workflow-ui-design`; optional decomposer/layout/token/component inputs only when already selected | Create the actual inspectable screen/component design from accepted requirements and return Core `design_result`. Do not write production UI code or create the implementation successor. |
| `D0` accepted design gate | Architect or declared design owner | task-matched analysis skill or none | Close the design/boundary decision before `phase_gate_delivery` implementation begins. |
| `P` runnable discriminator | Prototype owner | `skill-system-dev:workflow-prototype` | Answer one unresolved question with an isolated artifact and an explicit proof ceiling. |
| `C` direct feature slice | Implementation owner | `skill-system-dev:workflow-implementation` | Use for a concrete delegated production slice after its decisions close; return the Core `implementation_result` card. |
| `C-UI` design-to-code implementation | UI implementation owner | `skill-system-design:design-frontend` | Consume the accepted Core `design_result`, implement the repo-integrated surface, and return Core `implementation_result` with the design reference. Never select Code Review or another gate. |
| `TD` / `TD0` software Test Design | Test Design owner | `skill-system-testing:workflow-test-design`; only the test specialists already selected for material subquestions | Consume an executable target snapshot or accepted external contract plus authoritative basis and return Core `test_design_result`. Visual regression uses explicit `design` mode only. If one human-owned judgment blocks the design, conditionally use `skill-system-testing:plan-test-discovery`, yield without a result, and resume only after its decided IDs are admitted by the required Plan revision. |
| `TI` / `TI0` software Test Implementation | Test Implementation owner | `skill-system-testing:workflow-test-implementation`; only evidence-surface specialists named by the test contract | Consume Core `test_design_result` or a complete inline authoritative contract, write only the bounded test assets, execute the assigned conditions, and return Core `test_implementation_result`. Visual regression uses explicit `evidence` mode only. A failing condition is not repair authority. |
| `TCR` / `TCR0` test implementation static review | Review owner | `skill-system-dev:workflow-code-review` | Review one `test_implementation_result` against its optional `test_design_result` baseline. Production and test implementation cards use separate review nodes when both require review. |
| `BF1` / `BF2` concrete repair | Implementation owner | `skill-system-dev:workflow-bug-fix` | Run exactly the assigned A1 or A2 intervention and return `bug_fix_result`; only concrete CR1 `repair_required` plus an existing BF2 node authorizes A2. |
| `RF` behavior-preserving restructure | Implementation owner | `skill-system-dev:workflow-refactor-safely` | Preserve the established observable contract and validate each reversible batch. |
| `DEP` dependency/runtime upgrade | Implementation owner | `skill-system-dev:workflow-dependency-upgrade` | Keep migration and verification bounded to one dependency or runtime. |
| `M` obsolete-code/comment maintenance | Implementation owner | `skill-system-dev:workflow-source-maintenance` | Use only after behavior is established; do not hide feature or refactor work here. |
| `R-STATIC` / `CR0` / `CR1` / `CR2` static review | Coordinator or declared review owner | `skill-system-dev:workflow-code-review`; optional `analysis-codebase-map` aid; execution assurance only on the owning node's risk trigger | Return `pass`, `repair_required`, or `complete_with_deferred_items` under the Core item contract. Assurance never becomes another node, and the mandatory Workflow does not by itself require a fresh independent agent. |
| `I` fan-in integration | Coordinator | none; copied Plan/Handoff contract | Integrate only completed predecessors with non-overlapping ownership and keep increment status separate from integrated status. |
| `V` integration evidence | Coordinator | none unless the Plan names a verifier skill | Consume the compact `worker_done` body or Core `test_implementation_result` first; read one relevant artifact slice only if the decision otherwise cannot be made. Run only the verifier already named by the plan. Condition Fail does not create repair authority or a successor. |
| `V-DESIGN` scoped design evidence | Declared evidence owner | one of `design-tokens`, `design-component-mapper`, `design-visual-regression`, or `design-a11y-audit` only when named by the Plan | Verify only the assigned condition. Return compact evidence/gaps without implementation edits, successor selection, automatic retry, or relabeling the Human Test phase. |
| `R1` independent review | Fresh read-only reviewer | `skill-system-dev:workflow-code-review`; optional `analysis-codebase-map` aid | Optional only on explicit current-user request or a higher-priority repository/accepted-plan contract. Independence changes the reviewer, not the review-card meaning. |
| `RES-*` selected Research artifact | Research node owner | `skill-system-research:workflow-research` plus exactly one Plan-selected `skill-system-research:research-*` stage skill | Read `references/research_stage_contract.md`. The Workflow owns one node envelope and returns Core `research_result`; the selected specialist owns scientific method/artifact meaning. Search evidence remains a separate explicit node. Neither owner creates a successor. |
| `T0` human-test-ready transition | Coordinator | none | Close the current Waterfall immediately before Human Test with target/procedure plus new-worklist/design seeds; no agent waits, and test results never reopen this pair. |

## Lifecycle Routing

- Worker automation owns dispatch-input detection, inbox checks, follow-up consumption,
  heartbeat, and `worker_done`. Its start receipt confirms those capabilities; unavailable
  automation stays unresolved and is never replaced by Coordinator polling.
- Heartbeats remain worker-side liveness messages. They do not wake the Coordinator. Only an
  externally notified `question`, `escalation`, or `worker_done` permits one non-waiting
  check of the Coordinator's own mailbox. The Coordinator never consumes the worker inbox.
- Worker lifecycle bodies contain only outcome, artifact anchors, latest decisive evidence,
  remaining risk/open question, next owner, and start/finish/elapsed timing. Do not send
  transcript, raw source analysis, repeated terminal output, or large Git status/diff/plan dumps.
- Give every node one rough Expected timing. The Coordinator compares it once at `worker_done`
  and records `on_track`, `overrun_observed`, or `unknown`; timing never blocks or retries a node.
- Normal completion is `worker_done` only. A confirmed delivery failure permits one bounded
  resend or reconciliation attempt; then stop without polling.
- A worker that needs approval sends one `question`, continues independent authorized work, and
  yields its active turn. The session stays passively resumable from a later inbox follow-up;
  hours of human-response latency never become a timeout, retry, or DAG-level `blocked` state.
- Never schedule fixed-interval or busy waits for liveness. Sustained CPU/thermal pressure or a
  `kernel_task` spike stops the wait/process loop after one compact observation and requires an
  operator decision; it does not establish the cause.

## Compiled Graph Rules

- The Mermaid Task DAG is a finite execution instance. Spiral cycles, repair, re-review, and
  re-test append new uniquely named nodes under budget; they never point back to an executed node.
- `single_node_execution` has one executable workflow node after its baseline. It uses the
  Plan/Handoff pair for durable pause/resume and never creates a hidden state artifact or runner.
- Give every Mermaid edge one row in `Typed Edges` using the vocabulary declared by
  `graph-method-profiles.md`.
- `DAG Node Routing` records node kind and minimum Context / input. Do not send the entire plan,
  source tree, or another worker's transcript merely because the node follows it. It also records
  one advisory Expected timing, never a deadline or polling interval.
- `phase_gate_delivery` is the default when phase ownership is clear: lock-safe design and
  implementation work may fan out, all required slices fan in at `R-STATIC`, and the current DAG
  terminates at `T0` human-test-ready. Agent-side build/static/smoke nodes are optional support,
  not the Test phase. Human results plus a new worklist/design start a new Waterfall rather than
  reopening this pair. Choose another archetype only when its decisive condition is present.
- Cross-owner implementation, review, deferred, repair, and Known Bug results use the Core-owned
  `references/execution_item_contract.md`. Workers never select successor IDs or graph termination.
- Runtime Debugging nodes use Core `debugging_result`. `DBG0` scope performs no tool operation;
  `DBG1` operate consumes an accepted scope and preserves identity, effects, proof ceiling, and
  session handback. Neither node creates a repair, performance, test, or follow-up debugging node.
- Explicit software Test Design and Test Implementation nodes use Core `test_design_result` and
  `test_implementation_result`. They are agent-machine evidence under the selected test authority;
  they do not relabel or replace Human Test. A Test Design node that needs human-owned oracle input
  remains in progress and uses the package-local Test Discovery decision path; it emits no partial
  card and never edits Plan/Handoff itself.
- Research nodes use `references/research_stage_contract.md`; `workflow-research` manages exactly
  one preselected stage and returns `research_result`. A stage artifact is not authority to start
  the next stage. A scaffold node owns wiring only, a statistical result requires adequate data,
  and peer review gates only when the Plan explicitly says so.
- Design nodes use `references/design_stage_contract.md`; only `design-frontend` writes production
  UI, and each evidence node closes only its named condition. A design result or evidence finding
  never starts implementation, repair, another gate, or Human Test.

Context helpers may be added only when the repository declares the source and the node needs it:

- `skill-system-core:management-memory-bank-harness` for a small matching active Memory slice.
- `skill-system-core:management-knowledge-base-read` for a bounded declared Knowledge slice.
- `skill-system-core:search-deep-evidence` when a downstream decision genuinely needs
  several independent evidence lanes.

Do not attach `plan-execution-handoff`, a runner, or `workflow-implementation` to the Coordinator's
control role. The Orchestrator applies the copied Plan edges directly; an Implementation owner
receives a bounded concrete slice and uses the task-matched implementation workflow.
