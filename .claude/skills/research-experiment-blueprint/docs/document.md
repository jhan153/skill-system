# Research Experiment Blueprint Design Document

## Overview
`research-experiment-blueprint` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads research artifacts and targeted domain references.
- Writes `papers/experiment_blueprint.json` only when requested.
- No code writes, dataset downloads, dependency installs, or training.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- A blueprint does not guarantee experimental success.
- Dataset licenses and availability must be verified before use.
- Metric selection can still miss human or deployment relevance.
