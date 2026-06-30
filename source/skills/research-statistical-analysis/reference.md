# Research Statistical Analysis Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- metric tables
- result CSV/JSON
- experiment configs
- design description
- planned tests

## Owned Outputs
- data provenance
- planned vs exploratory tests
- test selection rationale
- assumption checks
- effect sizes
- confidence/credible intervals
- multiple comparison handling
- practical vs statistical significance
- missing data/exclusions/outliers
- limitations

## Workflow Checklist
- PREPARE - identify data provenance and analysis question.
- ACQUIRE - read only provided result tables/configs.
- SELECT TEST - choose tests from design and data type, not desired outcome.
- CHECK ASSUMPTIONS - independence, pairing, distribution, missingness, multiple comparisons.
- REPORT - include effect sizes, intervals, practical significance, and limitations.
- ABSTAIN - if data are missing, produce analysis plan only.

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
