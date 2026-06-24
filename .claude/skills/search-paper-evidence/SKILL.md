---
name: search-paper-evidence
description: Searches or plans searches for paper/reference evidence and builds evidence ledgers without hallucinating citations, papers, datasets, metrics, DOIs, or results.
---

# Search Paper Evidence

## Routing Card
- role: primary
- intent_signature:
  - latest research
  - paper evidence
  - citation search
  - literature evidence
  - related work evidence
  - claim support contradiction
  - arXiv
  - Semantic Scholar
  - OpenAlex
  - Crossref
  - 최신 논문
  - 문헌 근거
- use_when:
  - the user asks for latest research, papers, references, citations, literature evidence, or source-grounded research maps.
  - a research claim needs support, contradiction, baseline, dataset, metric, failure mode, survey, method, benchmark, or open-problem evidence.
- do_not_use_when:
  - the user says to use only provided papers.
  - an evidence ledger is already sufficient for the requested downstream work.
  - ordinary implementation or bug fixing.
  - single-paper summarization without broader evidence mapping.
- expected_inputs:
  - topic or claim
  - domain
  - time range
  - source preference
  - provided papers
  - desired evidence roles
- expected_outputs:
  - search_date
  - date_range
  - sources
  - query_plan
  - retrieved_papers
  - evidence_ledger
  - missing_evidence
  - do_not_assume
  - search_limitations
- context_targets:
  must_read:
    - current request
    - topic or claim
    - source constraints
  read_if_needed:
    - provided papers
    - prior evidence ledger
    - domain reference such as speech-enhancement-research
  do_not_load_by_default:
    - full repo
    - full memory bank
    - experiment scaffold
    - manuscript writing
- risk_profile:
  reads:
    - user topic or claim
    - provided papers
    - optional search results
  writes:
    - evidence artifacts only when explicitly requested
  tools:
    - web or paper search when available and required
  network:
    - allowed only for evidence acquisition and only when permitted
  credentials:
    - none
  generated_artifacts:
    - `papers/evidence_ledger.json` or evidence tables only if requested
  destructive_actions:
    - none
  forbidden_by_default:
    - dataset downloads
    - dependency installs
    - training
- entry_scene:
  - PREPARE

## Purpose
Searches or plans searches for paper/reference evidence and builds evidence ledgers without hallucinating citations, papers, datasets, metrics, DOIs, or results.

## When To Apply
- the user asks for latest research, papers, references, citations, literature evidence, or source-grounded research maps.
- a research claim needs support, contradiction, baseline, dataset, metric, failure mode, survey, method, benchmark, or open-problem evidence.

## When Not To Apply
- the user says to use only provided papers.
- an evidence ledger is already sufficient for the requested downstream work.
- ordinary implementation or bug fixing.
- single-paper summarization without broader evidence mapping.

## Workflow
1. PREPARE - define topic, claim, time range, domains, and source constraints.
2. QUERY DESIGN - split queries by method, dataset, metric, baseline, failure mode, survey, and contradiction.
3. ACQUIRE - use available search tools when literature-backed claims require it; if unavailable, produce query plan only.
4. NORMALIZE - capture title, authors when available, year, venue/source, URL/identifier, and relevance.
5. DEDUP/RANK - remove duplicates and classify evidence role.
6. FINALIZE - return an evidence ledger or draft artifact only when explicitly requested.

## Resource and Risk Boundary
Summary:
- Reads the user topic or claim, provided papers, and optional search results.
- Uses web/paper search only when evidence acquisition is required and permitted.
- Writes `papers/evidence_ledger.json` or evidence tables only when explicitly requested.
- Uses no credentials and performs no dataset downloads, dependency installs, or training.
- Required checkpoints: search scope, search date, source list, artifact intent, and evidence-not-acquired state when tools are unavailable.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Search date (`YYYY-MM-DD`)
2. Date range, such as `2023-2026` or user-specified
3. Sources searched or planned (`arXiv`, `Semantic Scholar`, `OpenAlex`, `Crossref`, `web`, `user_provided`)
4. Query plan
5. Retrieved papers with title, authors, year, venue, DOI, arXiv ID, URL, source, finding query, relevance, and evidence role when available
6. Evidence ledger entries with claim, label, supporting papers, contradicting papers, confidence, verification status, and notes
7. Missing evidence
8. Do not assume
9. Search limitations

## Evidence Ledger Rules
- No citation without a source.
- Do not hallucinate DOI, arXiv ID, venue, dataset, metric, or paper existence.
- Search date is mandatory for latest/current/recent research requests.
- Label each ledger entry `citation_status: verified | unverified | fabricated-risk` (shared vocabulary with `search-deep-evidence`): `verified` only when a real, retrievable source is confirmed; `fabricated-risk` when an identifier cannot be confirmed to exist; otherwise `unverified`.
- Current-source check: for latest/current/recent claims, re-confirm each entry against a fresh `search_date` before labeling it `verified`.
- If search tools are unavailable, fill the query plan and search limitations, then mark evidence as `not_acquired`.

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
- Search tools may be unavailable or incomplete.
- Retrieved metadata may omit authors, year, or venue.
- Evidence ledgers organize sources; they do not prove claims by themselves.
- Current literature claims require date-stamped search context.
