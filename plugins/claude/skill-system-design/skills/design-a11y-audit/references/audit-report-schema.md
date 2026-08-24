# Accessibility Audit Report Schema

Use this shape only for an audit artifact or several tracked conditions, and omit empty fields.

```yaml
accessibility_audit:
  target:
  viewport_or_state:
  conditions:
    - condition_id:
      scope:
      result: pass | fail | unverified | user-verification-needed
      evidence: []
      finding:
      missing_evidence:
  manual_checks_needed: []
  unresolved_gaps: []
```

This artifact closes only the listed condition IDs. It is not a full WCAG verdict, a repair
request, or a Plan transition.
