# Dashboard Implementation Checklist

Use this checklist when implementing or reviewing an operational dashboard.

## Regions

- Shell/navigation.
- Page title and primary action.
- KPI summary.
- Filters, search, date range, and segment controls.
- Chart or visualization region.
- Table/list/detail region.
- Empty/loading/error/partial/stale states.

## Constraints

- Primary metrics and actions are scannable without hero-style decoration.
- Filters are visibly connected to affected data.
- Tables have readable headers, row states, pagination or scrolling, and empty states.
- Charts have labels, legends, units, and fallback/summaries where possible.
- Dense data remains readable at desktop and narrower widths.
- Fake metrics or invented data semantics are not introduced.

## Evidence

- Desktop screenshot and narrower viewport when relevant.
- Component contract notes for filters, charts, tables, and states.
- Accessibility notes for labels, table semantics, focus order, and chart alternatives.
