# Claude hooks (opt-in)

`claude_hook_adapter.py` is the Claude-side counterpart of the Codex
`hooks.json` adapter. It records Claude Code lifecycle events into the same
hash-chained evidence ledger as Codex (`.codex/tools/hook_runtime.py`), so the
observed-evidence trail is the same across both runtimes. The discipline
contract itself lives in the byte-mirrored skills (`workflow-rigor`, etc.); this
file is only the runtime wiring.

## Status
- **Observational by default** — it records events and always allows stop. This
  matches the Codex adapter's non-strict default and decision 6 (observational
  default).
- **Strict block is deferred.** The Codex strict gate blocks a stop when an
  `agent-verified` claim contradicts observed evidence, which depends on a
  per-run `run.yaml` manifest. The Claude runtime does not yet emit that
  manifest, so strict mode degrades to observational here. A Claude run-manifest
  producer is the prerequisite for strict-block parity (future 8.4.x).
- **Fail-open** — any error (including missing `.codex/tools`) exits 0 so a host
  session is never broken.

## Enable (host-managed, not auto-installed)
Hooks are managed by the host environment. The bundle never auto-installs this.
Add it to your `settings.json` (user `~/.claude/settings.json`, or a project
`.claude/settings.json`) and approve it under your permission policy:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/claude_hook_adapter.py" }] }
    ],
    "PostToolUse": [
      { "matcher": "Bash|Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/claude_hook_adapter.py" }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/claude_hook_adapter.py" }] }
    ]
  }
}
```

Notes:
- Adjust the path to where the bundle is deployed. For a project-scoped install
  use `$CLAUDE_PROJECT_DIR/.claude/hooks/claude_hook_adapter.py`.
- Requires the Codex tools to be co-deployed (the adapter imports
  `hook_runtime` from a sibling `.codex/tools`). Without it, the adapter no-ops.
- The ledger path follows `hook_runtime.default_ledger()` (honors
  `SKILL_SYSTEM_HOOK_LEDGER`); runtime state is never written into the bundle.
