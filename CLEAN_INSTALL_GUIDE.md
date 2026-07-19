# Skill System 클린 설치 가이드

> 이 문서는 **버전과 무관한 설치 절차 계약**입니다. 릴리스 버전, 태그,
> 커밋 해시, 스킬 수를 이 문서에 기록하지 않습니다. 사용자가 선택한
> 체크아웃이 설치할 릴리스의 유일한 기준입니다.

## 1. 목적

클린 설치는 선택된 Skill System 체크아웃의 두 산출물을 현재 컴퓨터에
반영하는 작업입니다.

1. 마켓플레이스 플러그인은 공식 플러그인 명령으로 설치합니다.
2. 플러그인에 포함되지 않는 플랫폼별 런타임 보조 파일은 보호 대상과
   실행 상태를 보존하면서 정확히 동기화합니다.

버전이 바뀌어도 이 절차는 같습니다. 설치 구조나 공식 CLI가 달라질 때만
이 문서를 수정합니다.

## 2. 설치 요청에서 확정할 입력

작업 전에 다음 네 가지를 확정합니다.

- **소스 루트**: 안정적인 Skill System 저장소의 절대 경로
- **선택 릴리스**: 사용자가 지정한 태그 또는 커밋, 혹은 명시적으로
  선택한 현재 체크아웃
- **대상 플랫폼**: Codex, Claude Code 또는 둘 다
- **플러그인 구성**: 전체 마켓플레이스 항목 또는 사용자가 지정한 일부

사용자가 “현재 체크아웃을 설치”라고 했다면 현재 커밋을 사용합니다.
특정 태그나 커밋을 지정했다면 그 값만 사용합니다. 아무 기준도 주지 않은
경우 한 번만 물어봅니다.

다음 값으로 릴리스를 추측하지 않습니다.

- 이 문서에 과거에 적혀 있던 버전
- 원격의 최신 태그
- 원격 저장소의 현재 `main` 브랜치
- 홈에 이미 설치된 플러그인 버전
- 다른 세션이나 다른 프로젝트의 체크아웃

## 3. 절대 금지 사항

클린 설치를 수행하기 위해 새 설치 프로그램을 만들지 않습니다.

- `install_runtime.py` 같은 Python 설치 프로그램 작성 금지
- 임시 셸 설치 프로그램, JetShell 래퍼, 중간 배포 도구 작성 금지
- 기존 문서를 복제한 버전별 설치 가이드 작성 금지
- 플러그인 캐시 직접 복사·수정·삭제 금지
- `.codex/` 또는 `.claude/` 전체 디렉터리 복사 금지
- `rsync --delete`처럼 상태 파일까지 지울 수 있는 동기화 금지
- 설치 중 정본 `source/` 또는 생성 대상 수정 금지
- 실패한 소스 검증을 설치 과정에서 임의로 고치거나 우회 금지
- 기존 체크아웃에 `reset --hard`, `clean`, `stash` 실행 금지
- 다른 Codex/Claude 세션 열기, 중지, 조작 금지
- 내부 시나리오, A/B 평가나 성숙도 점수를 설치 완료 조건으로 사용 금지

`source/tools/generate_targets.py`와
`source/tools/check_generated_targets.py`는 저장소의 기존 생성·검증
도구이며 설치 프로그램이 아닙니다. 클린 설치용 새 도구를 만드는 근거로
사용하지 않습니다.

## 4. 승인과 명령 실행 원칙

사용자가 이 컴퓨터에 클린 설치를 명시적으로 요청했다면, 아래 경계 안의
백업·런타임 동기화·공식 플러그인 설치를 하나의 승인된 작업 단위로
취급합니다. 대화로 파일마다 승인을 다시 요청하지 않습니다.

호스트가 실제 권한 승인을 요구할 수는 있습니다. 이때도 이미 허용된
실행 파일이 식별되도록 명령을 직접 실행합니다.

```text
codex plugin ...
claude plugin ...
git ...
python3 source/tools/check_generated_targets.py ...
rsync ...
```

파이프라인, 리디렉션, 글로브 같은 실제 셸 문법이 필요 없는 명령을
`zsh -lc`, `bash -lc`, JetShell 또는 다른 래퍼로 감싸지 않습니다.
예상하지 못한 호스트 정책 충돌이 여러 개면 하나로 모아 한 번만
보고하고 결정받습니다.

