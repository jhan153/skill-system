# Codebase Analysis Report

- generated_at: 2026-07-10T18:41:46.569706+00:00
- repo_path: /private/tmp/skill-system-911-forward/cpp
- commit_range: Unverified
- mode: full
- policy_path: /Users/master/.codex/plugins/cache/skill-system-local/skill-system-dev/9.1.1/skills/analysis-codebase/references/policy-default.json

## 1. 실행 요약

| 항목 | 값 |
| --- | --- |
| 총 Finding | 0 |
| High/Critical | 0 |
| Static-only 확인 후보 | 0 |
| Quality Gate | FAIL |
| Unverified 항목 | 10 |
| 엔트리포인트 수 | 2 |
| 컨테이너/컴포넌트 | 2 / 2 |
| 대표 시나리오 수 | 2 |
| 콜그래프 노드/엣지 | 0 / 0 |
| C/C++ lizard 보강 | missing |

| Top10 품질속성 | 건수 |
| --- | --- |
| Unverified | Unverified |

- Gate 상태: **FAIL**
- Gate 실패 사유: unverified_ratio=1.0 > fail_threshold=0.35, fallback_diagrams=3 > 1, c_cpp_structural_evidence=not_evidenced
- Gate 경고: 없음

## 2. 범위/가정/비목표

- 범위
  - tracked files 기반 정적/동적/Git/보안 시그널을 결합해 단일 통합 마크다운 리포트를 생성
  - 증거를 context/container/component/interface/scenario/deployment 모델로 승격한 뒤 HLD/LLD 뷰를 파생 생성
  - finding 전수를 단일 개선 백로그 표로 출력
- 가정
  - 동적 워크로드/트레이스 입력이 제공되지 않으면 해당 구간은 Unverified로 유지
  - 정적 도구(coverage/semgrep/sca) 부재 시 실패 원인을 그대로 보고
  - 정책 가중치(priority_model)는 우선순위 점수 계산의 단일 기준
- 비목표
  - 자동 코드 수정/자동 병합
  - 근거 없는 일반론 다이어그램 생성
  - finding 축약 요약본 별도 생성

- 포함 파일 분류 수: 4
- 제외 파일 수: 0
| 카테고리 | 포함 파일 수 |
| --- | --- |
| unknown | 2 |
| code | 2 |

## 3. 코드베이스 개요

- 주요 모듈(파인딩 기준): Unverified
- 브랜치 수: 0
- 30일 초과 장기 브랜치: 0
- 엔트리포인트 수: 2
- 외부 인터페이스 수: 0
- 결정 후보 수: 0
- call graph 노드 수: 0
- call graph 엣지 수: 0
- 분석 카테고리: code, config, test

| 메트릭 | 현재 | 이전 | 추세 |
| --- | --- | --- | --- |
| Line Coverage(%) | None | Unverified | Unverified |
| Unverified Ratio | 1.0 | Unverified | Unverified |
| Avg Complexity Score | 1.5 | Unverified | Unverified |
| Fallback Diagrams | 3 | Unverified | Unverified |

| 모듈 | Finding 수 |
| --- | --- |
| Unverified | Unverified |

| 뷰 | 타입 | 생성 경로 | 근거 |
| --- | --- | --- | --- |
| Context View | context | primary | CMakeLists.txt, src/main.cpp |
| Container View | container | primary | CMakeLists.txt, include/app.hpp, src/main.cpp |
| Deployment View | deployment | fallback | Unverified |
| Component View | component | primary | CMakeLists.txt, include/app.hpp, src/main.cpp |
| main main | runtime | fallback | src/main.cpp |
| cmake skill-system-cpp | runtime | fallback | CMakeLists.txt |

## 4. 상위 설계 (HLD)

### Context View
```mermaid
flowchart LR
  C1(["Operator"])
  C2["CLI Container"]
  C1 -->|main main| C2
  C1 -->|cmake skill-system-cpp| C2
```

- provenance: CMakeLists.txt, src/main.cpp
- generation: primary

### Container View
```mermaid
flowchart LR
  T1["CLI Container / CPP"]
  T2["Core Library / HPP"]
```

- provenance: CMakeLists.txt, include/app.hpp, src/main.cpp
- generation: primary

### Deployment View
> _Unverified — Deployment Unverified: 다이어그램 생성에 필요한 구조 evidence가 부족하여 다이어그램을 생략합니다._

- provenance: Unverified
- generation: fallback

### Crosscutting Concepts
| 개념 | 증거 수 | 대표 근거 |
| --- | --- | --- |
| Unverified | 0 | Unverified |

### Architecture Decision Candidates
| 결정 후보 | 유형 | 상태 | 요약 | 확인 방법 | 대표 근거 |
| --- | --- | --- | --- | --- | --- |
| Unverified | Unverified | Unverified | Unverified | Unverified | Unverified |

### 결합도 상위 파일(보조 근거)

| 파일 | fan_in | fan_out | coupling | category |
| --- | --- | --- | --- | --- |
| src/main.cpp | 0 | 0 | 0 | code |
| include/app.hpp | 0 | 0 | 0 | code |

