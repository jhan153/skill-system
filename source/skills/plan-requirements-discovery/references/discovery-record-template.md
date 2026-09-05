# Requirements Discovery Record Template

Use this artifact only under the skill's existing persistence authority. When material working
state is projected, preserve hard/soft meaning and its authority/source in `constraints` or the
decision rationale; keep observed/inferred/assumed status distinct from a decision's status. A
dynamic fact's `statement` may name its last relevant observation, refresh condition, and affected
decision IDs; `source`/`unblocks` retain provenance/dependencies. Omit irrelevant annotations and
do not add a second envelope or elicitation history. Stale facts do not unblock decisions until
refreshed; a correction invalidates only actual dependents.

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
