---
name: search-router
description: Route explicit cross-domain evidence requests to one sufficient lane while preserving the final task owner. This router performs no acquisition, synthesis, implementation, reporting, or writes.
---

# Search Router

## Routing Card
- role: router
- intent_signature: `검색 스킬군`, evidence search, 근거 조사, source, proof, citation, verification, ledger
- use_when:
  - the user explicitly requests evidence/source acquisition across domains
  - a primary owner states an evidence gap before it can proceed
- do_not_use_when:
  - bare analysis/review without evidence intent
  - the requested result is synthesis, implementation, design change, report, or research-stage decision
- expected_inputs: claim/topic, evidence hints, final task owner, existing artifacts
- expected_outputs: one selected lane and bounded handoff; no acquisition or writes
- context_targets:
  must_read:
    - evidence intent, domain hints, and final task owner
  read_if_needed:
    - `references/evidence-lane-matrix.md` when two lanes remain plausible
    - `.claude/context-routing.md` when paper terms may hide a research-stage request
  do_not_load_by_default:
    - full repo/memory or lane artifacts
- risk_profile:
  reads: request and artifact hints only
  writes: none
  tools: none; lane owners acquire evidence
  sensitive_resources: credentials default deny
- entry_scene: ROUTE

## Decision Contract
1. Require explicit evidence intent: search, source, proof, citation, verification, or ledger. Bare domain words and ordinary implementation do not qualify.
2. Keep implementation, planning, analysis, research, design, or report as final owner.
3. Select exactly one lane from the table. Use `search-deep-evidence` only when multiple independent lanes are necessary to establish the same claim.
4. Return admitted inputs, exclusions, `Unverified` gaps, and handoff; stop without doing the lane's work.

## Evidence Lanes
| evidence needed | lane owner | routing note |
| --- | --- | --- |
| papers, citations, literature | `search-paper-evidence` | support implementation/planning; scientific claim/experiment/manuscript decisions keep `research-router` primary |
| multi-angle cross-domain verification | `search-deep-evidence` | require a stated reason one lane is insufficient |
| codebase behavior or structure | `analysis-codebase` | use `analysis-bug` instead for a concrete failure/RCA signal |
| runtime/test/change evidence | active implementation workflow with `workflow-rigor` as needed | execution stays with that workflow |
| screenshots or rendered UI | `design-visual-regression` | use `design-a11y-audit` for keyboard/semantic/contrast evidence |
| declared project Memory | `memory-bank-harness` | read only a task-relevant current slice; mutation stays with an explicit Memory owner |
| declared project Knowledge Base | `knowledge-base-read` | read only matching records; mutation stays with an explicit Knowledge owner |
| explicitly selected LLM Wiki | `llm-wiki-context` | follow that Wiki's own guide; read-only and no cross-Wiki merge |

If two lanes remain materially plausible, consult the matrix or ask one lane-changing question. Never open both speculatively.

## Invocation Contract
- automatic_handoff_targets: `search-paper-evidence`, `search-deep-evidence`, `analysis-bug`, `memory-bank-harness`, `knowledge-base-read`, `research-router`
- explicit_recommendation_targets: `analysis-codebase`, `workflow-rigor`, `design-visual-regression`, `design-a11y-audit`, `llm-wiki-context`

Load an automatic lane owner immediately after selection. A recommendation-only lane is never loaded by this router; return its canonical skill id and reason, adding an explicit invocation requirement only when that lane's own metadata is explicit-only. Do not acquire evidence in the router. If an automatic target is absent from the current capability surface, report a plugin version/exposure mismatch rather than calling it uninstalled or silently doing the lane work yourself.

## Output Contract
Return only:
- `evidence_intent_and_domain`
- `final_task_owner`
- `selected_lane` and why it is sufficient
- `handoff` (inputs, expected evidence, exclusions, and `Unverified` gaps)

## Stop Check
- Defer to normal routing when evidence intent is absent; keep final and evidence owners separate.
- Select one matching lane or record the real cross-lane reason for `search-deep-evidence`.
- Perform no search, tool/network call, evidence assessment, synthesis, implementation, report, research decision, or file write.
- Never invent availability, sources, citations, results, or quality; the lane owner determines them.
