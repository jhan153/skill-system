# Claude Harness Lifecycle Hooks

Claude owns a native Go dispatcher separate from the Codex dispatcher. Shared
packages provide the response guard, project-context resolution, redaction,
and OS notification implementation; the Claude
package owns Claude input normalization and output contracts.

Only `SessionStart`, `UserPromptSubmit`, `Stop`, and `Notification` are
registered. `prompt_id` is the primary turn key, with a hash-only session
sequence fallback for pre-2.1.196 clients. Stop reads
`last_assistant_message`, respects `stop_hook_active`, and never uses the
eventually-written transcript as current-turn evidence.

Native `Notification` payloads own approval, idle, elicitation, background
input, and background completion alerts. Stop does not infer those states.
Project context remains location-only.

The Claude runtime contains no hook-event ledger, Agent Run, Output Gate,
harness measurement, compact record, or Python adapter. Hook registration is a
host-owned settings merge described in `hooks/README.md`; generation never
edits live Claude settings or runtime state.
