---
name: analysis-codebase
description: "Repo-wide integrated analysis report from static/dynamic/security/git evidence with design diagrams, an actionable finding backlog, and explicit Unverified handling. Only when the user explicitly wants a codebase-wide report (정적분석/런타임분석/메트릭/Git 변화/설계 문서화 리포트 등)."
---

# Analysis Codebase

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - repo-wide integrated report, 코드베이스 분석 리포트, 정적/동적/보안/Git evidence report, architecture quality report
- use_when:
  - the user explicitly requests a codebase-wide report artifact or architecture/metrics/security/git-evidence report.
- do_not_use_when:
  - the user asks for a single bug diagnosis, short code review, one-file inspection, or algorithm recommendation.
  - `코드 리뷰 리포트` is ambiguous and the user does not ask for a repo-wide report artifact.
- expected_inputs:
  - repo root
  - report scope
  - requested evidence types and output path when relevant
- expected_outputs:
  - integrated markdown report, architecture models, findings backlog, quality gate result
- context_targets:
  must_read:
    - current explicit report request
    - repo root and policy defaults
    - report scripts and schemas
  read_if_needed:
    - tracked file list
    - static/dynamic/security/git evidence outputs
    - prior reports for comparison
  do_not_load_by_default:
    - unrelated memory bank
    - phase package templates
    - single-bug specialist workflows
- risk_profile:
  reads:
    - READ_CODEBASE high
  writes:
    - WRITE_LOCAL_FS high for report artifacts and architecture JSON
  tools:
    - CALL_PROCESS high for collection and report scripts
  sensitive_resources:
    - NETWORK normally no; CREDENTIALS must not access
- entry_scene:
  - PREPARE

## Goal
- 요약본/상세본 분리 없이 단일 통합 마크다운 리포트를 생성합니다.
- 증거를 공통 아키텍처 모델로 승격한 뒤 HLD/LLD 뷰를 파생 생성합니다.
- 모든 finding은 실행 가능한 개선 백로그 항목으로 연결합니다.
- 증거 부족 항목은 반드시 `Unverified`로 명시합니다.

## Related Skills
- `workflow-rigor`: 수집/생성 단계가 중간 이상 위험도를 가지거나 실행 통제가 필요할 때 evidence depth, validation, review rigor를 보강합니다.
- `report-qualitative`: 사용자가 형식적인 handoff나 감사형 요약을 원할 때 채팅 응답 형식을 정리합니다. 생성되는 리포트 파일의 장/섹션 계약은 이 스킬이 계속 소유합니다.
- `report-critical`: 생성된 리포트, `findings.json`, `quality-gate-result.json`에 대해 최종 QA gate가 필요할 때 후행 검토를 담당합니다.
- `report-diff`: 사용자가 실제 변경 줄 비교를 원할 때만 후처리 뷰로 사용합니다. 통합 리포트 자체를 대체하지 않습니다.

## Trigger
- `코드베이스 분석`
- `코드베이스 분석 리포트`
- `정적분석 리포트`
- `런타임분석 리포트`
- `아키텍처 품질`
- `코드 리뷰 리포트`
- `메트릭 리포트`
- `Git 변화 분석 리포트`
- `설계 문서 자동화`

## When Not To Use
- 단일 버그의 현재 원인만 찾는 요청
- 특정 증상 하나에 대한 재현/원인 분석 요청
- 알고리즘 추천이나 접근 비교가 핵심인 요청
- 사용자가 리포트 산출물보다 짧은 진단이나 한두 개의 finding만 원하는 요청
- 모호한 `코드 리뷰 리포트` 요청 중 repo-wide report artifact 의도가 확인되지 않은 요청

## Cross-Skill Resolution
- 이 스킬은 리포트 산출물 스키마와 장 순서의 source of truth입니다.
- `report-qualitative`가 함께 활성화되어도 리포트 파일 구조는 바꾸지 않고, 사용자에게 보여 주는 요약 응답만 정리합니다.
- `workflow-rigor`가 함께 활성화되면 실행 모드, 검증, 리뷰 강도는 그 스킬을 따르되 리포트 내용 계약은 이 스킬을 유지합니다.
- `report-critical`가 요청되면 리포트 생성 후 후행 QA gate로 실행합니다.
- 사용자가 diff 표현을 요구한 경우에만 `report-diff`를 추가로 사용하며, integrated report findings를 prose-only 요약으로 축소하지 않습니다.
- 현재 고장 원인, 반복 버그, 알고리즘 선택 같은 point diagnosis/recommendation 요청은 이 스킬의 우선 범위가 아니며, 그런 요청은 `analysis-router` 쪽을 우선합니다.

