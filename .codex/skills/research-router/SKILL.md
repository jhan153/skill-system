---
name: research-router
description: Route scientific evidence, hypothesis, experiment, analysis, manuscript, and review requests to one narrow Research Cluster owner without doing the specialist work.
---

# Research Router

## Routing Card
- role: router
- intent_signature: scientific stage, artifact-owner, or evidence-to-publication routing
- use_when: the research owner is unclear, stages compete, or the user asks what should happen next.
- do_not_use_when:
  - ordinary explanation, debugging, refactoring, or implementation
  - one research artifact already names a clear specialist owner
  - evidence-only lane choice: `search-router`
  - approved experiment scaffold implementation: `research-experiment-scaffold`
- expected_inputs: requested decision/artifact, latest verified upstream artifact, missing evidence or approval
- expected_outputs: one owner or explicit minimal sequence, direct context, gates, exclusions
- context_targets:
  - must_read: current request and named/provided artifact hints
  - read_if_needed: `.codex/research-routing.md` for ambiguous or multi-stage requests
  - do_not_load_by_default: full repo, research library, premature paper results, `.codex/skills/.system`
- risk_profile: route-only reads; no tools or writes; no sensitive resources
- entry_scene:
  - CLASSIFY

## Boundary
This skill chooses ownership. It does not search, synthesize, plan experiments, generate code, analyze data, write manuscripts, review them, or claim those stages succeeded.

- Cross-domain or lane-ambiguous evidence search belongs to `search-router`.
- Explicit paper-only acquisition or an evidence-ledger request may route directly to `search-paper-evidence`.
- Model, loss, metric, paper, or experiment vocabulary does not turn a concrete development request into research. Concrete implementation of a chosen method hands to `workflow-implementation`.
- Evidence search may be the first owner, but downstream claim work remains gated until its required evidence and readback exist.
- Heavy artifacts and scaffolds require explicit artifact intent, required upstream artifacts, and their own write gates.

## Stage Decision

| Requested decision/artifact | Owner | Required upstream |
| --- | --- | --- |
| cross-domain or lane-ambiguous evidence search | `search-router` | claim and evidence-domain hints |
| papers/citations or evidence ledger | `search-paper-evidence` | topic and source constraints |
| thematic literature synthesis | `research-literature-synthesis` | verified evidence ledger |
| gaps and candidate hypotheses | `research-literature-ideation` | verified evidence ledger or evidence-backed synthesis |
| claim, validation, ablation, or loss budget | `research-hypothesis-planning` | claim and baseline/evidence state |
| experiment specification without code | `research-experiment-blueprint` | selected hypothesis and constraints |
| approved experiment code skeleton | `research-experiment-scaffold` | approved blueprint and write boundary |
| result analysis or explicit pre-data analysis plan | `research-statistical-analysis` | data or pre-data planning intent |
| manuscript section or draft | `research-manuscript-writing` | evidence, results, citation status |
| manuscript critique | `research-peer-review` | draft and review goal |

## Invocation Contract
- automatic_handoff_targets: `search-router`, `search-paper-evidence`, `research-literature-synthesis`, `research-literature-ideation`, `research-hypothesis-planning`, `research-experiment-blueprint`, `research-statistical-analysis`, `research-peer-review`
- explicit_recommendation_targets: `research-experiment-scaffold`, `research-manuscript-writing`, `workflow-implementation`

Load one automatic stage owner immediately after selection. Keep experiment-scaffold and manuscript-file writers explicit even when their upstream gates are satisfied. `workflow-implementation` is recommendation-only from this research router but remains available to normal intent-matched development routing. Return the selected recommendation's canonical skill id and reason without doing its work, adding an explicit invocation requirement only when its own metadata is explicit-only. If an automatic target is absent from the current capability surface, report a plugin version/exposure mismatch rather than calling it uninstalled or replacing specialist work with router output.

## Decision Rules
1. Decide research versus development from the requested deliverable, not keywords.
2. Identify the latest verified upstream artifact. A claimed or planned artifact is not a completed upstream input.
3. Treat a verified evidence ledger as a valid direct upstream for literature ideation when it contains source-traceable gap evidence; require synthesis only when the requested artifact is collective thematic interpretation or the ledger cannot support the proposed gap relation.
4. Select exactly one owner. Only an explicitly multi-stage outcome with at least two chain-ready stages permits a sequence; set `owner` to its first stage and include it in the shortest dependency order.
5. If a required upstream artifact or write approval is missing, select the earliest stage that can produce it and keep later stages gated. Never lower the missing input to a warning or select the later owner as ready.
6. A preceding included stage may produce the next stage's input without creating a gate. Exclude later stages whose required input cannot be supplied or produced by the included sequence.
7. If the deliverable or upstream state is genuinely unclear, keep ownership with `research-router` and request that clarification.
8. Hand off without doing specialist work.

## Output Contract
Return only:
- `mode`: research or development
- `owner`: the only/first owner
- `sequence`: empty unless an explicit multi-stage outcome requires it
- `reason`: requested artifact plus upstream boundary
- `must_read`: direct upstream artifacts only
- `gates`: missing evidence, artifact, or approval
- `excluded`: tempting but premature skills

Validate that the route follows the artifact rather than incidental vocabulary, later stages stay gated, and the router performed no search, tool call, write, claim, or artifact generation.
