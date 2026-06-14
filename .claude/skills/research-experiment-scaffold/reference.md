# Research Experiment Scaffold Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- approved experiment_blueprint.json
- target directory
- language/framework constraints
- write approval
- smoke test preference

## Owned Outputs
- experiments/ README
- configs/default.yaml
- data/README.md
- src/
- tests/
- run.py
- evaluate.py
- requirements.txt or pyproject.toml

## Workflow Checklist
- PREPARE - verify explicit scaffold intent, approved blueprint, target directory, and write boundary.
- DESIGN - map blueprint to minimal directories, configs, fixtures, and interfaces.
- SCAFFOLD - create skeleton files only within target scope.
- SMOKE - optionally add synthetic fixture tests; CALL_PROCESS only if requested.
- FINALIZE - report files and state that no training/results were run.

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
