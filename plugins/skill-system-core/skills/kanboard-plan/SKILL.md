---
name: kanboard-plan
description: Onboard or operate Markdown-authoritative Kanboard plan projections through explicit rollout or ops modes. Use only for selected workspaces/plans; dry-run every live write, require matching approval, preserve stable mappings, and verify applied state by board readback.
---

# Kanboard Plan

## Routing Card
- role: primary
- intent_signature: explicit Kanboard plan onboarding, projection, pull candidates, validation/session record, or board curation
- use_when: the user explicitly requests first-time/bulk rollout or ongoing operations for a registered Markdown plan workspace
- do_not_use_when: Markdown plan authoring, Kanboard installation/theme/plugin work, concept explanation, or an unspecified board/workspace
- expected_inputs: mode, exact workspace/plan set, config/registry state, operation, mapping when required, and dry-run/apply intent
- expected_outputs: scoped registration/projection/candidate/readback result with exact approval or blocker state
- context_targets:
  must_read: selected plan, `.kanboard-plan.yml`, and current request
  read_if_needed: `references/rollout.md` or `references/ops.md`, workspace cache/registry, live board snapshot, and the integration README
  do_not_load_by_default: full repos, unrelated workspaces, other plan bodies, or raw session history
- risk_profile:
  reads: selected plans/config/state/registry and live board snapshot
  writes: workspace config/registry in rollout; Kanboard JSON-RPC only after reviewed dry-run and explicit apply approval; never Markdown on pull
  tools: `kanboard-plan-sync` MCP or documented CLI/JSON-RPC path
  sensitive_resources: token from environment/local DB only; never config, state, plan, log, or board text
- entry_scene: PREPARE

## Modes

- `rollout`: first-time or multi-workspace registration and bulk projection. Read [Rollout](references/rollout.md).
- `ops`: registered-board push, pull candidates, mapped validation/session records, or curation. Read [Ops](references/ops.md).

Markdown plan keys and registered workspace IDs remain canonical projection identities. Board state is operational evidence, not plan authority. Pull/curation never mutate or auto-promote Markdown.

## Common Write Gate

1. Fix the exact workspace, plan, operation, and stable mapping.
2. Run the same live-write operation as a dry-run and review every identity, operation, error, and skip.
3. Apply only after explicit approval for that unchanged scope; changed inputs require a fresh dry-run and approval.
4. Verify returned IDs/state through authoritative board response or readback. A clean receipt or dry-run alone is not applied completion.

Never write Kanboard SQLite, persist tokens, guess task mappings, duplicate cards/comments on retry, or infer Markdown completion from board motion.

## Output

Report `mode`, selected scope and mappings, config/registry changes, dry-run summary, approval state, applied IDs/readback, candidates, per-workspace errors/skips, and one next action. Use `ready_for_review`, `blocked`, `partial`, or `complete` without hiding mixed results.
