# Runtime Payload Policy (Phase 0)

> Phase 0 deliverable of `docs/plan/2026-06-29-skill-system-plugin-neutral-source.md`.
> Defines how each runtime-payload class in `source/runtime-inventory.yaml` maps to the
> neutral source layout and to generated targets. This is policy/classification only —
> no generator and no target content is changed in Phase 0.

## 1) Classification basis
Evidence collected 2026-06-29 from `skill-system/` root:
- `diff -qr .codex/skills .claude/skills` → only `.DS_Store` differs (skill bodies already mirrored).
- `diff -q .codex/context-routing.md .claude/context-routing.md` → identical.
- Shared docs generate verbatim; platform-owned document overlays remain intentionally distinct.
- `diff -qr .codex/eval .claude/eval` → only `eval/eval-case.schema.json` differs.
- `.codex` has 15 top-level entries; `.claude` has 9. `.codex/tools` has 29 top-level files plus `tests/`; generated Claude runtime has no tools root.
- `.gitignore` excludes `/docs/`, `/.github/`, `/.kanboard-plan/`, `/.kanboard-plan.yml`.

Current counts (`source/runtime-inventory.yaml`, 29 entries): shared-neutral 5,
platform-native 3, codex-only 8, maintainer-only 9, claude-only 2, and
local-only/ignored 2. Four entries remain `provisional`, three carry an explicit gap,
and Phase 1b decisions are recorded for eight inventory entries.

## 2) Bucket → source/target mapping

| class | source location | generated into | strategy |
|---|---|---|---|
| shared-neutral | `source/skills/`, `source/shared/docs`, `source/shared/eval`, `source/shared/schemas` | `.codex` AND `.claude` | `neutral-verbatim`, `platform-projected`, or `mirror-from-canonical` |
| codex-only | `source/platform/codex/` | `.codex` only | `codex-native` |
| claude-only | `source/platform/claude/` | `.claude` only | `claude-native` |
| maintainer-only | `source/maintainer/` (or kept under `.codex/tools` as canonical tooling) | maintainer/CI surface, not per-platform parity | `tooling` |
| plugin-packageable | `source/plugins/*.yaml` membership (Phase 2) | Codex `plugins/skill-system-*`; Claude `plugins/claude/skill-system-*` | Phase 2 |
| local-only/ignored | n/a | n/a (gitignored) | `local-ignored` |

### Generation strategies
- `neutral-verbatim` — copy unchanged to either generated target (e.g. `docs/`, `eval/`, `schemas/`).
- `platform-projected` — copy one canonical skill body, then translate the canonical invocation bit into host-native metadata. Codex keeps `agents/openai.yaml`; Claude adds `disable-model-invocation: true` only to explicit-only generated skills. Codex packages stay under `plugins/<name>` and paired Claude packages under `plugins/claude/<name>`, sharing one plugin name and version.
- `mirror-from-canonical` — generate the Claude copy from shared canonical data with a
  `generated_from` / `source_checksum` / `do_not_edit` header. The current instance is
  `eval/eval-case.schema.json`.
- `platform-template` — one neutral body + a per-platform overlay yields divergent output
  (e.g. `AGENTS.md` ↔ `CLAUDE.md`).
- `codex-native` / `claude-native` — lives in only one target.
- `tooling` — generator/CI machinery; not shipped as per-platform runtime content.

Since 9.3.1, `AGENTS.md`/`CLAUDE.md` and each platform's `context-routing.md` are platform-native harness surfaces. `runtime-codex` and `runtime-claude` generate and check them independently; `runtime` is the unified release aggregate. This split does not create platform-specific product versions or tags.

## 3) Phase 1a scope (regression baseline)
Phase 1a must regenerate **byte-identical** output for every confirmed committed path in both
`.codex` and `.claude`. No content changes, no allowlist diff. This includes shared-neutral,
codex-only, claude-only, and maintainer-only entries as they exist today. Only
`local-only/ignored` paths are excluded.

The existing `eval-case.schema.json` mirror is the proven precedent: Phase 1a generalizes that
mechanism to the full payload without changing any byte of current output.

**Byte-identical constraint — mirror headers carry a frozen timestamp.** The current
`.claude/eval/eval-case.schema.json` header contains a frozen `generated_at` plus a
`source_checksum`. A naive regenerate would emit a *new* timestamp and break byte-identity.
Phase 1a's generator must therefore be **idempotent**: when the canonical source content is
unchanged, it preserves the existing target's `generated_at` (and only refreshes the timestamp
when `source_checksum` actually changes). This keeps mirror-from-canonical files byte-identical
on regeneration. Implement this before claiming Phase 1a byte-identity for the mirror files.
Recommended sub-batch order for Phase 1a:
1. neutral-verbatim payload (skills, context-routing.md, docs/ and eval/ except the eval-schema mirror) — no timestamp concern.
2. mirror-from-canonical eval schema (idempotent timestamp preservation).
3. platform split (`AGENTS.md`/`CLAUDE.md`, hooks, codex-only/claude-only trees, maintainer tools).

