# Token Gap Policy

Use this reference when token names, values, aliases, or source priority are incomplete.

## Status labels

- `confirmed`: exact value and name are present in source.
- `mapped`: repo token maps to a source token through a documented alias.
- `inferred`: value or role is estimated from screenshot, rendered CSS, or nearby usage.
- `missing`: required token exists by name or need but no value is available.
- `conflict`: two sources disagree on name, value, mode, or role.
- `out_of_scope`: token exists but is unrelated to the requested UI surface.

## Rules

- Never turn `missing` into `confirmed`.
- Never invent palette names, spacing scales, or typography roles to make a report look complete.
- Prefer reporting a smaller confirmed subset over a broad inferred token system.
- Keep subjective palette critique separate from token source mismatches.
- If a user asks for implementation despite gaps, hand off the smallest scoped substitutions as assumptions.

## Gap report shape

```yaml
token_gap:
  token_name:
  category:
  required_by:
  missing_part: name | value | mode | alias | platform_mapping
  available_evidence:
  proposed_next_action:
  status: missing | inferred | conflict | unverified
```
