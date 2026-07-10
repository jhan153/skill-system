workflow-validation

상태: `agent-verified`  
임시 `CODEX_HOME`: `/private/tmp/codex-home-9.1.1-forward.bX4cwa`

실행 명령:

```bash
mktemp -d /private/tmp/codex-home-9.1.1-forward.XXXXXX

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa python3 .codex/tools/hook_runtime.py record --event request_received --host codex --host-event forward_regression --support-level native --status pass --evidence '{"fixture":"9.1.1-forward"}' --run-id forward-regression-alpha-9.1.1

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa python3 .codex/tools/hook_runtime.py record --event request_received --host codex --host-event forward_regression --support-level native --status pass --evidence '{"fixture":"9.1.1-forward"}' --run-id forward-regression-beta-9.1.1

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa python3 .codex/tools/hook_runtime.py verify --ledger <각 ledger 경로>

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa python3 .codex/tools/analyze_harness_measurement.py --ledger-root /private/tmp/codex-home-9.1.1-forward.bX4cwa/harness/hook-ledgers

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa SKILL_SYSTEM_AGENT_OUTPUT_GATE=observe SKILL_SYSTEM_RECOVERY_GUARD=audit python3 .codex/tools/hook_runtime.py status

env -u SKILL_SYSTEM_HOOK_LEDGER CODEX_HOME=/private/tmp/codex-home-9.1.1-forward.bX4cwa SKILL_SYSTEM_AGENT_OUTPUT_GATE=observe SKILL_SYSTEM_RECOVERY_GUARD=off python3 .codex/tools/hook_runtime.py status
```

두 ledger 경로는 분리되었습니다.

- Alpha: `.../bc74d244d3f129b08a75251b38f9934634bfb6a8eb3328ff5abd3abda972e5c9/hook-events.jsonl`
- Beta: `.../8842d59ba567f8846529866011f9dcb1ee7a3af436749c5a6076531b827ae128/hook-events.jsonl`

결과:

- Alpha verify: `PASS: hook ledger entries=1 hash_chain=valid`
- Beta verify: `PASS: hook ledger entries=1 hash_chain=valid`
- Analyzer: `"ledger_count": 2`
- Audit status: `{"agent_output_gate_mode": "observe", "recovery_guard_mode": "audit"}`
- Off status: `{"agent_output_gate_mode": "observe", "recovery_guard_mode": "off"}`

저장소와 live home은 수정하지 않았습니다.