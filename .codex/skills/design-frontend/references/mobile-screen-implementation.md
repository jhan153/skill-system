# Mobile Screen Implementation Reference

Use this reference from `design-frontend` when the requested UI is a mobile or native screen. For explicit mobile surface work, use `$design-mobile-screen`; generic design-to-code remains owned by `design-frontend`.

## Checkpoints

- Preserve platform navigation structure: stack, modal, tab, sheet, drawer, or route.
- Account for safe areas, status bars, navigation bars, tab bars, home indicator, and keyboard overlays.
- Keep touch targets large enough and spaced enough for pointer/touch use.
- Separate scroll containers from fixed headers, bottom bars, and sticky actions.
- Plan loading, empty, error, disabled, focused, selected, and validation states when visible or required.
- Keep copy readable on narrow widths and avoid text clipping inside controls.
- Use platform-native accessibility primitives where possible.

## Handoff

- Use `design-a11y-audit` for keyboard/focus/label/target-size evidence.
- Use `design-visual-regression` for mobile screenshot and overflow evidence.
- Keep platform-specific claims `Unverified` when no platform documentation or simulator evidence is available.
