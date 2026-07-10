---
name: search-deep-evidence
description: Gather and cross-check evidence for a claim across multiple relevant lanes such as papers, official code/docs, runtime observations, visual artifacts, memory, or project knowledge. Use for explicit multi-angle investigation or fact-checking; return an evidence set with verification records, not a final report or majority-vote verdict.
---

# Search Deep Evidence

## Routing Card
- role: primary
- intent_signature:
  - deep evidence sweep, multi-source fact-check, cross-lane verification, 심층 조사, 교차검증
- use_when:
  - the user explicitly wants multiple evidence types or a downstream owner identifies a cross-lane evidence gap.
- do_not_use_when:
  - one paper/citation lane is sufficient (`search-paper-evidence`).
  - the primary goal is final synthesis, critique, implementation, or ordinary analysis without source intent.
- expected_inputs:
  - claim/question, scope, freshness needs, allowed lanes, and existing evidence
- expected_outputs:
  - claim–evidence matrix, source status, contradictions, unresolved gaps, and synthesis handoff
- context_targets:
  must_read:
    - target claim/question and source constraints
  read_if_needed:
    - prior ledger and `references/deep-evidence-method.md`
    - `references/evidence-ledger-v2.md` only for an explicit ledger artifact or legacy-ledger migration
  do_not_load_by_default:
    - full repo, full memory bank, unrelated lanes, or downstream report templates
- risk_profile:
  reads:
    - scoped read-only evidence from relevant lanes
  writes:
    - evidence artifact only when explicitly requested
  tools:
    - lane-specific search/read tools within the user's and host's existing authority
  sensitive_resources:
    - credentials default deny; this skill never expands tool or mutation permission
- entry_scene:
  - PREPARE

## Evidence Model
Do not overload one `verified` label. Record separate axes:

- `acquisition_status`: `acquired | partial | inaccessible | not_acquired`
- `source_status`: `verified_identity | metadata_partial | duplicate_version | corrected | retracted | unverified`
- `claim_relation`: `supports | contradicts | mixed | mentions | not_assessed`
- `evidence_basis`: exact basis such as full text/table, official documentation, source code, runtime observation, screenshot, accepted memory, or user-provided artifact
- `locator`: URL, file/line, artifact ID, table/section, or observation receipt

Source existence does not verify a claim. User-provided is provenance, not truth status.

## Workflow
1. Break the question into only the claims or angles whose evidence requirements differ.
2. Select lanes by expected discriminating evidence; do not fan out to a fixed count.
3. Gather sources with the owning lane's rules. Read-only search does not authorize runtime execution, external writes, or memory mutation.
4. Build a claim–evidence matrix with provenance, directness, authority, independence, recency, and limitations.
5. Search for disconfirming evidence and alternative explanations.
6. Reconcile duplicate/dependent sources before weighing apparent agreement.
7. Preserve unresolved disagreement. One strong direct contradiction can outweigh many derivative mentions; no majority vote decides truth.
8. Return the evidence set and name the downstream synthesis/review owner when one exists.

## Output
For a focused fact-check, return the claim, strongest supporting/contradicting evidence, verdict limits, and links. Use a full ledger only for an explicit deep-evidence artifact or multiple claims. For that artifact, read `references/evidence-ledger-v2.md` and validate the result with `check_evidence_ledger.py`. The evidence set may be `supported`, `contradicted`, `mixed`, or `insufficient`, but retain the underlying records and uncertainty.

## Behavior Cases
- Positive: “이 공개 성능 주장을 논문, 공식 구현, 실제 runtime evidence로 교차검증해줘.”
- Negative: “이 주제 최신 논문 세 편만 찾아줘.” → `search-paper-evidence`.
- Edge: two lanes share the same upstream source and one independent runtime result disagrees → do not count the dependent sources as two votes; report the unresolved conflict.

## Validation
- Every retained claim relation has an exact evidence locator and basis.
- Source identity/metadata status is separate from claim support.
- Contradictory and unavailable lanes remain visible.
- No final report, implementation, or permission-expanding action is performed by this skill.

## Known Limits
- Cross-lane coverage reduces blind spots but cannot guarantee truth or completeness.
- Some runtime/private evidence may remain unavailable; do not replace it with agent consensus.
