---
name: coordination-multi-agent
description: Coordinates explicit multi-agent handoff notes, lock scopes, and review responsibilities for 7.1 without persistent workflow harness state.
---

# Multi-Agent Plan Executor

## Routing Card
- role: support
- intent_signature:
  - multi-agent handoff
  - lock scope
  - responsibility split
  - review ownership
  - merge coordination
- use_when:
  - the user explicitly asks to split an existing implementation plan across multiple agents or sessions.
  - a handoff note needs file ownership, lock scope, and validation ownership.
- do_not_use_when:
  - one agent can perform the task directly.
  - task ownership, lock scope, or validation ownership is unclear.
  - coordination would require install, deployment, signoff, operational recovery, or evidence-finality machinery.
- expected_inputs:
  - existing plan or task list
  - files in scope
  - ownership and validation constraints
- expected_outputs:
  - human-readable handoff packet
  - lock-scope note
  - validation ownership note
  - no `.agent-workflow` writes
  - no event log
- context_targets:
  must_read:
    - active plan or provided task list
  read_if_needed:
    - `.codex/docs/team_patterns.md`
    - `.codex/context-routing.md`
  do_not_load_by_default:
    - live `$HOME/.codex`
    - credentials
    - historical workflow harness files
- risk_profile:
  reads:
    - current plan context only
  writes:
    - none unless the user explicitly requested a handoff document
  tools:
    - none by default
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Guardrail
- Multi-agent coordination remains descriptive in 7.1.
- Do not create persistent workflow state or system-level status fields.

## Workflow
1. Confirm the user explicitly wants multi-agent or multi-session coordination.
2. Identify independent workstreams and the files each stream may touch.
3. Assign one owner per lock scope. If two streams need the same file, serialize them or assign a single owner.
4. Define expected output and validation owner for each stream.
5. Produce response-first task cards and handoff packets in the current response or an explicitly requested document.
6. Keep final integration with one owner; do not create an event log, status registry, or workflow directory.

## Task Card Schema

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

Required checks:
- `allowed_files` must be narrow enough that another agent can avoid collisions.
- `do_not_touch` must name high-risk or out-of-scope areas.
- `expected_output` must describe the concrete response, doc edit, code edit, or validation evidence.
- `validation_owner` must be one agent or `main_agent`, not "everyone".

## Handoff Packet Schema

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
  do_not_treat_as:
    - persistent event log
    - completion evidence
    - package readiness
```

## Artifact Note Schema

Use an artifact note only inside the response or explicitly requested handoff doc.

```yaml
artifact_note:
  artifact:
  path:
  produced_by:
  purpose:
  evidence_status: agent-observed
  next_use:
  do_not_treat_as:
    - persistent registry entry
    - release decision
    - system-wide completion claim
```

Allowed `evidence_status` values:
- `agent-observed`
- `user-verification-needed`
- `unverified`

## Validation
- A valid split has non-overlapping lock scopes or an explicit serialization order.
- Each task card must have expected output and validation owner.
- Each handoff must distinguish changed, not changed, validation done, and remaining risk.
- If the split adds more process than value, recommend a single-agent execution path instead.
