---
name: research-manuscript-writing
description: Write or revise scientific manuscript prose from verified research artifacts while preserving claim-to-evidence traceability and separating planned methods from completed results. Use for manuscript sections, not evidence search, analysis, or peer-review verdicts.
---

# Research Manuscript Writing

## Routing Card
- role: primary
- family: research
- intent_signature: manuscript section, paper draft, IMRAD, LaTeX prose, 논문 작성
- use_when: existing evidence/synthesis/method/result artifacts can support requested scientific prose
- do_not_use_when: citation acquisition, data analysis, or critique/review is primary
- expected_inputs: target section/audience plus identified supporting artifacts and evidence stage
- expected_outputs: calibrated prose with claim locators and a separate unresolved citation/evidence gap list
- context_targets: read the target and named artifacts; load only in-scope bibliography, venue style, synthesis, protocol, report, figures, and tables—not unrelated scaffold/corpus
- risk_profile: write manuscript files only when requested; formatting/build tools may verify presentation, while search/analysis remains with its owner; credentials denied
- entry_scene: PREPARE

## Stage Boundary
Read `references/research_stage_contract.md` only when upstream/downstream ownership, multi-stage
intent, or Plan/Handoff mapping matters. This skill owns only requested manuscript prose. Missing
evidence, statistics, or results remain named gaps and never start another stage automatically.

## Writing Contract
1. Identify section purpose, audience, contribution boundary, named canonical artifacts, and their evidence stage. Missing/mismatched artifacts remain gaps; never substitute stale results.
2. Build a compact claim map: claim → source/result → exact locator → strength/limitation.
3. Draft coherent prose with standard citation keys or the project's citation style.
4. Keep Introduction/Related Work claims distinct from Methods, Results, and Interpretation.
5. A blueprint supports planned Methods or Future Work; only actual execution/result artifacts support Results.
6. Calibrate language to evidence: association is not causation, exploratory is not confirmatory, and missing verification is not a positive result.
7. Put unresolved citation and evidence gaps in a separate list instead of polluting polished prose with status tags.

Inline markers such as `[citation needed]` belong only in an explicitly requested working draft. Never invent citations, values, tables, figures, venues, or completed experiments. A build, lint, or agent-authored prose check proves only presentation/its asserted contract, not the scientific claim or user/venue acceptance.

## Output
Return requested prose first, then only used evidence locators, unresolved claim/citation gaps, and material revision targets. Keep planned, observed, and interpreted content distinct; do not wrap a short edit in a process report or expose internal verification labels unless requested.
