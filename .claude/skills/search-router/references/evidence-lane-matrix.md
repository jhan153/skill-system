# Evidence Lane Matrix

| evidence domain | lane owner | router keeps |
| --- | --- | --- |
| paper / source / citation | `search-paper-evidence` | lane selection only |
| paper evidence for implementation/planning | `search-paper-evidence` (support) | implementation/planning skill stays primary |
| codebase (repo search, call path, config, test, log) | `analysis-codebase` or `analysis-bug` evidence phase | lane selection only |
| runtime (command output, validation, repro) | `workflow-rigor` evidence phase | lane selection only |
| visual (screenshot, diff, framing) | `design-visual-regression` | lane selection only |
| accessibility (focus, contrast, semantics) | `design-a11y-audit` | lane selection only |
| memory (accepted/stale/conflict signals) | `memory-bank-harness` / `memory-bank-maintenance` | lane selection only |

## Ambiguous examples
- "근거 자료 찾아서 ledger 만들어줘" -> evidence intent + no final owner stated -> `search-router` opens the paper/source lane (`search-paper-evidence`).
- "이 결과가 맞는지 근거랑 같이 평가해줘" -> the goal is a report, not evidence discovery -> `report-qualitative` primary; evidence lane only if it asks to go find new sources.

## Router-vs-router examples
- "연구 가설 세워줘 / ablation 설계해줘" -> `research-router` (research lifecycle), NOT `search-router`.
- "논문 좀 찾아줘 (가설/실험 아님)" -> `search-router` -> `search-paper-evidence`.

## Paper-evidence-for-implementation examples
- "이 논문 아이디어를 구현 플랜 근거로 써야 해" -> implementation/planning skill primary (e.g., `plan-short-term-docs` / `analysis-algorithm`), with `search-paper-evidence` attached as a support evidence lane. Do not hand the whole task to the research cluster.
- "loss/model/experiment 단어가 있지만 목적은 구현" -> stay in implementation; `search-router` only opens an evidence lane if the user explicitly wants sources.
