---
name: report-artifact-inventory
description: Helps summarize important task artifacts and verification notes without maintaining a persistent 7.0 artifact registry.
---

# Report Artifact Inventory

## Routing Card
- role: support
- intent_signature:
  - artifact summary
  - verification note
  - stale artifact note
  - follow-up artifact
  - output inventory
- use_when:
  - the user asks to summarize produced files, verification evidence, or stale follow-up candidates.
  - a handoff needs a small artifact inventory.
- do_not_use_when:
  - the task only needs source edits and a brief final answer.
  - a persistent registry, event log, deployment tracker, or evidence-finality queue would be required.
- expected_inputs:
  - changed file paths
  - checks run
  - relevant user-facing artifacts
- expected_outputs:
  - concise artifact inventory in the current response or an explicitly requested handoff note
  - no persistent artifact registry
  - no event log
- context_targets:
  must_read:
    - current task diff or provided artifact list
  read_if_needed:
    - active plan document
  do_not_load_by_default:
    - live `$HOME/.codex`
    - unrelated artifacts
    - historical workflow harness files
- risk_profile:
  reads:
    - task-local artifacts only
  writes:
    - none unless the user explicitly requested a document update
  tools:
    - local validation commands when relevant
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Goal
- Produce a task-local inventory of what this task produced and what still needs checking.
- Separate user-facing artifacts from internal ones, and completed work from stale or pending items.
- Hand off when a persistent registry or event log is actually required, instead of inventing one.

## Workflow
1. Collect changed files, generated artifacts, and validation evidence for the current task.
2. Separate user-facing artifacts from internal/intermediate ones.
3. Separate completed items from stale follow-ups and user-verification items.
4. If the request needs a persistent registry, event log, deployment tracker, or evidence-finality queue, stop and route to the proper owner instead of building one here.

## Output Contract
Return only the sections that apply:
- `changed_files`
- `generated_artifacts`
- `validation_evidence`
- `user_verification_needed`
- `stale_followups`
- `excluded_items`

Use the verification labels `agent-verified`, `user-verification-needed`, `unverified`, `blocked`.
Read `references/output-schema.md` for compact, handoff, and blocked/empty output shapes.

## Cross-Skill Boundaries
- `report-diff` owns changed-line and before/after diff presentation.
- `report-critical` owns blocker/QA verdicts and critical review.
- `report-qualitative` owns qualitative evaluation reports.
- Persistent registries, event logs, and finality queues are out of scope; route to the owning workflow.

## Resource and Risk Boundary
- Reads: task-local artifacts and the provided change set only.
- Writes: none unless the user explicitly requests a document or handoff update.
- Network/credentials: none by default; credentials default deny.
- Do not build or persist a registry, event log, or finality queue.

## Anti-Patterns
- Building or persisting a registry, event log, deployment tracker, or finality queue.
- Listing internal/intermediate files as if they were user-facing deliverables.
- Marking an item done without a validation label.
- Re-presenting a full diff instead of an inventory (that is `report-diff`).
- Inventing artifacts when none were produced, instead of reporting an empty/blocked inventory.

## Invocation Examples
Positive:
- "이번 작업 산출물과 검증 내역 정리해줘."
- "핸드오프용으로 바뀐 파일·검증·남은 확인거리 목록 만들어줘."

Negative:
- "변경 diff 보여줘." -> `report-diff`
- "이 작업 비판적으로 리뷰해줘." -> `report-critical`
- "이 결과 품질을 평가해줘." -> `report-qualitative`
- "프로젝트 전체 아티팩트 레지스트리를 유지해줘." -> out of scope (no persistent registry)

## Known Limits
- The inventory reflects only the current task's artifacts; it is not a project-wide registry.
- Items without evidence stay `unverified`; do not assert completion without it.
