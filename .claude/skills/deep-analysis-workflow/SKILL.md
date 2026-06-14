---
name: deep-analysis-workflow
description: "Routing workflow for deep technical analysis: choose bug diagnosis, algorithm recommendation, or a hybrid sequence based on the user's actual question."
---

# Deep Analysis Workflow

## Routing Card
- role: router
- intent_signature:
  - `deep-analysis`, `da`, 심층 기술 분석, 원인과 접근을 같이 봐야 하는 요청
- use_when:
  - bug diagnosis, algorithm proposal, or hybrid technical analysis must be selected before work starts.
  - the request needs a specialist workflow but not a repo-wide report artifact.
- do_not_use_when:
  - a quick fix, pure Q&A, ordinary architecture sketch, or explicit heavy report workflow is enough.
  - vague words like `탐색해` appear without deep technical diagnosis or recommendation intent.
- expected_inputs:
  - current user request
  - known symptom, decision, or analysis goal
- expected_outputs:
  - selected mode: `bug`, `algorithm`, `hybrid`, or `out-of-scope`
  - selected specialist skill and context boundary
- context_targets:
  must_read:
    - current request
    - selected specialist skill card
  read_if_needed:
    - repo source outline when the request is codebase-specific
    - failing output or constraints supplied by the user
  do_not_load_by_default:
    - full repo
    - full memory bank
    - codebase-intel artifacts
- risk_profile:
  reads:
    - current request and targeted repo context only
  writes:
    - none; selected specialist owns writes
  tools:
    - none by default
  sensitive_resources:
    - do not inspect credentials or broad reports during routing
- entry_scene:
  - PREPARE

## Related Skills
- `deep-bug-analysis`: owns reproducibility, evidence collection, root-cause selection, and bug-fix validation.
- `deep-algorithm-proposal`: owns constraint extraction, candidate comparison, recommendation, and validation planning.
- `strict-evidence-driven-reporting-workflow`: owns execution rigor when implementation work is requested.
- `strict-response-quality`: owns formal user-facing report structure when explicitly active.
- `codebase-intel-report`: use only when the user explicitly wants a repo-wide integrated analysis/report artifact rather than point diagnosis or recommendation.

## Trigger
- `deep-analysis`
- `deep`
- `da`

## Trigger Guard (Do Not Trigger)
- Pure quick-patch requests where the failure and fix are already obvious.
- Pure architecture/HLD/LLD requests where system boundaries are the main decision.
- Information-only requests that do not need deep diagnosis or recommendation.
- `탐색해` by itself; require explicit deep technical analysis, RCA, or approach-selection intent.

## Goal
- Route deep technical requests to the right analysis mode before doing substantial work.
- Prevent recommendation questions from being forced into RCA by default.
- Preserve backward compatibility for existing `$deep-analysis-workflow` invocations.

## Mode Gate
- `bug`: the main question is why something broke, where the root cause is, or why it recurs.
- `algorithm`: the main question is what algorithm, model, retrieval strategy, or local solution approach fits best.
- `hybrid`: the task needs both diagnosis and recommendation.
- `out-of-scope`: a lighter workflow or a different specialist skill is a better fit.

## Selection Rules
- Choose `bug` when the core request is to diagnose, debug, explain a malfunction, or confirm a root cause.
- Choose `algorithm` when the core request is to recommend or compare approaches.
- Choose `hybrid` when the current failure must be explained before recommending the replacement strategy.
- Choose `out-of-scope` when a quick local fix, architecture design, or information-only answer is enough.
- Do not escalate a point bug or recommendation request into `codebase-intel-report` unless the user explicitly asks for a repo-wide report artifact, architecture report, or metrics report.

## Execution Order
1. Frame the user request in one sentence.
2. Select one mode.
3. Use only the selected specialist skill.
4. For `hybrid`, fixed order is:
   1. `deep-bug-analysis`
   2. `deep-algorithm-proposal`
5. Pull in `strict-evidence-driven-reporting-workflow` only if implementation is requested.
6. Pull in `strict-response-quality` only if the user explicitly asks for a formal report.
7. Pull in `codebase-intel-report` only when the user explicitly requests a repo-wide integrated report or report artifact.

## Output Contract
- If routing is relevant, the first sentence should state which mode was selected.
- Do not dump router internals to the user unless they asked for the routing rationale.
- The selected specialist skill owns the rest of the answer.

## Resource and Risk Boundary
- Reads: current request and narrow source outline only when needed.
- Writes: none; routing must not mutate files, memory, plans, or reports.
- Tool/process calls: none by default.
- Network access: none by default.
- Credential access: default deny.
- Generated artifacts: none; heavy report/package artifacts require explicit user artifact intent.
- Destructive actions: never owned by this router.
- Required checkpoints: before delegating to a primary workflow, confirm that the selected skill matches the user's intent and that heavy artifacts were explicitly requested.

## Recovery and Context Expansion
- If the request looks like a bug but lacks a symptom or repro, route to `deep-bug-analysis` with missing inputs marked `Unverified`.
- If the request asks for an approach but lacks constraints or success metrics, route to `deep-algorithm-proposal`.
- If repo structure is unclear, read repo source outline first.
- If the user goal is unclear, state the assumption rather than loading unrelated context.
- If skill mismatch is detected, return to scheduling and select a more appropriate skill.
- Never recover by loading all memory, all repo docs, all skills, or codebase-wide reports at once.

## Anti-Patterns
- Defaulting every ambiguous request to root-cause analysis.
- Hijacking a single bug RCA request with a repo-wide codebase report workflow.
- Doing full RCA for a pure recommendation question.
- Recommending an algorithm without naming constraints or alternatives.
- Implementing changes during information-only analysis.

## Known Limits
- Routing is based on request intent and available context; ambiguous intent must return to scheduling.
- This router does not prove root cause or algorithm fit without downstream evidence.
- Context targets may miss repo-specific contracts; expand one layer at a time.
- Router skills must not perform writes.
