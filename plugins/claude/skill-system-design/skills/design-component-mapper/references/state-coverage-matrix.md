# State Coverage Matrix

Use this reference when checking whether design and implementation cover the same UI states.

## Common state families

- Interaction: default, hover, focus, active, pressed, selected.
- Availability: enabled, disabled, readonly, hidden.
- Async: loading, refreshing, skeleton, pending, optimistic.
- Data: empty, partial, populated, overflow, truncated.
- Result: success, warning, error, validation error.
- Disclosure: expanded, collapsed, open, closed.
- Navigation: current, visited, unavailable.
- Responsive: compact, regular, wide, touch, pointer.

## Matrix shape

```yaml
state_matrix:
  component:
  state:
  design_evidence:
  repo_evidence:
  visual_evidence:
  accessibility_evidence:
  status: implemented | missing | conflict | unverified
  notes:
```

## Escalation

- Missing focus, keyboard, target-size, or accessible-name states should hand off to `design-a11y-audit`.
- Missing visual state proof should hand off to `design-visual-regression`.
- Missing token/state styling should hand off to `design-tokens`.
