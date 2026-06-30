# memory-bank-init Reference

## Scope
- This pack covers initialization only.
- It creates the storage root and baseline artifacts for a project-scoped memory bank.

## Data Root
- Canonical root: `<project_root>/docs/memory-bank/projects/{project_id}/`
- Required files: `current.md`, `archive.md`, `events.jsonl`, `meta.json`

## Project ID Derivation
1. Use an explicit project slug if the user or repo config provides one.
2. Else derive from a normalized git remote identity such as `owner/repo`.
3. Else fall back to `sha256(repo_root_absolute_path)[:12]`.

Store both the final `project_id` and the locator source in `meta.json`.

## Canonical Enums
- `entity`: `project|goal|rule|mistake|system`
- `action`: `create|update|deprecate|consolidate|detect_conflict|resolve_conflict|validate`
- `status`: `active|candidate|deprecated`
- `verification`: `verified|unverified`
- `confidence`: `low|medium|high`
- `validation_state`: `agent-verified|user-verification-needed|unverified|blocked`

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
    "verification": "verified",
    "confidence": "high"
  },
  "reason": "memory bank initialized",
  "evidence": "initialization requested by user",
  "snapshot_base_version": 0,
  "validation_state": "agent-verified"
}
```

## `meta.json` Initial Contract
```json
{
  "schema_version": 2,
  "project_id": "owner-repo",
  "project_locator": {
    "type": "git-remote|explicit-slug|path-hash",
    "value": "git@github.com:owner/repo.git"
  },
  "snapshot_version": 1,
  "created_at": "2026-04-10T12:00:00Z",
  "updated_at": "2026-04-10T12:00:00Z",
  "last_consolidated_at": null
}
```

## `current.md` Baseline Sections
1. `이 프로젝트의 목표 & 방향 (Current)`
2. `여러 세션간 지켜야할 룰 (Current)`
3. `반복적으로 실수하는 실수 목록 (Current)`

Each section starts empty and must preserve the heading even when there are no items.

## `archive.md` Init Block
```markdown
## 2026-04-10T12:00:00Z | evt_20260410T120000Z_0001
- workflow: init
- entity: project
- action: create
- item_id: project
- reason: memory bank initialized
- evidence: initialization requested by user
- before: null
- after: {"project_id":"owner-repo","status":"active"}
```

## Validation Checklist
- The target directory exists.
- All four files exist and are non-empty.
- `events.jsonl` and `meta.json` are parseable.
- `snapshot_version` starts at `1`.
