# Field Feedback

Use this file to record real-use feedback before the next version cut.

## Entry

- date:
- environment:
- request:
- expected primary skill:
- actual primary skill:
- supporting skills:
- output shape:
- friction:
- missing context:
- over-triggered skills:
- under-triggered skills:
- useful behavior:
- risky behavior:
- suggested maturity change:
- suggested eval case:
- suggested skill text change:
- notes:

## Guidance

- Record observed behavior, not guesses.
- Prefer one request per entry.
- Mark uncertain conclusions as `unverified`.
- Do not paste secrets, credentials, session data, private chat logs, or unrelated project content.
- Feed recurring issues back into `.codex/docs/skill_registry.md`, `.codex/eval/*`, or the relevant `SKILL.md` in the next version cut.

## Examples

These examples show the expected shape. They are not measured field results.

### Example 1: Design Skill Over-Triggered

- user_request: "이 CSS 색상 하나만 바꿔줘."
- expected_primary_skill: none
- actual_primary_skill: design-to-frontend
- what_failed: A small local style edit was treated as full design implementation.
- friction: unnecessary design context loading and visual workflow overhead
- suggested_eval_case: add a negative routing case for small CSS-only edits
- suggested_registry_update: keep `design-to-frontend` scoped to concrete design artifacts and real UI implementation requests
- suggested_maturity_change: none unless this repeats

### Example 2: Research Router Over-Triggered

- user_request: "이 loss 함수는 이미 정했으니 코드와 테스트만 추가해줘."
- expected_primary_skill: none
- actual_primary_skill: research-router
- what_failed: Ordinary implementation was routed as research planning because the request mentioned loss.
- friction: delayed implementation and introduced unnecessary research framing
- suggested_eval_case: add a negative routing case for already-chosen ML formula implementation
- suggested_registry_update: reinforce that model/loss terms in implementation context do not imply research routing
- suggested_maturity_change: none unless repeated

### Example 3: Temporary Instruction Persisted

- user_request: "이번 답변에서만 이 스타일로 해줘. 메모리에 저장하지 마."
- expected_primary_skill: none
- actual_primary_skill: memory-bank-update
- what_failed: A temporary instruction was treated as persistent memory intent.
- friction: user had to correct persistence boundary
- suggested_eval_case: add or strengthen a negative memory case for temporary instructions
- suggested_registry_update: clarify memory mutation requires explicit persistent intent
- suggested_maturity_change: downgrade only if repeated after registry/eval update
