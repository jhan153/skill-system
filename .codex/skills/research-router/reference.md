# Research Router Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- research request
- stage hints
- artifact intent
- provided evidence or artifact paths

## Owned Outputs
- selected research cluster skill
- next skill sequence
- minimal context bundle
- excluded skills

## Workflow Checklist
- PREPARE - identify whether this is research or development mode.
- CLASSIFY - choose exactly one owning research stage or a short sequence when the user requests a multi-stage workflow.
- EXCLUDE - mark unrelated heavy generators and implementation skills as excluded.
- RETURN - route to the selected skill; do not perform the work locally.

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
