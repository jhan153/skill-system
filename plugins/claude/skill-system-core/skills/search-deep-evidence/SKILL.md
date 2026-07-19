---
name: search-deep-evidence
description: Cross-check a claim across explicitly needed evidence lanes, preserve source dependence and contradictions, and stop at a traceable evidence set before synthesis. Use for multi-angle investigation or a stated downstream cross-lane gap.
---

# Search Deep Evidence

## Routing Card
- role: primary
- intent_signature: deep evidence sweep, multi-source fact-check, cross-lane verification, 심층 조사, 교차검증
- use_when:
  - the user explicitly needs multiple evidence types for the same claim
  - a downstream owner states a cross-lane evidence gap
- do_not_use_when:
  - one lane or authoritative lookup is sufficient
  - the primary goal is synthesis, critique, implementation, or analysis without source intent
- expected_inputs: claim/question, scope, freshness, allowed lanes, existing evidence
- expected_outputs: evidence matrix, contradictions, unresolved gaps, synthesis handoff
- context_targets:
  must_read:
    - target claim/question and source constraints
  read_if_needed:
    - prior ledger; `references/deep-evidence-method.md` for a complex sweep
    - `references/evidence-ledger-v2.md` only for an explicit ledger artifact or legacy-ledger migration
  do_not_load_by_default:
    - full repo/memory, unrelated lanes, downstream report templates
- risk_profile:
  reads: scoped evidence from relevant lanes
  writes: evidence artifact only when explicitly requested
  tools: lane search/read tools within existing authority
  sensitive_resources: credentials default deny; never expand runtime, network, write, or mutation permission
- entry_scene: PREPARE

## Activation Boundary
Own acquisition only when two or more discriminating lanes are needed for the same claim. Send paper/citation-only work to `search-paper-evidence`; leave final synthesis, implementation, and ordinary analysis with their owner. Do not fan out merely because several sources exist.

## Evidence Model
Record separate axes; never overload one `verified` label:

- `acquisition_status`: `acquired | partial | inaccessible | not_acquired`
- `source_status`: `verified_identity | metadata_partial | duplicate_version | corrected | retracted | unverified`
- `claim_relation`: `supports | contradicts | mixed | mentions | not_assessed`
- `evidence_basis`: exact text/table, documentation, code, runtime, visual, memory, or supplied-artifact basis
- `locator`: URL, file/line, artifact ID, section/table, or observation receipt

Source existence does not verify a claim. Verified identity and user-provided provenance are not truth or a claim relation.

## Workflow
1. Define claim scope, freshness, and observations that would support or contradict it; split only independently falsifiable subclaims.
2. Select only lanes expected to discriminate the claim; never target a fixed count.
3. Acquire through each lane owner within existing authority. Keep inaccessible or partial lanes visible.
4. Record provenance, basis, locator, directness, authority, independence, recency, and limitations.
5. Search for disconfirming evidence and alternative explanations.
6. Collapse duplicate/dependent sources before weighing agreement.
7. Preserve unresolved disagreement: one direct contradiction may outweigh many derivative mentions; no majority vote decides truth.
8. Return the evidence set and named synthesis/review handoff, without performing that synthesis.

## Output
For one focused claim, return the strongest supporting and contradicting evidence, verdict limits, and links. Use a full ledger only for an explicit artifact or multiple claims; then read `references/evidence-ledger-v2.md` and run `check_evidence_ledger.py`. Conclusions are `supported | contradicted | mixed | insufficient`, with underlying records and uncertainty retained.

## Validation
- Every retained claim relation has an exact evidence locator and basis.
- Source identity/metadata status is separate from claim support.
- Contradictory, dependent, partial, and unavailable evidence remains visible.
- Stop at evidence and explicit limits; never substitute agent consensus for unavailable evidence or claim completeness.
