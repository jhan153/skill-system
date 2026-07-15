---
name: research-literature-synthesis
description: Synthesize an existing paper set or evidence ledger into an evidence-calibrated map of themes, methods, consensus, disagreements, contradictions, limitations, and gaps. Use for literature understanding; use manuscript writing to turn an accepted synthesis into publication prose.
---

# Research Literature Synthesis

## Routing Card
- role: primary
- intent_signature: literature review, survey synthesis, evidence map, related-work analysis, 문헌 종합
- use_when: an existing paper set/evidence ledger must be interpreted collectively
- do_not_use_when: acquisition, gap-derived hypothesis selection, or venue-ready manuscript prose is primary
- expected_inputs: identified evidence set, review question/scope, and search/coverage status
- expected_outputs: evidence-calibrated themes, agreements, contradictions, limitations, and corpus gaps
- context_targets: read the named set and scope; load search/inclusion rules and full-text loci only for disputed claims, excluding unrelated corpus, code, backlog, and manuscript templates
- risk_profile: no acquisition by default and write a review artifact only when requested; credentials denied
- entry_scene: PREPARE

## Synthesis Standard
1. State the review scope, search date/coverage, and whether the evidence set is narrative, systematic, or opportunistic.
2. Normalize the unit of comparison: task, population/data, intervention/method, comparator, outcome/metric, and study design.
3. Group evidence by the question it answers, not merely by paper title or chronology.
4. For each theme distinguish comparable convergence, disagreement explained by data/method/metric/design, unresolved contradiction, and limitation/boundary condition.
5. Weight directness, source quality, study design, independence, and evidence basis; do not use paper count as consensus.
6. Separate a field gap from a coverage gap in the supplied/search corpus.

`user_provided` is provenance, not verification. Track acquisition/metadata status separately from whether a source supports, contradicts, or only mentions a claim. If the named set/source is missing or mismatched, surface the acquisition gap; never replace it with a stale or convenient corpus.

## Output
For a focused question, lead with the synthesis and strongest limiting evidence. For an explicit artifact, include only supported scope/coverage, evidence table, themes, agreements/disagreements, contradictions, limitations, gaps, and source anchors. Preserve evidence asymmetry and dependence; never turn missing literature into consensus or novelty.
