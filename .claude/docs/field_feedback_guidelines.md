# Field Feedback Guidelines

Field feedback converts real use into the next version cut.

## When To Record

- the wrong primary skill was selected
- too many support skills were selected
- context was too broad or too narrow
- output shape did not match the request
- the user corrected a recurring behavior
- a skill produced useful behavior worth preserving
- a specialist skill needs more examples

## Entry Shape

```yaml
field_feedback:
  date:
  request:
  expected_primary_skill:
  actual_primary_skill:
  supporting_skills:
  friction:
  useful_behavior:
  risky_behavior:
  suggested_maturity_change:
  suggested_eval_case:
  suggested_skill_text_change:
  verification: unverified
```

## Routing Back Into 7.1

- Routing miss: update `skill_registry.md` and routing/negative cases.
- Context issue: update `context_pack_guidelines.md` or relevant `SKILL.md`.
- Output issue: update the skill's expected output shape.
- Repeated success: consider maturity upgrade.
- Repeated friction: add negative case or lower maturity.

## Maturity Feedback Rules

- Upgrade `skeleton` to `experimental` when at least one real task shows the skill can help but still needs routing or output tuning.
- Upgrade `experimental` to `usable` only after repeated successful use with no major over-trigger or unsafe context behavior.
- Upgrade `usable` to `field_tuned` only after repeated feedback improves routing, context, and output shape.
- Downgrade immediately when a skill repeatedly triggers without explicit intent or pushes the agent toward broad context loading.
- Do not change maturity from bundle hygiene results alone.

## Current 7.1 Watchlist

- `goal-workflow-orchestrator`: watch for trigger ambiguity around goal/목표.
- `phase-subplan-workflow`: watch for keyword-only over-trigger from phase, migration, rewrite, or handoff.
- `design-token-pipeline`: collect real token-source cases before raising maturity.
- `component-contract-mapper`: collect real Figma-to-code mapping cases before raising maturity.
- `visual-regression-harness`: collect browser/screenshot verification cases before raising maturity.
- `accessibility-audit-harness`: collect keyboard, focus, contrast, and overflow cases before raising maturity.

## Boundaries

- Do not paste secrets, credentials, private sessions, or unrelated project data.
- Do not turn feedback into package approval.
- Do not use one anecdote to upgrade a skill to `field_tuned`.
