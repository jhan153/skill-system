#!/usr/bin/env sh
# Optional example only. Do not install automatically.
# Wire this from a local Codex hook config if you want PreToolUse evidence.
# Set SKILL_SYSTEM_HOOK_LEDGER to choose the JSONL output path.

python3 .codex/tools/hook_runtime.py record \
  --event tool_preflight \
  --host codex \
  --host-event PreToolUse \
  --support-level native \
  --tool-id "${CODEX_TOOL_ID:-unknown}" \
  --status pass \
  --evidence "{\"argv\":\"${CODEX_TOOL_ARGS:-redacted}\"}"
