---
name: research-peer-review
description: Review a scientific manuscript, proposal, or research plan for validity, evidential support, reproducibility, ethics/reporting, and revision priority. Use for scholarly peer-review critique; do not claim venue authority or review generic software artifacts.
---

# Research Peer Review

## Routing Card
- role: review_gate
- intent_signature: scholarly peer review, manuscript/proposal review, reviewer critique, 논문 리뷰
- use_when: a manuscript, proposal, or research plan needs scientific critique
- do_not_use_when: the target is generic code/spec/release material or rewriting is primary
- expected_inputs: exact review target/slice, stance, criteria, and available supporting evidence
- expected_outputs: prioritized anchored findings with scientific consequence, evidence limits, and actionable revision/check
- context_targets: read the target and requested scope; load only cited sources, protocol, analysis artifacts, venue criteria, or checklist needed for a finding—not unrelated literature or hidden assumptions
- risk_profile: no external verification by default; disclose any verification and write a review artifact only when requested; credentials and fabricated identity denied
- entry_scene: PREPARE

## Review Contract
Lead with actionable findings ordered by scientific consequence. Each material finding needs an exact section/claim/table/figure anchor, observed issue/evidence, consequence for validity/interpretation/reproducibility/ethics/reporting, `major|minor|question` severity, and the smallest useful revision or discriminating check.

Assess validity and evidential support before novelty or presentation. Separate flaws in the work from evidence unavailable in the reviewed slice. Do not infer hidden methods, data, or results.

Review dimensions are conditional, not mandatory headings: research question/contribution, study design, data, methods, statistics, results, interpretation, reproducibility, ethics/reporting, citations, and presentation.

If the named target/source is missing or mismatched, stop or limit the review explicitly; never substitute another draft. Structural/reporting checks prove only their dimensions. Claims about current literature, citation correctness, or recomputed results require actual verification or an explicit limitation. Do not impersonate a reviewer/venue or issue an authoritative accept/reject decision.

## Output
Return prioritized findings first. Add a neutral contribution summary, bounded overall assessment, or author revision plan only when useful and after findings. Omit empty boilerplate sections. For partial targets, review only the supplied slice and list unavailable evidence without judging unseen results; if that evidence prevents the requested whole-target judgment, keep the overall result `unverified` and close only the supplied-slice review.