## 5. 릴리스 생성 검증과 설치 대상 확인의 분리

### 릴리스 생성 환경에서만 수행하는 재생성 검증

정본과 생성물의 재생성 일치는 릴리스 커밋과 태그를 만들기 전에 빌드 가능한
maintainer 환경에서 확인합니다.

```bash
python3 source/tools/check_generated_targets.py --target runtime --baseline
python3 source/tools/check_generated_targets.py --target plugins --baseline
```

runtime 검사는 Go와 플랫폼 빌드 도구를 사용할 수 있는 릴리스 환경의
책임입니다. 배포된 런타임에는 재현 가능한 실행 파일이 이미 포함되어
있으므로 설치 대상 컴퓨터가 정본을 다시 빌드하거나 Go·Swift 도구를
설치할 필요가 없습니다. 설치 작업은 이 검사를 대신 수행하거나 실패한
릴리스 소스를 수리할 권한을 포함하지 않습니다.

### 설치 대상에서 수행하는 체크아웃 무결성 확인

홈 경로를 쓰기 전에 선택된 체크아웃에서 다음을 확인합니다.

1. 저장소 루트와 현재 커밋을 읽습니다.
2. 선택한 태그 또는 커밋이 정확히 `HEAD`를 가리키는지 확인합니다.
3. `.codex/`, `.claude/`, `plugins/`, `source/` 아래의 tracked 또는
   untracked 변경을 확인하고, 명시적으로 선택되지 않은 변경이 있으면 중단합니다.
4. `HEAD`의 tree object ID를 설치 기록에 남깁니다. Git tree는 선택한
   커밋에 포함된 tracked 배포 파일의 content-addressed 식별자이며,
   게시자 신원이나 서명을 대신하지는 않습니다.
5. 빌드 도구가 필요 없는 bundle identity와 core 검사를 통과시킵니다.

저장소 루트에서 직접 실행합니다.

```bash
git rev-parse --show-toplevel
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short --untracked-files=all -- .codex .claude plugins source
python3 source/platform/codex/tools/check_release_identity.py --root .
python3 source/platform/codex/tools/verify_bundle.py --root . --profile core --format text
```

태그를 선택했다면 annotated/lightweight 여부를 기록하고 다음 두 결과의 commit
ID가 `HEAD`와 같은지 확인합니다.

```bash
git cat-file -t <selected-tag>
git rev-parse '<selected-tag>^{}'
```

태그나 커밋이 정확히 일치하고 배포 경로가 변경되지 않은 경우, 설치 대상에서
`check_generated_targets.py`를 다시 실행하지 않습니다. 설치 전 검증은 선택된
Git tree의 무결성과 번들 내부 일관성을 확인하며, 릴리스 생성 시점의 재현성
검증을 새로 증명하지 않습니다.

추가로 다음을 읽어 확인합니다.

- `.agents/plugins/marketplace.json`
- `plugins/.claude-plugin/marketplace.json`
- 각 `plugins/*/.codex-plugin/plugin.json`
- 각 `plugins/*/.claude-plugin/plugin.json`

모든 패키지 매니페스트가 선택된 체크아웃 안에서 일관된 번들 버전을
가져야 합니다. 예상 버전이나 플러그인 수를 이 가이드에서 고정하지
않습니다. 마켓플레이스 카탈로그에 선언된 현재 항목이 설치 목록입니다.

소스 확인 단계가 실패하면 홈을 쓰지 않습니다. 설치 작업은 소스를
재생성하거나 릴리스를 수리할 권한을 포함하지 않습니다.

## 6. 한 번의 사전 비교와 한 번의 백업

첫 홈 쓰기 전에 현재 소스와 대상 경로를 비교하여 다음만
구분합니다.

- 새로 추가할 관리 파일
- 교체할 이전 Skill System 관리 파일
- 이미 같은 파일
- 사용자가 수정했거나 소유권이 불명확한 충돌
- 절대로 건드리지 않을 보호 상태

그 후 이번 설치에서 변경할 기존 파일을 **타임스탬프가 붙은 단일 백업
세트**에 한 번 백업합니다. Codex와 Claude를 함께 설치하면 같은 백업
세트 아래에 플랫폼별 하위 디렉터리를 둡니다.

