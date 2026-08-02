# Coordination Handoff Schemas

Use only the shape requested; omit empty fields.

## Brief

```yaml
goal_brief:
  objective:
  non_goals: []
  do_not_touch: []
  success_signal:
  not_a_completion_claim: true
task_dag:
  - task_id:
    depends_on: []
    expected_output:
    validation_owner:
```

## Multi-agent handoff

```yaml
task_cards:
  - task_id:
    owner:
    purpose:
    selected_skills: []
    allowed_files: []
    do_not_touch: []
    lock_scope:
    depends_on: []
    expected_output:
    validation_owner:
integration_owner:
serialization_order: []
```

Use `selected_skills` only for exact canonical IDs already chosen for that task. Include those IDs verbatim in the worker instruction. Omit the field when the upstream owner made no selection; the worker then follows normal implicit routing. Never populate it by guessing from a nearby skill name.

For a completed handoff, add only observed fields:

```yaml
handoff:
  task_id:
  changed: []
  not_changed: []
  validation_done: []
  remaining_risk: []
  next_owner:
```

## Artifact inventory

```yaml
artifact_inventory:
  changed_files: []
  generated_artifacts: []
  validation_evidence: []
  user_verification_needed: []
  stale_followups: []
  excluded_items: []
```

Every validation item must use `agent-verified`, `user-verification-needed`, `unverified`, or `blocked`. If no artifacts are available, return `blocked` with the missing diff or artifact list instead of inventing entries.
