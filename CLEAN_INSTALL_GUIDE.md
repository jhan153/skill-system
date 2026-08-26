# Skill System 클린 설치 가이드

> 이 문서는 **버전과 무관한 개인용 설치 절차**입니다. 공개 릴리스 신원,
> clean tree, 태그, 커밋 해시 또는 고정된 스킬 수를 설치 조건으로 사용하지
> 않습니다. 사용자가 선택한 체크아웃의 현재 생성 결과가 설치 입력입니다.

## 1. 목적

클린 설치는 선택된 Skill System 체크아웃의 플러그인과 플랫폼별 runtime companion을
현재 컴퓨터에 반영하는 작업입니다.

1. 마켓플레이스 플러그인은 공식 플러그인 명령으로 설치합니다.
2. 플러그인에 포함되지 않는 플랫폼별 런타임 보조 파일은 보호 대상과
   실행 상태를 보존하면서 정확히 동기화합니다.

버전이 바뀌어도 이 절차는 같습니다. 설치 구조나 공식 CLI가 달라질 때만
이 문서를 수정합니다.

## 2. 설치 요청에서 확정할 입력

작업 전에 다음 네 가지를 확정합니다.

- **소스 루트**: 안정적인 Skill System 저장소의 절대 경로
- **선택한 체크아웃**: 현재 작업 트리 또는 사용자가 명시한 revision
- **대상 플랫폼**: Codex, Claude Code, Grok, Antigravity 중 설치할 항목
- **플러그인 구성**: 전체 마켓플레이스 항목 또는 사용자가 지정한 일부

사용자가 “현재 체크아웃을 설치”라고 했다면 현재 작업 트리의 생성 결과를
그대로 사용합니다. clean tree나 태그를 요구하지 않습니다. 특정 revision을
지정했다면 그 checkout을 사용합니다.

다음 값으로 설치 입력을 바꾸지 않습니다.

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
- `.codex/`, `.claude/`, `.grok/`, `.antigravity/` 전체 디렉터리 복사 금지
- `rsync --delete`처럼 상태 파일까지 지울 수 있는 동기화 금지
- 설치 중 정본 `source/` 또는 생성 대상 수정 금지
- 기존 체크아웃에 `reset --hard`, `clean`, `stash` 실행 금지
- 다른 provider 세션 열기, 중지, 조작 금지
- 내부 시나리오, A/B 평가나 성숙도 점수를 설치 완료 조건으로 사용 금지

`source/tools/generate_targets.py`는 저장소의 생성 도구이며 설치 프로그램이
아닙니다. 클린 설치용 새 도구를 만드는 근거로 사용하지 않습니다.

## 4. 승인과 명령 실행 원칙

사용자가 이 컴퓨터에 클린 설치를 명시적으로 요청했다면, 아래 경계 안의
백업·런타임 동기화·공식 플러그인 설치를 하나의 승인된 작업 단위로
취급합니다. 대화로 파일마다 승인을 다시 요청하지 않습니다.

호스트가 실제 권한 승인을 요구할 수는 있습니다. 이때도 이미 허용된
실행 파일이 식별되도록 명령을 직접 실행합니다.

```text
codex plugin ...
claude plugin ...
grok plugin ...
agy plugin ...
git ...
rsync ...
```

파이프라인, 리디렉션, 글로브 같은 실제 셸 문법이 필요 없는 명령을
`zsh -lc`, `bash -lc`, JetShell 또는 다른 래퍼로 감싸지 않습니다.
예상하지 못한 호스트 정책 충돌이 여러 개면 하나로 모아 한 번만
보고하고 결정받습니다.

## 5. 선택한 체크아웃을 그대로 설치

설치 과정은 다음 조건을 요구하지 않습니다.

- clean Git 작업 트리
- 태그·커밋·tree object 일치
- release identity 또는 bundle identity
- core verifier 통과
- workspace hygiene 또는 민감 파일 스캔

선택한 체크아웃의 `.codex/`, `.claude/`, `.grok/`, `.antigravity/`, `plugins/`에서
사용자가 지정한 플랫폼의 선언된 파일만 설치합니다. 필요한 생성 대상이 없으면 그
경로만 보고하며, 설치 과정에서 source를 재생성하거나 다른 검사로 대체하지 않습니다.

