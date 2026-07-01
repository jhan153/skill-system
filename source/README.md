# source/ — neutral canonical (post Phase 1.5 cutover)

As of the Phase 1.5 cutover, **`.codex/` and `.claude/` are generated targets. Do not edit them
directly.** Edit `source/` and regenerate.

## Layout
- `source/skills/` — 68 skills (neutral; generated verbatim into both targets)
- `source/shared/` — `context-routing.md`, `docs/`, `eval/` (neutral; generated into both)
- `source/platform/codex/` — codex-only + maintainer payload (AGENTS.md, hooks, hooks.json, rules, schemas, research, research-routing.md, harness, field-feedback, tools)
- `source/platform/claude/` — claude-only payload (CLAUDE.md, hooks, tools)
- `source/mirror-meta.json` — frozen `generated_from`/`generated_at`/`source_checksum` for the two mirror-from-canonical files (keeps regeneration byte-identical)
- `source/runtime-inventory.yaml`, `source/runtime-payload-policy.md` — Phase 0 classification + policy
- `source/tools/` — build system (not generated into any target)

## Workflow
1. Edit files under `source/`.
2. Regenerate targets:
   ```
   python3 source/tools/generate_targets.py --target runtime
   ```
3. Verify byte-identity / detect stray target edits (the cutover gate):
   ```
   python3 source/tools/check_generated_targets.py --target runtime --baseline
   ```
   PASS = every generated file matches the live target. FAIL = a target was hand-edited or
   `source/` changed without regenerating. Run this before committing target changes.

## Notes
- The `.generated` marker at each target root declares the do-not-edit policy.
- Integrity is enforced by regeneration (`check_generated_targets.py`), not a stored checksum
  manifest — re-deriving the target is stronger than comparing a stored hash.
- Mirror files (`docs/source_registry.yaml`, `eval/eval-case.schema.json`) keep their frozen
  `generated_at`; changing the canonical requires updating `source/mirror-meta.json` (Phase 1b).
- Phase 1b (shared-neutral gap remediation) and the AGENTS.md/CLAUDE.md platform-template
  refactor are not yet done; both are tracked in `docs/plan/2026-06-29-skill-system-plugin-neutral-source.md`.
