# Design Stage Contract

This contract defines shared role and transition rules for UI design creation, source analysis,
design-system mapping, production implementation, and condition-scoped evidence. It is not a
required pipeline, workflow runner, or permission to start another stage.

## Role Ownership

| Requested outcome | Owner | Output ceiling |
|---|---|---|
| new concrete UI design from accepted product behavior | `workflow-ui-design` | inspectable design plus Core `design_result`, not production code |
| existing-reference hierarchy/state decomposition | `design-ui-decomposer` | source-traced analysis, not design creation or code |
| layout constraint translation | `design-layout-translator` | code-ready rules, not implementation |
| token authority/mapping/gaps | `design-tokens` | token evidence or explicitly requested token artifact edits, not UI completion |
| component/catalog mapping and reuse evidence | `design-component-mapper` | mapping/reuse condition evidence, not component API redesign or UI code |
| concrete design to production UI | `design-frontend` | repo-integrated UI plus Core `implementation_result` |
| rendered target/family visual evidence | `design-visual-regression` | assigned visual condition evidence, not fixes or completion |
| accessibility evidence | `design-a11y-audit` | assigned accessibility condition evidence, not fixes or global compliance |

## Transition Rules

- Select one owner from the requested artifact or outcome. A completed design artifact, analysis,
  mapping, or evidence result never starts another skill automatically.
- Use several stages only when the user explicitly requests the combined outcome or an accepted
  Plan/Handoff DAG already contains those nodes and dependencies.
- Missing upstream input remains an explicit gap. Name its current owner without invoking it,
  creating a substitute artifact, or blocking independent accepted work.
- `design-frontend` is the only production UI writer in this family. Analysis and evidence owners
  never edit the implementation to make their condition pass.
- A gate closes only the condition assigned by the user or Plan. It never selects a successor,
  rewrites Plan/Handoff, triggers repair/retry, or globally blocks unrelated work.
- Agent visual, token, component, build, and accessibility evidence is pre-handoff support. It does
  not replace the Human Test phase or the user's product/design judgment.

## Direct Work And Execution Handoff

- Direct single-owner work may use the relevant principles without manufacturing separate stage
  artifacts. Explicitly requested artifacts retain their named owner.
- In Plan DAG mode, `workflow-ui-design` returns `design_result`; `design-frontend` consumes it and
  returns `implementation_result`; `workflow-code-review` may use the design result as an optional
  conformance baseline.
- Design evidence nodes return compact condition/evidence/gap fields and require no new Core Card.
  The Coordinator records the result and applies only existing Plan edges.
- Repeated visual or accessibility steering uses the shared repeated-work profile only when the
  Plan explicitly admits it. No Design skill owns a private loop, retry state, or back-edge.
- The default development Waterfall still terminates at `human_test_ready`. Design evidence remains
  supporting evidence before that boundary, not a separate Test phase.
