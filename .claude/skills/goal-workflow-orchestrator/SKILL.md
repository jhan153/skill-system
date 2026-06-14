---
name: goal-workflow-orchestrator
description: Frames explicit task DAGs and handoff notes only when the user asks for lightweight coordination; it does not trigger from the word goal alone.
---

# Goal Workflow Orchestrator

## Routing Card
- role: support
- intent_signature:
  - task DAG
  - workflow framing
  - handoff note
  - lock scope
  - lightweight coordination
- use_when:
  - the user explicitly asks for a task graph, handoff note, lock-scope map, or coordination outline from an existing plan or task list.
  - the user explicitly asks to split multi-agent or multi-session work into a small human-readable coordination note.
- do_not_use_when:
  - the request can be handled with ordinary implementation steps.
  - the user says goal, objective, 목표, or 목적 but only wants a summary, next step, or direct implementation.
  - the request depends on app-managed Codex Goal state mutation that this manual bundle cannot provide.
  - the work would create install, deployment, signoff, operational recovery, or evidence-finality machinery.
  - the requested output would model the skill system itself as a completable objective.
- expected_inputs:
  - existing plan or user task list
  - allowed files and lock scope
  - validation requirements
- expected_outputs:
  - a concise task DAG or handoff note in the current response or an explicitly requested plan document
  - no `.agent-workflow` directory
  - no event log
  - no artifact registry
- context_targets:
  must_read:
    - active plan or user-provided task list
  read_if_needed:
    - `.codex/context-routing.md`
    - `.codex/docs/team_patterns.md`
  do_not_load_by_default:
    - full memory bank
    - live `$HOME/.codex`
    - historical workflow harness files
- risk_profile:
  reads:
    - local plan context only
  writes:
    - none unless the user explicitly requested a plan document update
  tools:
    - none by default
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Boundary
- This skill is retained only as a lightweight coordination helper in 7.1.
- It must not create persistent workflow state, bundle-level finality labels, or a release pipeline.
- If coordination intent is ambiguous, prefer a normal checklist or one-sentence next step instead of invoking this skill.

## Workflow
1. Confirm that the user asked for task graph, handoff, lock scope, or multi-session coordination.
2. Reduce the plan to a small goal brief and task DAG slice.
3. Keep the graph descriptive and response-first; do not store state unless the user explicitly asks for a plan document.
4. Mark non-goals and do-not-touch boundaries before splitting tasks.
5. Hand off to `multi-agent-plan-executor` when lock scopes, task cards, or agent ownership are needed.

## Goal Brief Schema

```yaml
goal_brief:
  objective:
  non_goals: []
  current_workstream:
  do_not_touch: []
  success_signal:
  not_a_completion_claim: true
```

`success_signal` is a local task signal, such as "YAML parses" or "mirror diff is clean". It is not bundle readiness or system finality.

## Task DAG Slice Schema

```yaml
task_dag_slice:
  nodes:
    - task_id:
      owner_hint:
      depends_on: []
      allowed_files: []
      expected_output:
      validation_owner:
  integration_owner:
  notes:
```

## Output Rules
- Keep DAG slices small enough to fit in a normal handoff response.
- Prefer `goal_brief` plus 3-6 task cards over a large planning package.
- Do not trigger from a simple request to summarize the goal in one sentence.
- Do not model the skill bundle itself as complete or incomplete.
