# search-deep-evidence Loop Contract Template

This binds `search-deep-evidence` (the method) to the bundle's loop-engineering
runtime so a deep evidence sweep can run as a bounded, verifier-gated loop. It is
NOT a new workflow/skill: the executor is the existing `workflow-loop-runner` +
`init/evaluate/validate_loop_run.py`. This template only supplies the per-iteration
act and a deterministic success verifier.

- act (each iteration): run the `search-deep-evidence` method — decompose angles,
  route lanes via `search-router`, extend the evidence ledger, run adversarial
  verification, update `citation_status`.
- verifier: `python3 .codex/tools/check_evidence_ledger.py <ledger.yaml>` — PASS only
  when every retained claim is `verified` + `confirmed` + sourced.
- handoff on success: the verified ledger goes to `report-*` / `research-literature-synthesis`.

```yaml
schema_version: 1
contract_id: LC-YYYYMMDD-NNN
activation: explicit
goal:
  statement: "Produce a verified, citation-labeled evidence set for <topic> via a deep multi-angle sweep."
  success_conditions:
    - id: SC-001
      statement: "Evidence ledger exists for the topic."
      required: true
      verifier:
        type: artifact_exists
        path: "papers/evidence_ledger.yaml"
    - id: SC-002
      statement: "Every retained claim is verified, confirmed, and sourced (no fabricated-risk/unverified)."
      required: true
      verifier:
        type: command_exit
        command: "python3 .codex/tools/check_evidence_ledger.py papers/evidence_ledger.yaml --min-claims 3"
        expected_exit_code: 0
control:
  max_iterations: 6
  no_progress_limit: 3
  same_failure_limit: 3
  oscillation_limit: 2
  max_stop_continuations: 6
termination:
  precedence: [unsafe, fatal, success, approval_required, stalled, budget_exhausted, continue]
```

## How a run progresses
- Early iterations: ledger has `unverified` / `fabricated-risk` / `partial` claims → `check_evidence_ledger` FAILs → loop `continue` with the smallest action that adds/verifies evidence.
- Repeated identical failure → loop `recover` (hand to `workflow-recovery`).
- All retained claims resolved to `verified` + `confirmed` + sourced → verifier PASS → loop `success` → hand the ledger to the owning report/synthesis skill.
