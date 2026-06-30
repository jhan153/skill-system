# Skill Maturity

## Allowed Values

| maturity | Meaning |
| --- | --- |
| `skeleton` | Candidate or placeholder exists, but operational workflow, output shape, or routing boundary is still incomplete. |
| `usable` | Safe to use for the intended request class with normal judgment. |
| `field_tuned` | Improved through repeated real use and feedback. |
| `experimental` | Useful direction, but routing, context, or output quality may be unstable. |
| `deprecated` | Kept for compatibility or transition, but should not be selected for new work. |

## Assignment Rules

- Prefer lower maturity when real-use evidence is missing.
- Do not upgrade a skill based only on clean structure or a well-written description.
- Do not keep a skill at `skeleton` solely because field feedback is missing if it already has routing boundary, workflow, output schema, validation notes, and negative cases. Use `experimental` for that state.
- `field_tuned` requires repeated real-use feedback or repeated successful use in similar requests.
- `experimental` is appropriate for new specialist skills, broad orchestrators, and skills with over-trigger risk.
- `deprecated` requires a clear replacement or a clear reason to avoid new use.

## Update Inputs

- field feedback
- routing misses
- negative routing cases
- output quality issues
- context overloading
- repeated successful use
- user corrections
- friction signals from real runs
- impact evidence that repeated work, review effort, validation gaps, or context loading improved

## Friction Signals

Use friction signals as review aids, not automatic scores:

```yaml
friction_signals:
  repeated_work_reduced: unknown
  context_loaded_less: unknown
  review_time_reduced: unknown
  over_trigger_observed: false
  under_trigger_observed: false
  validation_gap_closed: false
  recurrence_prevented: false
  user_correction_needed: false
```

For maturity review, keep three ideas separate:

- `usage_count`: how often the skill was actually used
- `friction_count`: how often that use created routing, context, output, or validation friction
- `impact_evidence`: whether the skill measurably reduced repeated work, context loading, review time, or validation gaps

The system may generate a recommendation, but maturity changes require a reviewer decision.

## Non-Goals

- Maturity is a local use-readiness label.
- Task-specific validation remains separate from maturity assignment.
- Maturity must not be auto-promoted or auto-demoted from a numeric score alone.
