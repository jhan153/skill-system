---
name: research-experiment-blueprint
description: Turn one selected hypothesis into the smallest identifiable, reproducible protocol with matched evidence contracts and explicit refutation rules; never generate code or results.
---

# Research Experiment Blueprint

## Routing Card
- role: primary
- family: research
- intent_signature: selected-hypothesis protocol, experiment/benchmark design, controls, metrics, ablations, stop/refute
- use_when:
  - one hypothesis is selected and needs an executable scientific design without code
- do_not_use_when:
  - the claim is unselected, or the request is evidence search, code/scaffold, execution, result analysis, or writing
- expected_inputs: selected claim/mechanism, evidence status, target outcome, constraints, and checkpoint/baseline availability
- expected_outputs: identifying experiment, matched controls/data/metrics, focused ablations, uncertainty, stop/refute, compute, and provenance
- context_targets:
  must_read:
    - selected hypothesis/mechanism, target outcome, and constraints
  read_if_needed:
    - evidence set, checkpoints/results, dataset cards, metric definitions, prior protocol
  do_not_load_by_default:
    - full corpus, scaffold, manuscript, unrelated experiments
- risk_profile:
  reads:
    - scoped research and data/metric/baseline evidence
  writes:
    - blueprint artifact only when explicitly requested
  tools:
    - none by default; no download, install, training, analysis, or result generation
  sensitive_resources:
    - credentials/private datasets default deny
- entry_scene: PREPARE

## Stage Boundary
Read `references/research_stage_contract.md` only when upstream/downstream ownership, multi-stage
intent, or Plan/Handoff mapping matters. This skill owns the protocol only. A missing selected
claim remains an explicit upstream gap owned by `research-hypothesis-planning`; do not invoke that
stage or produce a generic blueprint.

## Identification Workflow
1. Rewrite the claim as intervention → mechanism → observable outcome, with scope and falsifier.
2. Define the experimental unit, sampling/analysis unit, treatment, control, frozen factors, dependence, and leakage risks.
3. Reuse a suitable checkpoint or baseline; new training requires a decision-relevant gap it cannot answer.
4. Select data and metrics for the mechanism. Record provenance, access/license, split integrity, representativeness, contamination, metric definition/direction, uncertainty, relevance, and failure modes.
5. Require simple and strongest baselines to share the treatment's data/split, preprocessing, and metric contract; otherwise reject or qualify the comparison.
6. Define the smallest core experiment that identifies the selected claim, with explicit factors, levels, and predeclared contrasts. A single main-effect question keeps a one-factor contrast with other factors frozen. An interaction claim uses only the factor combinations needed to compare that effect across the relevant levels; one claim does not require only one varying factor. Add an ablation only for a distinct prediction needed by that claim, and keep unrelated factors and hypotheses deferred.
7. Specify randomization, seeds/repeats, variance sources, exclusions/missingness, multiplicity/statistical plan, compute/time bounds, and early stop.
8. Predeclare support, refute, inconclusive, stop, and escalation outcomes.

## Evidence And Reproducibility
- Mark unsupported dataset, metric, license, checkpoint, comparator, or expected-effect claims `Unverified` and name the resolving check.
- Never fabricate an empirical effect, variance, or sample size; require a power or precision basis with analysis unit, variance, and effect/threshold assumptions, each sourced or explicitly labeled as a design assumption. Missing required inputs remain unresolved rather than invented measurements.
- Pin configuration, code revision, environment, data version, checkpoint provenance, and output locations needed for reproduction.
- An ablation list is not evidence, and a blueprint never counts as completed experimentation.

For a selected binary A×B interaction, predeclare the difference between B's effect at the two A
levels and the four necessary combinations; hold unrelated data/preprocessing/metric choices fixed.
For B's effect at one fixed A level, retain the simpler B contrast. Neither case authorizes extra
hypotheses, irrelevant ablations, or training beyond the gap that the existing baseline cannot answer.

## Output
Answer a narrow design question with the decisive choice and falsifier. For an explicit artifact, include only:

- claim/mechanism/evidence and units/treatment/controls/frozen factors
- data, metric, baseline, leakage, and uncertainty contracts
- smallest identifying factors/levels/contrasts and prediction-bearing ablations
- support/refute/inconclusive plus stop/go, compute, provenance, and reproduction rules
- unresolved evidence checks

## Completion Boundary
- Complete only when the outcome can distinguish the claim from credible alternatives and every material contract is evidenced or explicitly unverified.
- Do not generate scaffold code, execute experiments, calculate results, or imply success before evidence.
