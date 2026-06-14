# Team Patterns

Use these patterns only when the user explicitly asks for multi-agent or multi-session coordination.

## pipeline

Sequential ownership. Each step depends on the previous step's output.

Use when:
- validation must happen after implementation
- one artifact feeds the next artifact

Avoid when:
- tasks can be done independently

## fan_out_fan_in

Multiple independent investigations or edits happen in parallel, then one owner integrates findings.

Use when:
- tasks touch different files or domains
- comparison is useful

Avoid when:
- ownership boundaries are unclear

## expert_pool

Specialist agents inspect different domains without owning the final integration.

Use when:
- research, design, QA, or security review needs domain focus

Avoid when:
- a single implementation owner would be simpler

## producer_reviewer

One owner produces a change, another reviews against a defined risk boundary.

Use when:
- the change is risky
- the user asked for critical review

Avoid when:
- the change is small and already directly validated

## supervisor

One owner tracks work split and validation responsibility without doing all task work.

Use when:
- there are many independent subtasks
- file ownership matters

Avoid when:
- it would create persistent workflow machinery

## Response-First Task Card

Use a task card when work is split across agents or sessions. Keep it in the current response or in an explicitly requested handoff document.

```yaml
task_card:
  task_id:
  owner:
  purpose:
  allowed_files: []
  do_not_touch: []
  lock_scope:
  inputs: []
  expected_output:
  review_required: true
  validation_owner:
  handoff_note:
```

Rules:
- `lock_scope` should be a file list, directory list, or clearly named doc section.
- `validation_owner` must be one owner, usually `main_agent` for final integration.
- If two cards need the same file, mark them sequential instead of parallel.

## Handoff Packet

```yaml
handoff_packet:
  task_id:
  owner:
  lock_scope:
  changed: []
  not_changed: []
  validation_done: []
  remaining_risk: []
  next_agent_should: []
```

Use `not_changed` to prevent the next agent from assuming scope was completed. Use `remaining_risk` for unresolved checks, not as a release or readiness label.

## Goal Brief

```yaml
goal_brief:
  objective:
  non_goals: []
  current_workstream:
  do_not_touch: []
  success_signal:
  not_a_completion_claim: true
```

Use a goal brief only when multiple agents or sessions need a shared target. Do not create app-managed goal state from this bundle.

## hierarchical_delegation

Top-level work is split into subplans only when a large effort genuinely requires it.

Use when:
- the user asks for a planning package
- future continuation needs standalone docs

Avoid when:
- a simple checklist is enough
