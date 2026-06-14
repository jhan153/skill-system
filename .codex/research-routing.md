# Research Routing

Detailed routing for the 6.0 Research Cluster. Keep `.codex/context-routing.md` thin; use this file for internal research stage routing, artifact ownership, and research smoke tests.

## Cluster Principles
- `codex-research-lifecycle.zip` is source material only; do not install `codex-research-lifecycle` as a monolithic skill.
- Development/implementation remains strict, concrete, and spec-driven.
- Research is evidence-first and claim-skeptical.
- Evidence search and hypothesis ideation are separate stages.
- Search keywords are not conclusions.
- Work one active hypothesis at a time.
- Use checkpoint/baseline evaluation before new training.
- Heavy artifact generation requires explicit artifact intent.

## Route Matrix
| Request | Primary skill | Next skill(s) | Default exclude |
| --- | --- | --- | --- |
| research stage unclear | `research-router` | selected narrow skill | monolithic lifecycle, `.system` |
| latest papers/evidence/citations | `research-paper-evidence-search` | synthesis or ideation if requested | scaffold, manuscript, statistics |
| literature review / related work | `research-literature-synthesis` | ideation if requested | scaffold, blueprint |
| gap / hypothesis ideation | `research-literature-ideation` | hypothesis planning | scaffold, manuscript |
| claim-first research plan | `research-hypothesis-planning` | blueprint | scaffold unless explicitly requested |
| experiment blueprint | `research-experiment-blueprint` | scaffold if approved | paper search unless evidence missing |
| experiments/ scaffold | `research-experiment-scaffold` | optional smoke tests | ideation, manuscript, training |
| statistical analysis | `research-statistical-analysis` | manuscript writing | paper search, scaffold |
| manuscript writing | `research-manuscript-writing` | peer review | scaffold, statistics unless results missing |
| peer review | `research-peer-review` | revision planning | manuscript generation unless requested |

## Artifact Ownership
| Artifact | Owning skill |
| --- | --- |
| `papers/evidence_ledger.json` | `research-paper-evidence-search` |
| `papers/literature_review.md` | `research-literature-synthesis` |
| `papers/ideation_output.json` | `research-literature-ideation` |
| `papers/research_plan.json` | `research-hypothesis-planning` |
| `papers/experiment_blueprint.json` | `research-experiment-blueprint` |
| `experiments/` | `research-experiment-scaffold` |
| `analysis/statistical_report.md` | `research-statistical-analysis` |
| `papers/draft/` | `research-manuscript-writing` |
| `review/peer_review.md` | `research-peer-review` |

Files are written only when the user explicitly requests artifacts or workspace initialization.

## Speech Enhancement Reference Loading
Load `.codex/references/speech-enhancement-research/reference.md` only for speech/audio research such as denoising, dereverberation, separation, restoration, ASR robustness, or speech enhancement. Do not load it for ordinary development or non-audio research.

## Heavy Scaffold Gate
`research-experiment-scaffold` requires explicit scaffold intent, approved/provided blueprint, target directory, WRITE_LOCAL_FS/WRITE_CODEBASE boundary, and requirements-file approval when relevant. It must not download datasets, install dependencies, run training, or claim results.

