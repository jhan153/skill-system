# Mobile Screen Checklist

Use this checklist when implementing or reviewing a mobile/native screen.

## Structure

- Status/safe area.
- Header/navigation.
- Scrollable content.
- Sticky or bottom action region.
- Tab bar or bottom navigation.
- Modal, sheet, drawer, or overlay.
- Keyboard-affected input region.

## Constraints

- Safe area insets are handled at top and bottom.
- Keyboard does not hide focused inputs or primary submit actions.
- Touch targets are large enough and spaced enough for touch use.
- Scroll content is not hidden behind fixed bars.
- Long labels wrap or truncate intentionally.
- Empty/loading/error/disabled/focus/selected states are represented when required.

## Evidence

- Mobile viewport or simulator screenshot.
- Keyboard behavior evidence for input screens.
- Target size and label/focus evidence when accessibility is in scope.
- Explicit `Unverified` note for untested native behavior.
