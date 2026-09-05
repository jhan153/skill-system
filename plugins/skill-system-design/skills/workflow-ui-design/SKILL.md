---
name: workflow-ui-design
description: Create a concrete, inspectable UI design from accepted requirements, product behavior, brand or product-family context, target platform, content, and required states. Use when a screen, route, component, or native view needs an actual visual design artifact before production implementation. Do not use for unresolved product strategy, existing-reference analysis, production UI code, throwaway interaction prototypes, or evidence-only review.
---

# Workflow UI Design

## Routing Card
- role: execution_primary
- family: design
- intent_signature: create UI design, screen visual design, requirements-to-mockup, 화면 디자인 제작
- use_when:
  - accepted requirements or behavior need a concrete screen/component design artifact
  - the user explicitly delegates visual direction for a web, app, desktop, or native UI surface
- do_not_use_when:
  - product behavior, content ownership, or required functionality is still undecided
  - an existing visual reference only needs decomposition or layout translation
  - the request is production UI implementation, product research, UX writing, image-only illustration, or a throwaway interaction prototype
- expected_inputs: accepted requirements/behavior, target surface/platform, content, brand/product-family/repo context, required states/viewports, and artifact/write boundary
- expected_outputs: inspectable design artifacts, visual/system decisions, implementation handoff, unresolved decisions, and a Core `design_result` when graph-mode identity is supplied
- context_targets:
  must_read:
    - accepted requirements or behavior contract
    - target surface/platform, required content, states, and viewports
    - applicable brand, product-family, design-system, token, component, and asset sources
  read_if_needed:
    - nearby product surfaces and source-traced references that constrain the visual language
    - `references/design_stage_contract.md` when the task is part of a multi-stage request or Plan/Handoff DAG
    - `references/design_evidence_contract.md` for shared evidence labels and proof ceilings
    - `references/product_family_design_contract.md` when a repo/user supplies an applicable family profile, catalog, or visual baseline
    - `references/layout_constraint_contract.md` when material sizing, overflow, text-fit, or responsive constraints must be authored
    - `references/visual_decision_contract.md` whenever the user delegates a new visual direction or existing sources leave material visual choices open
    - `references/execution_item_contract.md` when the result crosses into `design-frontend`, Code Review, a Coordinator, Plan/Handoff, or another plugin
  do_not_load_by_default:
    - full repo, unrelated screens, research archives, production implementation files, private sessions, or credentials
- risk_profile:
  reads: accepted product/design context and only the source material needed for the target
  writes: explicitly requested design artifacts only; never production UI source
  tools: visual/design artifact authoring and bounded rendering or inspection within current authority
  sensitive_resources: authenticated design tools, private assets, and external publishing require explicit authority
- entry_scene: PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/design_result.md`

## Stage Boundary

Apply `references/design_stage_contract.md`. This workflow owns the visual design artifact only;
it never starts implementation or evidence stages. Apply `references/design_evidence_contract.md`
to every source and proposed decision without turning the design artifact into implementation
evidence.

## Design Authority

- Own visual and interface decisions only inside accepted product behavior, content, platform, and
  scope. Product strategy, missing requirements, business policy, and backend behavior remain with
  their current owners.
- Use authoritative brand, product-family, token, component, and asset sources when they exist. If
  the user delegated visual creation and those sources leave a choice open, make one explicit
  `proposed_design_decision` tied to the target's hierarchy, content, task, platform, and state;
  never disguise a factory default as sourced intent.
- Produce one resolved direction by default. Create alternatives only when the user asks for a
  comparison or an unresolved decision genuinely needs a discriminator.
- Do not start `design-frontend`, an evidence gate, or another DAG node. A design artifact is input
  to implementation, not permission or evidence that implementation exists.

## Workflow

1. Bind the target surface, accepted behavior, content, primary task, platform, required states and
   viewports, artifact format, write boundary, and non-goals. Keep a material missing product or
   content decision unresolved instead of inventing it.
2. Resolve the visual source hierarchy: explicit user direction, applicable brand/product-family,
   repository design system, approved tokens/components/assets, nearby surfaces, then delegated
   proposed decisions. When a product-family source applies, use
   `references/product_family_design_contract.md`. Record conflicts without silently choosing a
   lower-authority source.
3. Establish information hierarchy and composition: primary content/action, regions, navigation,
   density, fixed/flexible/scroll zones, responsive order, and text/overflow risks.
4. Design the visual system needed by the target: typography, color, spacing, sizing, radius,
   elevation, iconography, imagery, component language, interaction cues, and motion intent. Reuse
   supplied systems; when creating a direction, make each material choice purposeful and traceable
   rather than filling the screen with generic chrome.
5. Design the required frames and states. Include only material default, loading, empty, error,
   disabled, validation, success, focus/selection, permission, or recovery states supported by the
   accepted behavior. Define required mobile/desktop/native variants without pretending one frame
   proves every breakpoint.
6. Produce an inspectable design artifact in the user-specified format or repository convention.
   With neither, choose the smallest portable visual format that preserves the required frames and
   states; never claim a Figma or native design-tool artifact that was not actually created.
7. Inspect the artifact against the accepted behavior, brand/family sources, content hierarchy,
   required states/viewports, text fit, component/token intent, and obvious accessibility needs.
   This is design readback, not production visual regression or Human Test.
8. Return the design artifact, decision summary, implementation handoff, explicit assumptions and
   unresolved decisions. In graph mode, emit `design_result`; never select the implementation or
   successor node.

## Artifact Contract

The artifact must be visually inspectable. Prose alone is not a completed visual design. Record:

- target surface and exact artifact paths/anchors;
- required frames, viewports, themes, and states actually designed;
- sourced and explicitly proposed visual decisions;
- intended token/component/asset relationships without claiming repo reuse;
- interaction, responsive, overflow, and accessibility intent needed for implementation;
- substitutions, unavailable sources, assumptions, and unresolved product/design decisions;
- one bounded implementation handoff describing what `design-frontend` must realize.

A mockup proves only the design artifact. It does not prove component reuse, production behavior,
rendered fidelity, accessibility, or implementation completion.

## Output Contract

Return only applicable fields:
- `design_scope`
- `design_snapshot`
- `requirements_refs`
- `design_artifacts`
- `frames_and_states`
- `visual_decisions`
- `token_component_asset_intent`
- `implementation_handoff`
- `unresolved_decisions`
- `user_checks`
- Core `design_result` when graph-mode identity is supplied
