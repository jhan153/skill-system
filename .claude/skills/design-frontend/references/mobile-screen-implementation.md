# Design Mobile Screen Reference

Load only for the `mobile` profile of `design-frontend`: a mobile/native screen where safe areas, navigation, keyboard, touch, or fixed/scroll regions materially affect implementation.

## Checkpoints

- Preserve platform navigation structure: stack, modal, tab, sheet, drawer, or route.
- Account for safe areas, status bars, navigation bars, tab bars, home indicator, and keyboard overlays.
- Keep touch targets large enough and spaced enough for pointer/touch use.
- Separate scroll containers from fixed headers, bottom bars, and sticky actions.
- Plan loading, empty, error, disabled, focused, selected, and validation states when visible or required.
- Keep copy readable on narrow widths and avoid text clipping inside controls.
- Use platform-native accessibility primitives where possible.
- Verify focused inputs and primary actions remain visible when the keyboard is open.
- Keep scroll content clear of fixed headers, bottom actions, tabs, and home indicators.

## Handoff

- Use `design-a11y-audit` for keyboard/focus/label/target-size evidence.
- Use `design-visual-regression` for mobile screenshot and overflow evidence.
- Keep platform-specific claims `Unverified` when no platform documentation or simulator evidence is available.
