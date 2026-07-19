---
name: plan-long-term-package
description: Create a validated multi-document phase/package plan for a large rewrite, migration, or cross-session handoff. Use only when the user explicitly requests package-style planning; use plan-short-term-docs for a single active plan.
disable-model-invocation: true
---

# Plan Long Term Package

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - explicit phase/subplan/package artifact
  - large rewrite or migration package
  - cross-session handoff package
- use_when:
  - the user explicitly requests a multi-document phase/group package.
  - the work needs canonical contracts plus resumable execution decomposition.
- do_not_use_when:
  - one dated plan is sufficient.
  - the request is direct implementation, a local fix, a TODO, a summary, or a casual mention of plan/phase/migration.
  - research ideation does not explicitly request a multi-phase experiment package.
- expected_inputs:
  - package objective, scope, constraints, and available repo evidence
  - archetype/modifier decision inputs
- expected_outputs:
  - canonical dated plan, package README, phase/group docs, selected canonical specs, and validation result
- context_targets:
  must_read:
    - current package request
  read_if_needed:
    - matched rows in `references/archetype-catalog.md`
    - `references/package-core-invariants.md` after package intent is confirmed
    - explicitly relevant active plan, report, or prior package
    - source outline and validation contract
    - `.codex/docs/planning_state_model.md` when state names or release gates could drift
  do_not_load_by_default:
    - full repo or memory bank
    - all prior plans or codebase-intel artifacts
    - the entire `references/` tree
- risk_profile:
  reads:
    - selected repo evidence and references can still be broad
  writes:
    - WRITE_LOCAL_FS high: many requested docs under `docs/plan` and `docs/spec`
  tools:
    - CALL_PROCESS for bundled init, ingest, and validation scripts
  sensitive_resources:
    - credentials default deny; network normally unnecessary
- entry_scene:
  - PREPARE

## State Boundary
- Create a package, not production code or a single plan file.
- Scope/contracts belong to canonical `docs/spec/` owners; current status and approval belong to the canonical dated plan; README and phase/group docs are derived.
- `package_planned` is not `implementation_ready`, execution approval, or proof that implementation behavior works.

## Staged Admission
Admit one layer at a time:
1. **Intent** — Read only the request. Without explicit multi-document package intent, route to `plan-short-term-docs` or the task owner.
2. **Evidence** — Inspect named reports/plans and a compact source outline; open only evidence that can change scope, dependencies, contracts, or gates.
3. **Selection** — Search `references/archetype-catalog.md` for matching archetype/modifier rows. Read the full catalog only when no match is reliable or the task genuinely spans archetypes.
4. **Kernel** — Read `references/package-core-invariants.md`; it owns authority, claim ledger, manifest, budget, materialization order, phase readiness, and release truth. Read `references/source-of-truth-policy.md` only for an ownership conflict.
5. **Authoring** — Read `references/package-authoring-rules.md` for scaffold/update mechanics. Load only the 1-3 templates needed for the next canonical batch.
6. **Decomposition/review** — Read `references/decomposition-rules.md` only when splitting concerns and `references/review-checklist.md` only at the final gate.

On validation failure, inspect the validator message and failing document first; do not sweep the repo, memory, prior plans, or template library.

## Package Workflow
1. Grade each scope-shaping statement in the claim ledger; select one archetype, justified modifiers, package slug, and current planning state.
2. Freeze the complete manifest and authority map, including derived paths. Compute modifier deltas and pass the default 20-artifact cap or an explicitly justified higher-cap preflight before any mkdir/write. Never drop a required risk contract to fit the cap.
3. Ingest only cited relevant reports/plans as derived evidence. Retain source pointers and do not create an empty ingest summary.
4. Run `scripts/init_phase_plan_package.py --canonical-only`; fill canonical owners from admitted evidence in batches of 1-3 without leaving placeholders.
5. Once canonical IDs, gates, topology, ingest binding, and budget are stable, run `--derived-only` with the exact same selection. Any drift must fail before derived writes.
6. Decompose by independently verifiable concern, make hard predecessors explicit, and reconcile every derived statement to its canonical owner.
7. Validate the complete package and report unresolved claims, decisions, or evidence as `Unverified` or blockers.

## Completion Gate
- A phase needs bounded outcome/non-goals, target surface, canonical links, predecessors, first implementation step, and acceptance rows linking `Contract`, `Evidence`, `Test command`, and `Blocking`.
- Logic, parity, lifecycle, performance, accessibility, or UX claims need a behavior oracle with scenario/input, observable result, verifier, evidence destination, and owner. Static presence checks close structural requirements only.
- Scaffold-only prose, placeholders, vague acceptance, unknown critical interfaces, failed upstream gates, or open blocking claims cannot be promoted by a derived rollup or validation stamp.
- Create `package_planned` only after canonical and derived artifacts exist, the authority/manifest contracts hold, and full-package validation passes. It still does not authorize implementation.

## Validation
Run `scripts/validate_phase_plan_package.py` after each package update. Add `--strict` for release-critical semantics, `--strict-handoff` for implementation handoff, `--quality-lint` for executable/readable phase content, and `--write-validation-stamp` only after a pass.

Run `scripts/self_test_phase_plan_package.py` only after changing this skill's scripts, schema, catalog, or templates. Document validation never proves production runtime or user-visible behavior.

## Reporting
Return an index, not duplicated package content: canonical plan and `package_planned` evidence; package root and selection; changed spec/phase paths; validation commands/outcomes; blockers, residual risks, and `Unverified` items.
