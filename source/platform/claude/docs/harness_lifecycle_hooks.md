# Claude Harness Lifecycle Hooks

Claude hook behavior remains a separate, opt-in platform adapter. `hooks/claude_hook_adapter.py` records supported Claude lifecycle events through the Claude-owned `tools/hook_runtime.py` hash-chained ledger and fails open on adapter or storage errors.

The default is observational. The opt-in `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict` path reads the Claude transcript on Stop and blocks only an `agent-verified` claim contradicted by an unresolved failed tool result. This runtime is not installed or enabled by Codex generation, and it does not depend on Codex hook files.

Claude lifecycle records and optional measurement remain Claude platform assets. They do not authorize repair, bypass host approval, or mutate Memory, Knowledge, Wiki, plan, or project context stores.
