---
name: research-experiment-scaffold
description: Generates minimal experiment code skeletons from approved experiment blueprints, with explicit write gates, no dataset downloads, no dependency installs, and no training runs.
---

# Research Experiment Scaffold

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - experiment scaffold
  - experiments/
  - code skeleton
  - run.py
  - evaluate.py
  - 실험 코드 스켈레톤
  - blueprint로 코드
- use_when:
  - the user explicitly asks for code scaffold or an `experiments/` directory.
  - an approved `experiment_blueprint.json` exists or is provided and target directory is clear.
- do_not_use_when:
  - literature review, hypothesis generation, research planning, blueprint creation, paper evidence search, manuscript writing, or statistical analysis.
  - requests without approved blueprint or write boundary.
- expected_inputs:
  - approved experiment_blueprint.json
  - target directory
  - language/framework constraints
  - write approval
  - smoke test preference
- expected_outputs:
  - experiments/ README
  - configs/default.yaml
  - data/README.md
  - src/
  - tests/
  - run.py
  - evaluate.py
  - requirements.txt or pyproject.toml
- context_targets:
  must_read:
    - approved blueprint
    - target directory
    - explicit scaffold request
  read_if_needed:
    - repo validation contract
    - existing experiment directory
    - research-output-contracts reference
  do_not_load_by_default:
    - paper search
    - hypothesis ideation
    - training execution
    - dataset download
- risk_profile:
  reads:
    - approved experiment blueprint
    - target directory constraints
  writes:
    - `experiments/` scaffold only when explicitly requested
  tools:
    - optional safe smoke tests only when requested
  network:
    - none
  credentials:
    - none
  generated_artifacts:
    - scaffold files only within accepted write boundary
  destructive_actions:
    - none
  forbidden_by_default:
    - dataset downloads unless explicitly approved
    - dependency installs unless explicitly approved
    - training
- entry_scene:
  - PREPARE

## Purpose
Generates minimal experiment code skeletons from approved experiment blueprints, with explicit write gates, no dataset downloads, no dependency installs, and no training runs.

## When To Apply
- the user explicitly asks for code scaffold or an `experiments/` directory.
- an approved `experiment_blueprint.json` exists or is provided and target directory is clear.

## When Not To Apply
- literature review, hypothesis generation, research planning, blueprint creation, paper evidence search, manuscript writing, or statistical analysis.
- requests without approved blueprint or write boundary.

## Workflow
1. PREPARE - verify explicit scaffold intent, approved blueprint, target directory, and write boundary.
2. DESIGN - map blueprint to minimal directories, configs, fixtures, and interfaces.
3. SCAFFOLD - create skeleton files only within target scope.
4. SMOKE - optionally add synthetic fixture tests; CALL_PROCESS only if requested.
5. FINALIZE - report files and state that no training/results were run.

## Resource and Risk Boundary
Summary:
- Reads an approved experiment blueprint and target directory constraints.
- Writes `experiments/` scaffold files only after explicit scaffold request and accepted write boundary.
- May run optional safe smoke tests only when requested.
- Uses no network and no credentials.
- Dataset downloads, dependency installs, and training are forbidden unless separately approved where applicable.
- Required checkpoints: approved blueprint, WRITE_LOCAL_FS/WRITE_CODEBASE boundary, requirements-file decision, and what was not run.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Blueprint source
2. Target directory
3. Files to create/update
4. Risk gates
5. Scaffold layout
6. Synthetic smoke-test plan
7. Provenance logging fields
8. What was not run

## Workspace Initializer Script
`scripts/init_research_workspace.py` is a placeholder research artifact workspace initializer, not a lifecycle executor. It may create empty/template `papers/`, `experiments/`, `analysis/`, `review/`, and `manifest.json` files only after explicit user request. It does not search, download datasets, install dependencies, run training, run evaluation, or imply that the research lifecycle is complete.

## Validation
- Confirm `.codex/skills/.system` was not touched.
- Confirm user intent matches this skill, not ordinary development.
- Confirm required evidence or artifact inputs are present or explicitly marked missing.
- Confirm no secrets, credentials, hardcoded single-host paths, fabricated citations, or fabricated results are introduced.
- Confirm artifact writes happen only when explicitly requested.

## Anti-Patterns
- Installing or invoking monolithic `codex-research-lifecycle`.
- Treating search keywords as conclusions.
- Collapsing evidence search, ideation, blueprint, scaffold, analysis, writing, and review into one step.
- Creating custom transcribe/speech skills from research source material.
- Weakening development/implementation routing because a request mentions model, metric, loss, experiment, or training.

## Known Limits
- Scaffold code is not validated research output.
- Generated scaffolds need user/project adaptation.
- No results can be claimed until experiments are run and analyzed.