저장소와 홈의 실제 절대 경로는 각 컴퓨터에서 설치 시점에 해석합니다.
공유 manifest, 설치 기록 또는 생성 데이터에 특정 컴퓨터의 절대 경로를
저장하지 않습니다.

## 6. 한 번의 사전 비교와 한 번의 백업

첫 홈 쓰기 전에 현재 소스와 대상 경로를 비교하여 다음만
구분합니다.

- 새로 추가할 관리 파일
- 교체할 이전 Skill System 관리 파일
- 이미 같은 파일
- 사용자가 수정했거나 소유권이 불명확한 충돌
- 절대로 건드리지 않을 보호 상태

그 후 이번 설치에서 변경할 기존 파일을 **타임스탬프가 붙은 단일 백업
세트**에 한 번 백업합니다. 여러 provider를 함께 설치하면 같은 백업
세트 아래에 플랫폼별 하위 디렉터리를 둡니다.

백업에는 최소한 다음 정보만 평문으로 남깁니다.

- 대상 플랫폼
- 변경 전 존재했던 관리 상대 경로
- 설치 전 플러그인 목록
- 복구에 필요한 상대 경로 대응표

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
| `.codex/rules/skill-system.rules` | `<CODEX_HOME>/rules/skill-system.rules` |
| `.codex/schemas/` | `<CODEX_HOME>/schemas/`의 Skill System 관리 파일 |
| `.codex/docs/` | `<CODEX_HOME>/docs/`의 Skill System 관리 파일 |
| `.codex/harness/README.md` | `<CODEX_HOME>/harness/README.md` |
| `.codex/harness/config.toml.fragment` | `<CODEX_HOME>/harness/config.toml.fragment` 참고 조각 |

외부 source의 revision, license, 채택·거부 판단을 모은 원장은 설치 대상으로
선언되지 않았으므로 동기화하지 않습니다.

`CODEX_HOME`이 별도로 설정되지 않았다면 실제 기본 Codex 홈을
사용합니다. 경로를 추측해 다른 홈을 만들지 않습니다.

#### Codex 전용 실행 하네스

이 실행 하네스는 Codex의 `UserPromptSubmit`, `PreToolUse`,
`PermissionRequest`, `PostToolUse` 입력·출력 계약과 `permission_mode`를 소유하는
Codex 전용 런타임입니다. Claude, Grok, Antigravity 또는 다른 에이전트의 실행
하네스로 복사하거나 공용 분류기로 사용하지 않습니다. 각 에이전트는 해당 도구명,
승인 모드, hook wire format에 맞는 별도 하네스를 가져야 합니다.

Codex 설치에서는 다음을 하나의 경계로 적용합니다.

- `hooks.json`과 `bin/skill-system-harness`를 함께 갱신합니다.
- Skill System 정책은 `rules/skill-system.rules`에만 설치합니다.
- Codex TUI가 영구 승인을 누적하는 `<CODEX_HOME>/rules/default.rules`와 그 백업은
  생성·교체·정리하지 않습니다. 설치 전후 바이트 동일성을 확인합니다.
- `harness/config.toml.fragment`의 `allow_login_shell = false`는 사용자가 해당 키
  병합을 명시적으로 요청한 경우에만 host-owned `config.toml`에 추가합니다. 기존
  TOML의 다른 키와 주석은 보존합니다.
- 설치 후 새 Codex 작업을 시작하여 safe direct command, wrapper rewrite,
  `python3 -c`/`zsh -ic` 같은 opaque evaluator의 승인 전 거부,
  `dontAsk` 즉시 종료, 승인 1회 제한을 실제 hook 경로에서 확인합니다.

실행 상태는 `<CODEX_HOME>/harness/exec-guard/` 아래의 bounded digest 상태만
사용하며 raw prompt, command, patch, tool output 또는 자격 증명을 저장하지 않습니다.

### Claude에서 Skill System이 동기화하는 정적 런타임

선택한 체크아웃에서 생성된 `.claude/` 항목을 아래 표에 따라
Claude 홈 경로에 동기화합니다.

| 소스 | 대상 |
| --- | --- |
| `.claude/CLAUDE.md` | `<CLAUDE_HOME>/CLAUDE.md` |
| `.claude/context-routing.md` | `<CLAUDE_HOME>/context-routing.md` |
| `.claude/hooks/` | `<CLAUDE_HOME>/hooks/`의 Skill System 관리 파일 |
| `.claude/schemas/` | `<CLAUDE_HOME>/schemas/`의 Skill System 관리 파일 |
| `.claude/docs/` | `<CLAUDE_HOME>/docs/`의 Skill System 관리 파일 |

