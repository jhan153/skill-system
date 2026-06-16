# Layout Translation Map

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
