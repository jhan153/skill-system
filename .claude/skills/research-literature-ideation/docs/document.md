# Research Literature Ideation Design Document

## Overview
`research-literature-ideation` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads evidence/literature artifacts and domain references.
- Writes ideation artifacts only with explicit artifact intent.
- No network by default; route back to evidence search when evidence is missing.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Candidate hypotheses are scaffolds, not validated conclusions.
- Evidence gaps can make all hypotheses tentative.
- Intuition-only claims must remain `[assumption]`.
