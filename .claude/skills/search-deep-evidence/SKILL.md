---
name: search-deep-evidence
description: Runs a deep multi-angle evidence sweep across search lanes with adversarial verification and citation-status labels, producing a verified evidence set for report or synthesis skills to consume without owning final synthesis.
---

# Search Deep Evidence

## Routing Card
- role: primary
- intent_signature:
  - deep research
  - multi-source evidence
  - cross-check sources
  - fact-check
  - 심층 조사
  - 교차검증
  - evidence sweep
- use_when:
  - the user wants a broad, multi-angle investigation of a topic or claim with explicit fact-checking across more than one evidence lane.
  - a downstream report or synthesis skill needs a verified, citation-labeled evidence set before it can write.
- do_not_use_when:
  - the request is a single paper/citation lane only; use `search-paper-evidence`.
  - the user wants the final written report or literature synthesis; that is owned by `report-critical`/`report-qualitative`/`research-literature-synthesis`.
  - bare `분석`/`검토` with no evidence/source intent, or ordinary implementation.
- expected_inputs:
  - topic or claim
  - evidence lane hints (paper, code, runtime, visual, memory, project knowledge, web)
  - existing artifacts or prior ledgers when available
- expected_outputs:
  - decomposed search angles
  - per-lane evidence ledger entries
  - adversarial verification verdicts per claim
  - citation_status labels
  - verified evidence set + handoff note to the owning report/synthesis skill
- context_targets:
  must_read:
    - current request
    - topic or claim
  read_if_needed:
    - prior evidence ledger
    - `references/deep-evidence-method.md`
  do_not_load_by_default:
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - user topic or claim
    - optional search results across lanes
  writes:
    - verified evidence set only when explicitly requested
  tools:
    - lane search tools when available and permitted
  network:
    - allowed only for evidence acquisition and only when permitted
  credentials:
    - none
  forbidden_by_default:
    - final report/synthesis ownership
    - dataset downloads, dependency installs, training
- entry_scene:
  - PREPARE

## Purpose
Brings the deep-research harness shape (fan out angles, gather, adversarially verify, label confidence) into the bundle as a `search`-family specialist, while respecting the search↔synthesis boundary: it produces a verified, citation-labeled evidence set and hands final synthesis to report/research skills.

## Method
1. DECOMPOSE - split the topic/claim into 3-6 distinct search angles so one search blind spot does not hide evidence.
2. ROUTE - for each angle pick an evidence lane via `search-router` (paper, code, runtime, visual, memory, project knowledge, web).
3. GATHER - build an evidence ledger per lane reusing `search-paper-evidence` ledger discipline (no fabricated citations/DOIs/results).
4. VERIFY - for each falsifiable claim, run adversarial N-vote refutation (default 2 of 3 refutes kills the claim); record the verdict.
5. LABEL - tag every ledger entry `citation_status: verified | unverified | fabricated-risk` (shared vocabulary with `search-paper-evidence`).
6. HANDOFF - output the verified evidence set with a note naming the report/synthesis skill that should own the writeup.

## Boundary
- This skill does NOT write the final report, literature review, or synthesis prose. It stops at a verified evidence set and hands off.
- It is broader than `search-paper-evidence` (multi-lane sweep + adversarial verification), not a replacement for the single paper lane.

## Output Contract
1. Search date (`YYYY-MM-DD`)
2. Decomposed angles
3. Per-lane evidence ledger entries (claim, source, role)
4. Adversarial verification verdicts (confirmed | refuted | partial, with vote tally)
5. `citation_status` per entry (verified | unverified | fabricated-risk)
6. Verified evidence set + handoff target skill
7. Missing evidence and `Unverified` markers

## Validation
- Confirm explicit multi-source evidence/fact-check intent (not a single paper lane, not bare analysis).
- Confirm each retained claim has at least one source and a verification verdict.
- Confirm no fabricated citations, DOIs, datasets, metrics, or results were introduced.
- Confirm this skill did not produce the final report/synthesis; a handoff target is named.

## Anti-Patterns
- Owning the final synthesis or written report.
- Collapsing into `search-paper-evidence` (single lane) or duplicating `report-*`.
- Treating an unverified search hit as a conclusion.

## Known Limits
- Lane search tools may be unavailable; mark evidence `not_acquired` and fill the angle plan only.
- Adversarial verification reduces but does not eliminate false claims.

## Reference
- Read `references/deep-evidence-method.md` for the angle decomposition, lane mapping, and adversarial-verification rubric.
