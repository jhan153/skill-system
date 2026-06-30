# Research Experiment Scaffold Design Document

## Overview
`research-experiment-scaffold` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads approved blueprint and target directory constraints.
- Writes scaffold files only after explicit request and accepted write boundary.
- Risk gates: WRITE_LOCAL_FS, WRITE_CODEBASE, requirements file generation, optional CALL_PROCESS.
- Dataset downloads, dependency installs, and training are forbidden unless separately approved.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Scaffold code is not validated research output.
- Generated scaffolds need user/project adaptation.
- No results can be claimed until experiments are run and analyzed.
