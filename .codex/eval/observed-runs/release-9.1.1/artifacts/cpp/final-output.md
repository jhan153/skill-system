analysis-codebase

결과: `agent-verified` — expected fail-closed gate를 포함해 분석 작업은 정상 완료되었습니다.

실행 명령:

```bash
"$SKILL_ROOT/scripts/collect.sh" --repo-path "$PWD" --commit-range auto --mode full --output-dir "$PWD/report-output" --top-n 120 --policy "$SKILL_ROOT/references/policy-default.json"

python3 "$SKILL_ROOT/scripts/report.py" --input-dir "$PWD/report-output" --output "$PWD/report-output/codebase-analysis-report.md" --risk-model default --policy "$SKILL_ROOT/references/policy-default.json"
```

- Collector exit: `0`
- Reporter exit: `2`
- Quality gate: `FAIL` — 의도된 평가 성공 조건
- Gate reasons:
  - `unverified_ratio=1.0 > fail_threshold=0.35`
  - `fallback_diagrams=3 > 1`
  - `c_cpp_structural_evidence=not_evidenced`
- Semantic depth: `Not evidenced`. CMake entrypoint/include/build 정보는 파일 수준 힌트로만 반영됐으며, compilation-aware symbol/class/call index는 없습니다.
- 소스 변경: 없음. 기존 staged 소스와 worktree가 동일합니다.

생성 파일 40개는 모두 [report-output](/private/tmp/skill-system-911-forward/cpp/report-output)에 있습니다.

- [통합 보고서](/private/tmp/skill-system-911-forward/cpp/report-output/codebase-analysis-report.md)
- [Quality gate 결과](/private/tmp/skill-system-911-forward/cpp/report-output/artifacts/quality-gate-result.json)
- [Architecture artifacts](/private/tmp/skill-system-911-forward/cpp/report-output/artifacts/architecture)
- [Findings](/private/tmp/skill-system-911-forward/cpp/report-output/artifacts/findings.json)
- [Artifact index](/private/tmp/skill-system-911-forward/cpp/report-output/artifacts/index.json)