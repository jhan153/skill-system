# Research Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `research-experiment-blueprint`

- role: primary
- family: research
- intent_signature: selected-hypothesis protocol, experiment/benchmark design, controls, metrics, ablations, stop/refute
- use_when:
  - one hypothesis is selected and needs an executable scientific design without code
- do_not_use_when:
  - the claim is unselected, or the request is evidence search, code/scaffold, execution, result analysis, or writing
- expected_inputs: selected claim/mechanism, evidence status, target outcome, constraints, and checkpoint/baseline availability
- expected_outputs: identifying experiment, matched controls/data/metrics, focused ablations, uncertainty, stop/refute, compute, and provenance
- context_targets:
  must_read:
    - selected hypothesis/mechanism, target outcome, and constraints
  read_if_needed:
    - evidence set, checkpoints/results, dataset cards, metric definitions, prior protocol
  do_not_load_by_default:
    - full corpus, scaffold, manuscript, unrelated experiments
- risk_profile:
  reads:
    - scoped research and data/metric/baseline evidence
  writes:
    - blueprint artifact only when explicitly requested
  tools:
    - none by default; no download, install, training, analysis, or result generation
  sensitive_resources:
    - credentials/private datasets default deny
- entry_scene: PREPARE

## `research-experiment-scaffold`

- role: heavy_artifact_generator
- family: research
- intent_signature: experiment scaffold, experiments directory, run/evaluate skeleton, blueprint to code, 실험 코드 스켈레톤
- use_when: explicit code/scaffold request from an approved blueprint or equivalent complete experiment contract
- do_not_use_when: unsettled hypothesis/protocol, search, synthesis, statistics, writing, ordinary product implementation, data acquisition, or training execution
- expected_inputs: approved contract, target/write boundary, repository conventions, and validation boundary
- expected_outputs: minimal repo-native wiring scaffold, one runnable smoke path, and explicit method/data/metric/training gaps
- context_targets: contract, target instructions, and nearest runnable experiment pattern; manifest/data/config interfaces only as needed; exclude full literature, datasets, unrelated training, and manuscripts
- risk_profile: write only the accepted target; safe local checks only; no implicit network, install, download, training, credentials, or private data
- entry_scene: PREPARE

## `research-hypothesis-planning`

- role: primary
- family: research
- intent_signature: raw premise, mechanism, loss/ablation idea, or hypothesis validation
- use_when:
  - a premise must become one testable research decision
- do_not_use_when:
  - selected-method implementation or a later literature, protocol, scaffold, analysis, or manuscript stage
- expected_inputs: premise, mechanism, scope, evidence status, constraints, and baseline/checkpoint availability
- expected_outputs: premise status, one claim/falsifier, Stage 0, minimal discriminator, outcomes, and backlog
- context_targets:
  must_read:
    - premise/mechanism and supplied evidence or gap
  read_if_needed:
    - selected evidence, checkpoint/baseline, dataset/metric definitions
  do_not_load_by_default:
    - full repo/corpus, implementation, templates, unrelated artifacts
- risk_profile:
  reads:
    - scoped premise and research evidence
  writes:
    - plan artifact only when explicitly requested
  tools:
    - none by default; current literature claims route to evidence search
  sensitive_resources:
    - credentials default deny
- entry_scene: PREPARE

## `research-literature-ideation`

- role: primary
- family: research
- intent_signature: research gaps, candidate hypotheses from literature, active hypothesis, 문헌 기반 연구 아이디어
- use_when: an existing evidence set or synthesis can support gap-derived hypotheses or ranking
- do_not_use_when: papers need acquisition/synthesis, or a raw premise has no literature dependency
- expected_inputs: identified evidence artifact, scope, and ranking/selection constraints
- expected_outputs: provenance-linked gap classes, falsifiable candidates, ranking, optional active hypothesis, and evidence needs
- context_targets: read the named evidence set/synthesis and scope; expand only sources needed to resolve candidate provenance, not the full corpus, scaffold, manuscript, or unrelated results
- risk_profile: no search by default and write an ideation artifact only when requested; credentials denied
- entry_scene: PREPARE

## `research-literature-synthesis`

- role: primary
- family: research
- intent_signature: literature review, survey synthesis, evidence map, related-work analysis, 문헌 종합
- use_when: an existing paper or evidence set must be interpreted collectively
- do_not_use_when: acquisition, gap-derived hypothesis selection, or venue-ready manuscript prose is primary
- expected_inputs: identified evidence set, review question/scope, and search/coverage status
- expected_outputs: evidence-calibrated themes, agreements, contradictions, limitations, and corpus gaps
- context_targets: read the named set and scope; load search/inclusion rules and full-text loci only for disputed claims, excluding unrelated corpus, code, backlog, and manuscript templates
- risk_profile: no acquisition by default and write a review artifact only when requested; credentials denied
- entry_scene: PREPARE

