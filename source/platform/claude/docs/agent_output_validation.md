# Claude Agent Output Validation

Claude retains its opt-in transcript-derived contradiction gate. With `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict`, the Stop adapter blocks when the final assistant text claims `agent-verified` while the observed Claude transcript ends with a failed tool result and no later success.

The default remains observational and fail-open. This check does not create Codex Agent Run manifests, validate final-report artifacts, or grant repair authority. Its hook ledger and measurement support are Claude-owned under `.claude/tools`; the current Codex runtime has no corresponding Agent Run or output-gate runtime.
