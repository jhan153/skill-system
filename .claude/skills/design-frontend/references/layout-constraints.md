# Layout Constraints Reference

Use this reference when translating design layout constraints into implementation.

## Translation map

- Horizontal or vertical Auto Layout -> flex row/column when one axis dominates.
- Two-dimensional region layout -> CSS Grid or platform grid when both axes matter.
- Hug/intrinsic sizing -> content-sized element with max constraints and wrapping rules.
- Fill container -> flexible track, flex grow, or width/height 100% inside a bounded parent.
- Fixed size -> use only when the element is truly fixed-format or needs stable controls.
- Min/max bounds -> protect text fitting, controls, media, cards, and repeated tiles.
- Overflow -> choose visible, hidden, scroll, wrap, or truncate intentionally.

## Responsive checks

- Define what changes at each breakpoint: columns, order, spacing, visibility, and scroll.
- Keep stable dimensions for boards, grids, toolbars, counters, and icon buttons.
- Do not scale font size with viewport width.
- Check longest labels and dynamic content before claiming the layout is done.
