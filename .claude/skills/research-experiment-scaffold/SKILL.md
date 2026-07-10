---
name: research-experiment-scaffold
description: Project an approved experiment blueprint into a minimal runnable code scaffold with configuration, provenance, synthetic fixtures, tests, and safe smoke validation. Use only for explicit scaffold/code intent; do not download datasets, install dependencies, train models, or claim experimental results.
---

# Research Experiment Scaffold

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - experiment scaffold, experiments directory, run/evaluate skeleton, blueprint to code, 실험 코드 스켈레톤
- use_when:
  - the user explicitly asks to create experiment code from an approved blueprint or equivalent complete contract.
- do_not_use_when:
  - the hypothesis/blueprint is not settled, or the task is search, synthesis, statistics, writing, or training execution.
- expected_inputs:
  - blueprint, target repository/directory, existing project conventions, and validation boundary
- expected_outputs:
  - minimal runnable scaffold, config/provenance contract, synthetic tests, smoke result, and explicit unimplemented boundaries
- context_targets:
  must_read:
    - approved blueprint or equivalent experiment contract
    - target directory and repository instructions
    - nearest existing experiment/test pattern
  read_if_needed:
    - build/test contract, package manifest, and existing data/config interfaces
  do_not_load_by_default:
    - full literature corpus, real datasets, unrelated training code, or manuscript artifacts
- risk_profile:
  reads:
    - blueprint and narrow target-repository patterns
  writes:
    - scaffold files within the requested target
  tools:
    - safe local syntax/unit/smoke checks; no implicit network, install, data download, or training
  sensitive_resources:
    - credentials and private datasets default deny
- entry_scene:
  - PREPARE

## Projection Rules
1. Map each blueprint decision to an explicit interface: config field, dataset adapter, model/baseline adapter, metric, runner, evaluator, or provenance record.
2. Reuse repository structure and dependencies. Do not introduce a parallel framework when a local pattern exists.
3. Implement the thinnest end-to-end synthetic path that proves config → data → method → metric → result serialization.
4. Keep real dataset access and training bodies as explicit adapters or guarded TODOs only when the blueprint cannot supply them.
5. Record seed, config, code revision hook, data/version placeholders, device/environment, and output location.
6. Make invalid or missing inputs fail clearly; never silently substitute fake research data in a real run.
7. Run the narrowest safe syntax/unit/smoke validation by default when the local environment supports it. If unavailable, report the exact gap.

## Minimum Useful Scaffold
Select files from the blueprint and repository rather than forcing a universal tree. A typical scaffold may include:

- one config with documented fields
- data/model/baseline/metric interfaces needed by the core experiment
- a runner and evaluator
- deterministic synthetic fixture
- tests for config validation and one end-to-end synthetic pass
- provenance/result schema and concise usage note

Do not create empty directories, placeholder modules, requirements files, or broad abstractions with no immediate experiment role.

## Output
Report the blueprint source, changed files, runnable entry point, smoke/test evidence, intentionally unimplemented real-data/training pieces, and remaining user/environment checks. Scaffold existence is not an experiment result.

## Behavior Cases
- Positive: “이 approved blueprint를 기존 PyTorch repo 패턴에 맞춘 최소 runnable scaffold로 구현해줘.”
- Negative: “새 연구 아이디어를 제안해줘.” → research ideation/planning.
- Edge: required dependency is absent → do not install automatically; keep the adapter boundary and report the blocked smoke check.

## Validation
- A synthetic end-to-end path runs or the exact blocker is shown.
- Config and result/provenance shapes match the blueprint.
- No dataset download, dependency installation, training, or fabricated result occurred implicitly.
- Generated code stays inside the accepted target and follows repository conventions.
