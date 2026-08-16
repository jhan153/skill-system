# management-memory-bank-init Reference

## Target And Identity

- Default root for an explicitly requested init: `<project_root>/docs/memory-bank/projects/{project_id}/`
- Required files: `current.md`, `archive.md`, `events.jsonl`, `meta.json`
- Prefer `project_id` from `project-context.yaml`, then an explicit user slug, then normalized git remote identity, and finally `sha256(repo_root_absolute_path)[:12]`.
- Store the final ID and locator source in `meta.json`.

## Canonical Enums

- `entity`: `project|goal|rule|mistake|system`
- `action`: `create|update|deprecate|consolidate|detect_conflict|resolve_conflict|validate`
- `status`: `active|candidate|deprecated`
- `verification`: `verified|unverified`
- `validation_state`: `agent-verified|user-verification-needed|unverified|blocked`

Do not add confidence, maturity, usage, or satisfaction scores.

## Initial Event Record

```json
{
  "event_id": "evt_20260410T120000Z_0001",
  "at": "2026-04-10T12:00:00Z",
  "actor": "agent",
  "workflow": "init",
  "entity": "project",
  "action": "create",
  "item_id": "project",
  "before": null,
  "after": {
    "project_id": "owner-repo",
    "status": "active",
    "verification": "verified"
  },
  "reason": "memory bank initialized by explicit request",
  "evidence": "user initialization request",
  "snapshot_base_version": 0,
  "validation_state": "agent-verified"
}
```

## `meta.json`

```json
{
  "schema_version": 3,
  "project_id": "owner-repo",
  "project_locator": {
    "type": "project-context|git-remote|explicit-slug|path-hash",
    "value": "owner-repo"
  },
  "snapshot_version": 1,
  "created_at": "2026-04-10T12:00:00Z",
  "updated_at": "2026-04-10T12:00:00Z",
  "last_consolidated_at": null
}
```

## Compact `current.md`

Keep these headings even when empty:

1. `이 프로젝트의 목표 & 방향 (Current)`
2. `여러 세션간 지켜야할 룰 (Current)`
3. `반복적으로 실수하는 실수 목록 (Current)`
4. `효과가 좋았던 작업 방식 (Current)`

`current.md` is the present operational snapshot. It does not contain implementation chronology, raw conversations, logs, completed task narratives, or full plan bodies. Use stable pointers to a plan or Knowledge record when details matter.

## Manifest Section

```yaml
memory_bank:
  root: docs/memory-bank/projects/owner-repo
  storage: local
```

Merge this section into an existing `project-context.yaml` without reformatting or replacing unrelated keys. If safe section-preserving update is unavailable, stop before writing either artifact.

## Validation

- All four files exist and are non-empty.
- `events.jsonl` and `meta.json` parse.
- `snapshot_version` is `1` and all baseline artifacts share the first event ID.
- The manifest points to the created bank and every pre-existing unrelated section remains semantically unchanged.
