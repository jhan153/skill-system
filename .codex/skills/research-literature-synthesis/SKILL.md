---
name: research-literature-synthesis
description: Synthesize an existing paper set or evidence ledger into an evidence-calibrated map of themes, methods, consensus, disagreements, contradictions, limitations, and gaps. Use for literature understanding; use manuscript writing to turn an accepted synthesis into publication prose.
---

# Research Literature Synthesis

## Routing Card
- role: primary
- intent_signature:
  - literature review, survey synthesis, evidence map, related-work analysis, 문헌 종합
- use_when:
  - the user wants to understand what an existing evidence set collectively shows.
- do_not_use_when:
  - papers still need acquisition (`search-paper-evidence`).
  - the task is gap-derived hypothesis selection (`research-literature-ideation`).
  - an accepted synthesis must be rewritten as venue-ready prose (`research-manuscript-writing`).
- expected_inputs:
  - paper set/evidence ledger, scope, and search/coverage status
- expected_outputs:
  - evidence-calibrated themes, agreements, contradictions, limitations, and coverage gaps
- context_targets:
  must_read:
    - evidence set and review scope
  read_if_needed:
    - search strategy, inclusion/exclusion rules, and full-text loci for disputed claims
  do_not_load_by_default:
    - unrelated corpus, experiment code, hypothesis backlog, or manuscript templates
- risk_profile:
  reads:
    - provided papers and evidence artifacts
  writes:
    - review artifact only when explicitly requested
  tools:
    - none by default; missing evidence returns to acquisition
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Synthesis Standard
1. State the review scope, search date/coverage, and whether the evidence set is narrative, systematic, or opportunistic.
2. Normalize the unit of comparison: task, population/data, intervention/method, comparator, outcome/metric, and study design.
3. Group evidence by the question it answers, not merely by paper title or chronology.
4. For each theme, distinguish:
   - convergent result under comparable conditions;
   - disagreement explained by data, method, metric, or design differences;
   - unresolved contradiction;
   - limitation or uncovered boundary condition.
5. Weight directness, source quality, study design, independence, and evidence basis; do not use paper count as consensus.
6. Separate a field gap from a coverage gap in the supplied/search corpus.

`user_provided` is provenance, not verification. Track source acquisition/metadata status separately from whether a source supports, contradicts, or only mentions a claim.

## Output
For a focused question, answer with the synthesis and the strongest limiting evidence. For an explicit review artifact, add scope/coverage, compact evidence table, thematic synthesis, agreements/disagreements, contradictions, limitations, gaps, and references. Omit categories not supported by the evidence.

## Behavior Cases
- Positive: “이 evidence ledger를 방법·dataset·metric 차이를 반영해 문헌 흐름으로 종합해줘.”
- Negative: “이 synthesis를 journal Related Work 문체로 써줘.” → `research-manuscript-writing`.
- Edge: three abstract-only preprints agree but one full study contradicts them → preserve the conflict and evidence asymmetry; do not vote by paper count.

## Validation
- Every synthesized claim has source anchors and an evidence-basis note.
- Apparent disagreement is checked for non-comparable conditions.
- Coverage limits and source dependence are explicit.
- No missing literature is turned into a novelty claim.
