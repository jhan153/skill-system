---
name: coordination-handoff
description: Create lightweight task DAGs, multi-agent or multi-session handoffs, lock scopes, validation ownership, and task-local artifact inventories. Use only when the user explicitly asks for coordination, handoff, ownership splitting, or an artifact/verification summary; do not use for direct implementation, a simple goal summary, or persistent workflow state.
---

# Coordination Handoff

## Routing Card
- role: support
- intent_signature:
  - explicit task DAG, handoff, lock scope, ownership split, or artifact inventory
- use_when:
  - the user explicitly requests coordination across agents, sessions, or workstreams.
  - a handoff needs allowed files, ownership, validation responsibility, or produced-artifact evidence.
- do_not_use_when:
  - one agent can execute directly and no handoff or inventory was requested.
  - the request merely contains goal/목표 or asks for a normal status summary.
  - persistent event logs, workflow state, deployment tracking, or completion finality are required.
- expected_inputs:
  - existing plan or task list when coordination is requested
  - files, ownership constraints, changed artifacts, or validation evidence relevant to the requested mode
- expected_outputs:
  - the smallest sufficient brief, handoff packet, or artifact inventory in the response or an explicitly requested document
- context_targets:
  must_read:
    - current coordination or inventory request
    - active plan, task list, diff, or artifact list needed for the selected mode
  read_if_needed:
    - `references/handoff-schemas.md` when a structured packet is useful
    - `.codex/docs/team_patterns.md` for repository-specific team conventions
  do_not_load_by_default:
    - full memory, unrelated plans, historical workflow state, or live runtime homes
- risk_profile:
  reads:
    - task-local plans, paths, diffs, and validation evidence
  writes:
    - none unless the user explicitly requests a handoff or plan document
  tools:
    - none by default
  sensitive_resources:
    - redact secrets and credentials from evidence
- entry_scene:
  - PREPARE

## Select One Mode
- `brief`: frame the objective, non-goals, success signal, and a 3-6 node task DAG.
- `multi_agent`: add non-overlapping lock scopes, one owner per scope, serialization for shared files, and one validation owner per task.
- `artifact_inventory`: list changed/generated artifacts, labeled validation evidence, user checks, and stale follow-ups.

Combine modes only when the request explicitly needs both coordination and handoff evidence. An artifact list alone does not justify a task DAG.

## Workflow
1. Confirm the explicit coordination, handoff, or inventory intent and choose the smallest mode.
2. Read only the owning plan slice, task list, diff, or artifact set.
3. State non-goals and do-not-touch boundaries before splitting work.
4. For parallel work, assign non-overlapping lock scopes; otherwise serialize shared-file changes.
5. Give each task one concrete output and one validation owner.
6. Report observed artifacts and checks with `agent-verified`, `user-verification-needed`, `unverified`, or `blocked`; never infer completion from the handoff itself.

## Quality Gates
- Reject a split that adds more coordination cost than execution value.
- Do not invent agents, files, artifacts, checks, or completion evidence.
- Keep handoffs response-first and task-local; do not create `.agent-workflow`, registries, or event logs.
- Distinguish changed, not changed, validation done, remaining risk, and next owner when a handoff is requested.
- Use `references/handoff-schemas.md` only when structured fields materially improve the handoff.

## Output Contract
Return only the selected shape:
- `goal_brief` and `task_dag` for `brief`
- `task_cards`, `lock_scopes`, `integration_owner`, and `validation_owners` for `multi_agent`
- `changed_files`, `generated_artifacts`, `validation_evidence`, `user_verification_needed`, and `stale_followups` for `artifact_inventory`

## Boundaries
- Planning skills own plan creation and substantive plan state.
- Execution skills own implementation and validation work.
- Reporting skills own qualitative, critical, lifecycle, or diff reports.
- This skill describes coordination evidence; it never creates system-wide finality.
