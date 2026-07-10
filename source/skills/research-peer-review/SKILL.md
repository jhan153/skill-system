---
name: research-peer-review
description: Review a scientific manuscript, proposal, or research plan for validity, evidential support, reproducibility, ethics/reporting, and revision priority. Use for scholarly peer-review critique; do not claim venue authority or review generic software artifacts.
---

# Research Peer Review

## Routing Card
- role: review_gate
- intent_signature:
  - scholarly peer review, manuscript/proposal review, reviewer critique, 논문 리뷰
- use_when:
  - the user wants a scientific review of a manuscript, proposal, or research plan.
- do_not_use_when:
  - the target is a generic code/spec/release artifact (`report-critical`) or the user wants manuscript rewriting as the primary task.
- expected_inputs:
  - review target, scope, criteria, and supporting evidence when available
- expected_outputs:
  - prioritized anchored findings with scientific consequence and actionable revision
- context_targets:
  must_read:
    - review target and requested stance/scope
  read_if_needed:
    - cited sources, protocol, analysis artifacts, venue criteria, and reporting checklist relevant to a finding
  do_not_load_by_default:
    - unrelated literature, hidden experiment assumptions, or statistical reanalysis not requested
- risk_profile:
  reads:
    - review target and selected supporting evidence
  writes:
    - review artifact only when explicitly requested
  tools:
    - none by default; external verification is separate and must be disclosed
  sensitive_resources:
    - credentials default deny; do not fabricate reviewer identity
- entry_scene:
  - PREPARE

## Review Standard
Lead with actionable findings, ordered by scientific consequence.

For each material finding include:

- exact section/claim/table/figure anchor
- observed issue and evidence
- consequence for validity, interpretation, reproducibility, ethics, or reporting
- severity (`major`, `minor`, or question/clarification)
- smallest useful revision or discriminating check

Assess validity and evidential support before novelty or presentation. Separate flaws in the work from evidence unavailable in the reviewed slice. Do not infer hidden methods, data, or results.

Review dimensions are conditional, not mandatory headings: research question/contribution, study design, data, methods, statistics, results, interpretation, reproducibility, ethics/reporting, citations, and presentation.

## Output
Return prioritized findings first. Add a short neutral contribution summary and overall assessment only when useful. Omit empty “ethics,” “minor concerns,” or other sections rather than filling them with boilerplate. An author-facing revision plan is optional and should follow the findings, not replace them.

## Behavior Cases
- Positive: “이 manuscript를 validity와 reproducibility 중심으로 peer review해줘.”
- Negative: “이 API spec이 release-ready인지 리뷰해줘.” → `report-critical`.
- Edge: only Methods are provided → review that slice and list unavailable evidence; do not judge unseen Results.

## Validation
- Every major concern has a target anchor and scientific consequence.
- Claims about citations or current literature are verified or explicitly limited.
- Recommendations address the cause, not only wording.
- The response does not impersonate a venue decision or reviewer identity.
