---
name: search-paper-evidence
description: Acquire and verify paper/reference evidence for an explicit literature, citation, or current-research request, or a downstream paper-evidence gap. Return traceable sources and claim relations without inventing papers, identifiers, metadata, datasets, metrics, or results.
---

# Search Paper Evidence

## Routing Card
- role: primary
- intent_signature:
  - paper/citation search, latest research, literature evidence, arXiv/DOI references, 최신 논문, 문헌 근거
- use_when:
  - the user explicitly asks to find papers/citations or verify a literature-backed claim.
  - a research/report owner identifies a concrete paper-evidence gap.
- do_not_use_when:
  - only provided papers may be used, one supplied paper only needs summarization, or the task is ordinary implementation/analysis.
- expected_inputs:
  - topic/claim, date range, source constraints, desired evidence role, and provided papers when any
- expected_outputs:
  - date-stamped search result or query plan, retrievable sources, claim relations, missing evidence, and limitations
- context_targets:
  must_read:
    - search question and source/date constraints
  read_if_needed:
    - provided papers and prior evidence ledger
  do_not_load_by_default:
    - full repo, full memory bank, experiment scaffold, or manuscript templates
- risk_profile:
  reads:
    - user request, provided papers, and acquired source metadata/content
  writes:
    - evidence artifact only when explicitly requested
  tools:
    - authoritative web/paper search and source opening when evidence acquisition is needed
  sensitive_resources:
    - credentials default deny; no dataset download, dependency install, or training
- entry_scene:
  - PREPARE

## Acquisition and Claim Model
Track separate fields:

- `acquisition_status`: `acquired | partial | inaccessible | not_acquired`
- `source_status`: `verified_identity | metadata_partial | duplicate_version | corrected | retracted | unverified`
- `claim_relation`: `supports | contradicts | mixed | mentions | not_assessed`
- `evidence_basis`: `title | abstract | full_text | table | supplement | metadata_only`
- `locator`: direct URL/identifier plus section, page, table, or passage when a claim relation is assessed

`user_provided` belongs in provenance. A confirmed DOI/title proves source identity, not that the paper supports the requested claim.

## Workflow
1. Define the claim/topic, date range, inclusion boundary, and evidence roles.
2. Design the smallest query set that can find supporting, contradicting, baseline, dataset/metric, survey, and failure-mode evidence relevant to the question.
3. Search current authoritative sources when recency matters; record the search date.
4. Verify paper identity and open the strongest accessible source before assigning claim relation.
5. Deduplicate preprint/published versions and check correction/retraction status when material.
6. Record evidence basis and exact locator; abstract-only access cannot support a full-text-specific claim.
7. Rank by relevance, directness, study quality, and independence—not keyword frequency.
8. Return missing evidence and search limitations explicitly.

## Output
Match depth to the request:

- Simple paper list: concise citations/links, relevance, access/evidence limitation, and search date.
- Claim verification: supporting and contradicting records with evidence basis and locators.
- Explicit ledger artifact: structured acquisition/source/claim fields, query plan, missing evidence, and limitations.

Do not force a nine-section ledger around a request for two references.

## Behavior Cases
- Positive: “2024년 이후 이 claim을 지지하거나 반박하는 논문과 직접 링크를 찾아줘.”
- Negative: “첨부한 PDF 하나만 요약해줘.” → direct paper reading/summarization, not this search lane.
- Edge: a paywalled abstract and its published/preprint duplicate exist → deduplicate, label partial evidence, and do not claim full-text support.

## Validation
- No source is returned without a retrievable locator.
- Current/latest claims have a fresh search date.
- Source identity, provenance, and claim relation remain separate.
- Corrections/retractions and duplicate versions are not silently ignored.
- Missing access or tools yields a query plan/`not_acquired`, never fabricated evidence.

## Known Limits
- Search coverage and metadata can be incomplete.
- Evidence organization does not by itself establish causal or field-wide truth.
