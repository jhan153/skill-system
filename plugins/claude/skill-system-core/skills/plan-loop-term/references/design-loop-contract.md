# Design Loop Contract

Use this profile for UI, screenshot/Figma implementation, responsive behavior, or design-to-production work. Keep runtime verifier types schema-valid and represent visual/a11y judgment as separate quality verifiers.

## Owners

- implementation: `design-frontend`
- visual quality: `design-visual-regression`
- accessibility quality: `design-a11y-audit`
- optional tokens/states: `design-tokens`, `design-component-mapper`; make them required for the conditions declared by an applicable product-family profile
- deterministic build/schema checks: project command or `workflow-validation`
- loop execution after acceptance: `workflow-loop-runner`

## Condition Profile

Use `SC-NNN` only. Copy each `runtime_verifier.type` and its command/path into the runtime contract; keep `quality_verifiers` in the companion.

```yaml
contract_id: LC-YYYYMMDD-NNN
loop_run_id: null
success_conditions:
  - id: SC-001
    statement: "The target route/screen/component is integrated and passes its real build or smoke command."
    runtime_verifier:
      owner: workflow-validation
      type: command_exit
      evidence_target: "command output and exit code"
    quality_verifiers: []

  - id: SC-002
    statement: "Every required current screenshot is nonblank."
    runtime_verifier:
      owner: design-visual-regression
      type: command_exit
      evidence_target: "check_screenshot_nonblank.py command receipt over every required screenshot"
    quality_verifiers: []

  - id: SC-003
    statement: "Framing, hierarchy, layout, typography, color, imagery, and spacing meet the admitted source criteria."
    runtime_verifier:
      owner: "<accepting-user>"
      type: manual_check
      evidence_target: "accepted user event scoped to SC-003:visual-fidelity"
      acceptance_scope: "SC-003:visual-fidelity"
    quality_verifiers:
      - {owner: design-visual-regression, type: visual, evidence_target: "comparison verdict and gap list"}

  - id: SC-004
    statement: "Required viewports have no clipping, overflow, overlap, or off-canvas primary content."
    runtime_verifier:
      owner: "<accepting-user>"
      type: manual_check
      evidence_target: "accepted user event scoped to SC-004:viewport-behavior"
      acceptance_scope: "SC-004:viewport-behavior"
    quality_verifiers:
      - {owner: design-visual-regression, type: visual, evidence_target: "viewport screenshots and findings"}

  - id: SC-005
    statement: "Required keyboard, focus, semantics, labels, contrast, target-size, and readability checks pass."
    runtime_verifier:
      owner: "<accepting-user>"
      type: manual_check
      evidence_target: "accepted user event scoped to SC-005:accessibility"
      acceptance_scope: "SC-005:accessibility"
    quality_verifiers:
      - {owner: design-a11y-audit, type: a11y, evidence_target: "tool/manual observations and verdicts"}
```

Replace `<accepting-user>` and each scope with the accepted contract's real owner/scope. Record a real visual/a11y validator command or manual event as audit evidence, but local v2 cannot authenticate either as pass. Semantic conditions remain `unverified` or `user-verification-needed`; the quality report informs the decision but cannot close the condition by existing.

## Conditional Product-Family And UX Conditions

Add only the conditions supported by an applicable pinned profile or a task-bearing interactive requirement. Replace every placeholder with a real project command, baseline, path, or acceptance owner before accepting the loop. For a component/story, replace SC-008 with a scoped interaction/state condition instead of inventing an end-to-end user path.

```yaml
success_conditions:
  - id: SC-006
    statement: "Applicable hard family rules, governance-source write policies, and approved app-surface component reuse requirements pass their declared project checks."
    runtime_verifier:
      owner: workflow-validation
      type: command_exit
      evidence_target: "<family-policy-command> output and exit code, including pinned consume-only source checks when declared"
    quality_verifiers:
      - {owner: design-component-mapper, type: component_contract, evidence_target: "pinned catalog plus app-surface import/use report, exceptions, conflicts, and gaps"}

  - id: SC-007
    statement: "The target is coherent with each applicable pinned product-family baseline on its shared visual axes."
    runtime_verifier:
      owner: "<accepting-user>"
      type: manual_check
      evidence_target: "accepted user event scoped to SC-007:family-coherence"
      acceptance_scope: "SC-007:family-coherence"
    quality_verifiers:
      - {owner: design-visual-regression, type: visual, evidence_target: "separate family-coherence verdict with pinned baselines and viewport-specific findings"}

  - id: SC-008
    statement: "The supplied primary user task completes through its real integration path and material failure/recovery state without simulated success."
    runtime_verifier:
      owner: workflow-validation
      type: command_exit
      evidence_target: "<critical-path-command> output and exit code"
    quality_verifiers: []
```

If SC-006 lacks a real project-specific command, component inventory or a mapper report cannot substitute for deterministic enforcement; keep it `unverified` or use explicit accepted manual scope. If SC-008 lacks an executable user-path oracle, use scoped user acceptance and keep local v2 non-passing without authenticated provenance. Do not add SC-007 when the family has no applicable pinned baseline.

Use `artifact_exists` only when the condition itself is “this exact artifact exists.” It cannot prove framing, fidelity, responsive behavior, accessibility, or any report verdict. If no deterministic or accepted-manual oracle exists, keep the semantic condition `unverified` or `user-verification-needed`.

Use runtime `manual_check` only for explicit user acceptance. Local v2 validates the event shape/digest for audit but keeps it non-passing without host-authenticated provenance.

## Evidence Boundaries

- Build success proves build/smoke scope, not visual or accessibility quality.
- A nonblank screenshot proves render presence, not fidelity.
- Component catalog membership proves availability, not app-surface reuse; require import/use evidence and the declared policy command where one exists.
- Exact-target fidelity and product-family coherence are separate claims with separate sources and verdicts.
- A control-decision record does not prove the critical user task works; exercise the path and its material recovery state.
- Visual comparison does not prove keyboard, semantics, or screen-reader behavior.
- Static a11y hints do not prove complete WCAG compliance.
- A screenshot/report without source, viewport, owner, freshness, and verdict is incomplete evidence.
- Free-form refs and maker self-review never prove pass.

## Progress And Stop

Progress is a verified `SC-NNN`/evidence delta: a build failure becomes a quality-verifier result, a concrete visual/a11y finding is fixed, or a current report changes the next action. More edits or screenshots without a verdict delta are not progress.

- `success`: every required condition has a fresh schema-valid passing receipt; no user/manual gate remains open.
- `blocked`: source, asset, target, authenticated context, or preview environment is unavailable.
- `budget`: accepted viewport/fidelity iteration budget is exhausted.
- `unsafe`: next action requires private-session access, external publishing, paid API, credential, or unrelated broad redesign.
- `fatal`: source or verifier state is untrustworthy.

## Checkpoint And Handoff

```yaml
handoff:
  contract_id: LC-YYYYMMDD-NNN
  loop_run_id: null
  implementation_owner: design-frontend
  verifier_gates: [design-visual-regression, design-a11y-audit]
  optional_gates: [design-tokens, design-component-mapper]
  loop_runner: workflow-loop-runner
  max_iterations: 3
  strategy_change_after: 2
  checkpoint_after_each:
    - changed_files
    - rendered_target_and_viewports
    - quality_report_and_screenshot_refs
    - structured_evidence_receipts
    - remaining_SC_NNN
```
