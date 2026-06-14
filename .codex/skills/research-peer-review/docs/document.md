# Research Peer Review Design Document

## Overview
`research-peer-review` is a narrow Research Cluster skill. It exists to keep scientific workflows evidence-grounded while preventing a broad all-in-one research lifecycle skill from stealing unrelated tasks.

## Position In Artifact Chain
See `.codex/research-routing.md` for the full chain and owning skill map.

## Boundary
Summary:
- Reads the review target and evidence anchors.
- Writes `review/peer_review.md` only when requested.
- No network by default and no credentials.
- Does not claim venue authority or fabricate reviewer identity.

## Non-Goals
- Do not install or emulate `codex-research-lifecycle` as a single skill.
- Do not modify `.codex/skills/.system`.
- Do not create audio/transcribe/speech custom skills.
- Do not weaken ordinary development routing.

## Validation Focus
- Peer review is advisory and not a venue decision.
- Findings depend on the provided manuscript/proposal slice.
- External literature verification requires explicit search.
