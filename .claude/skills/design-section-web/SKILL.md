---
name: design-section-web
description: Apply section-based web page implementation constraints as an explicit-only surface specialist. Use when Codex is explicitly asked to use this skill, or when a design-frontend task needs guidance for landing, product, docs, portfolio, venue, brand, or marketing-style pages with hero sections, semantic section trees, CTA flow, responsive order, media placement, first-viewport signal, accessibility, and text-fitting checks.
---

# design-section-web

## Routing Card
- role: surface_specialist_implementation_modifier
- intent_signature:
  - section-based web implementation
  - landing product docs portfolio venue brand page
  - hero section CTA flow responsive section order
  - semantic sections and accessible headings
  - first viewport signal and text fitting
- use_when:
  - the user explicitly invokes `design-section-web`.
  - `design-frontend` is implementing a section-based web page and section order, hero behavior, CTA flow, or responsive media matters.
  - the task mentions hero, landing page, product page, portfolio, venue page, docs page, sections, CTA, or responsive section layout.
- do_not_use_when:
  - the user asks for an app/tool/operational interface first screen rather than a page.
  - the target is a mobile-native screen or dense operational dashboard.
  - the task is only token, component, visual, or accessibility evidence.
- expected_inputs:
  - section-based design artifact, screenshot, spec, copy, or target page
  - target repo framework, route, layout shell, assets, and content constraints
  - viewport priorities and page purpose when available
- expected_outputs:
  - section tree
  - hero and first-viewport plan
  - CTA and content flow
  - responsive section order and media rules
  - semantic/accessibility checklist
  - unresolved section-page gaps
- context_targets:
  must_read:
    - page design artifact or target route
    - relevant repo page/layout/components/assets when implementation is requested
  read_if_needed:
    - `references/section-page-checklist.md`
    - `design-frontend` for repo integration workflow
    - `design-visual-regression` for first viewport and responsive evidence
    - `design-a11y-audit` for headings, landmarks, CTA names, contrast, and focus order
  do_not_load_by_default:
    - unrelated app workflows
    - backend modules
    - live credentials
- risk_profile:
  reads:
    - page design references and scoped UI source files
  writes:
    - section page files only when implementation is explicitly requested
  tools:
    - local preview, browser screenshots, lint/build/test when available
  sensitive_resources:
    - private brand assets and authenticated design sessions default deny
- entry_scene:
  - PREPARE

Use this skill as a real section-page surface specialist. Keep `allow_implicit_invocation: false`; generic visual implementation still routes to `design-frontend` unless this skill is explicitly invoked or attached.

## Workflow
1. Confirm page type and first-screen intent:
   - Identify landing, product, docs, portfolio, venue, brand, object, or campaign page.
   - If the user asked for an app/tool/operational interface, do not turn it into a landing page.
2. Build the section tree:
   - Hero/first viewport, proof/product reveal, feature/workflow/comparison, detail/spec, social proof, FAQ/supporting content, and final CTA.
   - Keep the brand/product/place/object visible as a first-viewport signal when relevant.
3. Translate content and CTA flow:
   - Preserve supplied copy unless edits are requested.
   - Place CTAs where they match user intent; avoid decorative CTA spam.
   - Keep descriptive value props in supporting copy rather than overloaded headings.
4. Translate responsive layout:
   - Define section order, media placement, text wrapping, image cropping, spacing, and mobile/desktop changes.
   - Avoid nested cards, floating section cards, and decorative-only layouts unless established by the repo or design.
5. Implement or hand off:
   - If code changes are requested, follow repo patterns and `design-frontend` integration rules.
   - If only guidance is requested, return the section implementation contract.
6. Validate:
   - Check first viewport, next-section visibility, responsive section order, text fitting, media framing, CTA labels, headings, landmarks, and contrast.
   - Use visual/accessibility gates for screenshot and operability evidence.

## Output schema
```yaml
surface: section-based-web
page_type:
target_route:
section_tree: []
hero_rules: []
first_viewport_signal:
cta_flow: []
content_rules: []
media_rules: []
responsive_order: []
semantic_accessibility: []
visual_validation: []
unresolved_section_gaps: []
unverified: []
```

## Validation
- Verify the first viewport signals the product/place/object/person or literal offer when applicable.
- Verify mobile and desktop text fits without overlap or button clipping.
- Verify responsive order leaves the next section discoverable when this is a landing-style page.
- Verify semantic headings, sections, landmarks, link/button names, and CTA focus order where possible.
- Do not claim page fidelity from build success alone.

## Recovery
- If images/assets are missing, use existing repo assets only when they fit and report substitutions.
- If copy is incomplete, preserve available copy and mark missing sections as gaps.
- If the design resembles marketing but the user asked for an app, hand off to `design-frontend` and avoid a landing-page default.
- If section count is too large, implement the first complete viewport plus the next section and list remaining sections.

## Known Limits
- This skill does not own product strategy, campaign copywriting, or SEO planning.
- It does not replace `design-frontend` for generic visual implementation.
- It does not certify accessibility or visual fidelity without evidence gates.

## Optional resources
- Read `references/section-page-checklist.md` for detailed section-page surface checks.
