---
name: plan-long-term-package
description: Create a validated multi-document phase/package plan for a large rewrite, migration, or cross-session handoff. Use only when the user explicitly requests package-style planning; use plan-short-term-docs for a single active plan.
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

## Objective And State Boundary
- Create a package, not production code or a single plan file.
- Create the `package_planned` overlay only after the package has one canonical authority map and measurable release gates.
- Keep scope/contracts in `docs/spec/`, execution status in the canonical dated plan, and navigation/phase docs derived.
- Do not treat `package_planned` as `implementation_ready` or execution approval.

## Staged Context Admission
Admit one layer at a time and stop when the next decision is supported:

1. **Intent** — Read only the request. Require explicit multi-document package intent; otherwise route to `plan-short-term-docs` or the task owner.
2. **Evidence index** — Inspect named reports/plans and a repo source outline before opening raw content. Admit only sources that can change scope, dependencies, contracts, or gates.
3. **Archetype index** — Search `references/archetype-catalog.md` for task terms. Read the matching archetype row, selection rule, and relevant modifier rows; read the full catalog only when no match is reliable or the task genuinely spans archetypes.
4. **Manifest** — Read `references/package-core-invariants.md`, create the claim ledger and authority map, then freeze the artifact manifest before opening templates. Read `references/package-authoring-rules.md` only for scaffold/update mechanics and `references/source-of-truth-policy.md` only when ownership is ambiguous or conflicting.
5. **Artifact batch** — Load only the 1-3 templates needed for the next canonical artifact batch. Extract their constraints into the manifest; do not carry unrelated template prose forward.
6. **Decomposition/final review** — Read `references/decomposition-rules.md` only when splitting phases and `references/review-checklist.md` only for the final gate.

If validation fails, inspect the validator message and failing document first. Never recover by sweeping the repo, memory, prior plans, or template library.

## Artifact Budget And Modifier Gate
- The default cap is 20 artifacts in the final manifest. Count the canonical plan, every required `docs/spec/` artifact, README, every phase/group doc, and one ingest summary only when at least one real report/plan input is admitted. Delayed artifacts still count.
- Run the manifest preflight before any package mkdir or write. A higher cap is valid only when the canonical plan records the projected count, complete projected path list, and a nonempty explicit override reason.
- For every modifier, cite the claim-ledger IDs that justify it and compute both its artifact delta and release-blocking delta against the selected archetype. When both are zero, record `absorbed-by-archetype`; do not invent a new document or gate.
- Prefer the archetype that directly owns the primary work and required risk contracts when two candidates fit. Do not choose a narrow artifact set by dropping a requested parity, rollback, security, data, or handoff condition.
- Once a modifier is selected, keep the full `required_specs_for` union and final validator contract. Never omit a modifier-required document merely to fit the cap.
- If the projected manifest still exceeds 20, reconsider the archetype/modifier evidence first. Otherwise stop before writing until the user request or an accepted decision explicitly authorizes a higher cap and states why each added artifact is needed.

## Deterministic Package Workflow
1. Record one `archetype`, zero or more modifiers, package slug, current planning state, and a claim ledger that grades each scope-shaping statement.
2. Compute modifier deltas, the de-duplicated archetype/modifier/universal contract union, and the complete final-manifest budget. Pass the default-cap or explicit-override preflight before any mkdir/write.
3. Build an authority map for scope, state names, interfaces, release gates, and execution status. Give each concern exactly one canonical owner.
4. Ingest only cited, relevant analysis or prior plans. Mark the ingest summary as derived evidence and retain source pointers.
5. Scaffold the canonical plan, canonical specs, and any admitted ingest evidence with `scripts/init_phase_plan_package.py --canonical-only`; then replace placeholders from admitted evidence in 1-3 artifact batches.
6. After canonical owners, IDs, and gates are stable, materialize README, phase/group docs, and the procedural handoff view once with `--derived-only`. Reuse the exact archetype, modifiers, phase topology, ingest binding, artifact cap, and projected manifest recorded by the canonical stage; drift must fail before a derived write. The no-flag full scaffold remains a compatibility path, not the default authoring path.
7. Decompose by independently verifiable concern, not document count. Make hard predecessors explicit.
8. Reconcile every derived statement to its canonical owner, then validate and report remaining unknowns as `Unverified` or blockers.

