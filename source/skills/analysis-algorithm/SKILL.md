---
name: analysis-algorithm
description: "Constraint-first workflow for recommending algorithms, modeling approaches, or technical solution patterns: frame the problem, compare candidates, choose one, explain why it fits, and define validation."
---

# Analysis Algorithm

## Routing Card
- role: primary
- intent_signature:
  - `deep-algo`, `algorithm-proposal`, `best approach`, `recommend algorithm`, `무슨 알고리즘`, `어떤 접근`
- use_when:
  - the user needs candidate algorithm or technical approach comparison under constraints.
  - validation thresholds, rollback triggers, or integration constraints matter before implementation.
- do_not_use_when:
  - a concrete failure still needs root-cause diagnosis.
  - the task is a small local edit with the approach already selected.
- expected_inputs:
  - problem statement
  - constraints and success metrics
  - integration limits and current baseline when available
- expected_outputs:
  - candidate comparison, selected primary approach, fallback, implementation outline, validation plan
- context_targets:
  must_read:
    - problem constraints
    - success metrics
    - integration constraints
  read_if_needed:
    - candidate algorithm families
    - `references/problem-class-map.md` only when the problem class is broad or ambiguous
    - relevant source outline if implementation integration is part of the decision
  do_not_load_by_default:
    - full repo
    - full memory bank
    - codebase-intel artifacts
- risk_profile:
  reads:
    - request context, constraints, and narrow integration context
  writes:
    - none unless the user asks for an implementation plan document or code change
  tools:
    - none by default; CALL_PROCESS only for explicit benchmark or validation commands
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Related Skills
- `analysis-router`: router and backward-compatible entry point.
- `analysis-bug`: use first when the current failure mode is still unclear.
- `report-qualitative`: owns final formal report shape when explicitly active.
- `workflow-rigor`: owns execution rigor when the recommendation is immediately implemented.
- `research-hypothesis-planning`: owns research plans, paper ideas, ablation/loss design, training plans, and hypothesis-driven experiment design.

## Trigger
- `deep-algo`
- `algorithm-proposal`
- `algo-proposal`
- `best approach`
- `recommend algorithm`
- `무슨 알고리즘`
- `어떤 접근`
- `알고리즘 추천`

## Research Planning Boundary
- If the request is a research plan, paper idea, ablation design, loss design, training plan, or hypothesis-driven experiment design, return to scheduling and use `research-hypothesis-planning` unless the user only wants a generic algorithm recommendation.
- If the user asks to implement a specific algorithm or approach, do not redirect to research planning. Treat it as Development / Implementation Mode and proceed through the appropriate implementation workflow.
- For research-like requests, do not treat user claims as facts.
- For implementation-like requests, treat user-provided requirements as task specifications unless unsafe, contradictory, impossible, or repo-conflicting.
- Avoid proposing new training or multiple losses unless `research-hypothesis-planning` owns the plan.

## Trigger Guard (Do Not Trigger)
- Pure root-cause or debugging questions with a concrete failure to diagnose.
- Pure architecture/HLD/LLD requests where module boundaries are the main decision.
- Small local implementation tasks where the approach is already chosen.
- Research plans, paper ideas, ablation/loss/training-plan design, or hypothesis-driven experiment design.
- Quick patch requests that do not need candidate comparison.

## Goal
- Recommend the best-fit algorithm, pattern, or technical approach for the given problem.
- Make trade-offs explicit instead of naming a favorite method too early.
- Explain how the chosen approach solves the problem under the stated constraints.
- Define a validation plan before implementation.

## Required Inputs
- problem statement
- current baseline or current approach when available
- constraints:
  - latency / throughput / memory
  - data size / input quality / label quality
  - platform / dependency / deployment limits
  - implementation budget or complexity budget
- success metric
- missing information must be marked `Unverified`

## Reference Use
- When the problem class is ambiguous or candidate families are broad, load [problem-class-map.md](references/problem-class-map.md).
- Use the reference as a candidate discovery aid, not as an automatic answer.

## Outcome-First Decision Loop
Success means the recommendation identifies the decision being made, states constraints and success metrics, compares credible candidates, selects one primary approach plus fallback when useful, explains the causal mechanism, and defines validation thresholds or rollback triggers. Use the shortest decision path that proves those outcomes.

Recommended loop:
1. Frame the problem and decision.
2. Extract constraints and success metrics.
3. Classify the problem type only as far as it changes candidate choice.
4. Generate 2-4 credible candidates, including the current baseline when it exists.
5. Compare candidates on fit, cost, risk, and validation.
6. Select one primary recommendation and explain why the alternatives lose.
7. Define implementation stages and validation thresholds.

## Step 1) Problem Framing
- Rewrite the request in one tight sentence.
- Separate:
  - current issue or goal
  - desired outcome
  - decision to make
- If the user mixed multiple decisions, split them before recommending.

## Step 2) Constraint Extraction
- Capture explicit constraints first.
- Infer only when reasonable, and label inferred items as `Assumed`.
- Always check:
  - performance limits
  - data and input conditions
  - integration or dependency limits
  - implementation budget
  - success metric

