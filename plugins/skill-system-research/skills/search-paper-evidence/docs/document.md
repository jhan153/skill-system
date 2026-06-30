# Search Paper Evidence Design Document

## Overview
`search-paper-evidence` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Network is allowed only when search is needed and permitted.
- Writes are limited to explicit evidence artifacts.
- No credentials, dataset downloads, dependency installs, or training.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Search tools may be unavailable or incomplete.
- Retrieved metadata may omit authors, year, or venue.
- Evidence ledgers organize sources; they do not prove claims by themselves.
- Current literature claims require date-stamped search context.
