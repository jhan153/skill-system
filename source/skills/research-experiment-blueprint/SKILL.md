---
name: research-experiment-blueprint
description: Turn one selected research hypothesis into an identifiable experiment blueprint with matched baselines, controls, datasets, metrics, ablations, compute bounds, falsification criteria, and reproducibility requirements. Use after hypothesis selection; do not generate code or claim results.
---

# Research Experiment Blueprint

## Routing Card
- role: primary
- intent_signature:
  - experiment blueprint, benchmark design, selected-hypothesis experiment, 실험 설계서
- use_when:
  - one primary hypothesis is selected and the user needs an executable scientific design.
- do_not_use_when:
  - the claim is still being formed (`research-hypothesis-planning` or `research-literature-ideation`).
  - code scaffold or experiment execution is requested (`research-experiment-scaffold`).
- expected_inputs:
  - selected hypothesis, mechanism, evidence status, constraints, and available baseline/checkpoint
- expected_outputs:
  - identifying experiment, controls, data/metrics, baseline, ablations, stop/go/refute criteria, compute and reproducibility plan
- context_targets:
  must_read:
    - selected hypothesis and claimed mechanism
    - target outcome and constraints
  read_if_needed:
    - evidence ledger, existing checkpoints/results, dataset cards, metric definitions, and relevant prior protocol
  do_not_load_by_default:
    - full literature corpus, code scaffold, manuscript, or unrelated experiments
- risk_profile:
  reads:
    - selected research artifacts and targeted data/metric/baseline evidence
  writes:
    - blueprint artifact only when explicitly requested
  tools:
    - none by default; no downloads, installs, training, or result generation
  sensitive_resources:
    - credentials and private datasets default deny
- entry_scene:
  - PREPARE

## Experimental Identification Standard
A blueprint is good only if its outcome can distinguish the primary claim from credible alternatives.

1. Rewrite the selected hypothesis as intervention → mechanism → observable outcome, with scope and falsifier.
2. Define the experimental unit, sampling unit, treatment, control, frozen factors, and leakage risks.
3. Reuse an existing checkpoint or baseline when it can test the claim; new training is justified only by an identified gap.
4. Choose datasets and metrics because they expose the claimed mechanism, not because they are conventional.
5. Include a simple baseline and the strongest comparable baseline that fits the same data/evaluation contract.
6. Define the smallest core experiment that changes one causal factor.
7. Add ablations only when each one separates mechanisms or boundary conditions; an ablation checklist is not evidence.
8. Predeclare support, refute, inconclusive, stop, and escalation conditions.

## Blueprint Decisions
Cover only decisions material to the claim:

- dataset provenance, license/access, split integrity, representativeness, and contamination risk
- metric definition, direction, uncertainty, human/deployment relevance, and failure cases
- baseline comparability and checkpoint provenance
- randomization, seeds/repeats, variance sources, exclusion/missing-data policy, and statistical plan
- compute/time budget and early termination
- artifacts required to reproduce configuration, code revision, environment, data version, and outputs

Do not claim a dataset, metric, license, checkpoint, or expected effect is suitable without evidence; mark it `Unverified` and name the check.

## Output
For a narrow design question, return the decisive experimental choice and its falsification check. For an explicit blueprint artifact, include:

- hypothesis/mechanism and evidence status
- experimental unit, treatment, controls, and frozen factors
- dataset/metric/baseline contracts
- minimal core experiment and mechanism-focused ablations
- uncertainty/statistical plan
- support/refute/inconclusive and stop/go rules
- compute, provenance, and reproducibility plan

Omit empty boilerplate and do not fabricate precise sample sizes without a power/precision basis.

## Boundary
- `research-hypothesis-planning` selects and sharpens the claim.
- `research-experiment-scaffold` projects an approved blueprint into code.
- `research-statistical-analysis` analyzes real results or writes a no-data analysis plan.
- A blueprint never counts as completed experimentation.

## Behavior Cases
- Positive: “선정된 hypothesis H1을 검증할 dataset, control, metric, ablation과 stop/go가 있는 blueprint로 만들어줘.”
- Negative: “이 아이디어가 연구 가설이 될지 봐줘.” → `research-hypothesis-planning`.
- Edge: no suitable checkpoint exists → record the gap and cheapest prerequisite; do not jump straight to a large training program.

## Validation
- The core experiment can refute the claim and isolates the claimed factor.
- Baselines share a comparable data/metric contract.
- Every ablation has a distinct prediction and frozen factors.
- Missing data, variance, leakage, and reproducibility risks are explicit.
- No result is implied before execution.
