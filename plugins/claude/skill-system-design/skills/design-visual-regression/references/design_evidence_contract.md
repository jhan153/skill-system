# Design Evidence Contract

This contract defines evidence labels and proof ceilings shared across Design skills. It does not
choose a visual direction, require every evidence lane, or decide Plan completion.

## Evidence Labels

- `observed`: directly visible or measured in the cited artifact/runtime surface.
- `source_metadata`: explicitly supplied by a design tool, specification, token source, catalog, or
  other named authority.
- `inferred`: a bounded interpretation from observed evidence; state the assumption and falsifier.
- `unverified`: the required evidence or authority is unavailable, conflicting, or outside scope.
- `user-verification-needed`: only the declared human owner can supply or judge the remaining
  condition after agent-owned work is complete.

Source identity and existence do not prove the design, implementation, or user-facing claim. Keep
conflicts and unavailable evidence visible instead of promoting a lower-scope observation.

## Proof Ceilings

| Evidence | Proves | Does not prove |
|---|---|---|
| screenshot or flat image | visible pixels and spatial relationships for that frame | DOM/native hierarchy, offscreen behavior, breakpoints, interaction, exact tokens, accessibility |
| Figma/design metadata | only the values, constraints, component links, and states it explicitly exposes | production implementation or undeclared responsive behavior |
| design artifact | intended design for its declared frames/states | production code, repo component reuse, runtime behavior, Human Test |
| token source/readback | token identity, value, alias, mode, and selected consumer path in scope | rendered fidelity or subjective quality |
| component catalog/export | component availability and declared contract | actual app-surface reuse |
| app-surface import/use evidence | use of the named component at the cited site | visual fidelity, complete state coverage, or accessibility |
| build/type/static check | its declared structural/integration contract | rendered appearance, interaction, or design conformance |
| rendered screenshot comparison | target/family visual condition at named viewport/state | code correctness, keyboard behavior, semantics, complete responsiveness |
| DOM/accessibility tree/interaction/measurement | the exact semantic, keyboard, focus, contrast, size, or reflow condition observed | full WCAG compliance or unrelated conditions |
| agent-authored mock, fixture, scan, or heuristic | only its encoded or sampled boundary | product truth, human preference, or broader completion |

## Gate And Handoff Rules

- Verify only conditions material to the current user request or accepted Plan. Do not assemble a
  full token/component/visual/a11y suite by default.
- A pass, fail, unavailable result, or finding remains local to its condition. Gate workers never
  edit production, select Plan nodes, or start another evidence owner.
- Missing capture/runtime/tool capability normally leaves the affected condition `unverified` or
  `user-verification-needed`; use lifecycle escalation only when a required accepted node cannot
  produce any result. Do not create substitute tests or artifacts merely to improve the label.
- Human Test remains outside agent evidence. A polished mockup, green build, clean static scan, or
  screenshot match never proves the user's end-to-end product observation.
