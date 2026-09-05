# Search & Evidence Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `search-deep-evidence`

- role: primary
- family: search
- intent_signature: deep evidence sweep, multi-source fact-check, cross-lane verification, 심층 조사, 교차검증
- use_when:
  - the user explicitly needs multiple evidence types for the same claim
  - a downstream owner states a cross-lane evidence gap
- do_not_use_when:
  - one lane or authoritative lookup is sufficient
  - the primary goal is synthesis, critique, implementation, or analysis without source intent
- expected_inputs: claim/question, scope, freshness, allowed lanes, existing evidence
- expected_outputs: evidence matrix, contradictions, unresolved gaps, synthesis handoff
- context_targets:
  must_read:
    - target claim/question and source constraints
  read_if_needed:
    - prior ledger; `references/deep-evidence-method.md` for a complex sweep
    - `references/evidence-set.md` only for an explicitly requested persisted evidence artifact
  do_not_load_by_default:
    - full repo/memory, unrelated lanes, downstream report templates
- risk_profile:
  reads: scoped evidence from relevant lanes
  writes: evidence artifact only when explicitly requested
  tools: lane search/read tools within existing authority
  sensitive_resources: credentials default deny; never expand runtime, network, write, or mutation permission
- entry_scene: PREPARE

## `search-paper-evidence`

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
