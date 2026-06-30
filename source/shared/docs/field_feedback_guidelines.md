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
feedback_id: FF-YYYYMMDD-001
bundle_version: "7.3.1"
bundle_hash_or_commit: "uncommitted"
date: "YYYY-MM-DD"
host: "codex"
host_version: "unknown"
model: "unknown"
request_class: "routing"
expected_primary_skill: "skill-name"
actual_primary_skill: "skill-name"
artifact_refs:
  - "path/to/changed-or-validated-artifact"
validation_evidence:
  - "command or user-visible validation result"
outcome: pass
friction: "none recorded"
privacy_redactions: []
harness_improvement_candidate:
  needed: false
  category: validation
  failure_prevented: "not applicable"
  priority: low
```

## Routing Back Into The Next Cut

- Routing miss: update `skill_registry.md` and routing/negative cases.
- Context issue: update `context_pack_guidelines.md` or relevant `SKILL.md`.
- Output issue: update the skill's expected output shape.
- Repeated success: consider maturity upgrade.
- Repeated friction: add negative case or lower maturity.

## Harness Improvement Candidates

Use `harness_improvement_candidate` only when a real run exposes a recurring or high-impact system gap. It is optional; most feedback entries should not grow a harness task.

Record a candidate when one of these is true:

- the same failure is likely to recur
- a completion claim could pass without enough evidence
- the issue crosses a tool, permission, validation, recovery, loop, WorkItem, or reporting boundary
- context overload or wrong skill routing is likely to repeat
- the user explicitly asks for recurrence prevention

Do not use this field to turn every bug fix, correction, or weak output into a new validator or workflow asset.

## Maturity Feedback Rules

- Upgrade `skeleton` to `experimental` when at least one real task shows the skill can help but still needs routing or output tuning.
- Upgrade `experimental` to `usable` only after repeated successful use with no major over-trigger or unsafe context behavior.
- Upgrade `usable` to `field_tuned` only after repeated feedback improves routing, context, and output shape.
- Downgrade immediately when a skill repeatedly triggers without explicit intent or pushes the agent toward broad context loading.
- Do not change maturity from static validation results alone.

## Current Field-Tuning Watchlist

- `coordination-brief`: watch for trigger ambiguity around goal/목표.
- `plan-long-term-package`: watch for keyword-only over-trigger from phase, migration, rewrite, or handoff.
- `design-tokens`: collect real token-source cases before raising maturity.
- `design-component-mapper`: collect real Figma-to-code mapping cases before raising maturity.
- `design-visual-regression`: collect browser/screenshot verification cases before raising maturity.
- `design-a11y-audit`: collect keyboard, focus, contrast, and overflow cases before raising maturity.

## Boundaries

- Do not paste secrets, credentials, private sessions, or unrelated project data.
- Keep feedback focused on routing, output quality, maturity, and concrete improvement candidates.
- Do not use one anecdote to upgrade a skill to `field_tuned`.
- Do not make `harness_improvement_candidate` mandatory.
