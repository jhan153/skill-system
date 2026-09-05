# Requirements Contract Template

Project only material sourced working-state entries into this existing artifact. Keep binding
constraints in scope/non-goals with their authority; identify soft preferences in handoff notes
unless the named owner explicitly adopted them as requirements. Preserve any dynamic dependency's
refresh obligation alongside its source and affected criterion. Unverified, stale, assumed, or
conflicting input remains visible in assumptions/risks/open questions and cannot establish an
accepted criterion. `execution_contract` retains execution authority only; do not put epistemic
state, confidence history, or elicitation decisions there. These notes add no mandatory envelope
or persistence beyond the owning skill's existing contract.

```yaml
requirements_contract:
  kind: requirements_contract
  plan_id:
  status: proposed | accepted
  authority_owner:
  source_refs: []
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
