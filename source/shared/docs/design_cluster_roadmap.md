# Design Cluster Roadmap

The design cluster grows through distinct analysis/evidence skills and conditionally loaded implementation profiles. A profile is not a skill when it shares the same implementation owner, write boundary, and completion oracle.

## Current Skills

| skill | maturity | role |
| --- | --- | --- |
| `design-frontend` | `usable` | High-fidelity implementation with conditional product-family governance, approved-component reuse, and evidence-based UX control choice. |
| `design-tokens` | `experimental` | Normalize token sources, platform mappings, gaps, conflicts, and no-fabrication token evidence. |
| `design-component-mapper` | `experimental` | Map component contracts and prove approved app-surface reuse with scoped exceptions or unmapped gaps. |
| `design-visual-regression` | `experimental` | Capture visual evidence and keep exact-target fidelity separate from product-family coherence. |
| `design-a11y-audit` | `experimental` | Review keyboard, focus, semantic, contrast, target-size, and responsive readability evidence. |
| `design-ui-decomposer` | `experimental` | Decompose UI references into implementation-ready structure without writing code. |
| `design-layout-translator` | `experimental` | Translate Auto Layout, flex/grid, sizing, overflow, and breakpoint constraints into code-ready rules. |

## Three-Stage Growth Direction

Stage 1: evidence gate hardening.
- `design-tokens`
- `design-component-mapper`
- `design-visual-regression`
- `design-a11y-audit`

Stage 2: orchestration and limited analysis.
- `design-frontend` consumes gate outputs.
- `design-ui-decomposer` and `design-layout-translator` exist as conservative analysis skills.
- Surface, product-family, and conditional UX decision guidance lives under `design-frontend/references/`, not as primary skills.

Stage 3: field-trial expansion.
- `design-frontend` selects `mobile`, `dashboard`, `section-web`, or `general` and loads one profile reference.
- Promote a profile to a skill only after field evidence proves it needs a distinct owner, write boundary, or validation oracle.
- Expansion requires route cases, negative cases, and field feedback.

## Planned Candidates

These are roadmap candidates only; they are not active registry skills yet.

| candidate | planned role | expansion precondition |
| --- | --- | --- |
| `information-hierarchy-mapper` | analysis | repeated requests where `design-ui-decomposer` is too broad |
| `component-api-designer` | analysis | component API design requests not covered by contract mapping |
| `state-interaction-modeler` | analysis/modifier | repeated state planning requests beyond component mapping |
| `ui-implementation-polish-review` | review gate | review-only UI quality requests with stable output shape |

## Guardrails

- Do not use design specialists for backend-only work.
- Do not generate marketing-style pages when the user asks for an app, tool, or operational interface.
- Do not treat screenshots alone as proof of implementation quality.
- Do not treat a component export inventory as reuse proof or one sibling screenshot as a product-family oracle.
- Keep specialist skills narrow and add negative routing cases before adding more design skills.
- Keep `allow_implicit_invocation: false` for new and recently hardened design skills until route evidence and field feedback justify broader routing. `design-frontend` is the bounded exception for concrete repo-integrated UI implementation; analysis and evidence specialists remain explicit.
- Do not create a surface skill when a conditional `design-frontend` reference is sufficient.

## Improvement Track

- Add field feedback for the four evidence gates after real projects.
- Add field feedback for `design-ui-decomposer` and `design-layout-translator` before allowing implicit invocation.
- Track dashboard/mobile/section profile quality, incorrect multi-profile loading, and missing surface constraints.
- Track product-family profile conflicts, catalog reuse violations/exceptions, target-vs-family verdict divergence, and UX decisions reversed by missing context.
- Promote UX pattern planning to a distinct skill only after repeated field cases show that the conditional `design-frontend` reference needs a separate owner or oracle.
- Track `design-frontend` over-trigger on critique, audits, layout translation, and small edits, plus under-trigger on concrete implementation, before broadening the exception or changing primary ownership rules.
