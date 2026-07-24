---
name: workflow-task-ledger
description: Keep accepted findings and step evidence resume-safe when work is explicitly expected to cross a turn, session, or handoff boundary. Use between one-shot execution and a LoopRun; do not create a ledger merely because an ordinary task has several steps.
disable-model-invocation: true
---

# Workflow Task Ledger

## Routing Card
- role: execution_modifier
- intent_signature: resume-safe task state, checkpointed task, findings gate, 멀티턴 작업 추적
- use_when: durable resumption or a real handoff/session boundary would otherwise lose accepted findings or dependent step state
- do_not_use_when: ordinary work can finish now; use LoopRun ownership when verifier feedback repeatedly selects the next action
- expected_inputs: objective, resumable steps, current ledger, and observed step/finding evidence
- expected_outputs: durable state, condition-scoped completion decision, and one next action or blocker
- context_targets: read the objective and current ledger; load only active-step evidence and the task-run schema, not unrelated repo, memory, plans, or LoopRun state
- risk_profile: write runtime `task-run.yaml` only through the active host's compatible `task_ledger.py` tool; never copy credentials or secrets into evidence
- entry_scene: PREPARE

## Ledger Contract
Activate only when durable resumption has concrete value; step count, difficulty, or the word “plan” is insufficient. Add the ledger at the first real boundary rather than speculatively. A TaskRun records state but does not execute work or provide Stop continuation, retry, budget, or verifier-driven convergence.
On activation, preserve supplied accepted findings together with their dependent steps; do not reduce a handoff to a step list.

See `.claude/schemas/task/task-run.schema.json` and `.claude/schemas/task/work-contract.schema.json`. TaskRun v2 stores an immutable `work_contract_ref` plus hash; form it from explicit natural-language scope rather than requiring the user to know ledger flags or YAML.

- Classify every step as `core`, `required_prerequisite`, `agent_validation`, `test_authoring`, `validation_artifact`, `optional_quality`, or `meta`, with requiredness, dependencies, stable semantic `intent_key`, and interaction need.
- Steps: `pending -> in_progress -> complete | failed | blocked | deferred`; `complete` needs observed `evidence_refs`, and `deferred` needs a reason.
- An explicitly excluded auxiliary step remains non-required even if a workflow tries to promote it. An interaction-required step is automatically deferred only for `unattended_goal_loop` plus forbidden interaction; attended and interaction-enabled work keeps it pending for the host's normal flow.
- After local deferral, select another independent required runnable step. A TaskRun becomes globally `blocked` only when required incomplete steps remain and none is runnable. A different command, wrapper, or validation class with the same deferred purpose reuses the same intent and remains deferred.
- Findings: `open -> resolved | rejected | accepted_risk`.
- `resolved` needs both a resolution and new verification evidence; discovery evidence alone cannot close it.
- `accepted_risk` needs accepter, reason, and review time.
- Record what each evidence ref directly proves. A narrower command, structural check, or agent-authored check cannot close an uncovered semantic or user-only condition.
- If ledger state conflicts with current files/runtime, re-observe the source of truth and correct the ledger before claiming progress.

## Completion Gate
Close only when every required step has direct evidence and no finding is open or blocked. For agent-owned verification, `final_verification.status == pass` must cover the material conditions. For user-owned verification, `user-verification-needed` is a normal completed implementation handoff; `unverified` is valid only when the accepted contract names that handoff. A finding's fail/needs-review/unverified state survives narrower passes until resolution/readback evidence addresses that same condition. Closing a TaskRun does not close a parent WorkItem.

Use the active host's compatible `task_ledger.py <dir>` tool for ledger operations and reuse actual runtime evidence; never replace receipts with free-text “looks done” claims. If the host exposes no compatible ledger tool, stop `blocked` rather than editing `task-run.yaml` directly.

Return current status, changed step/finding IDs, decisive evidence refs and their scope, completion blockers, and exactly one next action. Do not restate the ledger unless a handoff artifact is requested. Runtime ledger state is not a distributable bundle artifact.