백업에는 최소한 다음 정보만 평문으로 남깁니다.

- 선택한 소스 루트, 커밋, tree object ID와 태그(선택한 경우)
- 대상 플랫폼
- 변경 전 존재했던 관리 경로
- 설치 전 플러그인 목록
- 복구에 필요한 소스-대상 경로 대응표

대화 원문, 도구 출력 전체, 자격 증명, 토큰, 설정 파일 내용은 기록하지
않습니다. 별도 설치 기록 체계, 데이터베이스, Python 수집기 또는
원격 측정 체계를 만들지 않습니다. 백업이 실패하면 첫 쓰기 전에 중단합니다.

## 7. 소유권 경계

### Codex에서 Skill System이 동기화하는 정적 런타임

선택한 체크아웃에서 생성된 `.codex/` 항목을 아래 표에 따라
Codex 홈 경로에 동기화합니다.

| 소스 | 대상 |
| --- | --- |
| `.codex/AGENTS.md` | `<CODEX_HOME>/AGENTS.md` |
| `.codex/context-routing.md` | `<CODEX_HOME>/context-routing.md` |
| `.codex/hooks.json` | `<CODEX_HOME>/hooks.json` |
| `.codex/bin/` | `<CODEX_HOME>/bin/`의 Skill System 관리 실행 파일 |
| `.codex/tools/` | `<CODEX_HOME>/tools/`의 Skill System 관리 파일 |
| `.codex/rules/` | `<CODEX_HOME>/rules/`의 Skill System 관리 파일 |
| `.codex/schemas/` | `<CODEX_HOME>/schemas/`의 Skill System 관리 파일 |
| `.codex/docs/` | `<CODEX_HOME>/docs/`의 Skill System 관리 파일 |
| `.codex/eval/` | `<CODEX_HOME>/eval/`의 정적 번들 파일 |
| `.codex/harness/README.md` | `<CODEX_HOME>/harness/README.md` |
| `.codex/research-routing.md` | `<CODEX_HOME>/research-routing.md` |

Research Ledger 검증 fixture는 `source/maintainer/fixtures/research-ledger/`에만
있으며 `.codex/`, `.claude/`, 플러그인으로 생성되지 않습니다. clean install은
`<CODEX_HOME>/research/`을 복사·초기화·갱신하지 않습니다.

외부 source의 revision, license, 채택·거부 판단을 모은 원장은 공개 bundle의
관리 payload가 아닙니다. release identity와 outer bundle hygiene는 해당 파일이나
구조화된 원장 데이터가 다시 들어오면 실패해야 합니다.

`CODEX_HOME`이 별도로 설정되지 않았다면 실제 기본 Codex 홈을
사용합니다. 경로를 추측해 다른 홈을 만들지 않습니다.

### Claude에서 Skill System이 동기화하는 정적 런타임

선택한 체크아웃에서 생성된 `.claude/` 항목을 아래 표에 따라
Claude 홈 경로에 동기화합니다.

| 소스 | 대상 |
| --- | --- |
| `.claude/CLAUDE.md` | `<CLAUDE_HOME>/CLAUDE.md` |
| `.claude/context-routing.md` | `<CLAUDE_HOME>/context-routing.md` |
| `.claude/hooks/` | `<CLAUDE_HOME>/hooks/`의 Skill System 관리 파일 |
| `.claude/tools/` | `<CLAUDE_HOME>/tools/`의 Skill System 관리 파일 |
| `.claude/schemas/` | `<CLAUDE_HOME>/schemas/`의 Skill System 관리 파일 |
| `.claude/docs/` | `<CLAUDE_HOME>/docs/`의 Skill System 관리 파일 |
| `.claude/eval/` | `<CLAUDE_HOME>/eval/`의 정적 번들 파일 |

Claude 훅 설정은 선택된 체크아웃의
`.claude/hooks/README.md`에 선언된 현재 구성을 따릅니다.
`settings.json` 전체를 교체하지 않고, 기존 훅 이외의 최상위 키를
보존한 채 명시된 훅 블록만 반영합니다.

### 항상 보존하는 상태

Codex:

