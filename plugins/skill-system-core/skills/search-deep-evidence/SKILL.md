---
name: search-deep-evidence
description: Cross-check a claim across explicitly needed evidence lanes, preserve source dependence and contradictions, and stop at a traceable evidence set before synthesis. Use for multi-angle investigation or a stated downstream cross-lane gap.
---

# Search Deep Evidence

## Routing Card
- role: primary
- family: search
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
    - `references/evidence-set.md` only for an explicitly requested persisted evidence artifact
  do_not_load_by_default:
    - full repo/memory, unrelated lanes, downstream report templates
- risk_profile:
  reads: scoped evidence from relevant lanes
  writes: evidence artifact only when explicitly requested
  tools: lane search/read tools within existing authority
  sensitive_resources: credentials default deny; never expand runtime, network, write, or mutation permission
- entry_scene: PREPARE

## Activation Boundary
Use two or more discriminating lanes for the same claim; several sources alone do not require fan-out.
Paper/citation-only work uses `search-paper-evidence` when exposed. Use available lane tools without
requiring or installing sibling plugins.

## Evidence Model
Record separate axes; never overload one `verified` label:

- `acquisition_status`: `acquired | partial | inaccessible | not_acquired`
- `source_status`: an identity assessment plus independent, source-kind-relevant version/correction/retraction observations
- `claim_relation`: `supports | contradicts | mixed | mentions | not_assessed`
- `evidence_basis`: exact text/table, documentation, code, runtime, visual, memory, or supplied-artifact basis
- `locator`: URL, file/line, artifact ID, section/table, or observation receipt

Source existence does not verify a claim. Verified identity and user-provided provenance are not truth or a claim relation.

`source_status` is faceted, not one exclusive enum. Identity is `verified_identity`,
`metadata_partial`, `unverified`, or `unknown`; `duplicate_version`, `corrected`, and `retracted`
are independent observations in the applicable version, correction, and retraction facets. Carry
all evidenced facts together with their locators. For example, a paper may have
`identity=verified_identity; version=duplicate_version; correction=corrected; retraction=retracted`.
Use `unknown` for each relevant facet that is not established; omit inapplicable facets for a source
kind without treating omission as a checked negative. A negative status check records its bounded
source/date/scope and never proves universal absence of notices.

An existing scalar retains only the fact it states: `corrected` does not verify identity or imply
no retraction, and `verified_identity` does not imply a unique, uncorrected, unretracted source.
Keep the other relevant facets unknown and preserve existing records without automatic migration.
Compact inline prose may carry these distinctions; only an explicitly requested artifact uses the
evidence-set form.

## Workflow
1. Define claim scope, freshness, and observations that would support or contradict it; split only independently falsifiable subclaims.
2. Select only lanes expected to discriminate the claim; never target a fixed count.
3. Acquire through each exposed lane owner within existing authority. If an owner or evidence
   surface is unavailable, keep that lane unavailable and continue independent discriminating
   lanes; never invent an alias or substitute another lane's evidence.
4. Record provenance, basis, locator, directness, authority, independence, recency, and limitations; preserve incoming status facets and legacy unknowns instead of collapsing them into one preferred status.
5. Search for disconfirming evidence and alternative explanations.
6. Collapse duplicate/dependent sources before weighing agreement.
7. Preserve unresolved disagreement: one direct contradiction may outweigh many derivative mentions; no majority vote decides truth.
8. Return the evidence set and named synthesis/review handoff.

## Output
For one focused claim, return the strongest supporting and contradicting evidence, conclusion
limits, and links. Multiple claims may remain a compact inline matrix. Only when the user explicitly
requests a persisted evidence artifact, read `references/evidence-set.md` and write that
provider-neutral shape. Conclusions are `supported | contradicted | mixed | insufficient`, with
underlying records and uncertainty retained.

## Validation
- Every retained claim relation has an exact evidence locator and basis.
- Source identity, independent lifecycle/version observations, and claim support stay separate; a legacy scalar establishes only its declared facet.
- Contradictory, dependent, partial, and unavailable evidence remains visible.
- Stop at evidence and explicit limits; never substitute agent consensus for unavailable evidence or claim completeness.
