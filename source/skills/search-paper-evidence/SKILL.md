---
name: search-paper-evidence
description: Acquire traceable paper evidence for an explicit literature/citation request or downstream paper gap. Separate source identity, access, and claim relation; never invent papers, metadata, datasets, metrics, or results.
---

# Search Paper Evidence

## Routing Card
- role: primary
- family: search
- intent_signature: paper/citation search, latest research, literature evidence, arXiv/DOI, 최신 논문, 문헌 근거
- use_when:
  - the user explicitly requests papers/citations or literature-backed claim verification
  - a downstream owner states a concrete paper-evidence gap
- do_not_use_when:
  - only supplied papers may be used, one paper needs summarization, or the task lacks source intent
- expected_inputs: topic/claim, date range, source constraints, evidence role, supplied papers
- expected_outputs: date-stamped result or query plan, retrievable sources, claim relations, gaps, limits
- context_targets:
  must_read:
    - search question and source/date constraints
  read_if_needed:
    - provided papers and prior paper/evidence set
  do_not_load_by_default:
    - full repo/memory, experiment scaffold, manuscript templates
- risk_profile:
  reads: request, supplied papers, acquired metadata/content
  writes: evidence artifact only when explicitly requested
  tools: authoritative paper/web search and source opening when needed
  sensitive_resources: credentials default deny; no dataset download, install, or training
- entry_scene: PREPARE

### Resource Closure

```json
[]
```

## Acquisition and Claim Model
Track separate fields; never collapse them into `verified`:

- `acquisition_status`: `acquired | partial | inaccessible | not_acquired`
- `source_status`: an identity assessment plus independent version/correction/retraction observations, as below
- `claim_relation`: `supports | contradicts | mixed | mentions | not_assessed`
- `evidence_basis`: `title | abstract | full_text | table | supplement | metadata_only`
- `locator`: retrievable URL/identifier plus section/page/table/passage for assessed relations

`user_provided` is provenance. A confirmed DOI/title proves source identity, not claim support.
`acquired` requires content sufficient for the recorded basis; identity/landing-page/metadata-only access is `partial` with a limitation.

Treat `source_status` as facets, not mutually exclusive alternatives. Identity may be
`verified_identity`, `metadata_partial`, `unverified`, or `unknown`; independently retain an evidenced
`duplicate_version`, `corrected`, or `retracted` fact in its matching version, correction, or
retraction facet. For example, one compact status cell can say
`identity=verified_identity; version=duplicate_version; correction=corrected; retraction=retracted`
when the actual locators support all four facts. A DOI match never clears a correction or retraction.

Mark a relevant facet `unknown` when it is not established; an absent flag does not mean no notice
exists. A bounded negative check states the checked source/date/scope, not universal good standing.
Read an existing scalar as only its declared fact: legacy `corrected` leaves identity, version, and
retraction unknown; legacy `verified_identity` leaves the other facets unknown. Preserve existing
records and do not migrate or rewrite them merely to read this notation. A short inline answer may
express the same distinctions in prose; named facets are not a mandatory large schema.

## Workflow
1. Define claim/topic, date/inclusion boundary, source constraints, and needed evidence roles.
2. Use the smallest query set that can discriminate support, contradiction, baselines, datasets/metrics, and failure modes.
3. Search authoritative current sources when recency matters and record the search date.
4. Verify identity and open the strongest accessible source before assigning a claim relation.
5. Deduplicate preprint/published versions; retain identity and every independently evidenced correction/retraction/version fact together, with locators and unchecked facets visible.
6. Record basis and exact locator. Abstract-only access cannot support a full-text/table-specific claim; a keyword mention is not support.
7. Rank by relevance, directness, study quality, and independence, not frequency. Organized papers
   alone do not establish causal or field-wide truth.
8. Return unavailable/missing evidence and limitations; without search/access, return a query plan with `not_acquired`.

## Output
Match depth to intent:
- Simple list: concise citations/links, relevance, access limit, search date.
- Claim check: supporting/contradicting records with basis and locators.
- Explicit evidence artifact: structured acquisition/source/claim fields, query plan, gaps, and limits.

Never force a persisted evidence artifact around a short reference request.