Claude 훅 설정은 선택된 체크아웃의
`.claude/hooks/README.md`에 선언된 현재 구성을 따릅니다.
`settings.json` 전체를 교체하지 않고, 기존 훅 이외의 최상위 키를
보존한 채 명시된 훅 블록만 반영합니다.

### Grok에서 Skill System이 동기화하는 정적 런타임

Grok에는 독립 공용 Go 하네스 모듈의 binary를 설치하지만 native hook adapter로
사용하지 않습니다. Orca가 worker lifecycle을 소유하며, 아래 companion을
`<GROK_HOME>`에 동기화합니다.

| 소스 | 대상 |
| --- | --- |
| `.grok/AGENTS.md` | `<GROK_HOME>/AGENTS.md` |
| `.grok/harness.json` | `<GROK_HOME>/harness.json` |
| `.grok/harness/` | `<GROK_HOME>/harness/`의 공용 하네스 설명 |
| `.grok/bin/` | `<GROK_HOME>/bin/`의 Grok 공용 하네스 실행 파일 |
| `.grok/docs/` | `<GROK_HOME>/docs/`의 Skill System 관리 파일 |
| `.grok/schemas/` | `<GROK_HOME>/schemas/`의 Skill System 관리 파일 |

`GROK_HOME`이 설정되지 않았다면 Grok이 사용하는 현재 기본 홈을 확인해 사용합니다.

### Antigravity에서 Skill System이 동기화하는 정적 런타임

Antigravity에도 독립 공용 Go 하네스 모듈의 binary를 설치하지만 native hook adapter로
사용하지 않습니다. Orca가 worker lifecycle을 소유하며, 생성된 companion을
Antigravity가 실제로 읽는 global root에 동기화합니다.

| 소스 | 대상 |
| --- | --- |
| `.antigravity/GEMINI.md` | `<ANTIGRAVITY_GLOBAL_ROOT>/GEMINI.md` |
| `.antigravity/harness.json` | `<ANTIGRAVITY_GLOBAL_ROOT>/harness.json` |
| `.antigravity/harness/` | `<ANTIGRAVITY_GLOBAL_ROOT>/harness/`의 공용 하네스 설명 |
| `.antigravity/bin/` | `<ANTIGRAVITY_GLOBAL_ROOT>/bin/`의 Antigravity 공용 하네스 실행 파일 |
| `.antigravity/docs/` | `<ANTIGRAVITY_GLOBAL_ROOT>/docs/`의 Skill System 관리 파일 |
| `.antigravity/schemas/` | `<ANTIGRAVITY_GLOBAL_ROOT>/schemas/`의 Skill System 관리 파일 |

현재 Antigravity CLI의 기본 global rule root는 `~/.gemini`이지만, 설치 시 실제 host
설정에서 확인하며 공유 데이터에 해석된 절대 경로를 기록하지 않습니다.

### 항상 보존하는 상태

Codex:

- `<CODEX_HOME>/config.toml`
- `<CODEX_HOME>/rules/default.rules`와 그 백업·사용자 규칙 파일
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

Grok:

- `config.toml`, credentials, sessions, memories, hooks, plugin store/cache
- Skill System 소유로 확인되지 않은 모든 파일

Antigravity:

- `settings.json`, credentials, conversations, hooks, plugin store/cache
- Skill System 소유로 확인되지 않은 모든 파일

`.codex/skills/`, `.claude/skills/`, `.grok/skills/`, Antigravity global skills,
`.generated`, `.DS_Store`, 바이트코드와
캐시는 런타임 보조 파일 복사 대상이 아닙니다. 스킬은 마켓플레이스
플러그인이 소유합니다.

## 8. 런타임 보조 파일 적용

백업 뒤에 현재 생성 대상의 관리 대상 정적 파일을 대상 경로에
바이트 단위로 동일하게 반영합니다.

- 이전 설치의 변경되지 않은 Skill System 파일은 교체할 수 있습니다.
- 사용자가 수정했거나 소유권이 불명확한 파일은 보존하고 충돌로
  묶습니다.
- 선택한 체크아웃에 없는 과거 관리 파일은 이전 설치나 백업으로 소유권을
  입증할 수 있을 때만 활성 경로 밖으로 격리합니다.
