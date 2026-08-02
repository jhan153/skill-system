---
name: coordination-handoff
description: Create lightweight task DAGs, multi-agent or multi-session handoffs, lock scopes, validation ownership, and task-local artifact inventories. Use only when the user explicitly asks for coordination, handoff, ownership splitting, or an artifact/verification summary; do not use for direct implementation, a simple goal summary, or persistent workflow state.
---

# Coordination Handoff

## Routing Card
- role: support
- intent_signature: explicit task DAG, handoff, ownership/lock split, or artifact/verification inventory
- use_when: the user explicitly requests coordination across agents, sessions, or workstreams, or a handoff/inventory
- do_not_use_when: direct implementation, ordinary goal/status summary, or persistent event, workflow, deployment, or completion state
- expected_inputs: request plus the minimum relevant plan slice, task list, diff, artifact set, and any canonical skill IDs already selected for delegated tasks
- expected_outputs: smallest requested response or explicitly requested document, preserving already selected skills at the worker boundary
- context_targets: task-local inputs; `references/handoff-schemas.md` when structure helps; repository team conventions only when needed
- risk_profile: task-local reads, no tools by default, no file write without an explicit document request, and secrets redacted
- entry_scene: PREPARE

Choose the smallest requested mode:
- `brief`: provide a short objective, non-goals, success signal, and continuation note. Add a 3-6 node task DAG only when the user requests decomposition or dependencies.
- `multi_agent`: add non-overlapping lock scopes, one owner per scope, serialization for shared files, and one validation owner per task.
- `artifact_inventory`: list changed/generated artifacts, labeled validation evidence, user checks, and stale follow-ups.

An explicit changed/generated-file or validation-evidence list is `artifact_inventory` even without the word handoff.
Combine modes only when both needs are explicit. An artifact list or short session handoff alone does not justify a task DAG.

## Workflow
1. Confirm the explicit coordination, handoff, or inventory intent and choose the smallest mode.
2. State non-goals and do-not-touch boundaries before splitting work. Reject a split whose coordination cost exceeds its execution value.
3. For parallel work, assign non-overlapping lock scopes; serialize any shared-file changes. Give each task one concrete output and one validation owner. Copy canonical skill IDs already selected for that task into `selected_skills` and the worker instruction instead of asking the worker to rediscover them. When no skill was selected upstream, omit the field and let the worker use normal implicit routing; never invent an adjacent skill ID.
4. For an artifact handoff, distinguish changed, not changed, validation done, remaining risk, user checks, and next owner.
5. Label only observed evidence as `agent-verified`, `user-verification-needed`, `unverified`, or `blocked`; pure planning or response-shape decisions need no result label. A handoff packet never establishes implementation or completion.
6. Do not invent agents, files, artifacts, checks, or evidence. Keep the result response-first and task-local; create no registries or event logs.

## Output Contract
Return only the selected shape:
- `goal_brief` and continuation note for `brief`; include `task_dag` only when requested
- `task_cards` with applicable `selected_skills`, `lock_scopes`, `integration_owner`, and `validation_owners` for `multi_agent`
- `changed_files`, `generated_artifacts`, `validation_evidence`, `user_verification_needed`, and `stale_followups` for `artifact_inventory`

## Boundaries
- Planning skills own plan creation and substantive plan state.
- Execution skills own implementation and validation work.
- Reporting skills own qualitative, critical, lifecycle, or diff reports.
- A handoff propagates an upstream skill selection but does not make a new specialist decision merely to fill `selected_skills`.
- This skill describes coordination evidence; it never creates system-wide finality.
