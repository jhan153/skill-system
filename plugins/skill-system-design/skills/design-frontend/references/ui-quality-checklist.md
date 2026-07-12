# UI Quality Checklist

Use this checklist before reporting a design-frontend task complete when visual quality matters.

## Check order

1. Governance: pin any applicable product-family profile, catalog, policy, and visual baseline; resolve conflicts by source ownership.
2. Information hierarchy: primary user task, primary information, and primary action are clear.
3. UX decision: material control/pattern choices cite supplied needs, rejected alternatives, required states, and recovery behavior.
4. Layout: regions align, spacing is intentional, and responsive order is stable.
5. Components: app-surface controls reuse approved catalog matches with import/use evidence; unmapped controls follow the declared fallback or an authorized exception.
6. States: visible states and required loading, empty, error, validation, disabled, success, and recovery states are implemented or reported as gaps.
7. Tokens: colors, typography, spacing, radius, elevation, density, icons, and assets obey declared family rules or documented exceptions.
8. Accessibility: labels, focus, keyboard, target size, contrast, and text overflow are checked where possible.
9. Visual proof: source fidelity and, when declared, product-family coherence have separate viewport-specific verdicts.
10. Interaction proof: exercise a task-bearing route/screen through one critical success and material failure/recovery path; for a component/story, exercise relevant states, events, keyboard behavior, and rendering.

## Report discipline

- Mark unavailable design context, private assets, proprietary fonts, and inferred measurements.
- Do not claim visual completion from build success alone.
- Do not claim component reuse from export availability alone or family coherence from one unrelated sibling screenshot.
- Do not flag semantic primitives inside an approved component as an app-surface reuse violation.
- Keep subjective polish notes separate from standards-backed accessibility findings.
