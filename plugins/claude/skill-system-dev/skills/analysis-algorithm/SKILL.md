---
name: analysis-algorithm
description: Compare algorithms or technical approaches under concrete constraints before selecting one, and recommend the best fit. Not for bug diagnosis, research hypotheses, or implementing a chosen method.
---

# Analysis Algorithm

## Routing Card
- role: primary
- family: analysis
- intent_signature: algorithm/approach recommendation or candidate comparison under constraints
- use_when: credible solution families compete and workload, correctness, latency, memory, dependency, deployment, or implementation constraints change the winner.
- do_not_use_when:
  - failure mechanism/cause is the requested output: `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane; otherwise current task owner for diagnosis-only
  - an already-implemented accepted production contract needs one bounded defect repair: `workflow-bug-fix`
  - chosen method needs code: `workflow-implementation`
  - measured production bottleneck: `analysis-performance`
  - paper hypothesis, loss, ablation, or training plan: `research-hypothesis-planning`
  - selected interface/boundary contract: `analysis-boundary-design`
  - business identities, states, or invariants: `analysis-domain-modeling`
- expected_inputs: decision, current baseline, hard constraints, preferences, workload, success condition
- expected_outputs: recommendation or unverified gap, decisive trade-off, mechanism, evidence scope, falsifier, handoff
- context_targets:
  - must_read: current decision, success condition, constraints, and baseline when one exists
  - read_if_needed: narrow integration/measurement evidence; `references/problem-class-map.md` only for genuinely broad candidate discovery
  - do_not_load_by_default: full repo, memory bank, broad reports, unrelated candidate catalogs
- risk_profile: focused read-only comparison; no implementation writes; credentials denied
- entry_scene:
  - PREPARE

## Decision Gate
1. State the exact decision and observable success condition.
2. Separate non-negotiable constraints from preferences. A hard-constraint violation disqualifies a candidate; speed or popularity cannot offset it.
3. Establish the authority for correctness and fit: user decision, canonical source, external contract, formal invariant, or observed behavior. Mark missing material inputs `Unverified`.
4. Include the current baseline when viable. When only one candidate meets the constraints, use one direct recommendation; do not manufacture extra candidates. Otherwise compare two to four plausible winners.
5. For each candidate, explain the mechanism, assumptions, integration cost, failure modes, and the evidence that supports this workload—not merely a similar benchmark.
6. Recommend only when the winner follows from established constraints and evidence. Otherwise return no winner and request the smallest observation that would decide it.

Do not classify the problem more deeply than needed to change the candidate set. Do not reward novelty, familiarity, or leaderboard rank by itself.
A current failure does not exclude this Workflow when the requested output is still the choice among
credible approaches. Once an approach is accepted, its first production implementation or explicit
replacement belongs to `workflow-implementation`, even when that failure motivated the decision.

## Evidence Authority
- Production-fit claims require comparable actual-path observation, including material storage, serialization, data, and environment boundaries.
- External benchmarks establish only their measured workload and version. Verify changeable library/product facts with fresh authoritative evidence.
- Formal analysis can decide an exactly formal condition when its assumptions hold. An asymptotic proof does not establish runtime speed or constants.
- A runtime improvement claim needs comparable before/after evidence on the relevant path. Expected gains remain hypotheses.

## Comparison And Recommendation
Use only decision-changing axes: correctness/problem fit, data/workload assumptions, scaling, latency/throughput/memory/compute, dependencies/deployment, operational complexity, observability, failure modes, rollback, and implementation cost.

Name the evidence that would reverse the recommendation. Prefer the cheapest discriminating check before broad implementation. If evidence changes the problem—for example, I/O rather than algorithmic work is the measured bottleneck—handoff instead of forcing an algorithm winner.

For a small decision return:
- selected approach or `Unverified`
- decisive reason and evidence scope
- main risk or missing condition
- falsifying check

For consequential ambiguity, add a compact constraint/candidate comparison, causal mechanism, fallback, and handoff. Omit empty sections and avoid a matrix unless it clarifies a real trade-off.
