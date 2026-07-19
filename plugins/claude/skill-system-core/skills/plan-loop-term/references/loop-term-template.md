# Loop Contract Template

Read this only for runner-ready YAML or an explicitly persisted contract. The runtime artifact is authoritative; the companion contains only governance that does not fit its schema.

## Authoring Rules

- Use `contract_id: LC-YYYYMMDD-NNN` and condition ids `SC-NNN`. `loop_run_id` is assigned by `init_loop_run.py`.
- Give every required condition one runtime verifier and concrete pass/fail/evidence target.
- Runtime verifier types are only `command_exit`, `artifact_exists`, `manual_check`, or `diff_scope`.
- Keep visual/a11y/state/review quality verifiers in the companion and bind their durable output to a runtime verifier.
- Missing or user-only evidence blocks success. Free-form refs and maker self-report never prove pass.
- Record checkpoint, budget, retry, approval/idempotency, and all stop terms before execution.

## v2 Attestation Ceiling

The local v2 runner can auto-pass only `artifact_exists`, and that proves exact path presence/digest only. `command_exit`, `manual_check`, and `diff_scope` receipts are schema-valid audit candidates but their claimed outcomes are not host-authenticated; the evaluator rejects their `pass` status fail-closed. Keep those conditions `unverified`/`user-verification-needed` until a future host-authenticated producer exists. Never substitute `artifact_exists` for their semantic verdict.

## Runtime Contract

This is the direct `init_loop_run.py <contract.yaml>` input and must validate against `.codex/schemas/loop/loop-contract.schema.json`.

```yaml
schema_version: 2
contract_id: LC-20260101-001
activation: explicit
goal:
  statement: "Replace with the observable outcome."
  success_conditions:
    - id: SC-001
      statement: "Primary required artifact exists."
      required: true
      verifier:
        type: artifact_exists
        owner: "agent:codex"
        path: "replace/with/required-artifact"
    - id: SC-002
      statement: "Optional command evidence is collected; local v2 cannot authenticate it as pass."
      required: false
      verifier:
        type: command_exit
        owner: "ci:replace-with-real-owner"
        command: "replace-with-real-command"
        expected_exit_code: 0
control:
  max_iterations: 3
  no_progress_limit: 2
  same_failure_limit: 2
  oscillation_limit: 2
  max_stop_continuations: 3
  max_wall_time_seconds: 3600
termination:
  precedence: [unsafe, fatal, success, approval_required, stalled, budget_exhausted, continue]
```

The schema also accepts free-form top-level `scope:` and `recovery:` objects and `goal.invariants[]`. Do not put companion-only verifier types or planning prose into runtime fields.

## Minimal Governance Companion

Keep this artifact narrow and identity-aligned. Remove unused sections.

```yaml
loop_contract_companion:
  contract_id: LC-20260101-001
  loop_run_id: null
  objective: ""
  non_goals: []
  scope: {includes: [], excludes: []}

  verifier_map:
    - success_condition_id: SC-001
      runtime_verifier:
        owner: agent:codex
        type: artifact_exists
        evidence_target: "replace/with/required-artifact"
        pass_signal: "exact path exists and digest matches"
        fail_signal: "path missing or digest mismatch"
      quality_verifiers: []
      independence: checker
      evidence_receipt: canonical_iteration_result_schema
      unavailable:
        status: unverified|user-verification-needed|blocked
        fallback: ""
        blocks_success: true
      reward_hacking_watch: []

  progress:
    accepted_signals: []
    rejected_signals: []
    no_progress_after: 2
    strategy_change_after: 2

  checkpoint:
    cadence: after_each_iteration_or_verifier_result
    required_state:
      - contract_id
      - loop_run_id
      - condition_status
      - accepted_receipts
      - pending_decisions
      - side_effect_journal

  retry:
    max_attempts: 3
    retryable: [transient, model_recoverable, environment_recoverable]
    stop_classes: [user_input_required, permission_required, fatal]

  budget:
    max_iterations: 3
    max_wall_time_seconds: 3600
    token_or_cost_limit: null

  side_effects:
    approval_gates: []
    idempotency_keys: []
    rollback_or_dry_run: []

  stop:
    success: "Every required SC-NNN has a fresh structured passing receipt."
    blocked: "Required input, permission, verifier, or environment is unavailable."
    budget: "Accepted budget is exhausted."
    unsafe: "Next action crosses an unapproved or non-idempotent boundary."
    fatal: "Contract, state, or verifier integrity is untrustworthy."

  governance:
    quality_verifiers: []
    untrusted_sources: []
    anti_reward_hacking: []
    parallel_ownership: []
    runtime_capabilities: []
    persistent_context_mutation: explicit_only

  handoff:
    execution_owner: workflow-loop-runner
    verifier_map_ref: ""
    required_user_checks: []
    contract_path: ""
```

For a semantic quality condition, keep the quality report and manual evidence candidate separate, but leave the required condition open in the local v2 runner:

```yaml
- success_condition_id: SC-002
  runtime_verifier:
    owner: "<accepting-user>"
    type: manual_check
    evidence_target: "accepted user event scoped to SC-002:visual-quality"
    acceptance_scope: "SC-002:visual-quality"
  quality_verifiers:
    - owner: design-visual-regression
      type: visual
      evidence_target: artifacts/visual-review.json
```

Even when a real validator parses that report, local v2 cannot authenticate a claimed `command_exit` receipt. Record the exact command as audit evidence, keep the condition open, and never use `artifact_exists` to claim the report's semantic verdict.

For user-only acceptance, use runtime `manual_check`. A `manual_acceptance` event may record a loop-scoped durable artifact (`artifact_ref`, `artifact_scope: loop_run`, `artifact_sha256`), owner/scope, timezone-aware `observed_at`, and the user-input payload, but current local v2 treats it as procedural audit evidence rather than pass authority. The condition remains `user-verification-needed` without host-authenticated provenance.

## Compact Handoff

```text
Contract: LC-YYYYMMDD-NNN
Outcome / non-goals:
Required SC-NNN + runtime verifier + evidence:
Optional quality verifier:
Progress / stall:
Retry / budget / stop:
Checkpoint / approval gates:
Execution owner and contract path:
```
