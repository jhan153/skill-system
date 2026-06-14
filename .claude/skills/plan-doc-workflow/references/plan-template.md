# Plan Document Template

> File location: `docs/plan/YYYY-MM-DD-<task-slug>.md`
> Activation note: casual `플랜` mentions alone do not create a plan; use this template for persisted plan artifacts or active plan synchronization.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant P as Plan Doc

    U->>A: Persisted plan artifact request
    A->>P: Create or update docs/plan artifact
    loop During planning
        U->>A: Question or adjustment
        A->>P: Update 질의/결정/TODO
    end
    alt Implementation transition phrase detected
        U->>A: "구현 시작" (or equivalent)
        A->>P: Mark implementation transition = active
        A->>A: Start implementation
    else Planning continues
        A->>A: Keep planning-only mode
    end
```

## 1) 작업 개요
- 목적:
- 범위:
- 비범위:

## 2) 변경 파일 목록
- [ ] `<path>`

## 3) 변경 요약 (What / Why)
- What:
- Why:

## 4) 현재 상태 vs 예정 상태

### 4.1 코드
### 변경 전
```cpp
printf("hello\n");
```

### 변경 후
```cpp
std::cout << "hello" << std::endl;
```

### 4.2 수식 (필요 시)
### 수식 변경 전
$$C_{old} = a + b$$

### 수식 변경 후
$$C_{new} = a + b + \delta$$

### 4.3 다이어그램 (필요 시)
- 권장 기준:
  - 클래스 변경: 클래스 다이어그램
  - 호출/상호작용 변경: 시퀀스 다이어그램
  - 컴포넌트/배치 변경: 아키텍처 다이어그램
  - 스키마 변경: ERD

#### 현재 구조
```mermaid
classDiagram
    class Printer {
        +print()
    }
```

#### 변경 예정 구조
```mermaid
classDiagram
    class Printer {
        +print()
    }
    class ConsolePrinter {
        +printWithCout()
    }
    Printer <|-- ConsolePrinter
```

## 5) 리스크
- 리스크:
- 영향:
- 대응:

## 6) 검증 절차
### Agent 실행 검증
1. 명령:
2. 기대 결과:

### User 런타임 검증
1. 시나리오:
2. 기대 결과:

## 7) 질의 (Questions)
- Q1:
  - 상태: `open | answered | decided`
  - 답변:
  - 근거:

## 8) TODO
- [ ] `todo` 항목
- [ ] `doing` 항목
- [ ] `blocked` 항목 (차단 원인 명시)
- [x] `done` 항목

## 9) 승인 게이트
- 현재 상태: `pending | approved`
- 승인 문구:
- 승인 시각:
- 승인자:

## 10) 진행 로그
- YYYY-MM-DD HH:mm: 변경 사항 요약
