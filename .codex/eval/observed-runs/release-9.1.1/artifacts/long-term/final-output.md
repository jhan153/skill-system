skill-system-core:plan-long-term-package

- 실행 순서: `--canonical-only` → 동일 인자의 `--derived-only` → default validator
- 산출물: canonical 12개, derived 7개, 총 19개 / cap 20
- Modifier delta:
  - parity `+1/+1`
  - rollback `+1/+1`
  - data `+1/+1`
  - security `+1/+1`
  - handoff `+1/+2`
  - legacy-parity `absorbed-by-archetype (0/0)`
- Ingest: 0개, ingest summary 미생성
- Validator: `python3 .../validate_phase_plan_package.py --root . --package PaymentEngineReplacement --slug payment-engine-replacement --dated-plan docs/plan/2026-07-10-payment-engine-replacement.md --archetype migration-modernization --modifiers strict-behavior-parity,rollback-required,data-sensitive,security-sensitive,cross-session-handoff,legacy-parity`
- Validator 결과: `VALIDATION_OK`, exit `0`
- 상태: `planning-only`; 런타임 검증 또는 구현 완료를 의미하지 않습니다.
- Canonical plan: [2026-07-10-payment-engine-replacement.md](/private/tmp/skill-system-911-forward/long-term-911c/docs/plan/2026-07-10-payment-engine-replacement.md)
- Package root: [README.md](/private/tmp/skill-system-911-forward/long-term-911c/docs/plan/PaymentEngineReplacement/README.md)

결과 상태: `agent-verified` — staged scaffold와 default validator 범위에 한정됩니다.