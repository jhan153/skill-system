# Layout Constraint Contract

Use this reference when mapping design constraints to implementation rules.

## Common mappings

| Design intent | Implementation mapping |
| --- | --- |
| Horizontal Auto Layout | flex row, inline stack, or horizontal native stack |
| Vertical Auto Layout | flex column, vertical stack, or list |
| Two-axis board/region | CSS Grid, platform grid, or explicit row/column layout |
| Fill container | flex grow, grid `1fr`, bounded `width: 100%`, or platform fill |
| Hug contents | intrinsic/content-sized element with max constraints |
| Fixed control | explicit width/height or aspect ratio when stability matters |
| Responsive wrap | flex wrap, grid auto-fit, or stacked native layout |
| Long text | wrap, clamp, truncate, or resize container |
| Overflow content | scroll region, pagination, disclosure, or clipping with explicit rationale |

## Shared rules

- Define what changes at each breakpoint: columns, axis/order, spacing, visibility, and scroll.
- Keep stable dimensions for boards, grids, toolbars, counters, and icon buttons when their control
  contract requires it.
- Do not scale font size directly with viewport width.
- Check longest labels and dynamic content before claiming text fit.
- A single screenshot supports only a responsive hypothesis unless source metadata, requirements,
  additional frames, or current repo rules establish the transition.

## Breakpoint report

```yaml
breakpoint_rule:
  viewport:
  container_change:
  column_or_axis_change:
  spacing_change:
  visibility_change:
  overflow_strategy:
  evidence:
```

## Multi-region contract

For an explicit multi-region contract, omit empty fields:

```yaml
source_reference:
target_platform:
layout_hierarchy: []
sizing_and_spacing_rules: []
overflow_and_text_rules: []
breakpoint_rules: []
implementation_mapping: []
evidence:
  confirmed: []
  inferred: []
  unverified: []
```
