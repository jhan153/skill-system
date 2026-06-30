# Research Peer Review Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- manuscript/proposal/research plan
- review criteria
- evidence anchors
- target venue if provided

## Owned Outputs
- neutral summary
- major concerns
- minor concerns
- reproducibility concerns
- ethics/reporting concerns
- evidence/citation concerns
- revision advice
- author-facing revision plan

## Workflow Checklist
- PREPARE - identify review target and review stance.
- SUMMARIZE - state contribution neutrally.
- ASSESS - separate validity, novelty, reproducibility, ethics/reporting, evidence, and presentation issues.
- PRIORITIZE - classify major vs minor concerns.
- ADVISE - provide concrete revision actions.
- FINALIZE - produce review artifact only when requested.

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
