---
name: research-experiment-scaffold
description: "Project an approved experiment contract into a small repo-native wiring scaffold: entry point, config loading, data boundary, result/provenance envelope, and deterministic local smoke. Real method, baseline, metric, data pipeline, training, and product implementation remain separate workflow-implementation work."
disable-model-invocation: true
---

# Research Experiment Scaffold

## Routing Card
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

## Build Contract
1. Require an approved contract or equivalent accepted slice that fixes the scaffold boundary, target repository, input/data interface, entry point, result envelope, and local smoke expectation. Keep an unresolved hypothesis or protocol field explicit and leave its dependent wiring unbuilt.
2. Inspect the target and nearest runnable pattern. Reuse its language, framework, dependencies, entry-point style, and result schema instead of creating a parallel tree.
3. Create the entry point, config loading, data-provider boundary, runner wiring, result/provenance envelope, and the smallest marked stub needed to keep those interfaces coherent. Leave real method, baseline, metric, dataset, and training implementation absent.
4. Use one deterministic synthetic fixture or no-op reference component to exercise wiring without pretending to implement the experiment. It must enter through the declared data boundary and produce a clearly synthetic result or explicit not-implemented state.
5. Run the narrowest local smoke through `config -> data boundary -> runner wiring -> result/provenance envelope`; intentionally absent algorithm or data implementation is not a scaffold blocker.

## Minimal Output
Select only files needed to make the accepted wiring shape understandable and runnable. A marked method/data stub is allowed when it owns an immediate interface role; empty directories, speculative abstractions, dependency manifests, and broad test suites are not.

Report the contract source, changed files, runnable entry point, smoke evidence or exact blocker, and intentionally unimplemented method/data/metric/training pieces. Verify only the exercised wiring path; scaffold existence or synthetic output is never an experimental result.

Read `references/research_stage_contract.md` when upstream/downstream ownership, multi-stage intent,
or Plan/Handoff mapping matters.