## Mandatory Workflow
1. `collect.sh`로 tracked files를 분류하고 증거 아티팩트를 수집합니다.
2. 정적/동적/Git/보안 증거를 `architecture/*.json` 모델(`entrypoints/context/container/component/interface/scenario/deployment/crosscutting/decision`)로 승격합니다.
3. `report.py`가 모델 기반으로 우선순위/게이트/개선 백로그와 HLD/LLD 뷰를 계산합니다.
4. 단일 마크다운 리포트와 `findings.json`, `quality-gate-result.json`를 함께 출력합니다.

## Architecture Model Contract
- 내부 구조는 `evidence -> architecture model -> report views` 순서여야 합니다.
- `call-graph.json`, `class-hierarchy.json`은 보조 증거이며 HLD/LLD의 단일 소스가 아닙니다.
- 기본 정책은 repo-wide 수집을 허용하고, binary/resource 확장자는 `exclude_extensions`로 제외합니다.
- C/C++ repo에서는 regex 기반 `main()`/`#include`/CMake `add_executable()` 신호와 optional `lizard` 산출물을 보조 근거로 사용합니다.
- C/C++ `lizard` 산출물은 함수/CCN 보강 근거이며, clang AST나 `compile_commands.json` 기반 semantic graph를 대체하지 않습니다.
- interface/crosscutting은 단순 text grep보다 import/reference/env-access 신호를 우선 사용합니다.
- entrypoint는 코드 엔트리포인트 우선, 필요 시 manifest(`package.json`, `pyproject.toml`, `Procfile`, `Makefile`)에서 보강합니다.
- manifest entrypoint는 command path를 이용해 실제 컴포넌트/API/Worker 컨테이너에 연결합니다.
- 외부 시스템은 `DATABASE_URL`, `REDIS_URL`, `BROKER_URL`, `SENTRY_DSN` 같은 env/DSN 신호도 사용합니다.
- 시나리오는 컴포넌트 간 내부 경로가 약할 때도 entrypoint에서 external interface까지 확장해 대표 흐름을 만듭니다.
- deployment view는 `defines/manages/runs/builds/deploys` 관계를 우선 복원합니다.
- 최소 모델 아티팩트:
  - `architecture/entrypoints.json`
  - `architecture/context-model.json`
  - `architecture/container-model.json`
  - `architecture/component-model.json`
  - `architecture/interface-model.json`
  - `architecture/scenario-model.json`
  - `architecture/deployment-model.json`
  - `architecture/crosscutting-model.json`
  - `architecture/decision-candidates.json`

## Deliverables Contract
리포트 섹션 순서는 반드시 아래 순서를 따릅니다.
1. 실행 요약
2. 범위/가정/비목표
3. 코드베이스 개요
4. 상위 설계 (HLD)
5. 상세 설계 (LLD)
6. 정적 분석 결과
7. 동적 분석 결과
8. 수동 리뷰 결과
9. 우선순위 개선 백로그
10. 부록

## Section Rules
- 4장(HLD): `Context View + Container View + Deployment View + Crosscutting Concepts + Architecture Decisions` 필수.
- 5장(LLD): `대표 런타임 시나리오(복수) + Component View + Interface Contracts` 필수.
- 5장 코드 레벨: 클래스 다이어그램/함수 명세는 선택형 보강이며, 복잡한 핵심 컴포넌트가 있을 때 우선 생성합니다.
- 6장(정적): 표 위주가 아니라 그래프(LOC/Complexity/Branches/Density 축) 중심으로 작성.
- 9장(백로그): 아래 컬럼을 반드시 사용.
  - `파인딩`, `액션`, `Severity`, `Priority`, `구체적인 개선 내용`, `관련 파일`
- 모든 다이어그램은 provenance를 가져야 하며, fallback 생성 여부를 드러내야 합니다.

## Diagram Rendering Cautions
다이어그램 라벨은 파일 경로(`*.py`)를 그대로 노출하지 말고 도메인 주체명으로 표시합니다.
메시지는 `x10`, `call`, `return` 같은 축약 표기 대신 의미 있는 동작 문구를 사용합니다.

### QuadrantChart Rule
- 헤더는 `title`, `x-axis`, `y-axis`, `quadrant-1..4`의 7줄 패턴을 유지합니다.
- 데이터 포인트는 무따옴표 라벨을 사용합니다: `label: [x, y]`
- 데이터 라벨은 `^[A-Za-z_][A-Za-z0-9_]*$`로 정규화합니다. (비허용 문자는 `_`, 연속 `_` 축약, 숫자 시작 시 `item_` 접두사)
- 좌표는 `0..1` 범위 숫자를 사용합니다. 예: `[1, 1]`, `[0.608, 0.816]`

### Flowchart Rule
- 노드 라벨은 도메인 주체명으로 작성합니다.
- 엣지 라벨은 의미+수량 중심의 짧은 문구로 작성합니다.
- 엣지 라벨은 괄호 `()` 없이 작성합니다.

### SequenceDiagram Rule
- 참여자 라벨은 도메인 주체명으로 작성합니다.
- 메시지는 동작 의미가 드러나는 문장형으로 작성합니다.