## Required Artifact Manifest
Freeze these entries before content generation:

- `canonical_plan`: `docs/plan/YYYY-MM-DD-<task>.md`
- `package_root`: `docs/plan/<PlanPackage>/README.md`
- `phase_docs`: concern-based phase/group paths with stable order and dependencies
- `contract_docs`: selected canonical `docs/spec/` paths and owning concerns
- `domain_ingest_summary`: required when relevant prior analysis or plans exist
- `artifact_budget`: default/effective cap, projected count, complete projected paths, modifier deltas, and override reason or `none`
- `claim_ledger`: canonical-plan section mapping material claims to grade, source, impact, and unresolved decision
- `validation_modes`: default plus any justified `strict`, `strict-handoff`, or `quality-lint`

The canonical dated plan must include changed files, what/why, risks, validation, `질의`, status-bearing TODOs, implementation-transition status/marker, and progress log. Every generated planning document must include `doc_type`, `canonical`, `status`, `last_validated`, `source_of_truth_for`, and `derived_from`; phase/group docs also carry dependency and ownership metadata defined by the authoring rules.

## Implementation-Ready Phase Contract
Require every phase/group to state:

- bounded outcome and non-goals
- target files/components or an explicit discovery task
- canonical contract links, without redefining them
- hard/soft predecessors and blocking decisions
- concrete first step and implementation digest
- acceptance rows with `Contract`, `Evidence`, `Test command`, and `Blocking`
- a behavior oracle for logic, parity, lifecycle, performance, or UX claims; static presence checks are sufficient only for structural requirements
- exit gate and rollback/fallback when the phase is risky

Do not finalize scaffold-only prose, empty placeholders, vague verbs, or acceptance criteria without observable evidence. Unknown critical interfaces belong in a canonical integration contract and block dependents until resolved or explicitly waived.

## Quality Gates
- **Admission:** explicit package intent and bounded scope are present.
- **Manifest:** one archetype is selected; modifier/universal unions match the artifact set; every canonical concern has one owner.
- **Budget:** final-manifest preflight passes before writes; any cap increase has an explicit nonempty reason, and absorbed modifiers add neither docs nor gates.
- **Evidence:** every scope-shaping claim is graded in the claim ledger; inferred or unavailable facts cannot silently become requirements.
- **Execution:** each phase satisfies the implementation-ready contract, has no untracked hard predecessor, and closes its blocking behavior oracles rather than merely creating documents.
- **Anti-drift:** UI states, global status, approval, interfaces, and release gates are defined only by their canonical owners.
- **Release:** thresholds, datasets, regression evidence, and rollback triggers are measurable where applicable; every P0 capability links to a contract or an explicit downgrade.
- **Validation:** bundled validation passes at the strength required by the intended handoff.

## Validation
Run `scripts/validate_phase_plan_package.py` after every package update. Add:

- `--strict` for release-critical semantic readiness.
- `--strict-handoff` for an implementation handoff.
- `--quality-lint` for executable/readable phase content.
- `--write-validation-stamp` only after a passing run.

Run `scripts/self_test_phase_plan_package.py` only after changing this skill's scripts, schema, catalog, or templates. Do not report runtime behavior as validated from document checks alone.

Canonical-only staging is not a validated package and cannot create `package_planned`. Run the normal full-package validator only after derived materialization is complete.

## Reporting Contract
Report, in order:

1. canonical plan path and `package_planned` state/evidence
2. package root and selected archetype/modifiers
3. created/updated spec and phase paths
4. validation commands and outcomes
5. blockers, residual risks, or `Unverified` items

Keep the report as an index; do not reproduce the package contents.
