# search-deep-evidence Loop Contract Template

This binds `search-deep-evidence` (the method) to the bundle's loop-engineering
runtime so a deep evidence sweep can be checkpointed as a bounded, verifier-gated loop. It is
NOT a new workflow/skill: the executor is the existing `workflow-loop-runner` +
`init/evaluate/validate_loop_run.py`. This template only supplies the per-iteration
act and verifier intent.

Local LoopRun v2 auto-passes only exact `artifact_exists` evidence. Its `command_exit` receipts are not host-authenticated, so the semantic ledger check below remains `unverified` and cannot produce loop success. Use this contract for bounded evidence/checkpoint state only; choose `checkpointed_task` instead when automated terminal success is required without a host attestation producer. Never weaken SC-002 to ledger-file existence.

- act (each iteration): extend the claim–evidence matrix, acquire the most
  discriminating missing evidence, search for contradictions, and resolve each
  claim as `supported`, `contradicted`, `mixed`, or `insufficient`.
- verifier: `python3 .codex/tools/check_evidence_ledger.py <ledger.yaml>` — PASS
  checks schema-v2 traceability and resolution quality. It does not require a
  positive conclusion and does not allow exclusion to erase evidence.
- handoff on success: the resolved ledger goes to `report-*` / `research-literature-synthesis`.

```yaml
schema_version: 2
contract_id: LC-YYYYMMDD-NNN
activation: explicit
goal:
  statement: "Produce a traceable, resolved claim-evidence set for <topic> via a scoped multi-lane sweep."
  success_conditions:
    - id: SC-001
      statement: "Evidence ledger exists for the topic."
      required: true
      verifier:
        type: artifact_exists
        owner: search-deep-evidence
        path: "papers/evidence_ledger.yaml"
    - id: SC-002
      statement: "Every claim has a traceable supported, contradicted, mixed, or explicitly insufficient resolution."
      required: true
      verifier:
        type: command_exit
        owner: check-evidence-ledger
        command: "python3 .codex/tools/check_evidence_ledger.py papers/evidence_ledger.yaml --min-claims 1"
        expected_exit_code: 0
control:
  max_iterations: 6
  no_progress_limit: 3
  same_failure_limit: 3
  oscillation_limit: 2
  max_stop_continuations: 6
termination:
  precedence: [unsafe, fatal, blocked, success, approval_required, stalled, budget_exhausted, recover, continue]
```

## How a run progresses
- Early iterations: claims lack traceable evidence or an explicit missing-evidence resolution → `check_evidence_ledger` FAILs → loop `continue` with the smallest discriminating acquisition.
- Repeated identical failure → loop `recover` by handing the stuck slice to `workflow-recovery`.
- All claims structurally resolved with source/limitation records → record the command output as audit evidence, but keep SC-002 open in local v2. Hand off only as `user-verification-needed`/`unverified`; do not report LoopRun success without host-authenticated command attestation.
