---
name: plan-long-term-package
description: Create a heavy multi-document planning package only when the user explicitly asks for phase/subplan/package-style planning that future sessions must continue from docs alone.
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
Before generating or refilling a plan package, ingest existing analysis reports and prior planning docs.

Use the bundled ingest script:

```bash
python3 scripts/ingest_analysis_reports.py --root <repo-root> --auto --out docs/plan/<PlanPackage>/domain-ingest-summary.md
```

Or pass explicit sources:

```bash
python3 scripts/ingest_analysis_reports.py --root <repo-root> --report docs/codebase-intel --report docs/plan/<OldPlan> --out docs/plan/<PlanPackage>/domain-ingest-summary.md
```

`init_phase_plan_package.py` supports the same workflow:

```bash
python3 scripts/init_phase_plan_package.py ... --auto-ingest
python3 scripts/init_phase_plan_package.py ... --ingest-report docs/codebase-intel --ingest-report docs/plan/<OldPlan>
```

Rules:
- Treat the ingest summary as derived evidence, not canonical truth.
- Use cited source lines from `domain-ingest-summary.md` to fill canonical specs and group Purpose/Current State/Target State/Acceptance Criteria.
- If existing reports are available but the generated package still contains empty or generic group sections, the package is scaffold-only and must not be presented as a completed plan.
- `--quality-lint` must fail generic scaffold phrases such as empty Purpose/Current/Target sections, generic AC text, or generic Before/After text.

## Archetype Selection
Select one archetype and zero or more modifiers before generating the package.

```yaml
package_selection:
  archetype: "primary work type"
  modifiers:
    - "additional validation condition"
```

- `archetype` determines the required contract docs.
- `modifier` adds stronger validation docs without changing the primary archetype.
- Required docs are calculated from `archetype + modifiers`; the validator must check the same combination.
- `release-gate` and `agent-handoff-index` are universal outputs for every archetype.
- Release-blocking docs are calculated from `release_blocking_specs_by_archetype + release_blocking_specs_by_modifier`; they are seeded as required gate inputs in the release gate.
- Read [archetype-catalog.md](references/archetype-catalog.md) before choosing when the task type is not obvious.

Core archetypes:
- `application-product`
- `web-product`
- `backend-service`
- `architecture-refactor`
- `large-scale-refactor`
- `modularization`
- `migration-modernization`
- `algorithm-engine`
- `rendering-engine`
- `realtime-runtime-pipeline`
- `integration-adapter`
- `library-sdk`
- `infra-build-release`
- `test-validation-system`
- `stabilization-hardening`
- `performance-optimization`
- `firmware-hardware`
- `ml-data-training-pipeline`
- `documentation-handoff-package`

Supported modifiers:
- `no-behavior-change`
- `strict-behavior-parity`
- `legacy-parity`
- `performance-critical`
- `realtime-critical`
- `rendering-heavy`
- `local-device-runtime`
- `hardware-integration`
- `mesh-processing-heavy`
- `gap-tracking`
- `external-api`
- `rollback-required`
- `cross-session-handoff`
- `public-api-sensitive`
- `data-sensitive`
- `security-sensitive`

Compatibility aliases:
- `ui-product` -> `application-product`
- `algorithm-rewrite` -> `algorithm-engine`
- `migration-only` -> `migration-modernization`

## Source Of Truth Hierarchy
This is the most important rule set.

1. `docs/spec/*capability-map*.md`
   - Canonical for scope, priority, and parity target
2. `docs/spec/*ui-state-contract*.md`
   - Canonical for state names, state ids, transitions, error states, CTA rules
3. `docs/spec/*integration-contract*.md`
   - Canonical for module boundaries and extracted capability ownership
4. `docs/spec/*release-gate*.md`
   - Universal final verdict aggregator for pass/fail thresholds, datasets, regression matrix, tolerances, and specialized gates
5. Other archetype/modifier contract docs
   - Canonical for their declared `source_of_truth_for` front matter concerns
6. Canonical dated plan
   - Canonical for current execution status, approval state, TODO status, blocked items
7. Plan package README
   - Navigation and rollup only; never define canonical contracts
8. Phase/group docs
   - Work decomposition only; may not redefine canonical contracts

## Hard Anti-Drift Rules
These rules exist to prevent the exact failure modes seen in prior planning packages.

