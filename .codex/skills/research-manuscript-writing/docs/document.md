# Research Manuscript Writing Design Document

## Overview
`research-manuscript-writing` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads research artifacts and manuscript text.
- Writes `papers/draft/*` only with artifact intent.
- No network by default and no credentials.
- Does not invent citations, results, tables, or figures.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Writing quality depends on available evidence and results.
- It cannot invent completed experiments or verified citations.
- Venue-specific formatting may need separate style guidance.
