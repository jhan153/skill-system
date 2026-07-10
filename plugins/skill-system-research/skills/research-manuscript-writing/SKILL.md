---
name: research-manuscript-writing
description: Write or revise scientific manuscript prose from verified research artifacts while preserving claim-to-evidence traceability and separating planned methods from completed results. Use for manuscript sections, not evidence search, analysis, or peer-review verdicts.
---

# Research Manuscript Writing

## Routing Card
- role: primary
- intent_signature:
  - manuscript section, paper draft, IMRAD, LaTeX prose, 논문 작성
- use_when:
  - the user wants scientific prose from an existing evidence/synthesis/method/result artifact.
- do_not_use_when:
  - citations still need acquisition, data still need analysis, or critique is the primary goal.
- expected_inputs:
  - target section/audience and the evidence, method, result, or existing draft that can support it
- expected_outputs:
  - calibrated manuscript prose plus a separate citation/claim gap list
- context_targets:
  must_read:
    - target section and supporting artifacts
  read_if_needed:
    - bibliography, venue style, literature synthesis, protocol, analysis report, and figures/tables actually in scope
  do_not_load_by_default:
    - unrelated experiment scaffold, full corpus, or planned results presented as completed
- risk_profile:
  reads:
    - accepted evidence and target manuscript artifacts
  writes:
    - manuscript files only when explicitly requested
  tools:
    - local formatting/build checks when relevant; search/analysis stays with its owner
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Claim-to-Evidence Workflow
1. Identify section purpose, audience, contribution boundary, and available evidence stage.
2. Build a compact internal claim map: claim → source/result → exact locator → strength/limitation.
3. Draft coherent prose with standard citation keys or the project's citation style.
4. Keep Introduction/Related Work claims distinct from Methods, Results, and Interpretation.
5. A blueprint supports planned Methods or Future Work; only actual execution/result artifacts support Results.
6. Calibrate language to evidence: association is not causation, exploratory is not confirmatory, and missing verification is not a positive result.
7. Put unresolved citation and evidence gaps in a separate list instead of polluting polished prose with status tags.

Inline markers such as `[citation needed]` are appropriate only for an explicitly requested working draft. Never invent citations, values, tables, figures, venues, or completed experiments.

## Output
Return the requested prose first. Add only the evidence sources used, unresolved claim/citation gaps, and next revision targets that materially affect the text. Do not force a six-section process report around a short paragraph edit.

## Behavior Cases
- Positive: “실제 analysis report와 refs.bib를 근거로 Results와 Discussion을 써줘.”
- Negative: “이 주장에 맞는 최신 citation을 찾아줘.” → `search-paper-evidence`.
- Edge: methods are planned but no experiment ran → write planned Methods/Future Work only; do not create Results language.

## Validation
- Material claims resolve to actual evidence or appear in the separate gap list.
- Citation keys/links exist in the supplied project evidence.
- Planned, observed, and interpreted content remain distinct.
- Polished prose contains no internal verification labels unless requested.
