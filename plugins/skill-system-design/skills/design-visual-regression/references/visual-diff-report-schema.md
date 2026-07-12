# Visual Diff Report Schema

Use this schema when reporting rendered UI differences against an exact design reference and, when declared, pinned product-family baselines.

```yaml
visual_diff_report:
  target:
  source_reference:
  comparison_lanes: [target_fidelity, family_coherence]
  capture_method:
  viewports:
    - name:
      size:
      screenshot:
      nonblank:
      framing:
  target_fidelity:
    verdict: pass | fail | unverified | user-verification-needed
    differences:
      - viewport:
        area:
        type: hierarchy | layout | spacing | typography | color | asset | icon | state | overflow | clipping | responsive_order
        source_evidence:
        implementation_evidence:
        severity: blocker | major | minor | note
        suggested_fix:
  family_coherence:
    verdict: pass | fail | unverified | user-verification-needed | not_applicable
    baselines:
      - id:
        kind: component_state | surface_archetype
        source:
        state:
        viewport:
        theme_mode:
        version:
        sha256:
    findings:
      - viewport:
        area:
        axis: typography | color_tokens | spacing_rhythm | radius_elevation | control_height | icon_family | density | shell | component_state
        baseline_evidence:
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

Keep the two lane verdicts independent. Compare family baselines only on applicable shared axes; never interpret unrelated full-screen pixel differences as family drift by themselves.
