---
name: analysis-algorithm
description: Compare algorithms, modeling approaches, or technical solution patterns under concrete constraints and recommend the best fit with a causal explanation and validation criteria. Use when the approach is not yet selected; do not use for unresolved bug diagnosis, research-hypothesis planning, or direct implementation of an already chosen approach.
---

# Analysis Algorithm

## Routing Card
- role: primary
- intent_signature:
  - algorithm or approach recommendation
  - candidate comparison under constraints
  - best technical approach
  - 알고리즘 또는 접근 추천
- use_when:
  - the user needs to choose among credible solution families.
  - latency, memory, data, dependency, deployment, or implementation constraints change the choice.
- do_not_use_when:
  - a current failure still needs causal diagnosis; use `analysis-bug`.
  - the method is already selected and the user wants code; use `workflow-implementation`.
  - the request is a paper idea, hypothesis, ablation, loss, or training plan; use `research-hypothesis-planning`.
- expected_inputs:
  - decision to make, current baseline, constraints, and success signal
- expected_outputs:
  - recommendation, decisive trade-offs, mechanism, validation, and fallback when useful
- context_targets:
  must_read:
    - current decision and explicit constraints
    - baseline or current approach when one exists
  read_if_needed:
    - `references/problem-class-map.md` only when candidate discovery is genuinely broad
    - narrow integration source or current benchmark evidence
  do_not_load_by_default:
    - full repo, full memory bank, broad codebase reports, or unrelated candidate catalogs
- risk_profile:
  reads:
    - request context and narrow integration or measurement evidence
  writes:
    - none unless the user explicitly requests a plan artifact or implementation
  tools:
    - focused benchmark or validation commands only when they can discriminate candidates
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Decision Standard
Success is not a long candidate list. It is a defensible decision whose winner follows from the user's actual constraints.

1. State the decision and observable success signal.
2. Separate hard constraints from preferences and mark material assumptions `Unverified`.
3. Include the current baseline when it is a real option.
4. Compare only candidates that could plausibly win:
   - use one direct recommendation when constraints leave no meaningful alternative;
   - use two to four candidates when a genuine trade-off exists.
5. Explain the causal mechanism: what limitation changes, why the chosen mechanism helps, and where it can fail.
6. Define the cheapest check that can falsify the recommendation before broad implementation.

Do not classify the problem more deeply than needed to change the candidate set. Do not reward novelty, popularity, or benchmark rank without checking integration cost and workload fit.

## Comparison Axes
Select only axes that affect this decision:

- correctness and problem fit
- assumptions about data, workload, labels, or environment
- latency, throughput, memory, compute, and scaling behavior
- dependency and deployment constraints
- implementation and operational complexity
- failure modes, observability, and rollback cost

Expected gains without comparable evidence remain hypotheses. A static complexity claim does not prove runtime performance, and an external benchmark does not prove fit for the user's workload.

## Recommendation Shape
For a small decision, answer with:

- selected approach
- decisive reason
- main risk
- validation check

For a consequential or ambiguous decision, add the constraint set, compact candidate comparison, causal mechanism, fallback, and implementation stages. Omit empty sections and do not emit a formal matrix unless it makes the trade-off clearer.

## Implementation Boundary
- Recommendation-only requests do not authorize code or document writes.
- If the user asks to implement the selected approach, hand the decision and validation target to `workflow-implementation`.
- If measurements reveal that the real issue is a current bottleneck, use `analysis-performance`.
- If the decision depends on an unresolved failure cause, diagnose with `analysis-bug` first.

## Validation
- Tie every selection reason to a stated constraint or observed baseline.
- Name what evidence would reverse the recommendation.
- Distinguish offline checks, runtime checks, and user/environment checks only when each is relevant.
- Never claim measured improvement without comparable before/after evidence.

## Behavior Cases
- Positive: “대규모 sparse graph에서 이 세 접근 중 무엇이 맞는지 메모리와 latency 기준으로 비교해줘.”
- Negative: “이 failing test 원인 분석해줘.” → `analysis-bug`.
- Negative: “이미 선택한 A*를 이 함수에 구현해줘.” → `workflow-implementation`.
- Edge: only one option satisfies a hard platform constraint → recommend it directly; do not manufacture extra candidates.

## Known Limits
- Unstated workload and integration constraints can change the winner.
- Suggested validation is not evidence that the recommendation already works.
- Current product, library, or benchmark facts require fresh authoritative evidence when they may have changed.
