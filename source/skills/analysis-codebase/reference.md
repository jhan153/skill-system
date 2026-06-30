# Analysis Codebase Reference

## 1) Operating Principle
이 스킬은 단일 통합 보고서를 생성하는 코드베이스 분석 파이프라인입니다.
모든 결론은 아래 조건을 만족해야 합니다.
- quality attribute
- evidence refs
- decision summary
- improvement backlog row (`파인딩/액션/Severity/Priority/구체적인 개선 내용/관련 파일`)
- Unverified 명시

## 2) Artifact Layout
```text
<output-dir>/
  artifacts/
    index.json
    tools.json
    metrics.json
    finding-seed.json
    findings.json
    quality-gate-result.json
    policy-effective.json
    architecture/
      entrypoints.json
      context-model.json
      container-model.json
      component-model.json
      interface-model.json
      scenario-model.json
      deployment-model.json
      crosscutting-model.json
      decision-candidates.json
      architecture-summary.json
    git/
      churn_all.tsv
      churn_top.tsv
      recent_commits.tsv
      branches.tsv
    static/
      path-classification.tsv
      file_inventory.tsv
      complexity.json
      architecture.json
      class-hierarchy.json
      call-graph.json
      coverage-summary.json
      semgrep.json
      dependency-check-report.json
    dynamic/
      runtime.json
      trace-artifacts.json
    notes/
      unverified.tsv
  logs/
```

## 3) Priority Model
정책 파일의 `priority_model`이 단일 소스입니다.

기본 수식:
- $Priority=\sum(w_i\cdot signal_i)+category\_bias+rank\_boost$
- signal:
  - architecture: coupling + container/component 경계 신호
  - algorithm: complexity 기반
  - performance: churn+complexity 결합
  - refactor: churn+complexity+coupling 결합
  - test_guard: test 카테고리 회귀 방어 신호

## 4) Diagram Generation Rules
- HLD(상위 설계):
  - `architecture/context-model.json`, `container-model.json`, `deployment-model.json`, `crosscutting-model.json`, `decision-candidates.json`에서 생성
  - context/container/deployment/crosscutting/decision 뷰를 분리 생성
- LLD(상세 설계):
  - `architecture/scenario-model.json`의 대표 시나리오를 기준으로 복수 runtime sequence 생성
  - `architecture/component-model.json`, `interface-model.json`으로 component/interface view 생성
  - `static/class-hierarchy.json`과 소스 AST는 선택형 code-level 보강으로 사용
- 모델 추론:
  - interface/crosscutting은 import/reference/env-access 기반 신호를 우선 사용
  - entrypoint는 코드 패턴 우선, 필요 시 manifest script/Procfile/Makefile로 보강
  - manifest entrypoint는 command path를 기준으로 component/container에 연결
  - env/DSN(`DATABASE_URL`, `REDIS_URL`, `BROKER_URL`, `SENTRY_DSN` 등)도 외부 시스템 추론 근거로 사용
  - component 간 내부 path가 빈약하면 entrypoint에서 external interface까지 runtime scenario를 확장
  - deployment는 Docker/Compose/K8s/Terraform/GitHub Actions/Vercel/Render/Fly/Serverless/Skaffold 파일을 인식
  - deployment relation은 `defines/manages/runs/builds/deploys` 우선으로 생성
- Provenance:
  - 각 다이어그램은 생성에 사용한 `refs`를 가져야 함
  - call-graph fallback으로 만든 다이어그램은 `fallback=true`로 표시해야 함
- Mermaid 렌더 안정성:
  - `quadrantChart` 포인트 라벨은 반드시 무따옴표 정규화 라벨을 사용
  - 라벨은 파일 경로/함수 시그니처 원문 대신 도메인 주체명 우선
  - 시퀀스 메시지에 `xN`, `call/return` 축약 토큰 사용 금지

## 5) Static Analysis Visualization Rules
- `complexity.json` 기준으로 그래프 중심 표현을 사용합니다.
- 최소 포함 그래프:
  - Complexity 분포
  - Branch 분포
  - LOC 분포
  - LOC vs Complexity 분포(사분면)
  - Density 분포
- LOC vs Complexity는 표 대체 금지, Mermaid `quadrantChart`를 유지합니다.

## 6) Quality Gates
게이트는 `references/quality-gates.md`와 정책 `quality_gates`를 따릅니다.
- `require_top10_plan_fields`: 상위 10개 finding에 실행 가능한 계획 필드가 비어 있으면 FAIL
- `Unverified` 비율은 `warn/fail` 임계값 분리 평가
- Top10에서 테스트 카테고리 과점 여부 검사
- architecture 품질:
  - 필수 view(context/container/component/runtime/deployment) 누락 여부
  - fallback diagram 개수
  - provenance 없는 diagram 개수
  - entrypoint에 연결되지 않은 runtime scenario 개수

## 7) Permission-Blocked Policy
- 권한/보안 제한으로 도구가 실패하면 `PASS`로 가정하지 않습니다.
- 실패한 트랙의 결과는 `Unverified`로 남기고 이유를 기록합니다.
- 승인 후 동일 입력으로 재실행하여 재현성을 유지합니다.

## 8) Do Not
- 요약본/상세본을 분리해 복수 마크다운을 생성하지 않습니다.
- HLD를 단일 호출쌍으로 축약하지 않습니다.
- 개선 백로그에 템플릿 문구만 반복하지 않습니다.
- 권한 실패를 성공으로 가정하지 않습니다.
