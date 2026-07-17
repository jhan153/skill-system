---
name: project-context-init
description: Create a minimal repository-owned project-context.yaml location manifest. Use only when the user explicitly asks to initialize project context locations; do not initialize Memory, Knowledge, plan, Wiki, or skill stores as a side effect.
---

# Project Context Init

## Routing Card
- role: project_context_operation
- intent_signature: initialize project-context.yaml, 프로젝트 컨텍스트 경로 선언 시작
- use_when: the user explicitly requests a new project context manifest
- do_not_use_when: resolving, reading, updating, initializing a store, or ordinary project setup is primary
- expected_inputs: exact repository root or manifest path, stable project ID, and explicit initialization intent
- expected_outputs: one minimal manifest and direct readback
- context_targets:
  must_read: exact target state and `.codex/docs/project_context_manifest.md`
  read_if_needed: nearest repository instructions for project identity or persistence
  do_not_load_by_default: Memory, Knowledge, plans, Wikis, transcripts, home context, adjacent repositories
- risk_profile:
  reads: exact target and repository boundary only
  writes: one repository-local `project-context.yaml`
  tools: local file edit and `skill-system-harness context resolve` readback when available
  sensitive_resources: home/global context and undeclared stores denied
- entry_scene: PREPARE

## Workflow
1. Resolve the exact user path, otherwise the current repository root. Do not search home or adjacent repositories.
2. Stop if the target manifest already exists; use `project-context-update` for an existing file unless replacement is explicit.
3. Confirm a stable `project_id` from the repository or user. Do not infer store paths merely because common defaults exist.
4. Create only:

   ```yaml
   schema_version: 1
   project_id: <project-id>
   ```

   Add an optional location section only when the same request supplied or approved that location.
5. Read back the exact file and resolve it with the common harness resolver when available. Missing declared targets remain `unavailable`; initialization does not create them.

## Output
Report the manifest path, project ID, optional sections actually declared, and resolver readback. Do not claim that any store was initialized.
