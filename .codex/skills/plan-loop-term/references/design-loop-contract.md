# Design Loop Contract

Use this profile when a loop term targets UI, visual design, Figma/screenshot implementation, responsive behavior, or design-to-production work.

## Default Downstream Skills
- Implementation owner: `design-frontend`
- Visual evidence gate: `design-visual-regression`
- Accessibility evidence gate: `design-a11y-audit`
- Optional token evidence: `design-tokens`
- Optional component/state evidence: `design-component-mapper`
- Optional validation owner: `workflow-validation`
- Execution loop owner after acceptance: `workflow-loop-runner`

## Required Success Conditions
Use stable ids such as `SC-DESIGN-01`.

```yaml
success_conditions:
  - id: SC-DESIGN-01
    statement: "Target route/screen/component/story exists and is integrated into the repo."
    verifier_owner: design-frontend
    evidence: "changed files plus rendered target path or preview surface"
  - id: SC-DESIGN-02
    statement: "Rendered target is nonblank and primary UI is correctly framed."
    verifier_owner: design-visual-regression
    evidence: "screenshot path, viewport, nonblank/framing result"
  - id: SC-DESIGN-03
    statement: "Visual hierarchy, layout regions, typography, color, imagery, and spacing match the source reference within available evidence."
    verifier_owner: design-visual-regression
    evidence: "comparison notes or image diff, with unavailable source details marked"
  - id: SC-DESIGN-04
    statement: "Relevant desktop/mobile viewports have no obvious clipping, overflow, text overlap, or off-canvas primary content."
    verifier_owner: design-visual-regression
    evidence: "viewport-specific screenshots and findings"
  - id: SC-DESIGN-05
    statement: "Keyboard/focus, semantics, labels, contrast, target size, and responsive readability gaps are handled or explicitly marked."
    verifier_owner: design-a11y-audit
    evidence: "a11y result or user-verification-needed/unverified labels"
```

## Evidence Boundaries
- Build success proves the target can compile or run; it does not prove visual fidelity.
- A nonblank screenshot proves something rendered; it does not prove hierarchy, spacing, typography, or responsive quality.
- Visual comparison proves observable UI gaps; it does not prove keyboard, focus, semantic, or screen reader behavior.
- Static accessibility hints can identify gaps; they do not prove complete WCAG compliance.
- Human/user design acceptance is valid only when recorded as `user-verification-needed` resolved by the user or as explicit user-provided evidence.

## Progress Signals
- a required design success condition changes from fail/unverified to pass
- a screenshot becomes nonblank or correctly framed
- a viewport-specific overflow/clipping finding is fixed
- accessibility evidence is collected or a gap is resolved
- a build/render failure changes into a visual/a11y verifier result
- the next implementation batch is changed because a visual/a11y verifier identified a concrete gap

## Stop Policy Defaults
- `success`: required visual/build/a11y success conditions pass or have accepted user-verification-needed labels.
- `blocked`: source reference, assets, render target, authenticated design context, or preview environment is unavailable.
- `budget`: viewport/fidelity iteration budget is exhausted.
- `unsafe`: next action requires private session access, external publishing, paid API, credential, or unrelated broad redesign.
- `fatal`: screenshot/verifier tooling or source-reference state cannot be trusted.

## Design Loop State
```yaml
design_loop_state:
  source_reference:
    type: figma|screenshot|description|existing_app|unknown
    trust_status: accepted|untrusted_observation|user-verification-needed
  rendered_targets: []
  viewports: []
  visual_gaps: []
  accessibility_gaps: []
  unavailable_assets: []
  accepted_substitutions: []
```

## Handoff Shape
```yaml
handoff:
  primary_execution_skill: design-frontend
  verifier_gates:
    - design-visual-regression
    - design-a11y-audit
  optional_gates:
    - design-tokens
    - design-component-mapper
  loop_runner: workflow-loop-runner
  max_iterations: 3
  strategy_change_after: 2
  checkpoint_after_each:
    - changed files
    - rendered target
    - screenshot paths
    - verifier results
    - remaining failed success conditions
```

## Do Not Use As Proof
- Build success alone
- Agent self-review
- A screenshot without viewport/source context
- A11y static hints as full WCAG compliance
- Pixel-perfect claims without side-by-side evidence or image diff evidence
