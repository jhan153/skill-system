# Research Statistical Analysis Design Document

## Overview
`research-statistical-analysis` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads real result data, configs, and design descriptions.
- Writes `analysis/statistical_report.md` only when requested.
- No network, credentials, fabricated data, or fabricated conclusions.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Statistical validity depends on design and data quality.
- Missing raw data limits what can be checked.
- This skill cannot turn exploratory results into confirmatory evidence.
