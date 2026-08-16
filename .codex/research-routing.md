# Research Routing

Direct stage routing for the Research Cluster. The current task owner uses this file only when the requested scientific artifact or latest verified upstream state does not already select one specialist.

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
| research stage genuinely unclear | current task owner asks for the missing deliverable/upstream distinction | selected narrow skill after clarification | monolithic lifecycle, `.system`, speculative multi-stage fan-out |
| one claim needs independent evidence lanes | `search-deep-evidence` | research stage owner after evidence is ready | lane router, premature synthesis |
| latest papers/evidence/citations | `search-paper-evidence` | synthesis or ideation if requested | scaffold, manuscript, statistics |
| literature review / related work | `research-literature-synthesis` | ideation if requested | scaffold, blueprint |
| gap / hypothesis ideation | `research-literature-ideation` | hypothesis planning | scaffold, manuscript |
| claim-first research plan | `research-hypothesis-planning` | blueprint | scaffold unless explicitly requested |
| experiment blueprint | `research-experiment-blueprint` | scaffold if approved | paper search unless evidence missing |
| experiments/ scaffold | `research-experiment-scaffold` | optional smoke tests | ideation, manuscript, training |
| statistical analysis | `research-statistical-analysis` | manuscript writing | paper search, scaffold |
| manuscript writing | `research-manuscript-writing` | peer review | scaffold, statistics unless results missing |
| peer review | `research-peer-review` | revision planning | manuscript generation unless requested |

Select by requested artifact, not research vocabulary. Identify the latest verified upstream artifact; if it is missing, choose the earliest stage that can produce it and keep later stages gated. Use a sequence only for an explicitly multi-stage outcome whose included stages can produce the next inputs. Concrete implementation of an already selected method remains development work.

## Artifact Ownership
| Artifact | Owning skill |
| --- | --- |
| `papers/evidence_ledger.json` | `search-paper-evidence` |
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

## Research Behavior Evals
Canonical stage, negative-development, missing-input, and evidence-integrity cases live in `.codex/eval/research_regression_cases.yaml` plus the shared routing eval suites. Do not duplicate those case payloads here.

A routing change requires a focused stage case and a competing development or premature-stage case; prose presence is not route-quality evidence.
