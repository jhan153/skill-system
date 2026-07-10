릴리스 게이트는 **FAIL**입니다. 동일 invalid-amount 입력에서 legacy Qt는 `400/INVALID_AMOUNT`, candidate .NET은 `500/INTERNAL_ERROR`를 반환하는 high-severity 계약 차이가 확인되었습니다. 저장 0건은 동등했으며, valid-create와 cancel-order parity는 실행 증거 부족으로 `Unverified`입니다.

추가 실패 사유는 `Unverified` 비율 `0.933`과 fallback diagram 3건입니다.

생성 산출물:

- [통합 분석 보고서](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis/codebase-analysis-report.md:9)
- [Quality gate 결과](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis/artifacts/quality-gate-result.json)
- [Findings](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis/artifacts/findings.json)
- [Semantic contract 비교](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis/artifacts/manual/contract-comparisons.json)
- [Coverage ledger](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis/artifacts/manual/coverage-ledger.json)
- [전체 산출물 디렉터리](/private/tmp/skill-system-solar-910-20260710/codebase/out/codebase-analysis)

결과 상태: `agent-verified`. JSON 구조, evidence refs, scenario-entrypoint 연결, 보고서 10개 섹션을 검증했으며 추적 소스 변경은 없습니다.