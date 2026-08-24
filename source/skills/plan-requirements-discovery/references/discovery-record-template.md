# Requirements Discovery Record Template

```yaml
discovery_record:
  kind: requirements_discovery_record
  plan_id:
  status: active | ready_for_distillation | stopped_with_open_questions
  source_refs: []
  goal:
  target_users: []
  decisions:
    - id: DEC-001
      depends_on: []
      question:
      answer:
      rationale:
      status: decided
      source:
  fact_findings:
    - id: FACT-001
      statement:
      source:
      unblocks: []
  domain_terms: []
  constraints: []
  non_goals: []
  edge_cases: []
  acceptance_signals: []
  assumptions: []
  open_questions: []
  ready_questions: []
  deferred_questions:
    - id:
      waiting_on: []
      impact:
  handoff_target: plan-requirements-brief
```
