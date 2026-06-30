# Design Cluster Roadmap

The design cluster is a long-term specialist area, similar in shape to the research cluster. It should grow through narrow skills with clear routing boundaries, not one broad design mega-skill.

## Current Skills

| skill | maturity | role |
| --- | --- | --- |
| `design-frontend` | `usable` | High-fidelity implementation from concrete visual design inputs. |
| `design-tokens` | `experimental` | Normalize token sources, platform mappings, gaps, conflicts, and no-fabrication token evidence. |
| `design-component-mapper` | `experimental` | Map design components, variants, states, slots, events, and responsive behavior to repo components. |
| `design-visual-regression` | `experimental` | Capture or inspect screenshot, nonblank, framing, viewport, overflow, and visual diff evidence. |
| `design-a11y-audit` | `experimental` | Review keyboard, focus, semantic, contrast, target-size, and responsive readability evidence. |
| `design-ui-decomposer` | `experimental` | Decompose UI references into implementation-ready structure without writing code. |
| `design-layout-translator` | `experimental` | Translate Auto Layout, flex/grid, sizing, overflow, and breakpoint constraints into code-ready rules. |
| `design-mobile-screen` | `experimental` | Apply mobile/native screen constraints as an explicit-only surface specialist. |
| `design-dashboard` | `experimental` | Apply dashboard UI constraints as an explicit-only surface specialist. |
| `design-section-web` | `experimental` | Apply section-based web page constraints as an explicit-only surface specialist. |

## Three-Stage Growth Direction

Stage 1: evidence gate hardening.
- `design-tokens`
- `design-component-mapper`
- `design-visual-regression`
- `design-a11y-audit`

Stage 2: orchestration and limited analysis.
- `design-frontend` consumes gate outputs.
- `design-ui-decomposer` and `design-layout-translator` exist as conservative analysis skills.
- Surface guidance lives under `design-frontend/references/`, not as primary skills.

Stage 3: field-trial expansion.
- Surface-specific implementation skills now exist as active `experimental` explicit-only specialists.
- Expansion now means implicit invocation or stronger primary ownership, not merely creating the files.
- Stronger expansion requires route cases, negative cases, and field feedback.

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
- Keep specialist skills narrow and add negative routing cases before adding more design skills.
- Keep `allow_implicit_invocation: false` for new, recently hardened, and surface-specific design skills until route smoke tests and field feedback justify broader routing.
- Surface-specific implementation skills are operational, but should not displace `design-frontend` for generic design-to-code requests.

## Improvement Track

- Add field feedback for the four evidence gates after real projects.
- Add field feedback for `design-ui-decomposer` and `design-layout-translator` before allowing implicit invocation.
- Track dashboard/mobile/section field usage before enabling implicit invocation.
- Track over-trigger and under-trigger events before changing primary ownership rules.