## `research-manuscript-writing`

- role: primary
- family: research
- intent_signature: manuscript section, paper draft, IMRAD, LaTeX prose, 논문 작성
- use_when: existing evidence/synthesis/method/result artifacts can support requested scientific prose
- do_not_use_when: citation acquisition, data analysis, or critique/review is primary
- expected_inputs: target section/audience plus identified supporting artifacts and evidence stage
- expected_outputs: calibrated prose with claim locators and a separate unresolved citation/evidence gap list
- context_targets: read the target and named artifacts; load only in-scope bibliography, venue style, synthesis, protocol, report, figures, and tables—not unrelated scaffold/corpus
- risk_profile: write manuscript files only when requested; formatting/build tools may verify presentation, while search/analysis remains with its owner; credentials denied
- entry_scene: PREPARE

## `research-peer-review`

- role: review_gate
- family: research
- intent_signature: scholarly peer review, manuscript/proposal review, reviewer critique, 논문 리뷰
- use_when: a manuscript, proposal, or research plan needs scientific critique
- do_not_use_when: the target is generic code/spec/release material or rewriting is primary
- expected_inputs: exact review target/slice, stance, criteria, and available supporting evidence
- expected_outputs: prioritized anchored findings with scientific consequence, evidence limits, and actionable revision/check
- context_targets: read the target and requested scope; load only cited sources, protocol, analysis artifacts, venue criteria, or checklist needed for a finding—not unrelated literature or hidden assumptions
- risk_profile: no external verification by default; disclose any verification and write a review artifact only when requested; credentials and fabricated identity denied
- entry_scene: PREPARE

## `research-statistical-analysis`

- role: primary
- family: research
- intent_signature: statistical analysis, significance, effect size, interval, result-table interpretation, 통계 분석
- use_when: inference or bounded interpretation from supplied data/statistics, or an explicit analysis plan; inadequate inputs remain an insufficient-data response
- do_not_use_when: experiment/protocol design, scaffold code, manuscript prose, ordinary product implementation, or a non-statistical deliverable is primary
- expected_inputs: data/statistics, design, analysis unit, outcome/comparison, provenance, and prior plan when available
- expected_outputs: estimand/design assessment, reproducible result or plan-only finding, effect/uncertainty, and material limits
- context_targets: actual data or plan request plus design and sampling/analysis unit; load dictionary, exclusions, scripts, config, and metadata only as needed; exclude unrelated search, scaffold, and manuscript context
- risk_profile: privacy-check row data; write analysis code/report only when requested; use reproducible local computation for new statistics; credentials default deny
- entry_scene: PREPARE

## `workflow-research`

- role: execution_primary
- family: research
- intent_signature: explicit Research node execution, RES-* node management, bounded scientific stage envelope
- use_when:
  - an accepted Plan/Handoff assigns one Research node and one exact Research stage skill
  - the user explicitly requests a managed one-node Research execution with a fixed stage and result boundary
- do_not_use_when:
  - an ordinary direct request already matches one Research specialist
  - the Research stage is undecided, several stages must be designed, or a new DAG is needed
  - the request is evidence search, general implementation, graph coordination, polling, or lifecycle monitoring
- expected_inputs: node/scope identity, one canonical Research stage skill, upstream input references, artifact/write boundary, evidence ceiling, and user checks
- expected_outputs: one stage-bounded result, artifact/evidence anchors, unresolved inputs, user checks, and Core `research_result` when crossing a graph or owner boundary
- context_targets:
  must_read:
    - assigned node contract and exact selected Research stage skill
    - available required upstream artifacts and the declared status of missing ones
    - `references/research_stage_contract.md` for authoritative stage ownership, direct-vs-graph execution, and output ceilings
  read_if_needed:
    - `references/execution_item_contract.md` when the result crosses a Coordinator, Plan/Handoff, or plugin boundary
  do_not_load_by_default:
    - unselected Research skills, full paper corpus, unrelated experiments, implementation tree, manuscript, or another worker transcript
- risk_profile:
  reads: only the assigned node, selected stage inputs, and evidence needed by that stage
  writes: only the explicitly requested stage artifact within its accepted boundary
  tools: only those authorized by the selected Research stage; no automatic network, install, training, or external write
  sensitive_resources: credentials, private data, authenticated sources, and external publication require explicit authority
- entry_scene: PREPARE