## 5. 상세 설계 (LLD)

### 대표 런타임 시나리오
#### main main
```mermaid
sequenceDiagram
participant R1 as "Src"
R1->>R1: main main 처리
```
- entrypoint_id: cli-startup-src-main-cpp-main-main
- source: static-entrypoint
- provenance: src/main.cpp
- generation: fallback

#### cmake skill-system-cpp
```mermaid
sequenceDiagram
participant R1 as "Src"
R1->>R1: cmake skill-system-cpp 처리
```
- entrypoint_id: cli-startup-cmakelists-txt-cmake-skill-system-cpp
- source: static-entrypoint
- provenance: CMakeLists.txt
- generation: fallback

### Component View
```mermaid
flowchart LR
  K1["Src / Cli"]
  K2["Include / Core"]
```

- provenance: CMakeLists.txt, include/app.hpp, src/main.cpp
- generation: primary

### Interface Contracts
| Source Component | Kind | Target | Evidence |
| --- | --- | --- | --- |
| Unverified | Unverified | Unverified | Unverified |

### Code-Level Detail (Optional)
```mermaid
classDiagram
class AppState["AppState"]
```

### 클래스 근거 테이블
| Class | File | Parents | Children | Methods |
| --- | --- | --- | --- | --- |
| AppState | include/app.hpp | - | - | 0 |

### 클래스 함수 명세
| Class | File | Method Signatures |
| --- | --- | --- |
| AppState | include/app.hpp | Unverified(parse-failed) |

## 6. 정적 분석 결과

- 복잡도 측정식: $Complexity(file)=1+BranchCount$
- 결합도 측정식: $Coupling(file)=FanIn+FanOut$
- 우선순위 추정식: $Priority=\sum(w_i\cdot signal_i)+category\_bias+rank\_boost$

- files_analyzed: 2
- avg_complexity_score: 1.5
- line_coverage(%): None
- branch_coverage(%): None
- c_cpp_lizard_status: missing

### 복잡도 상위 파일 분포
```mermaid
xychart-beta
    title "Top Complexity (Branch+1)"
    x-axis ["main.cpp", "app.hpp"]
    y-axis "Complexity" 0 --> 2.2
    bar [2.0, 1.0]
```

### 브랜치 수 상위 파일 분포
```mermaid
xychart-beta
    title "Top Branch Count"
    x-axis ["main.cpp", "app.hpp"]
    y-axis "Branch Count" 0 --> 1.1
    bar [1.0, 0.0]
```

### LOC 상위 파일 분포
```mermaid
xychart-beta
    title "Top LOC"
    x-axis ["main.cpp", "app.hpp"]
    y-axis "Lines of Code" 0 --> 12.1
    bar [11.0, 7.0]
```

### LOC 대비 복잡도 사분면
```mermaid
quadrantChart
    title "LOC-Complexity 분포"
    x-axis "LOC 낮음" --> "LOC 높음"
    y-axis "Complexity 낮음" --> "Complexity 높음"
    quadrant-1 "고LOC-고복잡도"
    quadrant-2 "저LOC-고복잡도"
    quadrant-3 "저LOC-저복잡도"
    quadrant-4 "고LOC-저복잡도"
    main_cpp: [1, 1]
    app_hpp: [0.636, 0.5]
```

### 밀도 상위 파일 분포
```mermaid
xychart-beta
    title "Top Complexity Density"
    x-axis ["main.cpp", "app.hpp"]
    y-axis "Density" 0 --> 0.2
    bar [0.182, 0.143]
```

### 정적 분석 핵심 수치
| 지표 | 값 |
| --- | --- |
| 최대 복잡도 파일 | src/main.cpp |
| 평균 복잡도 점수 | 1.5 |
| 분석 파일 수 | 2 |
| Coverage(Line/Branch) | None / None |
| C/C++ lizard 보강 | missing (no artifact) |

## 7. 동적 분석 결과

- workload_status: Unverified
- workload_message: CBIR_WORKLOAD_CMD not set
- workload_exit_code: None
- trace_backed_scenarios: 0
- static_fallback_scenarios: 2
- tools_available: bpftrace=False, java=True, otelcol=False, perf=False, pprof=False, valgrind=False
- latency_percentiles: Unverified
- 참고: 동적 워크로드/트레이스 미제공 상태이므로 성능 결론은 Unverified입니다.

## 8. 수동 리뷰 결과

목적: 자동 분석으로 확정하기 어려운 구조/정확성/보안 판단을 사람이 검증하기 위한 근거 섹션입니다.

| 영역 | 수동 검토 포인트 | 활용 목적 |
| --- | --- | --- |
| Architecture | 컨테이너/컴포넌트 경계와 fallback 뷰 의존 여부 | architecture model + provenance 표를 기준으로 경계 타당성 검토 |
| Algorithm | 핫패스 분기/루프 복잡도와 입력 규모 증가시 기울기 | complexity + churn 상위 파일 중심으로 개선 우선순위 확정 |
| Runtime | 대표 시나리오가 실제 entrypoint/trace와 연결되는지 | trace-backed 여부와 runtime entrypoint linkage 확인 |
| Semantic Comparison | 동일 capability/input의 output, state, error, side effect 차이에 paired evidence가 있는지 | implementation vocabulary를 제외하고 material delta 또는 Unverified 검증 과제만 확정 |

