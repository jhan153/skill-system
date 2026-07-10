---
name: research-router
description: Routes scientific claim, experiment, analysis, manuscript, and review requests to one narrow Research Cluster owner without performing the research work.
---

# Research Router

## Routing Card
- role: router
- intent_signature:
  - scientific claim or experiment routing
  - literature-to-hypothesis workflow
  - research artifact stage selection
  - 연구 단계 선택
- use_when:
  - a scientific request spans stages or its owning research stage is unclear.
  - the user asks what should happen next in an evidence-to-publication workflow.
- do_not_use_when:
  - the request is ordinary implementation, debugging, refactoring, or explanation.
  - one narrow research stage is already clear from the requested artifact; route directly to that owner.
  - the user asks only for cross-domain or lane-ambiguous evidence search; use `search-router`.
  - the task is already an approved experiment scaffold implementation.
- expected_inputs:
  - research decision or artifact intent
  - available upstream artifact and missing evidence
- expected_outputs:
  - one owning skill or the shortest dependency-ordered sequence
  - admitted context and exclusions
- context_targets:
  must_read:
    - current request
    - named or provided artifact hints
  read_if_needed:
    - .codex/research-routing.md for ambiguous or multi-stage requests
  do_not_load_by_default:
    - full repo
    - full research skill library
    - paper results before an evidence-search route is selected
    - .codex/skills/.system
- risk_profile:
  reads:
    - request and artifact hints
  writes:
    - none
  tools:
    - none
  sensitive_resources:
    - none
- entry_scene:
  - CLASSIFY

## Boundary

This skill chooses ownership; it does not search, synthesize, plan experiments, generate code, analyze data, write manuscripts, or review them.

- Cross-domain or lane-ambiguous evidence search belongs to `search-router`. Explicit paper-only acquisition or an evidence-ledger request may route directly to `search-paper-evidence`.
- A scientific decision that depends on missing evidence stays owned by this router's selected research stage, with evidence search first in the sequence.
- Model, loss, metric, paper, or experiment vocabulary does not turn a concrete development request into research.
- Heavy artifact or scaffold skills require explicit artifact intent and their own write gates.

## Stage Decision

| User's decision or available input | Owner | Required upstream input |
| --- | --- | --- |
| cross-domain or lane-ambiguous evidence search | `search-router` | claim and evidence-domain hints |
| explicit papers/citations acquisition or evidence ledger | `search-paper-evidence` | topic and source constraints |
| thematic literature synthesis | `research-literature-synthesis` | verified evidence ledger |
| gaps and candidate hypotheses | `research-literature-ideation` | evidence-backed synthesis |
| claim, validation plan, ablation, or loss budget | `research-hypothesis-planning` | claim plus baseline/evidence state |
| experiment specification without code | `research-experiment-blueprint` | selected hypothesis and constraints |
| approved experiment code skeleton | `research-experiment-scaffold` | approved blueprint and write boundary |
| result-table analysis or analysis plan | `research-statistical-analysis` | data, or explicit pre-data planning intent |
| manuscript section or draft | `research-manuscript-writing` | evidence and results with citation status |
| manuscript critique | `research-peer-review` | draft and review goal |

When several stages are requested, return only the dependency-ordered stages needed for that deliverable. Do not route to later stages when their required upstream artifact is absent.

## Workflow

1. Decide `research` versus `development`; exit to normal scheduling for development.
2. Identify the decision being requested and the latest verified upstream artifact.
3. Select exactly one owner, or the shortest sequence when the user explicitly requests a multi-stage outcome.
4. Mark missing upstream evidence, write approvals, and unrelated heavy skills as gates or exclusions.
5. Hand off without doing the specialist work.

## Output Contract

Return a compact route:

- `mode`: research or development
- `owner`: one skill, or `sequence` when needed
- `reason`: the decision/artifact boundary that determined ownership
- `must_read`: only direct upstream artifacts
- `gates`: missing evidence or approval
- `excluded`: tempting but premature skills

## Validation

- The owner matches the requested decision, not incidental keywords.
- Cross-domain or lane-ambiguous evidence search does not displace `search-router`; explicit paper-only acquisition may route directly, and development does not enter the cluster.
- No later stage is selected without its required upstream artifact or explicit missing-input gate.
- The router performed no search, writes, tool calls, claims, or artifact generation.
- Focused positive and competing negative cases remain in the canonical routing eval suites.
