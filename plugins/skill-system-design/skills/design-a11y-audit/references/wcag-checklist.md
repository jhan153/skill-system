# WCAG/APG Evidence Checklist

Use this as a scoped evidence checklist. It is not a full conformance test plan.

## Common checks

- Text contrast: check WCAG 2.2 contrast minimum when foreground/background values are available.
- Non-text contrast: check visible boundaries and focus indicators where measurable.
- Target size: check minimum target size or spacing when dimensions are measurable.
- Reflow/readability: check small viewport readability, wrapping, and overflow.
- Keyboard: verify controls are reachable and operable without pointer input.
- Focus visible: verify focus indication is visible and not hidden by styling.
- Names and labels: check accessible names for inputs, buttons, links, and icon-only controls.
- Roles and semantics: prefer native semantic elements; custom widgets need role/state/keyboard evidence.
- Status messages: loading, success, error, and validation messages should be perceivable.

## Reporting discipline

- Cite source, DOM, screenshot, or tool output for each finding.
- Mark unmeasured contrast, target size, and keyboard behavior as `Unverified`.
- Do not claim full WCAG pass from static scanning alone.
