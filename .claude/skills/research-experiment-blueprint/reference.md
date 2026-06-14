# Research Experiment Blueprint Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- selected hypothesis
- research plan
- evidence references
- baseline/checkpoint availability
- dataset and metric constraints

## Owned Outputs
- selected hypothesis
- evidence references
- checkpoint-first plan
- datasets with license/access notes
- baselines with references
- metrics
- minimal core experiment
- ablation ladder
- loss budget
- compute/timeline
- stop/go criteria
- falsification conditions
- reproducibility plan

## Workflow Checklist
- PREPARE - confirm exactly one selected hypothesis.
- CHECKPOINT-FIRST - identify checkpoint, pretrained, baseline inference, metric-only, or label audit options before training.
- DATASET/METRIC - select only datasets and metrics that match the hypothesis.
- BASELINES - include a simple baseline and a strong baseline when possible.
- CORE - define the smallest discriminating experiment.
- ABLATION - add one factor at a time.
- STOP/GO - define support, refute, inconclusive, and stop criteria.

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
