---
name: plan-long-term-package
description: Create explicit multi-document phase/package plans for cross-session work; Agentic HLD-level planning.
---

# Plan Long Term Package

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - explicit `phase 플랜`
  - explicit `서브 플랜`
  - explicit `플랜 패키지`
  - large rewrite package
  - migration package
  - cross-session handoff package
- use_when:
  - the user explicitly requests a multi-document phase/group planning package.
  - the user explicitly asks for docs that future agents can continue from across sessions.
  - the task is too large for one dated plan document and the user wants package-style planning.
- do_not_use_when:
  - the user wants a simple plan doc, small local fix, single bug diagnosis, or one-off implementation plan.
  - the request only contains trigger-like words such as phase, migration, rewrite, plan, or handoff without asking for a package.
  - the user asks for direct implementation, a short TODO list, a summary, or a next-step recommendation.
- expected_inputs:
  - large task scope
  - repo context and prior reports/plans when available
  - archetype/modifier selection inputs
- expected_outputs:
  - canonical dated plan, package README, phase/group docs, required spec contracts, validation results
- context_targets:
  must_read:
    - current package request
    - archetype catalog when task type is not obvious
    - existing active plan or prior report if explicitly relevant
  read_if_needed:
    - prior `docs/plan` packages
    - `docs/spec` contracts
    - source outline and validation contract
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated codebase-intel artifacts
- risk_profile:
  reads:
    - repo docs and prior reports can be broad
  writes:
    - WRITE_LOCAL_FS high: creates many docs under `docs/plan` and `docs/spec`
  tools:
    - CALL_PROCESS for package scripts and validators
  sensitive_resources:
    - credentials default deny; network normally not required
- entry_scene:
  - PREPARE

## Purpose
- Create a planning **package**, not a single plan file.
- Separate product contracts from execution decomposition.
- Keep one source of truth for scope, one for UI state, one for release thresholds, and one for execution status.
- Produce docs that both AI agents and humans can edit safely across sessions.

## Trigger
Use only for explicit heavy artifact intent such as:
- `phase 플랜을 docs package로 만들어줘`
- `서브 플랜 패키지를 만들어줘`
- `플랜 패키지로 작성해줘`
- `다른 세션 에이전트가 이어받을 수 있게 문서 패키지로 만들어줘`
- `multi-phase rewrite plan package`

Do not trigger from a keyword alone.

## When To Use
- Large rewrites, migrations, or multi-phase implementations.
- Work that must outlive the current chat and be resumed by later agents.
- Tasks where product scope, algorithms, UI states, integration boundaries, and release criteria all need explicit docs.

## When Not To Use
- Small local edits.
- Single-bug fixes.
- One-off implementation plans that fit cleanly in a single dated plan file.
- Any casual `플랜` mention without explicit package, phase/group, rewrite, migration, or handoff intent.
- Any casual phase, migration, rewrite, handoff, objective, or goal mention without explicit multi-document package intent.
- A short TODO list, summary, translation, naming question, or next-step recommendation.
- Ordinary research brainstorming, hypothesis triage, paper-idea shaping, loss design, or ablation planning unless the user explicitly asks for a multi-phase experiment package, migration package, or cross-session handoff package.

## Resource and Risk Boundary
- Reads: current request, repo source outline, prior reports/plans, and selected templates.
- Writes: many local docs under `docs/plan` and `docs/spec`; never write production code by default.
- Tool/process calls: package init, ingest, validation, and quality-lint scripts only when their purpose is clear.
- Network access: none by default.
- Credential access: default deny.
- Generated artifacts: high; all generated docs must remain inside the requested package/spec scope.
- Destructive actions: out of scope.
- Required checkpoints: explicit heavy artifact intent, archetype/modifier selection, source-of-truth hierarchy, validation command before finalizing package.

## Recovery and Context Expansion
- If task type is unclear, read `references/archetype-catalog.md` before expanding to repo docs.
- If prior analysis is needed, ingest only cited reports or plan packages relevant to this package.
- If repo structure is unclear, read repo source outline first.
- If validation fails, read validator output and the failing generated doc before expanding wider.
- If the user only needs a lightweight active plan, return to scheduling and use `plan-short-term-docs`.
- Never recover by loading all repo docs, all memory, or all codebase-intel artifacts at once.

## Required Outputs
You must create or update all of the following:

1. Canonical dated plan under `docs/plan/YYYY-MM-DD-<task>.md`
2. Plan package root:
   - `docs/plan/<PlanPackage>/README.md`