### 1) UI State Contract Must Be Singular
- State names live only in the UI state contract.
- Phase/group docs may reference state ids, but must not redefine the state list.
- If a phase doc needs to discuss states, it must link to the canonical ids from the UI state contract.

### 2) Status Must Have One Authority
- Global progress and approval live only in the canonical dated plan.
- The package README may summarize status, but that summary is derived and non-authoritative.
- Never leave README checklist status contradicting the canonical dated plan.

### 3) Release Gate Must Be Numeric
- The release gate document must include:
  - test datasets
  - numeric tolerances
  - pass/fail thresholds
  - regression matrix
  - rollback triggers
- Directional claims like “good enough” are not sufficient.

### 4) P0 Scope Cannot Drift Silently
- Every P0 capability in the capability map must either:
  - have a corresponding closed contract doc, or
  - be explicitly downgraded via a decision record
- Do not leave a P0 item as a vague TODO without a contract.

### 5) Hard Predecessors Must Gate Implementation
- If a phase/group is marked `hard predecessor`, implementation cannot start until it is complete or explicitly waived.
- Typical examples:
  - stability refactor
  - integration contract
  - release-gate thresholds

### 6) Critical Interfaces Need Explicit Contracts
- If a module boundary is still uncertain, create or update the integration contract before proceeding.
- Do not hide unresolved ownership questions inside phase notes.

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
Every generated planning document should include front matter where possible.

Required metadata fields:
- `doc_type`
- `canonical`
- `status`
- `last_validated`
- `source_of_truth_for`
- `derived_from`

Recommended metadata fields for phase/group docs:
- `phase`
- `phase_order`
- `group_id`
- `hard_predecessor`
- `depends_on`
- `soft_depends_on`
- `blocking_interfaces`
- `relevant_specs`
- `owned_concerns`

## Phase Decomposition Rule
Use phase/group decomposition by concern, not by arbitrary document count.
Default is 4 phases, but this is configurable. Do not hardcode 4 phases in the conceptual workflow.

- Phase 1: domain baseline and contracts
- Phase 2: product surface and interaction model
- Phase 3: shared capability gaps and stability
- Phase 4: validation and release

Recommended groups:
- functional parity baseline
- algorithm inventory
- mesh or engine gap analysis
- theme and UI architecture
- handoff contract
- product surface
- workspace state
- export and metadata contract
- stability refactor
- integration and migration
- validation and release

## Implementation Density Rules
The generated package must be safe **and** implementation-oriented.

- Generate or update `domain-ingest-summary.md` first when prior reports/plans exist.
- Do not rely on scaffold generation alone. The ingest summary must be used to inject domain-specific capabilities, algorithms, gaps, target components, and evidence anchors.
- Group docs must list only `relevant_specs`; the full spec list belongs in README.
- Group front matter must include `depends_on`, `soft_depends_on`, and `blocking_interfaces` when known.
- Group docs must include `Implementation Digest` with target files/components, responsibilities, before/after, critical gap, and first implementation step.
- Acceptance Criteria should use structured rows:
  - `Contract:`
  - `Evidence:`
  - `Test command:`
  - `Blocking:`
- README must separate `Human Quickstart` from `Canonical Read Order`.
- README should include a dependency graph generated from group dependency metadata.
- Application product, modularization, migration, and architecture packages should include a target module structure diagram.
- Use `--quality-lint` to detect safe-but-noisy packages that pass validation but are hard to implement from.

## Canonical Spec Requirements

The exact spec set comes from the archetype and modifiers. Common specialized contracts have dedicated templates. Other contracts use `generic-contract-template.md` with front matter declaring the concern they own.

### Capability Map
Must contain:
- capability list
- capability id
- owner
- current state
- target state
- priority (`P0/P1/P2`)
- canonical contract link
- evidence or source asset
- status enum
- explicit descoping rule

### Algorithm Inventory
Must contain:
- algorithm name
- dependent capability ids
- code path or module
- owner
- owned capability
- current code asset
- input/output contract
- validation dataset link
- measured tolerance
- known failure conditions
- recommendation / fallback
- manual-style columns where useful: legacy meaning, current asset, status enum, primary use, fallback, validation

### Mesh Ops Contract
Use when mesh cut, patch, replacement, topology validity, or cross-section operations are core to the task.
Must contain:
- mesh operation matrix
- geometry risk matrix
- PoC plan
- output validity rules

