---
name: report-implementation-explainer
description: Create an explicitly requested, source- and runtime-anchored Report Canvas explanation of an existing implementation, including causal execution, evidence status, and productization gaps. Use when a user needs a working model for a concrete next decision; do not use for diff-only output, verdicts, pre-implementation algorithm choice, local line explanation, or an automatic post-implementation gate.
---

# Report Implementation Explainer

## Routing Card
- role: report_primary
- intent_signature: source-anchored implementation explanation, literate code review, algorithm walkthrough, or code-review-style HTML
- use_when:
  - the user explicitly requests an explanation artifact for a concrete implementation, change, branch, or pull request and a next decision benefits from causal understanding.
- do_not_use_when:
  - changed lines belong to `report-diff`; quality/readiness verdicts to `report-qualitative` or `report-critical`; approach selection to `analysis-algorithm`; code changes to `workflow-implementation`.
  - a direct answer is sufficient, no concrete implementation target exists, or the artifact would be added automatically after ordinary implementation.
- expected_inputs: concrete target and snapshot, reader/decision purpose, production path, and available runtime evidence
- expected_outputs: Report Canvas `trace` or evidence-backed `spatial` HTML with a source-linked causal explanation, calibrated evidence/status, productization gaps, and one next handoff
- context_targets:
  must_read:
    - requested target, format, audience, decision purpose, and canonical caller-to-output path
  read_if_needed:
    - accepted intent, focused tests, runtime trace/readback, rationale history, and a material failure/counterexample
  do_not_load_by_default:
    - full repository/history, unrelated plans, generated mirrors, or broad logs
- risk_profile:
  reads: narrow source, config, tests, traces, and accepted decisions
  writes: one self-contained report HTML by default; no production source or instrumentation mutation
  tools: focused read-only inspection and safe local rendering; new production instrumentation belongs to implementation
  sensitive_resources: credentials default deny; redact sensitive runtime data for the audience
- entry_scene: FINALIZE

## Evidence Contract

Pin a commit, diff, branch, release, or clearly labeled current-worktree snapshot. Treat the explainer as a derived index, never evidence or a new source of truth:

1. accepted intent states desired behavior;
2. production source/config/schema establishes the implemented path;
3. runtime readback establishes only what it observed;
4. tests establish only their named contract; rationale/history explains why.

Label material claims `intent_stated`, `source_established`, `runtime_observed`, `inferred`, `hypothetical`, or `unverified`. Do not turn source inspection into runtime behavior or a passing test/interface into operability or release readiness.

Keep status axes separate when relevant: `core_capability` (operation exists), `integration` (real callers reach it), `operability` (a person can control and observe it), and `release` (acceptance/safety/performance/compatibility evidence). Never emit `understood: true` or credit scrolling; source and side-chat use are valid open-book navigation.

## Artifact And Workflow

- For every admitted invocation, read `references/report_canvas_contract.md` and render the primary human-facing explanation with `scripts/report-canvas/render_report.py` as Report Canvas `trace` HTML, or `spatial` when authoritative 3D data materially improves inspection. Return only a concise chat receipt with the outcome and artifact link. Use chat-only output only when the user explicitly prohibits file creation or the host has no safe artifact surface; use archival Markdown only when explicitly requested or required by the repository.
- Add interactive, stepwise, or spatial views only from an authoritative production trace/readback. Never recreate the algorithm independently in JavaScript. Feed supplied geometry, stable IDs, state snapshots, and issue indices to the shared renderer; if trace points are missing, name the smallest readback seam for `workflow-implementation` and keep the view `unverified`.

1. Name the target snapshot and the decision the reader should be able to make.
2. Trace the smallest production caller-to-output path, including policy ownership, identity/state transitions, and applicable failure boundaries.
3. Use one representative scenario. Add a counterexample only when a branch, failure, or invariant can materially change the decision; for high-risk mutation capture initial state, observable result, and falsifier.
4. Gather evidence proportional to the claims. Require runtime readback for mutation, source selection, adapters, transforms, or failure atomicity claims; otherwise label the limit.
5. Include only useful sections: outcome/status, intuition, causal path, representative state change, invariants/failures, source map, evidence ledger, productization gaps, source index.
6. Keep excerpts small and navigational. End with one action: behavior decisions to `plan-behavior-discovery`, instrumentation/product changes to `workflow-implementation`, or verdicts to their report owner.

## Participation And Validation

Artifact creation proves only `explainer_generated`. Report `scenario_exercised`, `behavior_compared`, `decision_confirmed`, or `assumption_delegated` only when observed; otherwise keep `participation_unverified`.

If the user explicitly requests a comprehension check, keep it open-book and tied to a real decision. Name the exact target, underlying source/runtime anchor, initial state, observable difference, and decision consequence; require a falsifier only for high-risk or irreversible behavior.

Before returning, confirm the snapshot, evidence label/anchor for each material claim, separate status axes, applicable counterexample/unknown, working links/navigation, no duplicated production logic, and no claim about the reader's mental state.
