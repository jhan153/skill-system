---
name: design-dashboard
description: Apply SaaS/admin/analytics dashboard implementation constraints as an explicit-only surface specialist. Use when Codex is explicitly asked to use this skill, or when a design-frontend task needs dashboard-specific guidance for KPI hierarchy, filters, search, date ranges, charts, tables, dense layouts, async states, pagination, empty/error/loading states, data readability, and operational UI accessibility.
---

# design-dashboard

## Routing Card
- role: surface_specialist_implementation_modifier
- intent_signature:
  - dashboard UI implementation
  - KPI filters charts tables dense data
  - SaaS admin analytics monitoring reporting UI
  - data loading empty error and partial states
  - operational accessibility and responsive density
- use_when:
  - the user explicitly invokes `design-dashboard`.
  - `design-frontend` is implementing a dashboard where data density, filters, charts, tables, or async states dominate.
  - the task mentions KPI cards, filters, search, chart/table regions, pagination, dashboard shell, admin console, or analytics UI.
- do_not_use_when:
  - the request is a generic visual artifact implementation with no dashboard/data surface.
  - the task is a marketing landing page, mobile-native screen, backend analytics query, or data modeling task.
  - the task only needs token, component, visual, or accessibility evidence.
- expected_inputs:
  - dashboard design artifact, screenshot, spec, or existing dashboard route
  - target repo framework, component library, chart/table stack, and data source assumptions
  - required states, filters, breakpoints, and density constraints when available
- expected_outputs:
  - dashboard region map
  - KPI/filter/chart/table hierarchy
  - async and empty/error state model
  - table/chart/component contract notes
  - responsive density rules
  - unresolved dashboard gaps
- context_targets:
  must_read:
    - dashboard design artifact or target route
    - relevant repo dashboard/table/chart/filter components when implementation is requested
  read_if_needed:
    - `references/dashboard-implementation-checklist.md`
    - `design-frontend` for repo integration workflow
    - `design-component-mapper` for table/filter/chart state mapping
    - `design-visual-regression` for viewport density/overflow evidence
    - `design-a11y-audit` for labels, table semantics, focus, and chart alternatives
  do_not_load_by_default:
    - unrelated marketing pages
    - backend data pipelines unless explicitly part of the UI task
    - live credentials
- risk_profile:
  reads:
    - dashboard design references and scoped UI source files
  writes:
    - dashboard UI files only when implementation is explicitly requested
  tools:
    - local preview, Storybook, browser screenshot, lint/build/test when available
  sensitive_resources:
    - production dashboards, customer data, and authenticated sessions default deny
- entry_scene:
  - PREPARE

Use this skill as a real dashboard surface specialist. Keep `allow_implicit_invocation: false`; generic implementation still routes to `design-frontend` unless this skill is explicitly invoked or attached.

## Workflow
1. Confirm dashboard type and task boundary:
   - Identify admin, SaaS, analytics, monitoring, reporting, CRM, finance, or operational dashboard.
   - Separate UI implementation from data pipeline, metric definition, or backend query work.
2. Build the region model:
   - Page shell, title/action bar, KPI summary, filters/search/date controls, chart regions, table/list/detail regions, and secondary panels.
   - Keep filters close to affected data and preserve scanning order.
3. Map data and async states:
   - Define loading, skeleton, empty, partial, stale, error, permission, offline, filtered-empty, and pagination states.
   - Do not invent metrics, chart semantics, or data values not present in source or repo fixtures.
4. Map components:
   - Prefer existing table, chart, card, filter, dropdown, date, pagination, and empty-state components.
   - Use `design-component-mapper` for variants, slots, events, responsive behavior, and state coverage.
5. Implement or hand off:
   - If code changes are requested, follow repo patterns and `design-frontend` integration rules.
   - If only guidance is requested, return a dashboard implementation contract.
6. Validate:
   - Check desktop density and at least one narrower responsive width when relevant.
   - Check table/chart overflow, sticky headers/actions, filter behavior, and readable labels.
   - Use visual/accessibility gates for screenshot and operability evidence.

## Output schema
```yaml
surface: dashboard
dashboard_type:
target_route:
region_map: []
kpi_hierarchy: []
filter_model: []
chart_model: []
table_model: []
async_state_model: []
component_contract_gaps: []
responsive_density_rules: []
visual_validation: []
accessibility_validation: []
unresolved_dashboard_gaps: []
unverified: []
```

## Validation
- Verify hierarchy supports repeated scanning, comparison, and action.
- Verify dense layouts do not become marketing-style hero/card compositions.
- Verify filters, tables, pagination, and empty states are represented when visible or required.
- Verify chart/table regions have labels, alternatives, or summaries where possible.
- Do not claim data correctness from UI fixture rendering alone.

## Recovery
- If real data is unavailable, use existing fixtures/mock patterns and mark data semantics `Unverified`.
- If chart/table components are unavailable, implement the smallest local surface consistent with repo style and report the gap.
- If dashboard scope is too broad, implement the requested region first and list deferred regions.
- If authenticated data is unavailable, request safe screenshots/fixtures rather than credentials.

## Known Limits
- This skill does not validate analytics definitions, SQL, billing metrics, or product strategy.
- It does not replace `design-frontend` for generic visual implementation.
- It does not certify accessibility or visual fidelity without evidence gates.

## Optional resources
- Read `references/dashboard-implementation-checklist.md` for detailed dashboard surface checks.