### Gap Registry
Use when missing capabilities must be tracked explicitly across sessions.
Must contain:
- gap id
- severity
- owner
- required-before milestone
- linked capability
- closure or waiver rule

### UI State Contract
Must contain:
- state id naming rule
- canonical state ids
- state names
- transitions
- error states
- entry condition
- exit condition
- side effects
- CTA visibility/enabled rules
- strict validation requires real state id, error state, CTA rows, and a non-empty transition graph

### Integration Contract
Must contain:
- reused subsystems
- extracted capabilities
- ownership boundaries
- interface contracts with ids and versions
- upstream/downstream contracts

### Theme Token Contract
Must contain:
- token groups
- semantic components
- no-literal-style rule
- migration rule for visual redesigns
- strict validation requires at least one semantic component row and literal-style prohibition rules

### Release Gate
Must contain:
- gate inputs
- upstream gates
- gate input rows generated from `required_specs`
- upstream specialized gates such as performance budget, visual regression, evaluation, observability, and tolerance contracts
- release-blocking archetype/modifier contracts such as behavior parity, rollback, hardware interface, pin map, protocol, and tolerance contracts
- datasets
- dataset version/source/split/frozen flag
- numeric thresholds
- unit
- measurement method
- baseline
- fail severity
- parity tolerances
- regression matrix
- waivers
- evidence artifacts
- pass/fail rules
- rollback triggers

### Agent Handoff Index
Must contain:
- current canonical plan path
- active blockers
- read order
- required docs before implementation
- update rules
- prohibited shortcuts

### Generic Contract Docs
Must contain:
- purpose
- contract scope
- contract matrix
- validation rules
- open decisions
- evidence

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
Each phase/group doc should include:
- purpose
- current state
- target state
- derived document notice
- referenced canonical docs
- referenced canonical ids
- dependencies
- implementation digest
- proposed changes to canonical contracts
- structured acceptance criteria with contract/evidence/test command/blocking fields
- prohibited shortcuts
- TODO

It may include algorithms or UI discussion, but it must reference canonical contracts instead of redefining them.
It must never claim that it is the source of truth for any canonical contract.

## Validation Rules
After writing the package:

1. Validate that all required docs exist.
2. Validate that README links to all phase/group docs.
3. Validate that canonical state definitions exist only in the UI state contract.
4. Validate that release thresholds are numeric.
5. Validate that README status does not contradict the canonical dated plan.
6. Validate that the canonical dated plan exists and has the required sections.
7. Validate that the handoff index contains `Prohibited Shortcuts`.
8. Validate that every P0 capability has a contract link or an explicit downgrade decision.
9. Validate that unresolved blocking interfaces do not coexist with open implementation state.
10. Validate that incomplete hard predecessors do not coexist with progressed dependent phases.
11. Validate that the selected archetype and modifiers match the package metadata.
12. Validate that modifier-required docs exist.
13. Validate required front matter on every generated planning document.
14. Validate hard predecessor order using `phase_order`, not phase-name parsing.
15. For implementation handoff or handoff readiness, run validator with `--strict` and resolve placeholder/empty release-critical contract rows.
16. Strict validation must check every real release-critical row, not just one representative row.
17. For handoff readiness, run validator with `--strict-handoff`; Active Blockers must not remain `Unverified`.
18. Validate README and canonical dated plan use the same generated validation commands.
19. In quality lint mode, validate implementation readability: compact group specs, dependency graph, structured acceptance criteria, and non-vague canonical ids.

Use bundled scripts when available.

Validation modes:
- default mode: confirms scaffolding, source-of-truth separation, required docs, required headings, and anti-drift structure
- `--strict` mode: additionally checks that every real release-critical contract row has numeric thresholds/budgets/tolerances, evidence artifacts, and no unresolved template placeholders in critical slots
- `--strict-handoff` mode: additionally checks that the handoff index no longer contains unverified active blockers, an active group is present, and group AC is concrete enough for handoff
- `--quality-lint` mode: emits readability and implementation-density warnings for packages that validate structurally but are noisy or vague

## Bundled Resources
- Read [source-of-truth-policy.md](references/source-of-truth-policy.md) before editing package docs.
- Read [archetype-catalog.md](references/archetype-catalog.md) before selecting an archetype or modifiers.
- Read [decomposition-rules.md](references/decomposition-rules.md) when choosing phases/groups.
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
