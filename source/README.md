# source/ — neutral canonical (post Phase 1.5 cutover)

**`.codex/`, `.claude/`, `.grok/`, and `.antigravity/` are generated targets. Do not edit them
directly.** Edit `source/` and regenerate.

## Layout
- `source/skills/` — 65 canonical skills packaged into one Codex set and one portable
  Claude/Grok/Antigravity set
- `source/shared/` — portable `docs/`, schemas, and Core-owned contract/card sources projected into their declared consumers
- `source/platform/codex/` — Codex-owned runtime companion instructions, routing, hooks, rules, and harness docs
- `source/platform/claude/` — Claude-owned runtime companion instructions, routing, and hook docs
- `source/platform/grok/` — Grok global rules; Orca owns worker lifecycle
- `source/platform/antigravity/` — Antigravity global rules; Orca owns worker lifecycle
- `source/runtime-inventory.yaml`, `source/runtime-payload-policy.md` — current 10.0 distribution inventory and policy
- `source/tools/` — build system (not generated into any target)

## Workflow
1. Edit files under `source/`.
2. Regenerate runtime companions and/or plugin packages for the changed distribution surface:
   ```
   python3 source/tools/generate_targets.py --target runtime-codex
   python3 source/tools/generate_targets.py --target runtime-claude
   python3 source/tools/generate_targets.py --target runtime-grok
   python3 source/tools/generate_targets.py --target runtime-antigravity
   ```
   Runtime generation never creates skill mirrors; skills ship through plugins.
3. Read back the affected generated paths. There is no unconditional all-change evaluation gate;
   run only the approved test category whose declared surface changed.

The repository-wide contract surface has exactly four Go tests. The Core Card check runs only for
Core Card, execution-item kind/binding, or Plan/Handoff ledger-table changes:

```text
go test ./internal/corecards -run TestCoreCardsMatchPlanExecutionHandoff
```

Run it only when a Core Card, execution-item kind, `## Core Cards` binding, or the Plan Execution
Handoff ledger tables change.

The remaining three repository-wide tests are under `internal/systemcontract`:

```text
go test ./internal/systemcontract -v
```

They cover canonical skill/plugin ownership, active-provider package/manifest/resource closure, and
declared global-rule plus harness wiring. Run them only when those system surfaces change; ordinary
skill prose and model changes do not trigger them.

Direct harness tests live with each provider-owned Go module. Run only the provider module whose
runtime behavior changed. They are component tests, not a release gate or a Skill System-wide
suite.

Harness modules are provider-owned under `source/runtime/go/{codex,claude,grok,antigravity}`.
Run `go test ./...` from each affected provider module. The root `source/runtime/go` module owns
repository contract tests only; provider modules never import one another.

There is no persistent per-skill behavior-test category, no automatic all-suite command, and no
runtime Python validator. Model-dependent skill behavior is observed only through an explicitly
requested, non-gating fresh task. Plan/Handoff authoring performs one bounded structural readback
inside the owning task instead of invoking a validator executable.

## Notes
- The `.generated` marker at each target root declares the do-not-edit policy.
- Generation updates repository targets only. Installing into a home directory or live plugin cache is a separate, explicit deployment action.