## 4) Phase 1b scope (gap remediation) — DONE
Phase 1b closed genuine Claude mirror gaps. **Content inspection narrowed the four candidates to
one real shared gap (schema definitions); the other three were correct platform divergence, not
gaps.** Applied to live: `.codex` byte-identical (no regression), `.claude` gained `schemas/` only.

Applied:
- **`schemas/` → shared-neutral**: 24 schema definitions + neutral examples moved to
  `source/shared/schemas`, generated to BOTH targets. The one codex-tool-referencing example
  (`schemas/workitem/examples/work-item.example.yaml`, refs `.codex/tools/validate_work_item.py`)
  stays codex-only in `source/platform/codex` and is merge-overlaid onto `.codex` only.
  Result: `.codex/schemas` = 25 (byte-identical), `.claude/schemas` = 24 (new, no `.codex` leak).

Corrected after content inspection (recorded decisions overridden by evidence):
- `research/` (ledger + schema) → **maintainer-only** (was `codex-only`). The only
  active consumer is the repository-relative research verification profile; no skill,
  hook, execution-assurance check, or live-home runtime reads `<CODEX_HOME>/research/`.
  Both files live under `source/maintainer/fixtures/research-ledger/` and are not
  generated into `.codex`, `.claude`, or plugins.
- `research-routing.md` → **codex-only** (was "shared"). It references codex-only/dangling assets
  (`codex-research-lifecycle` skill and `.codex/references/...`, neither of which exists even under
  `.codex`). Generating to `.claude` would ship a broken doc. Sharing would require a content
  rewrite — out of Phase 1b scope.
- Desktop notification → **shared Go OS core with platform-native event mapping**. Both generated
  dispatchers use the redacted Go notification package and packaged macOS Swift overlay. Claude
  consumes native `Notification` types while Codex keeps its own permission/Stop event branches.
- `harness/README.md` → **codex-only** (was "shared"). Documents `.codex/harness/` paths; Claude
  already has its own `hooks/README.md`.

Review record (the "reviewed allowlist diff"): post-cutover the integrity gate enforces
`live == generator(source)`, so a standalone allowlist file is redundant. The Phase 1b change is
the git-visible `+ .claude/schemas/` (24 files) and nothing else; `.codex` stayed byte-identical
and the applicable `verify_bundle` profiles pass.

## 5) Recorded Phase 1b decisions
These decisions intentionally keep Claude lightweight for v1. Executable runtime tools stay
Codex-only unless there is an explicit Claude-side runtime contract. Platform-neutral contracts
can be shared.

1. **Loop engine tools** (`init/activate/resume/deactivate/evaluate_loop_run.py`, `loop_policy.py`) — `codex-only` for v1.
2. **`tools/task_ledger.py`** — `codex-only` explicit workflow runtime. Codex Agent Run was removed in 9.3.2.
3. **Active portable schemas** (knowledge/loop/orchestration/task/tools/workitem) — `shared-neutral`; removed Agent Run and lifecycle-ledger schemas are not platform payload.
4. **`research/`** (ledger + schema) — originally recorded as `codex-only` for v1;
   current consumer inspection supersedes that classification with a source-only
   `maintainer` fixture outside all runtime targets.
5. **`tools/requirements.txt`** — `codex-only` for v1, because no runtime-logic tools move to Claude.
6. **`rules/default.rules`** — `codex-only` for v1; no Claude equivalent is generated.

Phase 1b implementation scope after these decisions:
- Add/generate `research-routing.md` to Claude as `shared-neutral`.
- Keep notification implementations platform-owned.
- Reconcile `harness/README.md` against Claude's `hooks/README.md`.
- Add/generate `schemas/` to Claude as `shared-neutral`.

## 6) Non-goals (restated)
- No 1:1 tool/hook/schema parity is forced; only `shared-neutral` items reach both targets.
- No new security/artifacts skills, no marketplace/runtime/config changes, no edits to
  `.codex/skills/.system` or app-managed runtime.

## 7) Next phase entry conditions
- Phase 1a may start now: inventory + policy exist and the regeneration set is enumerated.
- Phase 1b may start for the recorded `shared-neutral` items above. The decisions are recorded
  back into `source/runtime-inventory.yaml`.