## Step 3) Problem Classification
- Select one primary problem class.
- Add one secondary class only if it materially changes the candidate set.
- Typical classes:
  - search or retrieval
  - ranking or reranking
  - optimization or scheduling
  - estimation or fitting
  - detection, segmentation, or pose
  - forecasting
  - control or tracking
  - recommendation or matching
  - system performance or scaling
  - workflow orchestration

## Step 4) Candidate Generation
- Generate 2-4 credible candidates.
- Include the current baseline as one candidate when it exists.
- Do not collapse to one answer unless only one family is realistically valid.

## Step 5) Candidate Comparison
- Compare each candidate on:
  - problem fit
  - assumptions or prerequisites
  - expected gain
  - compute, latency, and memory cost
  - data requirement
  - implementation effort
  - failure modes
  - rollbackability
- Avoid comparing only by raw accuracy or only by speed.

## Step 6) Recommendation
- Select:
  - one primary recommendation
  - one fallback when appropriate
- State:
  - why the winner fits best
  - why the others were not selected

## Step 7) Solve Mechanism
- Explain the recommendation causally:
  - current limitation
  - what changes
  - why that change improves the result
- Avoid slogan-like claims such as "more robust" without a mechanism.

## Step 8) Implementation Outline
- Give implementation in stages:
  1. minimum viable version
  2. integration points
  3. instrumentation or logging
  4. rollback or fallback path
- Do not output full code unless the user explicitly asks for implementation.

## Step 9) Validation Plan
- Always define:
  - offline validation
  - online or real-world validation
  - success threshold
  - rollback trigger
- Prefer measurable thresholds over vague confidence.

## Resource and Risk Boundary
- Reads: problem statement, constraints, existing approach, and narrow integration context.
- Writes: none for recommendation-only work; plan/code writes require explicit implementation or document request.
- Tool/process calls: none by default; benchmark/test commands require a clear purpose and non-destructive check.
- Network access: none by default unless external benchmark data or current docs are explicitly needed.
- Credential access: default deny.
- Generated artifacts: only requested plan or comparison artifacts.
- Destructive actions: out of scope.
- Required checkpoints: constraints before recommendation, validation thresholds before implementation, repo validation context before WRITE_CODEBASE.

## Recovery and Context Expansion
- If problem class is unclear, read `references/problem-class-map.md`.
- If integration boundary is unclear, read repo source outline or nearby module docs.
- If success metric is missing, state the assumption or ask one focused question before expanding context.
- If validation command is unclear, read repo validation contract.
- If a current failure must be diagnosed first, return to scheduling and use `analysis-bug`.
- Never recover by loading the full repo, full memory bank, or codebase-intel artifacts at once.

## Output Contract
1. Problem summary
2. Constraint set
3. Candidate approaches
4. Recommended algorithm or approach
5. Why it fits this problem
6. How it solves the problem
7. Alternatives not selected
8. Implementation outline
9. Validation plan
10. Risks, confidence, or missing info

## Output Templates
### Problem Summary Template
```markdown
problem summary
- current issue or goal:
- desired outcome:
- decision to make:
- primary problem class:
- secondary class:
```

### Constraint Template
```markdown
constraints
- latency / throughput:
- memory / compute:
- data / input quality:
- platform / dependency limits:
- implementation budget:
- success metric:
- assumed items:
```

### Candidate Comparison Template
```markdown
candidate A
- approach type:
- problem fit:
- assumptions:
- expected gain:
- compute cost:
- data requirement:
- implementation effort:
- failure modes:

candidate B
- approach type:
- problem fit:
- assumptions:
- expected gain:
- compute cost:
- data requirement:
- implementation effort:
- failure modes:

selected recommendation
- primary:
- fallback:
- selection reason:
```

### Solve Mechanism Template
```markdown
how this solves the problem
- current limitation:
- chosen mechanism:
- expected effect:
- why this beats the baseline:
```

### Validation Template
```markdown
validation plan
- offline test:
- online or real-world test:
- success threshold:
- rollback trigger:
```

## Effectiveness Metrics
- `problem_classification_rate`
- `constraint_capture_rate`
- `candidate_generation_rate`
- `algorithm_explicit_rate`
- `mechanism_explanation_rate`
- `validation_plan_presence_rate`
- `recommendation_acceptance_rate`
- `outcome_verified_rate`

## Metrics Logging Rules
- Include one `metrics:` line only when the user asked for a formal or structured report.
- Example:
  `metrics: problem_classification_rate=5/5, constraint_capture_rate=5/5, candidate_generation_rate=5/5, algorithm_explicit_rate=5/5, mechanism_explanation_rate=4/5, validation_plan_presence_rate=5/5, outcome_verified_rate=Unverified`

## Anti-Patterns
- Naming one trendy algorithm without a trade-off comparison.
- Ignoring constraints such as latency, data quality, or integration cost.
- Giving no baseline and no fallback.
- Claiming an expected gain without stating the mechanism.
- Recommending an option with no measurable validation threshold.

## Known Limits
- Recommendations depend on stated constraints and metrics; unstated requirements remain `Unverified`.
- This skill does not benchmark or prove performance unless evidence is supplied or validation is run.
- Generated or sample implementations need tests before adoption.
- Return to scheduling when the task is actually bug diagnosis or implementation.
