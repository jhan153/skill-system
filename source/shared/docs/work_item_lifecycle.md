# WorkItem Lifecycle

WorkItem is the 8.5.0 state model for work that needs durable lifecycle governance before it becomes a `TaskRun`, a `LoopRun`, or an external board card.

It is not a queue runtime, scheduler, autonomous worker, Kanboard replacement, or LoopRun replacement.

## State Model

```text
triage -> explore -> ready -> implement -> verify -> review -> closed
blocked is allowed from any non-closed state and must record a reason plus next action
```

Allowed states:

- `triage`: decide whether the item is real, in scope, and owned.
- `explore`: gather enough context to make it executable.
- `ready`: scope, owner, primary skill, and next action are clear.
- `implement`: bounded execution is active, usually through ordinary workflow or a `TaskRun`.
- `verify`: evidence is being collected.
- `review`: residual findings or acceptance decisions are being checked.
- `blocked`: progress needs user input, permission, external state, or a scope decision.
- `closed`: required evidence exists and no open or blocked findings remain.

## Artifact Shape

Canonical schema:

- `.codex/schemas/workitem/work-item.schema.json`

Example:

- `.codex/schemas/workitem/examples/work-item.example.yaml`

Validation:

```bash
python3 .codex/tools/validate_work_item.py .codex/schemas/workitem/examples/work-item.example.yaml
```

## Evidence Gate

WorkItem completion is evidence-bound:

- `history[-1].state` must match `state`.
- state transitions must follow the lifecycle order, except `blocked` can interrupt and then resume to a concrete state.
- `closed` requires non-empty `evidence_refs`.
- `closed` is invalid when any finding is `open` or `blocked`.
- `blocked` requires `blocked_reason` and a non-empty `next_action`.
- runtime boundary flags must stay false unless a separate orchestration capability contract verifies those capabilities.

## Relationship To TaskRun

Use a `TaskRun` when a WorkItem enters `implement`, `verify`, or `review` and the work needs resume-safe step/finding state.

`TaskRun` remains narrower than WorkItem:

- WorkItem owns lifecycle state and source/ownership context.
- TaskRun owns checkpointed steps, findings, and final verification for an execution slice.
- TaskRun may reference a WorkItem with `work_item_ref`.
- Closing a TaskRun does not automatically close the WorkItem.

## Relationship To LoopRun

Use a `LoopRun` only when repeated verifier-feedback convergence is required and a valid loop contract exists.

WorkItem can point to a LoopRun with `loop_run_ref`, but it does not inherit LoopRun budgets, retry policy, Stop continuation, or verifier governance.

## Relationship To Kanboard

Kanboard may project or mirror WorkItem state only after an explicit integration decision.

The WorkItem schema intentionally records:

```yaml
runtime_boundary:
  mode: state_model
  queue_runtime: false
  scheduler_runtime: false
  kanboard_source_of_truth: false
  looprun_replacement: false
```

This keeps 8.5.0 as lifecycle governance, not an automation runtime.
