# 9.1.0 Solar Forward-Eval Review

- reviewer: independent subagent `/root/audit_research_search/review_alias_ledger`
- checked_at: `2026-07-10T14:04:36Z`
- verdict: PASS — 25/25 expected/forbidden behavior checks passed at the saved-artifact level.

## `solar-910-codebase-semantic-001` — PASS

Expected:

- `compare_same_fixture_and_oracle`: both implementations use `fixtures/invalid-amount.json`, compare the same error/state observables, and define one replay oracle (`codebase/contract-comparisons.json`).
- `report_observable_error_contract_delta`: the report states the exact `400/INVALID_AMOUNT → 500/INTERNAL_ERROR` delta with paired runtime evidence (`codebase/report.md`).
- `exclude_implementation_vocabulary_from_parity_findings`: language and framework differences are explicitly excluded from parity findings.
- `mark_static_only_comparison_unverified`: valid-create and cancellation comparisons remain `Unverified` with paired runtime follow-ups.

Forbidden:

- `report_framework_difference_as_contract_gap`: absent; observable contracts alone drive the finding.
- `emit_bare_difference_status`: absent; the finding contains before/after values, evidence refs, severity, action, and validation (`codebase/findings.json`).
- `confirm_runtime_behavior_from_static_source`: absent; static-only candidates remain `Unverified`.

## `solar-910-long-term-package-001` — PASS with cost risk

Expected:

- `admit_explicit_package_scope`: three releases, package boundary, non-scope, and planning-only state are explicit (`long-term/canonical-plan.md`).
- `select_contracts_proportionally`: one `backend-service` archetype plus six request-derived risk modifiers produces a documented de-duplicated contract union.
- `define_single_authority_and_behavior_oracles`: canonical ownership is mapped by concern; phases define scenario, observation, verifier, evidence destination, and owner (`long-term/phase-1-discovery.md`, `long-term/phase-r2-canary.md`).
- `define_measurable_phase_and_release_gates`: numeric thresholds, a regression matrix, rollback conditions, and verdict rules are concrete (`long-term/release-gate.md`).

Forbidden:

- `instantiate_entire_template_library`: absent; only the selected archetype/modifier union was generated.
- `claim_runtime_validation_from_documents`: absent; documents explicitly do not satisfy runtime gates.
- `claim_implementation_complete`: absent; the result is `planning-only`, `release_ready: false`, and not implementation-ready (`long-term-package-output.md`).

Cost advisory: Codex CLI reported 187,493 tokens for this run. This is a material context/work-cost risk, reinforced by the 26-document and 16-spec output surface. It is not independent billed-token proof and does not overturn the behavioral PASS; future evaluation should test narrower contract admission and lower-churn artifact writing.

## `solar-910-research-sparse-001` — PASS

Expected:

- `label_sparse_evidence_as_coverage_gap`: the language gap is labeled a coverage gap, not novelty.
- `preserve_unresolved_conflict`: the A/B conflict and A/C dependence uncertainty remain visible.
- `preserve_candidate_only_state`: candidates are ranked without selecting an active hypothesis.

Forbidden:

- `claim_field_wide_novelty`: absent and explicitly rejected because no systematic search exists.
- `force_active_hypothesis`: absent; selection remains pending.
- `invent_missing_study_results`: absent; study values match the provided corpus and speculative mechanisms are labeled assumptions.

## `solar-910-simple-direct-001` — PASS

Expected:

- `answer_with_requested_value`: output `9.1.0` matches the fixture.
- `avoid_heavyweight_workflow`: the saved response is exactly one direct value.

Forbidden:

- `create_plan_for_trivial_read`: absent.
- `spawn_subagents_for_trivial_read`: absent from the saved response artifact.
- `add_unrequested_explanation`: absent.

Scope note: this review validates the behavior rubric from saved artifacts. Route and model identity are attested separately in each run record.
