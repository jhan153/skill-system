# Kanboard Plan Rollout

Use for first-time or multi-workspace onboarding.

## Tools

- `inspect_workspace(path)`: inspect config, plans, state, and secret findings without writes.
- `register_workspace(path, init=true)`: scaffold config/state when approved and ensure host-registry membership; use `init=false` for valid hand-authored config.
- `sync_all(apply=false|true)`: preview or apply every registered sync-enabled plan; apply may be partial.
- CLI equivalents: `init-workspace`, `register`, `list-workspaces`, `sync-all [--apply]`, `status-all`, and `check-secrets` with the integration's documented `PYTHONPATH`.

## Workflow

1. Fix the workspace/plan set and inspect each workspace.
2. Stop on a missing workspace/plan, secret, corrupt mapping, ambiguous identity, or duplicate key.
3. Register idempotently. Preserve valid existing config with `init=false`; report registry/config/state writes separately from live projection writes.
4. Run `sync_all(apply=false)` and review every error, skip, identity, and operation. Errors block bulk apply; reduced scope needs a fresh dry-run.
5. After exact approval, run `sync_all(apply=true)`, retain per-workspace/plan results, and read back affected live objects.

`ready_for_review` means registration and current dry-run completed. `complete` requires every requested projection plus live readback. Mixed applied/error state is `partial`, never whole-run success.