## 9. 우선순위 개선 백로그

| 파인딩 | 액션 | Severity | Priority | 구체적인 개선 내용 | 관련 파일 |
| --- | --- | --- | --- | --- | --- |
| Unverified | Unverified | Unverified | Unverified | Unverified | Unverified |

## 10. 부록

### Artifact Index
```json
{
  "architecture.architecture-summary.json": "artifacts/architecture/architecture-summary.json",
  "architecture.component-model.json": "artifacts/architecture/component-model.json",
  "architecture.container-model.json": "artifacts/architecture/container-model.json",
  "architecture.context-model.json": "artifacts/architecture/context-model.json",
  "architecture.crosscutting-model.json": "artifacts/architecture/crosscutting-model.json",
  "architecture.decision-candidates.json": "artifacts/architecture/decision-candidates.json",
  "architecture.deployment-model.json": "artifacts/architecture/deployment-model.json",
  "architecture.entrypoints.json": "artifacts/architecture/entrypoints.json",
  "architecture.interface-model.json": "artifacts/architecture/interface-model.json",
  "architecture.scenario-model.json": "artifacts/architecture/scenario-model.json",
  "dynamic.runtime.json": "artifacts/dynamic/runtime.json",
  "finding-seed.json": "artifacts/finding-seed.json",
  "git.branches.tsv": "artifacts/git/branches.tsv",
  "git.recent_commits.tsv": "artifacts/git/recent_commits.tsv",
  "index.json": "artifacts/index.json",
  "metrics.json": "artifacts/metrics.json",
  "notes.unverified.tsv": "artifacts/notes/unverified.tsv",
  "policy-effective.json": "artifacts/policy-effective.json",
  "static.architecture.json": "artifacts/static/architecture.json",
  "static.call-graph.json": "artifacts/static/call-graph.json",
  "static.class-hierarchy.json": "artifacts/static/class-hierarchy.json",
  "static.complexity.json": "artifacts/static/complexity.json",
  "static.coverage-summary.json": "artifacts/static/coverage-summary.json",
  "static.file_inventory.tsv": "artifacts/static/file_inventory.tsv",
  "static.path-classification.tsv": "artifacts/static/path-classification.tsv",
  "tools.json": "artifacts/tools.json",
  "tools.tsv": "artifacts/tools.tsv"
}
```

### Policy Snapshot
```json
{
  "weights": {
    "architecture": 0.35,
    "algorithm": 0.25,
    "performance": 0.2,
    "refactor": 0.15,
    "test_guard": 0.05
  },
  "category_bias": {
    "code": 0.8,
    "config": 0.4,
    "test": -1.1,
    "asset": -2.5,
    "doc": -2.5,
    "unknown": 0.0
  },
  "severity_thresholds": {
    "critical": 4.6,
    "high": 3.8,
    "medium": 2.9,
    "low": 2.0
  },
  "profile_thresholds": {
    "architecture": 3.6,
    "algorithm": 3.3,
    "performance": 3.2,
    "refactor": 2.4
  },
  "due_days_by_severity": {
    "critical": 14,
    "high": 30,
    "medium": 60,
    "low": 90,
    "info": 120
  }
}
```

### Architecture Summary
```json
{
  "status": "ok",
  "counts": {
    "entrypoints": 2,
    "containers": 2,
    "components": 2,
    "interfaces": 0,
    "scenarios": 2,
    "deployment_nodes": 0,
    "crosscutting": 0,
    "decision_candidates": 0
  },
  "warnings": [
    "trace-backed scenario 없음",
    "deployment evidence 없음"
  ]
}
```

### View Provenance
| 뷰 | 타입 | 생성 경로 | 근거 |
| --- | --- | --- | --- |
| Context View | context | primary | CMakeLists.txt, src/main.cpp |
| Container View | container | primary | CMakeLists.txt, include/app.hpp, src/main.cpp |
| Deployment View | deployment | fallback | Unverified |
| Component View | component | primary | CMakeLists.txt, include/app.hpp, src/main.cpp |
| main main | runtime | fallback | src/main.cpp |
| cmake skill-system-cpp | runtime | fallback | CMakeLists.txt |

### Unverified
- git.commit_range: Unable to resolve commit range automatically
- git.churn: Commit range unresolved
- git.recent_commits: Failed to collect recent commits
- static.coverage: Coverage file not found (coverage.xml or coverage/lcov.info)
- static.semgrep: semgrep command not found
- static.sca: dependency-check.sh not found
- dynamic.workload: CBIR_WORKLOAD_CMD not set
- dynamic.trace: CBIR_TRACE_FILE not provided
- dynamic.latency: CBIR_LATENCY_CSV not provided
- architecture.c_cpp_semantic_depth: Not evidenced: C/C++ symbol, class, and call-graph structure requires a compilation-aware extractor; include/build hints are file-level only.