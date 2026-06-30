# Research Literature Ideation Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- evidence_ledger.json
- literature_review.md
- domain references

## Owned Outputs
- gap map
- candidate hypotheses
- claim labels
- selected active hypothesis
- backlog
- ideation_output.json when requested

## Workflow Checklist
- PREPARE - verify evidence or synthesis exists; otherwise route to evidence search.
- GAP MAP - identify open problems, contradictions, metric mismatches, dataset gaps, and failure modes.
- CANDIDATES - generate 2-4 temporary hypotheses with [paper], [math], [experiment], [dataset], or [assumption] labels.
- SELECT - choose exactly one active hypothesis for validation.
- BACKLOG - move non-active hypotheses to backlog.
- FINALIZE - output ideation summary or `papers/ideation_output.json` only when requested.

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
