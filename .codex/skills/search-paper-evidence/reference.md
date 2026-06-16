# Research Paper Evidence Search Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- topic or claim
- domain
- time range
- source preference
- provided papers
- desired evidence roles

## Owned Outputs
- query_plan
- retrieved_papers
- evidence_ledger
- missing_evidence
- do_not_assume
- search_limitations

## Workflow Checklist
- PREPARE - define topic, claim, time range, domains, and source constraints.
- QUERY DESIGN - split queries by method, dataset, metric, baseline, failure mode, survey, and contradiction.
- ACQUIRE - use available search tools when literature-backed claims require it; if unavailable, produce query plan only.
- NORMALIZE - capture title, authors when available, year, venue/source, URL/identifier, and relevance.
- DEDUP/RANK - remove duplicates and classify evidence role.
- FINALIZE - return an evidence ledger or draft artifact only when explicitly requested.

## Risk Checklist
- Artifact writes require explicit artifact intent.
- Network access is off by default except literature evidence search when needed and allowed.
- Dataset downloads, dependency installs, and training jobs are never implicit.
- `.system` is outside scope.

## Validation Checklist
- [ ] Correct research stage selected.
- [ ] Required source artifact or evidence is present or marked missing.
- [ ] No fabricated papers, citations, DOIs, datasets, metrics, or results.
- [ ] Development/implementation requests are returned to development mode.
- [ ] Output matches the declared artifact owner in `.codex/research-routing.md`.
