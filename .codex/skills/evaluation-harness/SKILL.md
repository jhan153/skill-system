---
name: evaluation-harness
description: Reviews runtime usage eval cases as field-quality examples for routing and output improvement.
---

# Evaluation Harness

## Routing Card
- role: support
- intent_signature:
  - runtime usage eval
  - routing case review
  - negative routing
  - usage quality case
  - field quality examples
- use_when:
  - the user asks to inspect or improve `.codex/eval` usage cases.
  - routing, negative routing, context, memory, handoff, design, or research cases need consistency review.
- do_not_use_when:
  - the user wants release governance, readiness signoff, or broad bundle validation.
  - the request is ordinary code execution unrelated to usage cases.
  - the work would create deployment, signoff, operational recovery, or evidence-finality machinery.
- expected_inputs:
  - `.codex/eval/*.yaml`
  - `.codex/docs/skill_registry.md`
- expected_outputs:
  - concise findings in the current response or an explicitly requested usage-quality note
  - no generated report directory
  - no readiness decision
  - no live settings mutation
- context_targets:
  must_read:
    - `.codex/eval`
    - `.codex/docs/skill_registry.md`
  read_if_needed:
    - `.codex/context-routing.md`
    - `.codex/research-routing.md`
  do_not_load_by_default:
    - live `$HOME/.codex`
    - archived sessions
    - credentials
- risk_profile:
  reads:
    - local bundle files only
  writes:
    - none unless the user explicitly asks to edit eval cases
  tools:
    - optional read-only bundle hygiene check
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Boundary
- Runtime usage eval is for observing skill quality in real use.
- Release governance and readiness signoff belong to the owning release workflow.

## Workflow
1. Select a small representative case set from `.codex/eval`.
2. Compare the expected primary/supporting skills with the observed behavior from a real or dry-run request.
3. Record routing, context, output shape, and friction using the manual result capture fields.
4. Map each finding to candidate changes in eval cases, routing docs, registry notes, or skill text.
5. Keep the result focused on usage-quality observations and improvement candidates.

## Manual Result Capture Fields

```yaml
result_capture:
  case_id:
  request_date:
  evaluator:
  observed_primary_skill:
  observed_supporting_skills: []
  context_overload: false
  unexpected_trigger: []
  missing_trigger: []
  output_shape_match: true
  friction:
  follow_up_change:
  verification: unverified
```

Allowed `verification` values:
- `agent-verified`
- `user-verification-needed`
- `unverified`

## Result Mapping
- `unexpected_trigger` -> add or adjust `negative_routing_cases.yaml`, then consider `context-routing.md` trigger guard changes.
- `missing_trigger` -> add or adjust `routing_cases.yaml`, then consider `SKILL.md` description or Routing Card changes.
- `context_overload` -> tighten `context_pack_guidelines.md`, skill-local `read_if_needed`, or `do_not_load_by_default`.
- `output_shape_match: false` -> update skill-local expected outputs or usage eval expected shape.
- `friction` -> add `FIELD_FEEDBACK.md` entry only when the friction was observed in real use.

## Validation
- Eval cases must stay YAML-parseable.
- Result capture is evidence for improvement, not readiness.
- A single dry run can update a case; maturity changes require repeated field feedback or one severe routing failure.
