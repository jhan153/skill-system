---
name: research-peer-review
description: Produces peer-review-style critique for manuscripts, proposals, or research plans with major/minor concerns, reproducibility, ethics/reporting, citation issues, and revision advice.
---

# Research Peer Review

## Routing Card
- role: review_gate
- intent_signature:
  - peer review
  - reviewer 2
  - 논문 리뷰
  - proposal review
  - major concerns
  - minor concerns
  - reproducibility review
- use_when:
  - the user asks for peer-review-style critique of a manuscript, proposal, or research plan.
  - major/minor/reproducibility/ethics/reporting concerns should be separated.
- do_not_use_when:
  - general QA gate outside research; use report-critical.
  - write the manuscript as primary task.
  - fabricate reviewer identity or venue authority.
- expected_inputs:
  - manuscript/proposal/research plan
  - review criteria
  - evidence anchors
  - target venue if provided
- expected_outputs:
  - neutral summary
  - major concerns
  - minor concerns
  - reproducibility concerns
  - ethics/reporting concerns
  - evidence/citation concerns
  - revision advice
  - author-facing revision plan
- context_targets:
  must_read:
    - review target
    - review goal
  read_if_needed:
    - evidence ledger
    - analysis report
    - target venue criteria
  do_not_load_by_default:
    - manuscript writing
    - statistical reanalysis unless requested
- risk_profile:
  reads:
    - manuscript
    - proposal
    - research plan
    - supporting evidence if provided
  writes:
    - `review/peer_review.md` only when requested
  tools:
    - none by default
  network:
    - none by default
  credentials:
    - none
  generated_artifacts:
    - peer review artifact only if requested
  destructive_actions:
    - none
  forbidden_by_default:
    - claimed venue authority
    - fabricated reviewer identity
- entry_scene:
  - PREPARE

## Purpose
Produces peer-review-style critique for manuscripts, proposals, or research plans with major/minor concerns, reproducibility, ethics/reporting, citation issues, and revision advice.

## When To Apply
- the user asks for peer-review-style critique of a manuscript, proposal, or research plan.
- major/minor/reproducibility/ethics/reporting concerns should be separated.

## When Not To Apply
- general QA gate outside research; use report-critical.
- write the manuscript as primary task.
- fabricate reviewer identity or venue authority.

## Workflow
1. PREPARE - identify review target and review stance.
2. SUMMARIZE - state contribution neutrally.
3. ASSESS - separate validity, novelty, reproducibility, ethics/reporting, evidence, and presentation issues.
4. PRIORITIZE - classify major vs minor concerns.
5. ADVISE - provide concrete revision actions.
6. FINALIZE - produce review artifact only when requested.

## Resource and Risk Boundary
Summary:
- Reads the manuscript, proposal, research plan, and supporting evidence provided for review.
- Writes `review/peer_review.md` only when explicitly requested.
- Uses no tools or network by default.
- Does not claim venue authority or fabricate reviewer identity.
- Required checkpoints: review target, citation/evidence status, reproducibility concerns, and artifact intent.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Neutral summary
2. Overall assessment
3. Major concerns
4. Minor concerns
5. Reproducibility concerns
6. Ethics/reporting concerns
7. Evidence/citation concerns
8. Concrete revision advice
9. Optional author-facing revision plan

## Citation Status Review
Use `citation_status` values: `verified`, `user_provided`, `placeholder`, `missing`, `unverified` when assessing evidence and citation concerns. Flag unsupported manuscript claims without inventing references or reviewer authority.

## Validation
- Confirm `.codex/skills/.system` was not touched.
- Confirm user intent matches this skill, not ordinary development.
- Confirm required evidence or artifact inputs are present or explicitly marked missing.
- Confirm no secrets, credentials, hardcoded single-host paths, fabricated citations, or fabricated results are introduced.
- Confirm artifact writes happen only when explicitly requested.

## Anti-Patterns
- Installing or invoking monolithic `codex-research-lifecycle`.
- Treating search keywords as conclusions.
- Collapsing evidence search, ideation, blueprint, scaffold, analysis, writing, and review into one step.
- Creating custom transcribe/speech skills from research source material.
- Weakening development/implementation routing because a request mentions model, metric, loss, experiment, or training.

## Known Limits
- Peer review is advisory and not a venue decision.
- Findings depend on the provided manuscript/proposal slice.
- External literature verification requires explicit search.
