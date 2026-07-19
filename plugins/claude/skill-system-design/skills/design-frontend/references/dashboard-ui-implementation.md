# Design Dashboard Reference

Load only for the `dashboard` profile of `design-frontend`: an admin, SaaS, analytics, monitoring, reporting, or dense operational surface dominated by data scanning and control.

## Region model

- Global shell/navigation.
- Page title and primary action.
- KPI summary region.
- Filter/search/date controls.
- Chart or visualization region.
- Table/list/detail region.
- Empty, loading, error, partial-data, and stale-data states.

## Implementation checks

- Preserve scanning order and density; avoid oversized hero or marketing-style composition.
- Keep filters close to the data they affect.
- Make table headers, sort controls, pagination, selected rows, and empty states explicit.
- Use existing chart/table components when available.
- Avoid inventing metrics or data semantics not present in the source or repo fixtures.
- Verify responsive behavior: collapse, horizontal scroll, column hiding, or stacked summary.
- Make loading, empty, filtered-empty, partial, stale, error, permission, and pagination states explicit when relevant.
- Provide labels, units, legends, or accessible summaries for charts; do not encode meaning by color alone.

## Handoff

- Use `design-component-mapper` for table, filter, chart, card, and state component contracts.
- Use `design-visual-regression` for viewport-specific density and overflow evidence.
- Use `design-a11y-audit` for table semantics, filter labels, focus order, and chart alternatives.
