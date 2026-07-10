skill-system-dev:workflow-bug-fix

- 실패 재현: `python3 -m unittest discover -s tests -v` → 1개 실패 (`9650 != 10350`, 종료 코드 1)
- 변경: [src/fees.py](/private/tmp/skill-system-911-forward/bug-fix/src/fees.py:4)에서 수수료를 빼던 `-`를 `+`로 수정했습니다. 테스트 파일은 변경하지 않았습니다.
- 재검증: 동일 명령 → 1개 테스트 통과, `OK` (종료 코드 0)
- 상태: `agent-verified`