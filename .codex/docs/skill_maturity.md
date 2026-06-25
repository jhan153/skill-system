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

## Non-Goals

- Maturity is a local use-readiness label.
- Task-specific validation remains separate from maturity assignment.
