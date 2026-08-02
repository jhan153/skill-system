# UI Prototype

Use this branch only when the question is primarily visible or interactional: layout, information hierarchy, density, control placement, navigation, or comparison flow.

## Build Shape

1. Prefer the existing real route, screen, story, or preview over a detached demo. Preserve enough authentic shell, data shape, components, tokens, typography, and viewport behavior for the comparison to be meaningful.
2. Stub writes, server actions, analytics, authentication changes, and external requests. Use safe fixtures or read-only real context where repository policy permits it.
3. Build the minimum credible comparison. Use the current behavior plus one candidate, or two explicit candidates, when that can decide the question. Add a third variant only when it represents a distinct credible hypothesis that the first two cannot test; never fabricate an option to fill a quota and never exceed five. Vary hierarchy, grouping, control position, result organization, or interaction model—not merely color, copy, spacing, or icons.
4. Keep all variants on one comparable surface. Prefer a stable URL selector such as `?variant=A`, `B`, or `C` plus a small floating development-only switcher with the active label.
5. Make switching fast and repeatable. Support direct links and previous/next controls; arrow-key shortcuts are useful when they do not intercept typing in inputs, textareas, selects, or editable content.
6. Render only states that can change the active decision. Loading, empty, error, mobile, and long-content states belong only when the question depends on them.

## Observation

- State the task the user should attempt, the viewport or device, and what differs among variants.
- Ask the decision owner to select, reject, rank, or combine concrete structural elements. Record which observation changed the decision rather than a generic preference score.
- Treat a build, screenshot, or visual diff as run/fidelity evidence only. Human preference, comprehension, and workflow fit require the decision owner's observation.

## Closure

Keep the full comparison, switcher, fixtures, and alternatives runnable in the isolated prototype until the decision owner responds. Do not copy them into production. After explicit selection, reimplement the accepted composition through the normal production UI workflow with its accessibility, integration, responsive, and visual checks; clean up the prototype only on request or at its pre-agreed retention trigger.
