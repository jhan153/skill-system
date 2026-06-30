# Examples

Use these examples to tune routing, prompts, and output shape. Do not load this file for ordinary reports unless examples are needed.

## Skill Draft Evaluation

User:

```text
$report-qualitative

다음 SKILL.md 초안을 정성평가해 주세요.

평가 목적:
- Codex에서 실제로 잘 호출될 수 있는지
- 평가 리포트 품질이 안정적인지
- 근거 기반 판단이 잘 강제되는지
- 개선할 부분이 무엇인지 확인하고 싶습니다.

출력 형식:
- Executive Summary
- 기준별 평가표
- 강점/약점
- P0/P1/P2 개선안
- 최종 readiness 판정
```

Expected mode: Qualitative Evaluation Report.

Must include:
- invocation clarity
- input/output contract
- progressive disclosure
- tool/resource boundaries
- evidence map
- prioritized recommendations
- readiness judgment

Must not become:
- a blocker-first QA gate unless requested
- an implementation task
- a score-only table

## Plan Or Product Spec Evaluation

User:

```text
이 기획안을 실무 적용 가능성, 구조적 명확성, 리스크, 개선 우선순위 관점에서 정성평가 리포트로 작성해 주세요.
```

Expected mode: Qualitative Evaluation Report.

Use criteria:
- Purpose Fit
- Structural Clarity
- Practical Usability
- Risk and Failure Modes
- Improvement Leverage

## Compact Evidence Report

User:

```text
srq로 검증 결과를 보고해줘.
```

Expected mode: Compact Evidence Report.

Use:
- Conclusion
- Evidence
- Action
- Verification when relevant

Do not expand into a full qualitative report unless the user asks for assessment, readiness, strengths/weaknesses, or recommendations.
Do not enter this mode from vague "보고해줘", "검토해줘", or "요약해줘" requests.

## Qualitative Diff Evaluation

User:

```text
이 diff를 품질, 리스크, 개선안 중심으로 정성평가해줘.
```

Expected mode: Qualitative Evaluation Report.

Must include:
- evidence-grounded judgment about the diff as an artifact
- risk and improvement recommendations
- limitations if the actual changed lines are not available

Must not include:
- changed-line diff blocks unless the user explicitly asks for them
- raw patch presentation owned by `report-diff`

## Negative Routing Examples

Do not trigger this skill for:

```text
이 문장 맞춤법만 봐줘.
```

Reason: proofreading without evaluation/report intent.

```text
이 diff 검토해줘.
```

Reason: ordinary review or critical review may apply depending on risk framing; qualitative report should not be the default.

```text
바뀐 부분만 읽기 쉽게 보여줘.
```

Reason: use `report-diff`.

```text
스킬 호출 통계 요약해줘.
```

Reason: use `evaluation-usage-tracker`.

```text
보고해줘.
```

Reason: too vague for compact evidence mode unless the user explicitly requests `srq`, formal evidence-first completion reporting, or qualitative evaluation.
