# Research Literature Synthesis Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- evidence_ledger.json
- provided papers
- search strategy
- inclusion/exclusion criteria

## Owned Outputs
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

## Workflow Checklist
- PREPARE - define scope and whether the review is narrative or systematic.
- ACQUIRE - read evidence ledger or provided papers; if missing, return to evidence search.
- SYNTHESIZE - group by themes, methods, datasets, metrics, and failure modes.
- CALIBRATE - separate consensus, disagreement, contradictions, limitations, and gaps.
- FINALIZE - write concise synthesis or `papers/literature_review.md` only when artifact intent is explicit.

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
