---
name: research-experiment-scaffold
description: Project an approved experiment contract into a minimal repo-native scaffold whose production runner can execute a deterministic synthetic data-boundary smoke. Use only for explicit scaffold/code intent; do not download data, install dependencies, train models, or claim experimental results.
---

# Research Experiment Scaffold

## Routing Card
- role: heavy_artifact_generator
- intent_signature: experiment scaffold, experiments directory, run/evaluate skeleton, blueprint to code, 실험 코드 스켈레톤
- use_when: explicit code/scaffold request from an approved blueprint or equivalent complete experiment contract
- do_not_use_when: unsettled hypothesis/protocol, search, synthesis, statistics, writing, ordinary product implementation, data acquisition, or training execution
- expected_inputs: approved contract, target/write boundary, repository conventions, and validation boundary
- expected_outputs: minimal repo-native production path, config/result/provenance contract, synthetic-boundary smoke, and explicit real-data/training gaps
- context_targets: contract, target instructions, and nearest runnable experiment pattern; manifest/data/config interfaces only as needed; exclude full literature, datasets, unrelated training, and manuscripts
- risk_profile: write only the accepted target; safe local checks only; no implicit network, install, download, training, credentials, or private data
- entry_scene: PREPARE

## Build Contract
1. Require an approved contract that fixes the method, comparison baseline, data boundary, metric semantics, result shape, and write/validation scope. Route incomplete protocol decisions back to `research-experiment-blueprint`; never invent defaults.
2. Inspect the target and nearest runnable pattern. Reuse its language, framework, dependencies, entry-point style, and result schema instead of creating a parallel tree.
3. Implement the blueprint-selected production config, data boundary, method, baseline, metric, runner, result serialization, and provenance path. Interfaces, mocks, tests, or TODO bodies without that core path are not scaffold progress.
4. A deterministic synthetic fixture may replace only the external data source and must enter through the same production interface. Never substitute it when a real run requests missing canonical data; fail clearly.
5. Record seed, config, code revision hook, data/version placeholder, device/environment, and output location as the repository supports them.
6. Exercise the thinnest end-to-end synthetic path through the production runner: config → data → method/baseline → metric → result/provenance. Use the narrowest safe local smoke; do not install, download, or train, and keep an unavailable required dependency as an explicit blocker.

## Minimal Output
Select only files needed by the contract and repository. Add focused tests only when the repository contract or immediate regression risk requires them; a passing mock proves only its mock boundary. Do not create empty directories, placeholder modules, requirements files, or abstractions with no immediate experiment role.

Report the contract source, changed files, runnable entry point, smoke evidence or exact blocker, and intentionally unimplemented real-data/training pieces. Verify only the exercised scaffold path; scaffold existence or synthetic output is never an experimental result.
