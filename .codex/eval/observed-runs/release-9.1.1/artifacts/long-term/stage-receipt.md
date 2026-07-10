# Staged materialization receipt

- Primary owner: `skill-system-core:plan-long-term-package`
- Selection: `migration-modernization`
- Modifiers: `strict-behavior-parity,rollback-required,data-sensitive,security-sensitive,cross-session-handoff,legacy-parity`
- Final phase topology: `R1 Shadow Authorization`, `R2 Test-Tenant Canary`, `R3 Legacy Retirement`, `Cross-Release Validation and Handoff`
- Effective artifact cap: `20`
- Projected/final artifact count: `19`

The first preflight supplied three custom phase names for an archetype with four concern phases. It exited `1` before `docs/` existed. The corrected topology then used the exact same arguments for both successful stages:

1. `init_phase_plan_package.py ... --canonical-only` — exit `0`; `ARTIFACT_BUDGET_OK projected=19 cap=20`; `MODIFIER_ABSORBED_BY_ARCHETYPE legacy-parity`.
2. `init_phase_plan_package.py ... --derived-only` — exit `0`; exact canonical identity/topology/manifest binding accepted.
3. `validate_phase_plan_package.py ...` — exit `0`; `VALIDATION_OK`.

No `--auto-ingest` or `--ingest-report` argument was used. No `domain-ingest-summary.md` exists.
