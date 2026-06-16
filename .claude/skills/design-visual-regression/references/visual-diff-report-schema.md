# Visual Diff Report Schema

Use this schema when reporting rendered UI differences against a design reference.

```yaml
visual_diff_report:
  target:
  source_reference:
  capture_method:
  viewports:
    - name:
      size:
      screenshot:
      nonblank:
      framing:
  differences:
    - viewport:
      area:
      type: hierarchy | layout | spacing | typography | color | asset | icon | state | overflow | clipping | responsive_order
      source_evidence:
      implementation_evidence:
      severity: blocker | major | minor | note
      suggested_fix:
  unavailable_evidence:
    - item:
      reason:
      impact:
  unverified:
    - item:
      reason:
```

## Severity guidance

- `blocker`: target is blank, wrong route, unusable, inaccessible primary content, or essential content missing.
- `major`: hierarchy, responsive behavior, state, or layout differs enough to affect intended use.
- `minor`: spacing, color, type, icon, or polish differences that do not block use.
- `note`: implementation choice or assumption that needs user awareness.
