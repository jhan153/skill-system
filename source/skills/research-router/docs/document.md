# Research Router Design Document

## Overview
`research-router` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Does not search the web, write files, generate code, create experiment scaffolds, perform statistical claims, write manuscripts, mutate memory, or touch `.system`.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Router decisions depend on explicit user intent and artifact names.
- It does not verify evidence or perform research work.
- Ambiguous multi-stage requests may need one clarification before routing.