## CLI
### Path Contract
Prefer `$CODEX_HOME` when set. If unset, fall back to `$HOME/.codex`. This setup may run under multiple host-specific homes; reusable examples must not hardcode any single home path. If neither `$CODEX_HOME` nor `$HOME/.codex` resolves to the skill root, require the runtime or user to provide `SKILL_ROOT`.

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_ROOT="${SKILL_ROOT:-$CODEX_HOME/skills/analysis-codebase}"
test -d "$SKILL_ROOT" || { echo "Set CODEX_HOME or SKILL_ROOT to analysis-codebase" >&2; exit 1; }
```

### Collector
```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_ROOT="${SKILL_ROOT:-$CODEX_HOME/skills/analysis-codebase}"
"$SKILL_ROOT/scripts/collect.sh" \
  --repo-path /abs/repo \
  --commit-range auto \
  --mode full \
  --output-dir /abs/output \
  --top-n 120 \
  --policy "$SKILL_ROOT/references/policy-default.json"
```

### Reporter
```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_ROOT="${SKILL_ROOT:-$CODEX_HOME/skills/analysis-codebase}"
python3 "$SKILL_ROOT/scripts/report.py" \
  --input-dir /abs/output \
  --output /abs/repo/docs/report/codebase-analysis-report.md \
  --risk-model default \
  --policy "$SKILL_ROOT/references/policy-default.json"
```

## Evidence Rules
- 모든 finding은 `evidence_refs`를 가져야 합니다.
- 증거가 부족하면 `evidence_grade`를 낮추고 `Unverified`를 유지합니다.
- 권한/실행 제한으로 증거 수집 실패 시 실패 이유를 `notes/unverified.tsv`에 남깁니다.
- 시나리오는 가능한 경우 trace/root span과 연결하고, 없으면 entrypoint 기반 대표 흐름으로 생성합니다.
- deployment view는 IaC/compose/k8s/workflow 파일이 없으면 `Unverified`로 유지합니다.

## Permission Handling
- 수집/실행 단계에서 권한 거부가 발생하면 결과를 추정하지 않습니다.
- 거부 원인을 `Unverified`로 남기고, 승인 후 동일 명령으로 재실행합니다.

## Resource and Risk Boundary
- Reads: repo tracked files, build/test metadata, static/dynamic/security/git evidence, and report policy.
- Writes: local report artifacts, architecture JSON, findings JSON, and quality-gate outputs only.
- Tool/process calls: collector, report generator, optional safe analysis commands; each needs a clear purpose.
- Network access: normally no; do not fetch external data unless explicitly requested and bounded.
- Credential access: must not access secrets, tokens, private keys, or credential files.
- Generated artifacts: high; keep outputs in the requested report directory.
- Destructive actions: out of scope.
- Required checkpoints: explicit repo-wide artifact intent, output directory, evidence scope, no credential access, validation status for generated report.

## Recovery and Context Expansion
- If repo structure is unclear, start with tracked file list and repo source outline.
- If a collector step fails, read the exact failure output and mark missing evidence `Unverified`.
- If architecture boundary is unclear, inspect only entrypoints/manifests and relevant module docs before broader scans.
- If the user asks a point-diagnosis question, return to scheduling and use `analysis-router`.
- If validation fails, read the failing artifact and command output before rerunning broad collection.
- Never recover by loading all memory, all repo docs, or all unrelated reports at once.

## References
- Core rules: [`reference.md`](reference.md)
- Quality gates: [`references/quality-gates.md`](references/quality-gates.md)
- Policy: [`references/policy-default.json`](references/policy-default.json)
- Schemas: [`references/schemas.md`](references/schemas.md)
- Manual review: [`references/review-checklists.md`](references/review-checklists.md)
- CI guide: [`docs/document.md`](docs/document.md)

## Anti-Patterns
- HLD를 import fan-in/fan-out 요약만으로 대체하는 보고
- LLD를 하드코딩된 anchor 함수 세트에만 의존하는 보고
- 대표 시나리오를 entrypoint/trace와 연결하지 못한 채 호출쌍만 나열하는 보고
- 정적 분석을 표만으로 표현하고 그래프를 생략하는 보고
- 개선 백로그에 실행 가능한 구체 작업 없이 템플릿 문구만 반복하는 보고

## Known Limits
- Static architecture models can miss runtime behavior, generated-code semantics, and deployment conditions.
- Dynamic, security, or Git evidence remains `Unverified` when tools or permissions are unavailable.
- C/C++ support is shallow unless external tools are available: default collection detects files, `main()`, `#include`, CMake executable declarations, and optional `lizard` complexity, but does not build a clang semantic call graph.
- Repo-wide collection requires explicit artifact intent, output scope, and side-effect risk gates.
- If `$CODEX_HOME` and `$HOME/.codex` do not resolve the skill root, require `SKILL_ROOT` instead of assuming an empty path.
