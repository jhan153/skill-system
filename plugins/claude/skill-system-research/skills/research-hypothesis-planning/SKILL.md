---
name: research-hypothesis-planning
description: Narrow a raw research premise into one falsifiable claim and the cheapest discriminating evidence plan before blueprinting or implementation.
---

# Research Hypothesis Planning

## Routing Card
- role: primary
- intent_signature: raw premise, mechanism, loss/ablation idea, or hypothesis validation
- use_when:
  - a premise must become one testable research decision
- do_not_use_when:
  - selected-method implementation or a later literature, protocol, scaffold, analysis, or manuscript stage
- expected_inputs: premise, mechanism, scope, evidence status, constraints, and baseline/checkpoint availability
- expected_outputs: premise status, one claim/falsifier, Stage 0, minimal discriminator, outcomes, and backlog
- context_targets:
  must_read:
    - premise/mechanism and supplied evidence or gap
  read_if_needed:
    - selected evidence, checkpoint/baseline, dataset/metric definitions
  do_not_load_by_default:
    - full repo/corpus, implementation, templates, unrelated artifacts
- risk_profile:
  reads:
    - scoped premise and research evidence
  writes:
    - plan artifact only when explicitly requested
  tools:
    - none by default; current literature claims route to evidence search
  sensitive_resources:
    - credentials default deny
- entry_scene: PREPARE

## Exact Stage Route
| Request | Owner |
| --- | --- |
| raw premise, mechanism, loss, or ablation validity | `research-hypothesis-planning` |
| hypotheses derived from an evidence ledger | `research-literature-ideation` |
| current paper evidence acquisition | `search-paper-evidence` |
| selected claim to full protocol | `research-experiment-blueprint` |
| approved blueprint to runnable code | `research-experiment-scaffold` |
| real result analysis | `research-statistical-analysis` |
| selected method implementation | `workflow-implementation` |

Use the exact owner. Research vocabulary inside coding work does not change the route.

## Workflow
1. Label each premise `supported`, `user_hypothesis`, `unverified`, `overgeneralized`, or `needs_current_evidence`; never invent literature, novelty, or results.
2. Define one target with scope, intervention, mechanism, observable prediction, and falsifier. Request missing essentials instead of emitting a large plan.
3. Keep two rival explanations until one observation separates their predictions. Mark broad field/dataset/model claims as non-assumptions and route current evidence acquisition to `search-paper-evidence`.
4. Choose the cheapest Stage-0 discriminator: checkpoint/baseline evaluation, re-scoring, error analysis, or dataset/label audit. Train only for a gap Stage 0 cannot resolve.
5. If needed, change one causal factor, freeze the rest, and defer architecture, data, schedule, and extra objectives.
6. Predefine metric plus support, refute, and inconclusive signals.

## Loss And Ablation Discipline
- Separate primary objective, auxiliary loss, regularizer, evaluation metric, and diagnostic metric; “more training/losses” is not a mechanism.
- An auxiliary term needs a mechanism and its own ablation.
- Each ablation names changed and frozen factors, predicted signal, and failure interpretation.

## Output
For a small premise, lead with testability and the cheapest falsifier. An explicit plan includes only:

- premise status and evidence gaps
- claim/mechanism/scope/falsifier and non-assumptions
- Stage-0 baseline/checkpoint check
- one-factor core, frozen factors, metric, three outcomes, and deferred backlog

## Completion Boundary
- Complete only when the claim is narrower than unsupported premises, falsifiable, and paired with the cheapest discriminator.
- Hypothesis planning does not prove the claim, complete experimentation, write implementation, or authorize a positive conclusion.
