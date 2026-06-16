# Quality Gates

## 목적
근거 없는 요약 보고를 차단하고, 실행 가능한 개선 백로그 품질을 보장합니다.

## 입력
- `artifacts/findings.json`
- `artifacts/notes/unverified.tsv`
- `artifacts/exceptions.json` (선택)
- 정책: `references/policy-default.json`의 `quality_gates`

## 기본 프로파일 (`default`)
- `security_critical_max`: 0
- `security_high_max`: 1
- `expired_exceptions_max`: 0
- `unverified_warn_ratio`: 0.20
- `unverified_fail_ratio`: 0.35
- `require_top10_plan_fields`: true
- `max_test_findings_top10`: 2
- `max_missing_architecture_views`: 0
- `max_fallback_diagrams`: 1
- `max_diagrams_without_provenance`: 1
- `max_runtime_views_without_entrypoint`: 0

## 엄격 프로파일 (`strict`)
- `security_critical_max`: 0
- `security_high_max`: 0
- `expired_exceptions_max`: 0
- `unverified_warn_ratio`: 0.10
- `unverified_fail_ratio`: 0.20
- `require_top10_plan_fields`: true
- `max_test_findings_top10`: 1
- `max_missing_architecture_views`: 0
- `max_fallback_diagrams`: 0
- `max_diagrams_without_provenance`: 0
- `max_runtime_views_without_entrypoint`: 0

## 평가 규칙
1. 보안 게이트: `critical/high` 개수가 임계값 초과 시 FAIL
2. 예외 게이트: 만료 예외가 임계값 초과 시 FAIL
3. 계획 완전성 게이트: Top10 finding의 `action.title`, `improvement_plan.detail`, `scope.file` 누락 시 FAIL
4. 증거 게이트: `Unverified` 비율이 fail 임계값 초과 시 FAIL, warn 초과 시 WARN
5. 우선순위 편향 게이트: Top10의 test 카테고리 과점 시 FAIL
6. 아키텍처 뷰 게이트: context/container/component/runtime/deployment view 누락 시 FAIL
7. fallback 게이트: fallback 다이어그램이 임계값 초과 시 FAIL
8. provenance 게이트: 근거 refs 없는 다이어그램이 임계값 초과 시 FAIL
9. runtime linkage 게이트: entrypoint 미연결 runtime 시나리오가 임계값 초과 시 FAIL

## 권한 차단/실행 실패 처리
- 권한 문제로 수집이 차단되면 해당 트랙은 `Unverified`로 계산합니다.
- `Unverified` 비율이 임계값을 초과하면 FAIL 또는 WARN이 됩니다.
- 승인 후 재실행 전까지 PASS로 가정하지 않습니다.

## 출력 예시
```json
{
  "status": "FAIL",
  "reasons": [
    "top10_plan_fields_missing"
  ],
  "warnings": [],
  "metrics": {
    "security_critical": 0,
    "security_high": 0,
    "expired_exceptions": 0,
    "unverified_ratio": 0.18,
    "missing_top10_plan": 3,
    "test_findings_top10": 1,
    "missing_architecture_views": 0,
    "fallback_diagrams": 1,
    "diagrams_without_provenance": 0,
    "runtime_views_without_entrypoint": 0
  },
  "applied_thresholds": {
    "security_critical_max": 0,
    "security_high_max": 1,
    "expired_exceptions_max": 0,
    "unverified_warn_ratio": 0.2,
    "unverified_fail_ratio": 0.35,
    "require_top10_plan_fields": true,
    "max_test_findings_top10": 2,
    "max_missing_architecture_views": 0,
    "max_fallback_diagrams": 1,
    "max_diagrams_without_provenance": 1,
    "max_runtime_views_without_entrypoint": 0
  }
}
```