## Route Smoke Tests
```yaml
research_route_smoke_tests:
  - request: "음성 향상 최신연구를 하고싶어. 다만 clean label이 clean하지 못하고 기존 discriminative 모델들이 over-denoising을 하면서 PESQ를 맞추고 있다는게 내 주장이야."
    expected_primary_skill: "research-router"
    expected_next_skills:
      - "research-paper-evidence-search"
      - "research-hypothesis-planning"
    expected_reference:
      - "speech-enhancement-research"
    must_include:
      - "premise triage"
      - "evidence search or evidence-not-acquired state"
      - "user claim not treated as fact"
      - "checkpoint/baseline-first plan"
      - "progressive ablation ladder"
      - "loss budget"
    must_not_include:
      - "fabricated citations"
      - "direct assumption that the user claim is true"
      - "new training before evidence/checkpoint/baseline evaluation"
      - "multi-loss soup in the core experiment"
  - request: "이 논문 아이디어에서 loss를 어떻게 설계할까?"
    expected_primary_skill: "research-hypothesis-planning"
    expected_mode: "loss_budget"
    must_include:
      - "training loss vs evaluation metric separation"
      - "progressive ablation rather than multi-loss soup"
  - request: "이 연구 계획을 비판적으로 검토해줘."
    expected_primary_skill: "agent-critical-review"
    review_goal: "research_validation"
    must_include:
      - "premise validity check"
      - "checkpoint-first check"
      - "ablation isolation check"
      - "loss overloading check"
  - request: "이 연구 계획을 docs/plan으로 저장해줘."
    expected_primary_skill: "research-hypothesis-planning"
    expected_attachments:
      - "plan-doc-workflow only for persisted artifact"
    notes: "Research skill owns content; plan-doc writes artifact only when explicitly requested."
  - request: "speech enhancement 최신 논문을 찾아서 gap과 연구 가설을 뽑아줘"
    expected_primary_skill: "research-router"
    expected_next_skills:
      - "research-paper-evidence-search"
      - "research-literature-ideation"
    expected_reference:
      - "speech-enhancement-research"
    must_include:
      - "evidence ledger"
      - "gap map"
      - "selected active hypothesis"
    must_not_route_to:
      - "research-experiment-scaffold"
  - request: "arXiv에서 논문 찾아서 hypothesis 만들어줘"
    expected_primary_skill: "research-paper-evidence-search"
    if_search_tools_unavailable:
      - "do not hallucinate citations"
      - "produce query plan"
      - "mark evidence as not acquired"
  - request: "evidence_ledger.json 기반으로 literature review 작성해줘"
    expected_primary_skill: "research-literature-synthesis"
    must_include:
      - "search strategy and verification status"
      - "thematic synthesis"
      - "contradictions and gaps"
      - "citation status"
    must_not_include:
      - "final hypothesis selection"
  - request: "literature_review.md에서 gap과 active hypothesis 하나만 뽑아줘"
    expected_primary_skill: "research-literature-ideation"
    must_include:
      - "candidate hypotheses"
      - "selected active hypothesis"
      - "claim labels"
  - request: "이 selected hypothesis로 experiment_blueprint.json 만들어줘"
    expected_primary_skill: "research-experiment-blueprint"
    must_include:
      - "checkpoint-first plan"
      - "minimal core experiment"
      - "ablation ladder"
      - "loss budget"
  - request: "experiment_blueprint.json 기준으로 experiments/ 코드 스켈레톤 만들어줘"
    expected_primary_skill: "research-experiment-scaffold"
    expected_route_class: "development_implementation"
    risk_gates:
      - "WRITE_LOCAL_FS"
      - "requirements_file_generation"
    must_not_route_to:
      - "research-literature-ideation"
  - request: "이 result.csv 통계 분석해서 statistical_report.md 만들어줘"
    expected_primary_skill: "research-statistical-analysis"
    must_include:
      - "data provenance"
      - "test selection rationale"
      - "effect sizes"
  - request: "아직 결과는 없는데 어떤 통계 분석을 하면 좋을지 계획해줘"
    expected_primary_skill: "research-statistical-analysis"
    expected_route_class: "analysis_plan_only"
    must_include:
      - "planned vs exploratory analysis distinction"
      - "test selection rationale"
      - "data requirements"
      - "assumption checks to run after data arrives"
    must_not_include:
      - "p-value"
      - "effect size claim"
      - "statistical conclusion"
  - request: "analysis 결과와 evidence ledger로 논문 초안 써줘. 인용은 아직 일부 비어 있어."
    expected_primary_skill: "research-manuscript-writing"
    must_include:
      - "citation_status"
      - "[citation needed]"
      - "[unverified claim]"
      - "methods/results/interpretation separation"
    must_not_include:
      - "invented citation"
  - request: "이 논문 초안 peer review 해줘"
    expected_primary_skill: "research-peer-review"
    must_include:
      - "major concerns"
      - "minor concerns"
      - "reproducibility"
      - "ethics/reporting"
      - "evidence/citation concerns"
  - request: "일반 웹앱 버그 수정해줘"
    expected_route_class: "development_implementation"
    must_not_load:
      - "speech-enhancement-research"
      - "research-router"
  - request: "이 loss 함수 구현하고 테스트까지 추가해줘"
    expected_route_class: "development_implementation"
    must_not_route_to:
      - "research-hypothesis-planning"
      - "research-router"
  - request: "approved blueprint 없이 experiments/ 전체 코드 만들어줘"
    expected_primary_skill: null
    expected_route_class: "blocked_missing_blueprint_or_write_boundary"
    must_not_route_to:
      - "research-experiment-scaffold"
  - request: "codex-research-lifecycle 스킬 그대로 설치해줘"
    expected_primary_skill: null
    expected_route_class: "blocked_monolithic_research_skill"
    must_not_create:
      - ".codex/skills/codex-research-lifecycle"
```
