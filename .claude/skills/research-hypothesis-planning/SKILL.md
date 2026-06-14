---
name: research-hypothesis-planning
description: Claim-first research planning skill for paper ideas, hypotheses, experiment design, ablation, loss design, and training plans. Treats user research premises as hypotheses, prefers checkpoint-first evaluation, and keeps development implementation workflows separate.
---

# Research Hypothesis Planning

## Routing Card
- role: primary
- intent_signature:
  - "연구 계획"
  - "논문 아이디어"
  - "실험 설계"
  - "ablation 설계"
  - "loss 설계"
  - "학습 계획"
  - "새로운 방법"
  - "hypothesis"
  - "paper idea"
  - "research plan"
  - "training plan"
- use_when:
  - user asks to form or evaluate a research hypothesis.
  - user asks for paper/research/experiment/ablation/loss/training plan.
  - user asks whether a claim can be turned into a research direction.
- do_not_use_when:
  - user asks to implement a specific algorithm or code change.
  - user asks for ordinary bug analysis.
  - user asks for generic algorithm recommendation without a research claim.
  - user asks for repo docs/plan artifact only.
  - user asks to execute an existing skill.
  - user asks one-turn explanation or formatting.
- expected_inputs:
  - user research premise
  - claimed mechanism
  - domain constraints
  - baseline/checkpoint availability
  - metrics
  - dataset/label assumptions
  - provided papers or evidence if any
- expected_outputs:
  - premise triage
  - primary research claim
  - checkpoint-first baseline plan
  - minimal core experiment
  - progressive ablation ladder
  - loss budget
  - metrics and failure criteria
  - ablation backlog
  - deferred/rejected ideas
- context_targets:
  must_read:
    - current user request
    - explicitly provided research premise or evidence
  read_if_needed:
    - `papers/evidence_ledger.json`
    - `papers/ideation_output.json`
    - provided papers
    - baseline/checkpoint descriptions
    - dataset/metric docs
  do_not_load_by_default:
    - full repo
    - full memory bank
    - codebase-intel-report
    - phase-subplan-workflow
    - implementation files unless user asks for implementation
- risk_profile:
  reads:
    - user-provided text
    - optionally papers or experiment notes
  writes:
    - no code writes by default
    - plan artifacts only if user explicitly asks for persisted docs/plan
  tools:
    - none by default
  sensitive_resources:
    - no credentials
    - no network unless explicitly requested and allowed
- entry_scene:
  - PREPARE

## Purpose
Produce skeptical, claim-first research plans that treat user research claims as hypotheses, not facts, while leaving software development and implementation workflows strict, direct, and concrete.

## When To Apply
- Research plan, paper idea, novel method framing, experiment design, ablation design, loss design, training plan, or hypothesis planning.
- Requests where a causal, field-state, dataset, metric, or model-behavior claim must be shaped into a testable research direction.
- Requests that need separation between the main claim, core experiment, ablation backlog, and deferred ideas.

## When Not To Apply
- Coding, refactoring, tests, scripts, APIs, build/lint/test work, bug fixing, or implementation of an already chosen method.
- Generic algorithm recommendation without a research claim; use `deep-algorithm-proposal`.
- Persisted docs/plan writing without research content ownership; use `plan-doc-workflow` only when artifact intent is explicit.
- Multi-document phase packages or handoff packages; use `phase-subplan-workflow` only when explicitly requested.
- Casual concept explanation or one-turn formatting preferences.

## Input Priority
1. `papers/evidence_ledger.json`
2. `papers/ideation_output.json` selected hypothesis
3. User-provided claim

If the user asks for current/latest literature-backed claim planning and no evidence is available, recommend or route to `research-paper-evidence-search` first. Do not weaken the development boundary: implementation requests stay in Development / Implementation Mode even when they mention model, metric, experiment, loss, or training.

## Workflow
1. PREPARE - Confirm research-planning intent
   - Decide whether this is Research Hypothesis Planning Mode or Development / Implementation Mode.
   - If implementation mode, return to scheduling and do not use this skill.
2. CLAIM TRIAGE - Separate premise types
   - Classify user statements as confirmed fact, user hypothesis, plausible but unverified, risky/overgeneralized, potentially false, needs literature check, or not needed for the main claim.
3. MAIN CLAIM SELECTION - Choose one primary research claim
   - Select one central claim only.
   - Move secondary ideas into Ablation Backlog.
   - Mark dangerous or overgeneralized claims as not assumed.
4. CHECKPOINT-FIRST BASELINE - Prefer existing assets before new training
   - Check whether the claim can be tested by existing checkpoint evaluation, pretrained baseline inference, re-scoring existing outputs, metric/error analysis, dataset/label audit, or small controlled fine-tune only if evaluation-only is insufficient.
5. MINIMAL CORE EXPERIMENT - Design the smallest test
   - Test the primary claim with the fewest changes.
   - Avoid architecture + data + loss + schedule changes in the same core experiment.
6. ABLATION LADDER - Add one factor at a time
   - Order ablations from core to secondary.
   - Each stage changes only one factor and states changed factor, frozen factors, expected signal, and failure interpretation.
7. LOSS BUDGET - Prevent multi-loss soup
   - Separate training loss, evaluation metric, analysis metric, auxiliary loss, and regularizer.
   - Use at most one primary objective and at most one directly justified auxiliary loss per ablation stage.
8. VALIDATION - Define support/refute/inconclusive criteria
   - State what result supports the claim, refutes it, or leaves it inconclusive.
