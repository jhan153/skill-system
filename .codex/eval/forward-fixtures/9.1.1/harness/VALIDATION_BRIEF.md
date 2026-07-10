# Hook ledger and mode validation

- Use a new temporary `CODEX_HOME`; never write to the live user home.
- Record one event for each of two distinct explicit run IDs without an explicit ledger path.
- Confirm two hashed per-run `hook-events.jsonl` files, each with a valid single-run chain.
- Run the ledger-family measurement analyzer against the temporary root and report the discovered ledger count.
- Report `hook_runtime.py status` once with Recovery Guard audit and once with Recovery Guard off while the output gate remains non-strict.
- Keep `agent_output_gate_mode` and `recovery_guard_mode` as independent fields.
