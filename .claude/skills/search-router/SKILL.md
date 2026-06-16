---
name: search-router
description: "Route cross-domain evidence-search requests (papers, code, runtime, visual, memory) to the right evidence lane without owning final synthesis, implementation, or reporting."
---

# Search Router

## Routing Card
- role: router
- intent_signature:
  - `검색 스킬군`, `evidence search`, `근거 조사`, `source`, `proof`, `ledger`
- use_when:
  - the user explicitly asks to find evidence, sources, proof, or build an evidence ledger across domains.
  - a selected primary skill explicitly needs an evidence lane before it can proceed.
- do_not_use_when:
  - bare `분석`/`검토` with no evidence/source/proof framing.
  - the user wants final synthesis, implementation, design changes, or a research-lifecycle decision.
- expected_inputs:
  - topic or claim
  - evidence domain hints (paper, code, runtime, visual, memory)
  - existing artifacts when available
- expected_outputs:
  - selected evidence lane and handoff to the owning skill; no writes of its own
- context_targets:
  must_read:
    - request intent and evidence domain hints
  read_if_needed:
    - registry Group Alias Map
    - `.codex/research-routing.md` for the paper lane
  do_not_load_by_default:
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - READ_CODEBASE only to identify the correct lane
  writes:
    - none
  tools:
    - none beyond routing selection
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - ROUTE

## Related Skills
- `search-paper-evidence`: paper/source evidence lane and ledger owner.
- `research-router`: owns the research lifecycle when the task is a scientific claim, not just evidence.
- `analysis-codebase`, `analysis-bug`: codebase evidence lanes.
- `design-visual-regression`, `design-a11y-audit`: visual evidence lanes.
- `memory-bank-harness`, `memory-bank-maintenance`: memory evidence lanes.

## Trigger
- `검색 스킬군`, `evidence search`, `근거/소스/증거 찾아줘`, `evidence ledger`

## Trigger Guard (Do Not Trigger)
- Bare `분석`/`검토`/`보고` without explicit evidence/source/proof intent.
- Requests whose actual goal is implementation, synthesis, or a publishability decision.

## Goal
- Pick the correct evidence lane and hand off; never own final synthesis or implementation.

## Evidence Lanes
- paper/source evidence -> `search-paper-evidence`
- paper evidence for implementation planning -> `search-paper-evidence` as support; implementation/planning skill stays primary
- codebase evidence -> `analysis-codebase` or `analysis-bug` evidence phase
- runtime evidence -> `workflow-rigor` evidence phase
- visual evidence -> `design-visual-regression` / `design-a11y-audit`
- memory evidence -> `memory-bank-harness` / `memory-bank-maintenance`

## Output Contract
1. Detected evidence intent and domain
2. Selected lane and owning skill
3. Handoff note (what the owner should produce)
4. Explicit `Unverified` for any missing inputs

## Resource and Risk Boundary
- Reads: only enough to choose a lane.
- Writes: none. This is a router; it must not mutate files or produce final artifacts.
- Tools/process calls: none beyond selection.
- Network/credentials: none by default; credential access default deny.

## Anti-Patterns
- Owning evidence collection or synthesis itself.
- Routing the whole task to the research cluster when the user only wanted evidence.
- Triggering on bare domain words without evidence framing.

## Known Limits
- A router cannot confirm evidence quality; the owning lane skill does that.
- If no evidence intent is present, defer to the normal Route Matrix.
