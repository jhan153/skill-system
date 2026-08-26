# Claude-native Go hooks

The Claude runtime ships a dedicated Go dispatcher. It reuses the bounded
response guard, project-context resolver, redaction, and OS notification
packages without reusing the Codex event dispatcher.

Claude owns the independent `source/runtime/go/claude` module. It receives the distributed common
harness baseline plus the Claude-specific event handler; it does not import Codex execution
admission or another provider's hook wire contract.

The runtime handles only four Claude events:

| Event | Behavior |
| --- | --- |
| `SessionStart` | Clear fresh-session correction state and inject only the nearest `project-context.yaml` location summary. |
| `UserPromptSubmit` | Record the current prompt identity and inject correction context only for an explicit user correction. |
| `Stop` | Respect `stop_hook_active` and apply the one-shot recovery-only response guard. |
| `Notification` | Forward selected native Claude attention/completion notifications through the redacted OS notifier. |

`Notification` is matched only for `permission_prompt`, `idle_prompt`,
`elicitation_dialog`, `agent_needs_input`, and `agent_completed`. Stop does not
infer notification intent, so approval, idle, input, and background-completion
alerts are not duplicated.

Claude Code 2.1.196 and later supplies `prompt_id`; that is the primary turn
identity. Older clients use a hash-only per-session sequence fallback. The
dispatcher reads `last_assistant_message` directly on Stop and never parses a
transcript for turn identity or final-response judgment. `stop_hook_active`
always disables another guard block.

The dispatcher has no lifecycle ledger, Agent Run, transcript-derived Output
Gate, harness measurement, or Python hook adapter. Runtime state is bounded to
hashed correction/turn state under
`${CLAUDE_CONFIG_DIR:-~/.claude}/harness/`; raw prompts and responses are not
persisted.

## Host registration

Generation does not edit `~/.claude/settings.json`. Start from
`settings.example.json`, replace `__ABSOLUTE_SKILL_SYSTEM_CLAUDE_HARNESS__`
with the absolute executable installed for that machine, and merge only its
`hooks` object into the existing settings file. Preserve all unrelated Claude
settings and hooks.

The template uses Claude's exec form (`"args": []`), so the binary is spawned
directly without Bash, Zsh, PowerShell, or another command wrapper.

Packaged artifacts:

- macOS arm64: `.claude/bin/skill-system-claude-harness`
- Windows amd64: `.claude/bin/skill-system-claude-harness.exe`
- Linux/WSL amd64: `.claude/bin/skill-system-claude-harness-linux-amd64`
- macOS overlay: `.claude/bin/skill-system-notify-overlay`

For Linux/WSL, install the Linux artifact at the absolute path used by the
settings template. Linux desktop notification uses `notify-send` when present
and otherwise skips without affecting the hook result.