3. Phase/group docs under the package
4. Canonical spec docs under `docs/spec/` required by the chosen archetype plus modifiers
5. Domain ingest summary when existing analysis, report, or prior plan docs are available:
   - `docs/plan/<PlanPackage>/domain-ingest-summary.md`

## Existing Analysis Ingest
Read `references/package-authoring-rules.md` before creating or refilling a package. It owns ingest commands, scaffold-only rules, validation modes, and reporting shape.

## Archetype Selection
Select one archetype and zero or more modifiers before generating the package. Read `references/archetype-catalog.md` for the archetype list, aliases, required docs, modifiers, and release-blocking contract rules.

## Source Of Truth Hierarchy
Read `references/source-of-truth-policy.md` before editing package docs. Canonical contracts live in `docs/spec/`; execution status lives in the dated plan; README and phase/group docs are derived.

## Hard Anti-Drift Rules
- UI state names live only in the UI state contract.
- Global progress and approval live only in the canonical dated plan.
- Release gates need numeric thresholds, datasets, regression matrices, and rollback triggers.
- P0 capabilities need contract links or explicit downgrade decisions.
- Hard predecessors gate implementation until complete or waived.
- Unresolved critical interfaces belong in integration contracts, not phase notes.

## Package Structure
Use this default structure:

```text
docs/plan/<PlanPackage>/
  README.md
  Phase*/
docs/spec/
  <slug>-capability-map.md
  <slug>-<required-contract>.md
docs/plan/YYYY-MM-DD-<task>.md
```

## Machine-Readable Metadata
Every generated planning document should include front matter. Required: `doc_type`, `canonical`, `status`, `last_validated`, `source_of_truth_for`, `derived_from`. Phase/group docs should also include dependency and ownership metadata from `references/package-authoring-rules.md`.

## Phase Decomposition Rule
Use phase/group decomposition by concern, not arbitrary document count. Read `references/decomposition-rules.md` for phase/group selection and drift smells.

## Implementation Density Rules
The package must be safe and implementation-oriented. Use ingest evidence, concrete implementation digests, structured acceptance criteria, dependency metadata, and `--quality-lint` as described in `references/package-authoring-rules.md`.

## Canonical Spec Requirements
The exact spec set comes from the archetype and modifiers. Use the dedicated `references/*-template.md` files for specialized contracts and `references/generic-contract-template.md` for other concerns. Do not copy template content into this SKILL.md.

## Canonical Plan Requirements
The canonical dated plan must always include:
- changed file list
- change summary
- risks
- validation procedure
- 질의
- TODO with status
- implementation transition status
- implementation transition marker
- progress log

## Phase/Group Doc Requirements
Each phase/group doc may discuss algorithms, UI, integration, or validation, but it must reference canonical contracts instead of redefining them. It must never claim source-of-truth ownership for a canonical contract.

## Validation Rules
Run `scripts/validate_phase_plan_package.py` after package updates. Use `--strict`, `--strict-handoff`, and `--quality-lint` when release readiness, handoff readiness, or implementation readability matters. Validation mode details live in `references/package-authoring-rules.md`.

## Bundled Resources
- Read [source-of-truth-policy.md](references/source-of-truth-policy.md) before editing package docs.
- Read [archetype-catalog.md](references/archetype-catalog.md) before selecting an archetype or modifiers.
- Read [decomposition-rules.md](references/decomposition-rules.md) when choosing phases/groups.
- Read [package-authoring-rules.md](references/package-authoring-rules.md) for ingest, required outputs, validation modes, and reporting.
- Read [review-checklist.md](references/review-checklist.md) before final validation.
- Use the templates in `references/` to generate package docs consistently.
- Use `scripts/init_phase_plan_package.py` to scaffold new packages.
- Use `scripts/validate_phase_plan_package.py` after updates.
- Use `scripts/validate_phase_plan_package.py --write-validation-stamp` only after validation passes and you want to mark docs as freshly validated.
- Use `scripts/self_test_phase_plan_package.py` after modifying the skill internals.
- The init script should generate a package that is validator-passable immediately after scaffolding.

## Reporting Contract
When finishing a package update:
- state the canonical plan path first
- list the package root
- list the spec docs created or updated
- report validation outcome
- mark any remaining ambiguity as `Unverified`

## Known Limits
- Planning packages do not validate runtime behavior without separate execution evidence.
- Cross-session docs can go stale; source and validation context must be rechecked.
- This heavy artifact generator does not own production code writes.
- Use `plan-short-term-docs` instead when a lightweight active plan is enough.
