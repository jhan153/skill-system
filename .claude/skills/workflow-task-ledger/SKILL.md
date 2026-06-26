---
name: workflow-task-ledger
description: Resume-safe checkpoint ledger for multi-turn tasks between one-shot work and a full LoopRun. Track steps and accepted findings with observed evidence, and gate completion on open findings. Use when work spans turns/sessions and findings must not be lost, but repeated verifier-feedback convergence (LoopRun) is not needed.
---

# Workflow Task Ledger

## Routing Card
- role: execution_modifier
- intent_signature:
  - checkpointed task
  - resume-safe task state
  - 멀티턴 작업 추적
  - findings gate
  - task ledger
- use_when:
  - work has 2+ dependent steps that may be resumed across turns or sessions.
  - accepted findings must not be lost before completion.
  - the task is heavier than one-shot but does not need repeated verifier-feedback convergence (a LoopRun).
- do_not_use_when:
  - one-shot work, simple edits, or pure explanation.
  - repeated verifier feedback should change the next action; use `plan-loop-term` + `workflow-loop-runner`.
  - the user wants a broad multi-document planning package; use `plan-long-term-package`.
- expected_inputs:
  - objective and the dependent steps
  - observed evidence per step (command exit, verifier result, file/artifact, readback)
  - accepted findings with severity and evidence
- expected_outputs:
  - resume-safe step/finding ledger with observed `evidence_refs`
  - completion decision gated on open findings and final verification
  - one next action or the exact blocker
- context_targets:
  must_read:
    - current objective and step list
    - current ledger state when resuming
  read_if_needed:
    - changed files or validation output tied to a step
    - the task-run schema for field shape
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated plans or LoopRun state
- risk_profile:
  reads:
    - the task-run ledger and step-tied evidence
  writes:
    - WRITE_LOCAL_FS only for the task-run ledger (runtime state, not the bundle)
  tools:
    - CALL_PROCESS for `task_ledger.py` ledger operations only
  sensitive_resources:
    - credentials default deny; the ledger redacts nothing, so keep secrets out of evidence text
- entry_scene:
  - PREPARE

## Related Skills
- `loop-readiness-router`: classifies a request as `checkpointed_task` and hands off here.
- `workflow-rigor`: owns execution rigor and the completion gate vocabulary (observed evidence, `accepted_risk`).
- `workflow-loop-runner` / `plan-loop-term`: own iterative verifier-feedback loops. This skill is NOT a loop.

## Purpose
- Keep multi-turn work resumable by fixing step and finding state in an external ledger, not in model memory.
- Refuse completion while accepted findings are open or blocked.
- Use observed evidence references, never free-text claims.

## TaskRun is not a LoopRun
- No repeated verifier-feedback convergence, no Stop-hook continuation, no budgets/idempotency/retry governance.
- If the next action depends on repeated verifier feedback, escalate to `plan-loop-term` + `workflow-loop-runner` instead.

## State (see `.codex/schemas/task/task-run.schema.json`)
- `task-run.yaml`: objective, workspace (root + revision), status, steps, findings, final_verification.
- Steps: `pending -> in_progress -> complete | failed | blocked`. A `complete` step requires non-empty observed `evidence_refs`.
- Findings: `open -> resolved | rejected | accepted_risk`. `resolved` needs resolution + evidence; `accepted_risk` needs `accepted_by`, `reason`, `review_at`.
- Resume priority: when the ledger conflicts with current files, prefer current files and re-confirm before claiming progress.

## Evidence model (observed, not strings)
- Each `evidence_ref` is a structured observation: `{type: command, command, exit_code}` / `{type: verifier, verifier_id, result}` / `{type: file, locator}` / `{type: artifact, locator}` / `{type: readback, locator}` / `{type: user_approval, note}`.
- Reuse existing runtime evidence; do not invent free-text "looks done" evidence.

## Completion contract (findings gate)
TaskRun closes only when all three hold:
1. every required step is `complete`,
2. `final_verification.status == pass`,
3. zero `open`/`blocked` findings (residual risk closed only as `accepted_risk`).

## Finding evidence types
Keep finding evidence distinct so admission and closure are not conflated:
- **admission / discovery**: the observed evidence that the finding is real (what was seen) — required to add a finding.
- **resolution**: what changed to address it (the diff or action taken).
- **verification**: the observed re-check that the fix holds (command exit, re-run, readback) — distinct from the discovery evidence.
A finding becomes `resolved` only with both a resolution and verification evidence (not just the original discovery); `accepted_risk` instead records why it is not resolved. The CLI enforces this: `finding-resolve` requires a non-empty `--resolution` plus new `--evidence` (the verification, distinct from the admission/discovery evidence). Mark each `evidence_ref` with `kind` (`discovery` | `resolution` | `verification`) so discovery is not mistaken for verification.

## CLI (`.codex/tools/task_ledger.py <dir> ...`)
- `init` — create a task-run; `add-step` — append a step.
- `checkpoint --step --status [--evidence ...]` — transition a step (complete requires evidence).
- `finding-add` / `finding-resolve` / `finding-accept-risk` — manage findings.
- `final-verify --status pass [--evidence ...]` — record final verification.
- `close` — evaluate the completion gate (exit 0 = closed, non-zero = blocked with reasons); `status` — summary.

## Anti-Patterns
- Creating a ledger for one-shot or trivial work.
- Free-text evidence instead of observed references.
- Using the ledger as a LoopRun (verifier-feedback convergence).
- Marking a step `complete` or closing the run while findings are open.

## Known Limits
- The ledger records decisions; it does not run verifications. Evidence must come from real tool output.
- Runtime ledger state lives outside the distributable bundle.
- Promotion past `experimental` waits on deployed field cases proving the one-shot↔LoopRun gap.
