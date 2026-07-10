---
name: search-router
description: "Route cross-domain evidence-search requests (papers, code, runtime, visual, memory, project knowledge) to the right evidence lane without owning final synthesis, implementation, or reporting."
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
  - evidence domain hints (paper, code, runtime, visual, memory, project knowledge)
  - existing artifacts when available
- expected_outputs:
  - selected evidence lane and handoff to the owning skill; no writes of its own
- context_targets:
  must_read:
    - request intent and evidence domain hints
  read_if_needed:
    - `references/evidence-lane-matrix.md` when two lanes remain plausible
    - `.codex/research-routing.md` when paper search may actually be a research-lifecycle request
  do_not_load_by_default:
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - request and artifact hints only
  writes:
    - none
  tools:
    - none; lane owners perform acquisition
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - ROUTE

## Decision Contract
1. Require explicit evidence intent: search, source, proof, citation, verification, or ledger. Bare domain words and ordinary implementation do not qualify.
2. Identify the final task owner (implementation, planning, analysis, research, design, or report). Keep that skill primary.
3. Select exactly one lane from the table. Use `search-deep-evidence` only when multiple independent lanes are necessary to establish the same claim.
4. Return the selected owner, admitted inputs, exclusions, and handoff. Do not collect evidence, synthesize findings, call tools, or write files.

## Evidence Lanes
| evidence needed | lane owner | routing note |
| --- | --- | --- |
| papers, citations, literature | `search-paper-evidence` | support an implementation/plan; use `research-router` as primary only for scientific claim/experiment/manuscript decisions |
| multi-angle cross-domain verification | `search-deep-evidence` | require a stated reason one lane is insufficient |
| codebase behavior or structure | `analysis-codebase` | use `analysis-bug` instead for a concrete failure/RCA signal |
| runtime/test/change evidence | active implementation workflow with `workflow-rigor` as needed | do not turn execution into a search artifact |
| screenshots or rendered UI | `design-visual-regression` | use `design-a11y-audit` for keyboard/semantic/contrast evidence |
| accepted project memory | `memory-bank-harness` | use `memory-bank-maintenance` only for explicit state review/mutation |
| Wiki/Runtime Projection knowledge | `knowledge-context-harness` | use `knowledge-base-maintenance` only for explicit store review/mutation |

If lane choice remains ambiguous after reading the request, consult `references/evidence-lane-matrix.md` or ask one question that changes the lane. Do not open several lanes speculatively.

## Output Contract
Return only:
- `evidence_intent_and_domain`
- `final_task_owner`
- `selected_lane` and why it is sufficient
- `handoff` (inputs, expected evidence, exclusions, and `Unverified` gaps)

## Validation and Stop Rules
- Confirm explicit evidence intent exists and the selected lane matches the evidence type.
- Confirm one lane is selected, or justify `search-deep-evidence` with a real cross-lane need.
- Confirm the final task owner remains separate from the evidence owner.
- Stop and defer to normal routing when evidence intent is absent.
- Stop after handoff; this router performs no search, network access, synthesis, implementation, report generation, or research-stage decision.
- Never invent tool availability, sources, citations, results, or evidence quality.

## Known Limits
- This router cannot assess evidence quality or availability; the lane owner does.
- Ambiguous requests may require one decision-bearing clarification.
