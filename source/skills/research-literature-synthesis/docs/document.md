# Research Literature Synthesis Design Document

## Overview
`research-literature-synthesis` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads evidence artifacts and provided papers.
- Writes review artifacts only when requested.
- No network by default; route back to evidence search if more evidence is required.
- No credentials.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- A synthesis is only as complete as the evidence ledger.
- Citation metadata can be stale or incomplete.
- This skill does not create final hypotheses or experiment designs.