9. FINALIZE - Separate plan from backlog
   - Output the primary plan, ablation backlog, deferred ideas, and non-assumptions separately.

## Research Premise Triage
User-provided research claims are not facts. Always mark them as one of:
- confirmed fact: supported by provided reliable evidence.
- user hypothesis: the user's proposed claim or mechanism.
- plausible but unverified: reasonable but not established from current context.
- risky / overgeneralized: likely too broad across models, datasets, papers, or metrics.
- potentially false: conflicts with known evidence or would need strong proof.
- needs literature check: cannot be responsibly accepted without source verification.
- not needed for the main claim: useful later but not required for the core experiment.

## Development Boundary
This skill must not block implementation tasks. If the user already chose a method and asks to implement it, treat requirements, file names, APIs, metrics, and keywords as development specifications unless unsafe, contradictory, impossible, or repo-conflicting. Return to implementation/development scheduling instead of performing premise triage.

## Checkpoint-First Rule
Do not propose new training until checkpoint-only or baseline-only evaluation is considered. Prefer this order:
1. checkpoint-only evaluation
2. pretrained baseline inference
3. re-score existing outputs
4. metric or error analysis
5. dataset/label audit
6. small controlled fine-tune only if evaluation-only is insufficient
7. new training only for a verified gap that cannot be tested otherwise

## Main Claim Contract
- The plan must have one primary research claim.
- The primary claim must be testable, falsifiable, and narrower than the user's raw premise when the premise is broad.
- Secondary claims belong in Ablation Backlog.
- Overgeneralized claims such as "all existing models fail" must be marked as not assumed unless evidence is provided.

## Ablation Ladder
Ablations must isolate effects. Each stage should include:
- changed factor
- frozen factors
- expected signal
- failure interpretation

Default ladder:
- A0: existing checkpoint/baseline evaluation
- A1: baseline re-scoring or error analysis
- A2: main intervention only
- A3: one data/label handling change
- A4: one architecture or inference change
- A5: one loss/objective change
- A6: one training schedule or fine-tuning change

## Loss Budget
- Primary objective: one.
- Auxiliary loss: at most one per ablation stage, only when directly tied to the primary claim.
- Regularizer: exclude by default unless it isolates a specific failure mode.
- Evaluation metrics and analysis metrics are not training losses.
- Do not treat PESQ or another evaluation metric as a training objective unless using a validated differentiable proxy and marking it as risky/unverified.

## Resource and Risk Boundary
- Reads: current request, user premise, provided evidence, and targeted paper/baseline/checkpoint/dataset/metric notes when needed.
- Writes: none by default; persisted `docs/plan` artifacts only when explicitly requested and routed with `plan-doc-workflow` as writer.
- Tool/process calls: none by default; literature search, repo inspection, or experiments require explicit request and context.
- Network access: none by default; browsing papers requires explicit request or current literature verification need.
- Credential access: default deny.
- Generated artifacts: research plan text only unless persisted artifact intent is explicit.
- Destructive actions: out of scope.
- Required checkpoints: mode decision, premise triage, one primary claim, checkpoint-first baseline, one-factor ablation, loss budget, support/refute criteria.

## Recovery and Context Expansion
- If mode is ambiguous, decide whether the user asks for implementation or research validity first.
- If the premise is broad, narrow to one primary claim before adding experiments.
- If evidence is missing, mark the claim as hypothesis or needs literature check instead of filling facts.
- If baseline availability is unknown, ask for checkpoint/baseline info or propose evaluation-only as Stage 0.
- If the user asks for implementation after the research plan, return to scheduling and use development/implementation workflows.
- Never recover by loading the full repo, full memory bank, codebase-intel artifacts, or phase package templates by default.

## Output Contract
The final answer should include:
1. Mode Decision
2. User Premise Triage
3. Primary Research Claim
4. What Not To Assume
5. Checkpoint/Baseline Reuse Plan
6. Minimal Core Experiment
7. Progressive Ablation Ladder
8. Loss Budget
9. Metrics and Failure Criteria
10. Ablation Backlog
11. Deferred / Rejected Ideas

## Validation
- Confirm the request is research planning, not implementation.
- Confirm user premises are not treated as facts unless verified by provided evidence.
- Confirm one primary research claim is selected.
- Confirm checkpoint/baseline reuse is considered before new training.
- Confirm the core experiment changes the fewest factors possible.
- Confirm each ablation changes one factor and names frozen factors.
- Confirm loss terms are separated from evaluation and analysis metrics.
- Confirm support/refute/inconclusive criteria are defined.
- Confirm persisted artifacts are not created unless explicitly requested.

## Anti-Patterns
- Treating user hypothesis as established fact.
- Applying research skepticism to ordinary implementation tasks.
- Planning new training before checkpoint-only evaluation.
- Adding architecture, data filtering, augmentation, and multiple losses in the first experiment.
- Optimizing many losses while claiming to isolate one effect.
- Making all existing models or datasets sound uniformly wrong without evidence.
- Hiding secondary ideas inside the main claim.
- Producing a plan that cannot say what result would refute the claim.

## Known Limits
- This skill does not verify literature claims unless sources are provided or browsing is explicitly requested.
- Research plans remain hypotheses until experiments or evidence validate them.
- Checkpoint availability, dataset quality, and metric validity may require domain-specific evidence.
- Conservative loss and ablation budgets may defer useful ideas to later stages rather than include them immediately.