- `<CODEX_HOME>/config.toml`
- `<CODEX_HOME>/automations/`
- `<CODEX_HOME>/skills/.system`
- 사용자 또는 앱 관리 스킬
- `<CODEX_HOME>/plugins/cache/`의 직접 파일 상태
- 자격 증명, 인증, MCP, 호스트별 정책
- 하네스 실행 기록, 훅 원장, 복구 세션 같은 런타임 상태
- `<CODEX_HOME>/research/` 전체와 실제 연구 원장·관찰 실행 기록
- 프로젝트 Memory Bank, Knowledge Base, LLM Wiki
- Skill System 소유로 확인되지 않은 모든 파일

Claude:

- `settings.json`의 훅 이외의 최상위 키
- `skills/.system`과 사용자 스킬
- 자격 증명, 인증, MCP, 권한 정책
- 런타임 상태와 사용자 데이터
- Skill System 소유로 확인되지 않은 모든 파일

`.codex/skills/`, `.claude/skills/`, `.generated`, `.DS_Store`, 바이트코드와
캐시는 런타임 보조 파일 복사 대상이 아닙니다. 스킬은 마켓플레이스
플러그인이 소유합니다.

## 8. 런타임 보조 파일 적용

백업 뒤에 현재 생성 대상의 관리 대상 정적 파일을 대상 경로에
바이트 단위로 동일하게 반영합니다.

- 이전 설치의 변경되지 않은 Skill System 파일은 교체할 수 있습니다.
- 사용자가 수정했거나 소유권이 불명확한 파일은 보존하고 충돌로
  묶습니다.
- 새 릴리스에 없는 과거 관리 파일은 이전 릴리스나 백업으로 소유권을
  입증할 수 있을 때만 활성 경로 밖으로 격리합니다.
- 상태를 보관하는 디렉터리를 통째로 삭제하지 않습니다.
- 훅과 전역 지침은 임의로 병합하거나 재작성하지
  않고 선택된 체크아웃의 플랫폼별 생성 파일을 사용합니다.
- 훅 이벤트 수, 매처, 시간 제한, 어댑터 동작을 이 문서에
  하드코딩하지 않습니다.

적용 중 하나가 실패하면 새로운 설치 프로그램이나 복사 스크립트를 만들지
않습니다. 같은 원인의 명령을 반복하지 말고 실패한 경계에서 중단하거나
단일 백업 세트로 이미 변경한 관리 파일만 복구합니다.

## 9. 마켓플레이스 플러그인 설치

마켓플레이스와 플러그인은 반드시 각 제품의 공식 명령으로 관리합니다.
캐시 경로를 직접 수정하지 않습니다.

### Codex

1. `codex plugin marketplace list`로 현재 등록된 소스를 확인합니다.
2. 선택한 저장소가 등록되지 않았다면 저장소 루트를 직접 등록합니다.
3. 같은 마켓플레이스 이름이 같은 경로를 가리키면 다시 등록하지
   않습니다.
4. 같은 이름이 다른 경로를 가리키면 임의로 덮지 않고 충돌 한 건으로
   묶어 보고합니다.
5. `.agents/plugins/marketplace.json`의 현재 `plugins[]` 항목 각각을
   공식 `codex plugin add` 명령으로 설치하거나 갱신합니다.
6. `codex plugin list --available --json`으로 결과를 다시 확인합니다.

명령 형태:

```bash
codex plugin marketplace add <absolute-repository-root>
codex plugin add <plugin-name>@<marketplace-name>
codex plugin list --available --json
```

로컬 마켓플레이스 등록은 저장소 루트를 사용합니다. 마켓플레이스 카탈로그의
상대 경로를 임의로 바꾸지 않습니다. 플러그인 변경은 새 Codex 세션부터
적용될 수 있으므로 기존 세션을 강제로 조작하지 않고 그 사실만
보고합니다.

### Claude Code

Claude Code가 설치 대상이면 생성된 카탈로그가 있는
`<absolute-repository-root>/plugins`를 마켓플레이스 루트로 사용합니다.

```bash
claude plugin marketplace add <absolute-repository-root>/plugins
claude plugin marketplace list
claude plugin install <plugin-name>@<marketplace-name>
claude plugin update <plugin-name>@<marketplace-name>
claude plugin list
```

