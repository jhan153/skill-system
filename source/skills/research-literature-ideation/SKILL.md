---
name: research-literature-ideation
description: Derive research-gap hypotheses from an evidence ledger or literature synthesis, preserving claim provenance and distinguishing observed gaps from speculative novelty. Use to generate/rank candidates and, when requested, select one active hypothesis for validation.
---

# Research Literature Ideation

## Routing Card
- role: primary
- intent_signature:
  - research gaps, candidate hypotheses from literature, active hypothesis, 문헌 기반 연구 아이디어
- use_when:
  - the user wants evidence-derived gaps or hypotheses from an existing paper set/synthesis.
- do_not_use_when:
  - evidence still needs acquisition (`search-paper-evidence`) or synthesis (`research-literature-synthesis`).
  - the starting point is a raw user premise with no literature dependency (`research-hypothesis-planning`).
- expected_inputs:
  - evidence ledger or synthesis, research scope, and selection constraints
- expected_outputs:
  - evidence-linked gap map, candidate hypotheses, ranking, selected hypothesis when requested, and backlog
- context_targets:
  must_read:
    - evidence ledger/synthesis and requested research scope
  read_if_needed:
    - only the papers or domain references needed to resolve a candidate's provenance
  do_not_load_by_default:
    - full corpus, code scaffold, manuscript, or statistical results unrelated to the gaps
- risk_profile:
  reads:
    - accepted evidence artifacts and selected sources
  writes:
    - ideation artifact only when explicitly requested
  tools:
    - no search by default; missing evidence routes back to acquisition
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Gap-to-Hypothesis Workflow
1. Identify evidence-supported tensions: contradictory findings, uncovered boundary conditions, method/data/metric mismatch, failure mode, or missing comparison.
2. Distinguish:
   - observed gap: directly supported by the reviewed evidence;
   - coverage gap: absent from this corpus but not necessarily from the field;
   - speculative opportunity: plausible mechanism needing evidence.
3. Generate only candidates that connect a gap to a mechanism and falsifiable outcome.
4. Tag every premise with its source role (`paper`, `dataset`, `experiment`, `math`, or `assumption`).
5. Rank candidates by evidence basis, identifiability, expected information gain, feasibility, and risk—not novelty wording.
6. Select one active hypothesis only when the user wants a next experiment; otherwise return a ranked shortlist without pretending a decision.
7. Move non-selected candidates to a backlog with the evidence needed to reconsider them.

Absence from the current search set is not proof of novelty. Current novelty claims require a fresh, appropriately scoped literature search.

## Output
Return the gap evidence, candidate mechanism/claim/falsifier, ranking rationale, active hypothesis if requested, and missing evidence. Keep the output proportional; do not emit a large idea catalog by default.

## Behavior Cases
- Positive: “이 evidence ledger의 모순에서 검증 가능한 가설 후보를 만들고 하나를 골라줘.”
- Negative: “관련 논문부터 찾아줘.” → `search-paper-evidence`.
- Edge: the corpus lacks a topic → label a coverage gap, not a novel research gap.

## Validation
- Every observed gap points to evidence; every speculation is labeled.
- Each retained hypothesis includes a mechanism, scope, observable prediction, and falsifier.
- Ranking reasons are distinct from popularity or rhetorical novelty.
- Selection is omitted when the user asked only for exploration.
