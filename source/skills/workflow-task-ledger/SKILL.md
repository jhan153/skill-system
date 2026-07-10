---
name: workflow-task-ledger
description: Keep accepted findings and step evidence resume-safe when work is explicitly expected to cross a turn, session, or handoff boundary. Use between one-shot execution and a LoopRun; do not create a ledger merely because an ordinary task has several steps.
---

# Workflow Task Ledger

## Routing Card
- role: execution_modifier
- intent_signature:
  - resume-safe task state, checkpointed task, findings gate, 멀티턴 작업 추적
- use_when:
  - the user requests durable resumption, a handoff/session boundary is expected, or interruption would lose accepted findings.
- do_not_use_when:
  - work can reasonably finish now, including ordinary multi-step change→validation work.
  - repeated verifier feedback must choose the next action (`plan-loop-term` + `workflow-loop-runner`).
- expected_inputs:
  - objective, resumable steps, current ledger when any, and observed evidence/findings
- expected_outputs:
  - durable step/finding state, completion-gate decision, and one next action/blocker
- context_targets:
  must_read:
    - objective and current ledger state
  read_if_needed:
    - only evidence tied to the active step/finding and the task-run schema
  do_not_load_by_default:
    - full repo, memory bank, unrelated plans, or LoopRun state
- risk_profile:
  reads:
    - task ledger and referenced evidence
  writes:
    - runtime `task-run.yaml` state only
  tools:
    - `.codex/tools/task_ledger.py` operations and the owning task's evidence producers
  sensitive_resources:
    - credentials default deny; never copy secrets into evidence text
- entry_scene:
  - PREPARE

## Activation Gate
Use a TaskRun only when durable resumption has concrete value. Step count, task difficulty, or the word “plan” is not enough. Add the ledger at the first real resumption boundary rather than speculatively at task start.

A TaskRun is not a LoopRun: it has no Stop continuation, convergence budget, retry policy, or verifier-driven next-action loop. Escalate when repeated verifier feedback controls execution.

## State And Evidence
See `.codex/schemas/task/task-run.schema.json`.

- Steps: `pending -> in_progress -> complete | failed | blocked`; `complete` needs observed `evidence_refs`.
- Findings: `open -> resolved | rejected | accepted_risk`.
- `resolved` needs both a resolution and new verification evidence; discovery evidence alone cannot close it.
- `accepted_risk` needs accepter, reason, and review time.
- Evidence records use structured command/verifier/file/artifact/readback/user-approval fields and `kind: discovery | resolution | verification`.
- If ledger state conflicts with current files/runtime, re-observe the source of truth before claiming progress.

## Completion Gate
Close only when all required steps are complete, `final_verification.status == pass`, and no finding is open/blocked. Closing a TaskRun does not close a parent WorkItem; link it with `work_item_ref` when one exists.

## CLI
Use `.codex/tools/task_ledger.py <dir>` with `init`, `add-step`, `checkpoint`, `finding-add`, `finding-resolve`, `finding-accept-risk`, `final-verify`, `status`, and `close`. Reuse actual runtime evidence; do not write free-text “looks done” receipts.

## Output
Return current status, changed step/finding IDs, decisive evidence refs, completion blockers, and exactly one next action. Do not restate the whole ledger unless the user requests a handoff artifact.

## Behavior Cases
- Positive: “이 작업은 다음 세션까지 이어지니 findings와 검증 상태를 ledger로 남겨줘.”
- Negative: “파일 두 개 고치고 테스트해줘.” → ordinary execution, no ledger.
- Edge: a long task is likely to finish now and has no accepted findings → start without a ledger; add one only if a real resumption boundary appears.

## Known Limits
- The ledger records evidence; it does not execute or independently verify checks.
- Runtime ledger state is not a distributable bundle artifact.