현재 카탈로그의 모든 항목을 확인해 설치되지 않은 항목에는 `install`, 이미
설치된 항목에는 `update`를 사용합니다. 사용자가 구성을 지정했다면 해당
항목만 처리합니다. 변경 내용은 Claude Code 재시작 뒤 적용될 수 있으므로
현재 세션을 강제로 조작하지 않고 그 사실만 보고합니다.

## 10. 최소 사후 확인

설치 후 내부 시나리오를 만들지 않고 다음 사실만 확인합니다.

- 설치에 사용한 소스 루트와 커밋이 처음 선택한 값과 같음
- 릴리스 생성 환경에서 런타임 및 플러그인 재생성 검사를 통과한 소스를 사용함
- 설치 대상에서 선택한 commit/tree, bundle identity와 core 검사를 확인함
- 복사된 관리 대상 정적 파일이 소스와 바이트 단위로 동일함
- 보호 상태를 수정하지 않음
- Codex 플러그인 목록이 현재 마켓플레이스 매니페스트와 일치함
- Claude가 대상이면 마켓플레이스와 플러그인 목록이 현재 매니페스트와 일치함
- 훅과 설정 파일이 구문상 읽히며 선택된 체크아웃 내용과 일치함
- 설치를 위해 새 설치 프로그램이나 래퍼가 생성되지 않음
- 예상하지 못한 다른 파일이나 세션이 변경되지 않음

실제 새 세션에서 스킬과 훅이 로드되는 확인만 제품 재시작이 필요한
사용자 확인으로 남길 수 있습니다. 정적 확인 결과를 제품 동작 검증으로
과장하지 않습니다.

## 11. 실패와 복구

부분 적용 실패 시 임의의 새 방법으로 계속 밀어붙이지 않습니다.

1. 실패 지점과 이미 변경된 관리 경로를 확인합니다.
2. 하나의 사전 백업 세트에서 해당 경로만 복구합니다.
3. 플러그인 복구가 필요하면 공식 플러그인 명령만 사용합니다.
4. 보호 상태와 무관한 파일은 건드리지 않습니다.
5. 해결에 새 권한이나 소스 수정이 필요하면 정확한 차단 원인 하나를
   보고하고 중단합니다.

성공한 설치에서는 되돌리기를 실행하지 않습니다.

## 12. 버전 변경 시 해야 할 일

새 번들 버전을 설치할 때 이 파일의 버전 문자열을 바꾸는 작업은
없습니다.

1. 사용자가 새 태그나 커밋 또는 현재 체크아웃을 선택합니다.
2. 같은 소스 확인 단계를 통과합니다.
3. 같은 백업과 런타임 동기화를 수행합니다.
4. 같은 공식 플러그인 명령으로 현재 매니페스트 항목을 갱신합니다.
5. 같은 최소 사후 확인으로 끝냅니다.

다음이 실제로 바뀔 때만 이 가이드를 수정합니다.

- 마켓플레이스 위치 또는 공식 플러그인 CLI
- 생성된 런타임 구성의 소유권
- 보호해야 할 호스트 상태
- 백업과 되돌리기 경계
- 플랫폼별 훅 설정 방식

## 13. 에이전트 실행 요청 예시

```text
이 저장소의 CLEAN_INSTALL_GUIDE.md를 설치 계약으로 사용해, 내가 선택한
현재 체크아웃을 이 컴퓨터에 클린 설치하세요. 소스 확인 단계를 통과한 뒤
백업은 한 번만 만들고, 관리 대상 런타임 보조 파일을 동기화한 다음
마켓플레이스 플러그인을 공식 CLI로 갱신하고 최소 사후 확인으로 끝내세요.

새 Python/셸 설치 프로그램을 만들지 말고, 명령을 불필요한 셸
래퍼로 감싸지 말며, 보호 대상과 다른 세션은 건드리지 마세요.
가이드에 없는 버전·태그·스킬 수를 추측하지 마세요.
```

## Codex 공식 문서

- [Codex 플러그인 CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-plugin)
- [Codex 플러그인 마켓플레이스 CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-plugin-marketplace)
- [플러그인 및 로컬 마켓플레이스 구성](https://learn.chatgpt.com/docs/build-plugins)
