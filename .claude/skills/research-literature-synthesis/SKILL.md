---
name: research-literature-synthesis
description: Turns an evidence ledger or provided papers into literature review and related work synthesis while separating consensus, disagreement, contradictions, limitations, and gaps.
---

# Research Literature Synthesis

## Routing Card
- role: primary
- intent_signature:
  - literature review
  - related work
  - survey synthesis
  - what is known
  - 문헌 리뷰
  - 관련 연구 정리
  - 이 분야 정리
- use_when:
  - the user asks for literature review, survey, related work, or thematic synthesis.
  - provided papers or an evidence ledger need to be synthesized into a review.
- do_not_use_when:
  - hypothesis generation or active hypothesis selection; use research-literature-ideation.
  - paper search when no evidence exists; use search-paper-evidence first.
  - final manuscript claims without verified citations.
- expected_inputs:
  - evidence_ledger.json
  - provided papers
  - search strategy
  - inclusion/exclusion criteria
- expected_outputs:
  - scope
  - search strategy and verification status
  - evidence table
  - thematic synthesis
  - consensus
  - disagreements
  - contradictions
  - limitations
  - gaps
  - references
- context_targets:
  must_read:
    - evidence ledger or provided paper set
    - review scope
  read_if_needed:
    - search strategy
    - inclusion/exclusion criteria
    - domain references
  do_not_load_by_default:
    - hypothesis ideation by default
    - experiment blueprint
    - code scaffold
- risk_profile:
  reads:
    - evidence ledger
    - provided papers
    - search strategy
  writes:
    - `papers/literature_review.md` only when requested
  tools:
    - none by default
  network:
    - none by default; return to `search-paper-evidence` if more evidence is needed
  credentials:
    - none
  generated_artifacts:
    - literature review artifacts only if requested
  destructive_actions:
    - none
- entry_scene:
  - PREPARE

## Purpose
Turns an evidence ledger or provided papers into literature review and related work synthesis while separating consensus, disagreement, contradictions, limitations, and gaps.

## When To Apply
- the user asks for literature review, survey, related work, or thematic synthesis.
- provided papers or an evidence ledger need to be synthesized into a review.

## When Not To Apply
- hypothesis generation or active hypothesis selection; use research-literature-ideation.
- paper search when no evidence exists; use search-paper-evidence first.
- final manuscript claims without verified citations.

## Workflow
1. PREPARE - define scope and whether the review is narrative or systematic.
2. ACQUIRE - read evidence ledger or provided papers; if missing, return to evidence search.
3. SYNTHESIZE - group by themes, methods, datasets, metrics, and failure modes.
4. CALIBRATE - separate consensus, disagreement, contradictions, limitations, and gaps.
5. FINALIZE - write concise synthesis or `papers/literature_review.md` only when artifact intent is explicit.

## Resource and Risk Boundary
Summary:
- Reads evidence ledgers, provided papers, search strategy, and inclusion/exclusion criteria.
- Writes `papers/literature_review.md` only when explicitly requested.
- Uses no tools or network by default; return to `search-paper-evidence` if more evidence is needed.
- Uses no credentials and performs no destructive actions.
- Required checkpoints: evidence availability, citation status, verification limitations, and artifact intent.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Scope
2. Search/verification status
3. Evidence table
4. Thematic synthesis
5. Consensus and disagreements
6. Contradictions and limitations
7. Gaps
8. References

## Citation Status Contract
Use `citation_status` values: `verified`, `user_provided`, `placeholder`, `missing`, `unverified`. Separate verified claims from search limitations and assumptions. Do not turn citation gaps into final literature claims.

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
- A synthesis is only as complete as the evidence ledger.
- Citation metadata can be stale or incomplete.
- This skill does not create final hypotheses or experiment designs.
