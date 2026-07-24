# Requirements Contract Template

```yaml
requirements_contract:
  problem:
  goals: []
  target_users: []
  scope: []
  non_goals: []
  execution_contract:
    mode: attended|unattended_goal_loop
    verification_owner: agent|user|shared|external
    interaction_mode: allowed|forbidden
    excluded_action_classes: []
    on_local_block: reevaluate_remaining_work
    global_block_condition: no_required_runnable_work
    time_budget_seconds:
    stop_condition:
  user_stories:
    - id: US-001
      as_a:
      i_want:
      so_that:
  acceptance_criteria:
    - id: AC-001
      statement:
      evidence:
  assumptions: []
  risks: []
  open_questions: []
  handoff_notes:
    recommended_next_skill:
```
