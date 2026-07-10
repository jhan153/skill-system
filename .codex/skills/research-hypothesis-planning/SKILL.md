---
name: research-hypothesis-planning
description: Turn a raw research premise, paper idea, loss/ablation concept, or training proposal into one scoped falsifiable primary claim and a minimal evidence plan. Use before a formal experiment blueprint; do not intercept implementation of an already selected method.
---

# Research Hypothesis Planning

## Routing Card
- role: primary
- intent_signature:
  - research hypothesis, paper idea, novel method, ablation/loss/training plan, 연구 계획
- use_when:
  - a premise or mechanism must be tested, narrowed, or turned into a research direction.
- do_not_use_when:
  - the user asks to implement an already selected algorithm or code change.
  - literature evidence already exists and the goal is gap-derived ideation (`research-literature-ideation`).
  - one hypothesis is selected and a full protocol is needed (`research-experiment-blueprint`).
- expected_inputs:
  - premise, claimed mechanism, scope, constraints, evidence, and baseline/checkpoint availability
- expected_outputs:
  - premise triage, primary claim, non-assumptions, Stage-0 evidence check, minimal discriminating experiment, and backlog
- context_targets:
  must_read:
    - current premise and claimed mechanism
    - provided evidence or explicit evidence gap
  read_if_needed:
    - evidence ledger, selected papers, checkpoint/baseline notes, and dataset/metric definitions
  do_not_load_by_default:
    - full repo, implementation files, broad phase templates, or unrelated research artifacts
- risk_profile:
  reads:
    - premise and targeted research evidence
  writes:
    - none by default; a plan artifact only when explicitly requested
  tools:
    - none by default; current literature verification routes to evidence search
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Claim-First Workflow
1. Decide whether the user is asking about research validity or direct implementation. Concrete implementation stays with development workflows even if it mentions models, metrics, losses, or training.
2. Split the premise into:
   - evidence-backed fact
   - user hypothesis
   - plausible but unverified assumption
   - overgeneralization or potentially false claim
   - claim needing literature evidence
3. Select one primary decision target with scope, intervention, mechanism, observable outcome, and falsifier. If two rival explanations cannot yet be separated, retain both only long enough to design the discriminating observation instead of choosing arbitrarily.
4. State what must not be assumed, especially broad field, dataset, or model claims.
5. Prefer the cheapest Stage-0 discriminator: existing checkpoint evaluation, baseline inference, re-scoring, error analysis, or dataset/label audit.
6. Propose the smallest experiment that changes one causal factor.
7. Put secondary ideas in an ablation backlog; do not combine architecture, data, schedule, and multiple objectives in the core test.
8. Define support, refute, and inconclusive signals.

## Loss and Ablation Discipline
- Separate training objective, auxiliary loss, regularizer, evaluation metric, and diagnostic metric.
- Start with one primary objective. Add an auxiliary term only when it tests a specific mechanism and has its own ablation.
- Each ablation names the changed factor, frozen factors, expected signal, and failure interpretation.
- “More losses” or “more training” is not a research mechanism.

## Output
For a small premise check, lead with whether the claim is testable and the cheapest falsifier. For a full research plan, include:

- premise classification and evidence gaps
- primary falsifiable claim and non-assumptions
- checkpoint/baseline Stage 0
- minimal core experiment
- metrics and support/refute/inconclusive criteria
- ablation/loss backlog and deferred ideas

Do not force a long plan when the premise fails a basic evidence or falsifiability gate.

## Behavior Cases
- Positive: “이 loss 아이디어를 검증 가능한 한 개의 claim과 최소 ablation plan으로 좁혀줘.”
- Negative: “선택한 loss를 training loop에 구현해줘.” → `workflow-implementation`.
- Edge: the premise depends on “all existing models fail” without evidence → narrow the claim and route current evidence acquisition to `search-paper-evidence`.
- Edge: two plausible causal mechanisms predict different subgroup behavior → preserve both predictions and make the subgroup check the first discriminator.

## Validation
- The primary claim is narrower than unsupported premises and can be refuted.
- Stage 0 considers existing evidence before new training.
- The core test changes the fewest causal factors possible.
- Metrics are not confused with loss terms.
- No literature or experimental result is invented.