- 상태를 보관하는 디렉터리를 통째로 삭제하지 않습니다.
- 훅과 전역 지침은 임의로 병합하거나 재작성하지
  않고 선택된 체크아웃의 플랫폼별 생성 파일을 사용합니다.
- 훅 이벤트 수, 매처, 시간 제한, 어댑터 동작을 이 문서에
  하드코딩하지 않습니다.

적용 중 하나가 실패하면 새로운 설치 프로그램이나 복사 스크립트를 만들지
않습니다. 같은 원인의 명령을 반복하지 말고 실패한 경계에서 중단하거나
단일 백업 세트로 이미 변경한 관리 파일만 복구합니다.

## 9. 공식 플러그인 설치

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

### Grok

Grok은 Claude Code plugin 형식을 직접 소비하므로 portable package root를 공식 CLI에
전달합니다. 별도 Grok용 skill 복사본이나 marketplace 파일을 만들지 않습니다.

```bash
grok plugin install <absolute-repository-root>/plugins/claude/<plugin-name>
grok plugin list
```

### Antigravity

Antigravity는 같은 portable package root의 생성된 `plugin.json`을 읽습니다.

```bash
agy plugin install <absolute-repository-root>/plugins/claude/<plugin-name>
agy plugin list
```

## 10. 최소 사후 확인

설치 후 내부 시나리오를 만들지 않고 다음 사실만 확인합니다.

- 복사된 관리 대상 정적 파일이 선택한 체크아웃의 파일과 바이트 단위로 동일함
- 보호 상태를 수정하지 않음
- Codex 플러그인 목록이 현재 마켓플레이스 매니페스트와 일치함
- Claude가 대상이면 마켓플레이스와 플러그인 목록이 현재 매니페스트와 일치함
- Grok 또는 Antigravity가 대상이면 해당 공식 CLI의 plugin 목록이 선택한 profile과 일치함
- 선택한 플랫폼의 Go 하네스 binary가 `--version`에 현재 bundle version을 반환함
- 훅과 설정 파일이 구문상 읽히며 선택된 체크아웃 내용과 일치함
- 설치를 위해 새 설치 프로그램이나 래퍼가 생성되지 않음
- 공유 manifest나 설치 기록에 현재 컴퓨터의 절대 경로를 기록하지 않음
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

## 12. 다른 체크아웃 설치

다른 체크아웃을 설치할 때 이 파일의 버전 문자열을 바꾸는 작업은 없습니다.

1. 사용자가 설치할 체크아웃을 선택합니다.
2. 같은 백업과 런타임 동기화를 수행합니다.
3. 같은 공식 플러그인 명령으로 현재 매니페스트 항목을 갱신합니다.
4. 같은 최소 사후 확인으로 끝냅니다.

다음이 실제로 바뀔 때만 이 가이드를 수정합니다.

- 마켓플레이스 위치 또는 공식 플러그인 CLI
- 생성된 런타임 구성의 소유권
- 보호해야 할 호스트 상태
- 백업과 되돌리기 경계
- 플랫폼별 훅 설정 방식

## 13. 에이전트 실행 요청 예시

```text
이 저장소의 CLEAN_INSTALL_GUIDE.md를 설치 계약으로 사용해, 내가 선택한
현재 체크아웃을 이 컴퓨터에 클린 설치하세요. 별도의 release·hygiene 검사를
실행하지 말고, 백업은 한 번만 만든 뒤 관리 대상 런타임 보조 파일을 동기화하고
마켓플레이스 플러그인을 공식 CLI로 갱신하고 최소 사후 확인으로 끝내세요.

새 Python/셸 설치 프로그램을 만들지 말고, 명령을 불필요한 셸
래퍼로 감싸지 말며, 보호 대상과 다른 세션은 건드리지 마세요.
PC별 절대 경로를 공유 데이터에 기록하지 마세요.
```

## Provider 공식 문서

- [Codex 플러그인 CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-plugin)
- [Codex 플러그인 마켓플레이스 CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-plugin-marketplace)
- [플러그인 및 로컬 마켓플레이스 구성](https://learn.chatgpt.com/docs/build-plugins)
- [Grok Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces)
- [Grok AGENTS.md](https://docs.x.ai/build/features/project-rules)
- [Antigravity Plugins & Skills](https://antigravity.google/docs/cli/plugins)
- [Antigravity migration and global rules](https://antigravity.google/docs/cli/gcli-migration/)
