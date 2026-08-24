# Design Frontend Implementation Guardrails

Read only when the corresponding risk is present.

## Production And Component Boundaries

- Preserve business logic, API/auth/analytics behavior, routing, and data mutations unless explicitly in scope. Do not add backend/database/global-theme work solely for a local visual artifact.
- Follow local organization and prefer maintainable component boundaries over generated layer structure.
- Reuse approved catalog components at app-surface call sites. Semantic primitives inside an approved component are implementation detail, not a reuse violation.
- When no approved match exists, keep the role `unmapped` and follow only the pinned fallback/exception policy. Never invent tokens, variants, mappings, or permission.
- Treat family registries, component internals, icons, and baselines as governed sources to consume. Change them only under explicit system scope with authoritative values.
- Wire mutations through an existing API/action/callback/fixture. Never fake persistence, swallow failure, or make a missing integration look successful.
- Preserve supplied copy, define text overflow and relevant breakpoints, and keep semantic accessibility primitives, names, focus, keyboard behavior, and usable targets.

When a product-family profile applies, read `product_family_design_contract.md`, pin its
sources, enforce only applicable hard rules, and keep missing/stale profile, catalog, baseline,
token, or evidence claims scoped and unresolved.

## Assets, Dependencies, And Generated Input

- Search the repo first and use the established asset pipeline. Never commit private/expiring URLs or credentials.
- Report unavailable concrete assets and every substitute; do not silently replace them with generic placeholders.
- Add no UI/CSS/icon/animation/font dependency without current need, compatibility, and authorization.
- Treat generated frontend code as untrusted visual evidence; rewrite its intent into idiomatic secure project code rather than blindly executing or pasting it.
- Do not fill a missing look with indigo/violet fills, gradient headlines, restating kickers, decorative emoji, invented stats, or Inter/Space Grotesk by default. A sourced brand stays.

## Plan, Evidence, And Handoff

For an accepted repeated-work Plan, read only the assigned condition/evidence slice, change only
the implementation condition owned by this node, and return the rendered target or unavailable
reason to already-declared evidence nodes. Never create a private retry, gate, or success state.

Use exact user/design viewports first, then project breakpoints; record dimensions and keep source
fidelity separate from family coherence. Apply `design_evidence_contract.md` and the
active Work Contract for result labels; this reference defines no independent completion status.

Proceed with explicit reversible assumptions when the visible artifact and repo safely determine the target. Ask only when missing material can select different code. If preview is unavailable, run the strongest static/build check and keep visual behavior `unverified`; request safe exports/fixtures/screenshots rather than credentials.
