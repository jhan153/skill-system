# Package Authoring Rules

Read this when creating, refilling, or validating a long-term planning package.

## Required Outputs
- Canonical dated plan under `docs/plan/YYYY-MM-DD-<task>.md`
- Package root at `docs/plan/<PlanPackage>/README.md`
- Phase/group docs under the package root
- Required `docs/spec/` contracts from the chosen archetype plus modifiers
- `docs/plan/<PlanPackage>/domain-ingest-summary.md` when existing analysis, report, or prior plan docs are available

## Existing Analysis Ingest
Before generating or refilling a package, ingest only relevant existing analysis reports and prior planning docs.

```bash
python3 scripts/ingest_analysis_reports.py --root <repo-root> --auto --out docs/plan/<PlanPackage>/domain-ingest-summary.md
python3 scripts/ingest_analysis_reports.py --root <repo-root> --report docs/codebase-intel --report docs/plan/<OldPlan> --out docs/plan/<PlanPackage>/domain-ingest-summary.md
python3 scripts/init_phase_plan_package.py ... --auto-ingest
python3 scripts/init_phase_plan_package.py ... --ingest-report docs/codebase-intel --ingest-report docs/plan/<OldPlan>
```

Rules:
- Treat the ingest summary as derived evidence, not canonical truth.
- Use cited source lines from `domain-ingest-summary.md` to fill canonical specs and group Purpose/Current State/Target State/Acceptance Criteria.
- If existing reports are available but generated package sections remain empty or generic, report the package as scaffold-only.
- Run `--quality-lint` when handoff readability matters.

## Archetype And Modifier Selection
Read `archetype-catalog.md` before choosing when the task type is not obvious.

```yaml
package_selection:
  archetype: "primary work type"
  modifiers:
    - "additional validation condition"
```

- `archetype` determines the primary required contract docs.
- `modifier` adds stronger validation docs without changing the primary archetype.
- Required docs are the union of archetype docs, modifier docs, `release-gate`, and `agent-handoff-index`.
- The validator must check the same selected archetype and modifiers recorded in package metadata.

## Source Of Truth
Read `source-of-truth-policy.md` before editing package docs.

- Canonical contracts live in `docs/spec/`.
- Current execution status lives in the canonical dated plan.
- Package README is navigation and rollup only.
- Phase/group docs decompose work and may propose contract changes, but they must not redefine canonical truth.

## Decomposition And Density
Read `decomposition-rules.md` before choosing phases or groups.

- Decompose by concern, not arbitrary document count.
- Default to four phases only when no better concern split exists.
- Group docs should list only relevant specs; the full spec list belongs in README.
- Group docs must include concrete implementation digest, target files/components, before/after, critical gap, first step, dependencies, and structured acceptance criteria.
- Acceptance criteria should include `Contract`, `Evidence`, `Test command`, and `Blocking`.
- README should separate `Human Quickstart` from `Canonical Read Order`.

## Validation Modes
Use bundled scripts when available.

```bash
python3 scripts/validate_phase_plan_package.py <args>
python3 scripts/validate_phase_plan_package.py --strict <args>
python3 scripts/validate_phase_plan_package.py --strict-handoff <args>
python3 scripts/validate_phase_plan_package.py --quality-lint <args>
```

- Default mode checks structure, source-of-truth separation, required docs, required headings, and anti-drift shape.
- `--strict` checks release-critical semantic content: numeric thresholds, budgets, tolerances, benchmark rows, evidence artifacts, and non-placeholder contract rows.
- `--strict-handoff` checks active blockers, active group, and concrete handoff acceptance criteria.
- `--quality-lint` checks readability, compact group specs, dependency metadata, structured acceptance criteria, vague canonical IDs, and compact quickstart.

## Reporting
When finishing a package update:
- state the canonical plan path first
- list the package root
- list the spec docs created or updated
- report validation outcome
- mark remaining ambiguity as `Unverified`
