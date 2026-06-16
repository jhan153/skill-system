# Design Section Web Reference

Use this reference from `design-frontend` when the requested UI is a landing, product, docs, portfolio, venue, or marketing-like web page. For explicit section-page surface work, use `$design-section-web`; generic design-to-code remains owned by `design-frontend`.

## Section tree

- Hero or first viewport signal.
- Primary proof or product/object reveal.
- Feature, workflow, or comparison sections.
- Details, specs, testimonials, FAQ, or supporting content.
- Final CTA or next action.

## Implementation checks

- Build the actual requested experience first; do not default to a marketing landing page when the user asks for an app or tool.
- Use semantic sections and headings.
- Keep the first viewport focused on the actual product/place/object/person or literal offer.
- Make responsive section order explicit.
- Avoid nested cards and decorative section cards unless the item itself is a repeated card.
- Keep text fitting and avoid overlap across mobile and desktop.

## Handoff

- Use `design-visual-regression` for first viewport, responsive order, overflow, and clipping checks.
- Use `design-a11y-audit` for headings, landmarks, CTA names, focus order, and contrast.
