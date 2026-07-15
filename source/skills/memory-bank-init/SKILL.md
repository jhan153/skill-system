---
name: memory-bank-init
description: Initialize project-scoped persistent memory by creating the canonical baseline files, project identity metadata, and first append-only event. Use only on an explicit init or reinit request; do not overwrite an existing bank as if it were a normal update.
---

# Memory Bank Init

## Routing Card
- role: memory_operation
- intent_signature: initialize memory bank, start persistent project memory, 메모리뱅크 초기화
- use_when: the user explicitly requests a fresh project bank or explicitly approved reinitialization
- do_not_use_when: update, correction capture, maintenance, or design discussion is primary
- expected_inputs: verified project root/identity, target path state, and explicit init/reinit intent
- expected_outputs: canonical baseline files, first event, stable identity, preservation decision, and readback result
- context_targets: read project identity and exact target state; before writing load `.codex/docs/memory_mutation_contract.md` and `reference.md`; use `docs/document.md` only for exceptional failure
- risk_profile: create one canonical bank only after explicit intent; never read unrelated banks or overwrite accepted history silently; credentials denied
- entry_scene: PREPARE

## Initialization Contract
Resolve the project root and `project_id` by `reference.md`, record the locator source, and inspect the exact target before writing. A missing/ambiguous identity or unwritable path blocks creation. If any bank exists, ordinary init stops; reinit requires explicit intent plus a safe repository-approved preservation/migration path. Reinitialization must never delete or overwrite accepted history silently; do not replace or merge it as fallback.

## Workflow
1. Stage `current.md`, `archive.md`, `events.jsonl`, and `meta.json` for the verified fresh target under the shared mutation contract.
2. Append the first `entity=project`, `action=create` event.
3. Write the baseline current/archive sections and project metadata.
4. Commit as one unit, then read back all four files, their shared event ID, snapshot version, and stable project identity.

Any partial creation, parse failure, or identity mismatch remains failed/blocked rather than a successful initialization.

## Output
Report created/preserved paths, project/event IDs, four-file readback, and identity/reinit uncertainty. Initialization creates storage, not substantive memory policy; surface the lower portability of a path-hash identity.
