# Viewport Policy

Use this reference before capturing or comparing UI screenshots.

## Viewport source priority

1. User-specified dimensions.
2. Design frame dimensions.
3. Project-defined breakpoints or Storybook viewports.
4. Platform conventions for the target surface.
5. Fallback responsive set:
   - mobile: `390x844`
   - desktop: `1440x900`

## Capture rules

- Capture exact dimensions and device scale factor when available.
- Include at least one mobile and one desktop viewport for responsive web surfaces.
- For fixed native/mobile screens, use the relevant device/simulator size when available.
- Do not compare different states as if they were the same design.
- Record viewport-specific failures separately.

## Framing checks

- Primary content should be visible and inside the frame.
- Text should not overlap controls or adjacent content.
- Important controls should not be clipped or off-canvas.
- Empty screenshots, loading-only screenshots, and auth/login redirects are not valid visual proof unless that state is the requested target.
