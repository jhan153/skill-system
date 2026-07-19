# Keyboard and Focus Procedure

Use this reference when a rendered target or interactive preview is available.

## Procedure

1. Start at the browser chrome or first focusable element.
2. Press Tab through all visible interactive elements.
3. Confirm focus order follows visual/logical order.
4. Confirm focus indicator is visible against the background.
5. Confirm Shift+Tab reverses order predictably.
6. Confirm Enter/Space activate buttons, links, toggles, tabs, and menu items as appropriate.
7. Confirm Escape closes dismissible popovers, modals, menus, or dialogs when present.
8. Confirm focus returns to the trigger after closing overlays when applicable.
9. For selected items, confirm selected state is visually distinct from focused state.
10. Record skipped, trapped, hidden, or off-screen focus targets.

## Composite widgets

Use WAI-ARIA APG patterns for tabs, menus, listboxes, comboboxes, dialogs, grids, and tree views. If implementation does not follow a known pattern, mark behavior as `Unverified` and record the observed keys.
