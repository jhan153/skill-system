---
name: design-mobile-screen
description: "Explicit-only mobile/native screen specialist for design-frontend tasks — safe areas, nav/tab bars, keyboard overlays, touch targets, scroll/fixed regions, responsive behavior, platform states, and mobile accessibility (React Native, Flutter, SwiftUI, Compose, mobile web)."
---

# design-mobile-screen

## Routing Card
- role: surface_specialist_implementation_modifier
- intent_signature:
  - mobile screen implementation
  - safe area navigation tab bar keyboard overlay
  - touch target and mobile accessibility
  - mobile scroll and fixed action regions
  - native or mobile web screen constraints
- use_when:
  - the user explicitly invokes `design-mobile-screen`.
  - `design-frontend` is implementing a mobile/native screen and mobile constraints materially affect layout, state, or validation.
  - the task mentions safe area, keyboard overlay, bottom action, tab bar, native navigation, touch target, or narrow-screen ergonomics.
- do_not_use_when:
  - the request is a generic design-to-code task with no mobile-specific constraints; keep `design-frontend` primary.
  - the task is only token normalization, component mapping, visual diff, or accessibility audit.
  - the target is a desktop-only dashboard or section-based web page.
- expected_inputs:
  - mobile design artifact, screenshot, spec, or existing screen path
  - target platform, framework, route/screen, or component
  - viewport/device assumptions, navigation model, and interaction states when available
- expected_outputs:
  - mobile screen structure
  - safe area and navigation behavior
  - scroll/fixed region rules
  - keyboard/touch/focus constraints
  - state and validation checklist
  - unresolved mobile gaps
- context_targets:
  must_read:
    - target mobile design artifact or screen spec
    - relevant repo screen/component/navigation files when implementation is requested
  read_if_needed:
    - `references/mobile-screen-checklist.md`
    - `design-frontend` for repo integration workflow
    - `design-visual-regression` for mobile viewport evidence
    - `design-a11y-audit` for keyboard/focus/label/target-size evidence
  do_not_load_by_default:
    - unrelated desktop routes
    - unrelated backend modules
    - live credentials
- risk_profile:
  reads:
    - mobile design references and scoped UI source files
  writes:
    - mobile screen/source files only when implementation is explicitly requested
  tools:
    - local preview, simulator, browser viewport, lint/build/test when available
  sensitive_resources:
    - authenticated device sessions and private design sessions default deny
- entry_scene:
  - PREPARE

Use this skill as a real surface specialist, not as a roadmap placeholder. Keep `allow_implicit_invocation: false`; generic visual implementation still routes to `design-frontend` unless this skill is explicitly invoked or attached.

## Workflow
1. Confirm surface and platform:
   - Identify mobile web, React Native, Flutter, SwiftUI, Jetpack Compose, or another native target.
   - Identify route/screen registration, navigation model, viewport/device, and preview path.
2. Extract mobile structure:
   - Separate status/safe area, navigation/header, scroll content, sticky action region, bottom tabs, modals/sheets, and keyboard-affected inputs.
   - Record which regions are fixed, scrollable, or overlayed.
3. Translate mobile constraints:
   - Define safe area padding, bottom inset behavior, keyboard avoidance, touch target sizing, text wrapping, and scroll restoration expectations.
   - Preserve platform conventions where the design does not specify otherwise.
4. Map state and interaction requirements:
   - Cover loading, empty, error, disabled, focus, selected, validation, offline, partial data, and permission states when relevant.
   - Record gestures, tap targets, input focus, and modal/sheet dismissal behavior.
5. Implement or hand off:
   - If code changes are requested, follow repo patterns and the `design-frontend` integration rules.
   - If only guidance is requested, return the screen structure and constraint report.
6. Validate:
   - Prefer actual mobile viewport, simulator, Storybook viewport, or native preview.
   - Use `design-visual-regression` for screenshot/framing/overflow evidence.
   - Use `design-a11y-audit` for labels, focus, target size, and responsive readability.

## Output schema
```yaml
surface: mobile-screen
platform:
target_screen:
navigation_model:
safe_area_rules: []
scroll_and_fixed_regions: []
keyboard_overlay_rules: []
touch_target_rules: []
state_model: []
component_contract_gaps: []
visual_validation: []
accessibility_validation: []
unresolved_mobile_gaps: []
unverified: []
```

## Validation
- Check at least one narrow mobile viewport or named device when tooling exists.
- Verify text does not clip inside buttons, inputs, cards, tab bars, or headers.
- Verify bottom actions and tab bars do not hide scroll content.
- Verify keyboard overlay behavior for input-heavy screens when possible.
- Do not claim native fidelity without simulator/device/browser viewport evidence.

## Recovery
- If simulator/native preview is unavailable, use mobile browser viewport or static screenshot evidence and mark native behavior `Unverified`.
- If safe area or keyboard behavior cannot be tested, report exact assumptions.
- If implementation target is unclear, ask for the target screen before editing source.
- If platform-specific standards are not sourced, keep platform claims conservative.

## Known Limits
- This skill does not replace `design-frontend` for generic visual implementation.
- It does not certify accessibility by itself.
- It does not create backend flows, authentication, permissions, or device APIs unless explicitly requested.

## Optional resources
- Read `references/mobile-screen-checklist.md` for the detailed mobile implementation checklist.
