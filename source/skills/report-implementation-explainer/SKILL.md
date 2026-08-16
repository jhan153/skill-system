---
name: report-implementation-explainer
description: Create an explicitly requested Report Canvas explanation of an existing implementation or a verified changed-lines comparison. Use `explain` for source/runtime causal understanding and `compare` for diff-only or before/after presentation; do not use for quality/readiness verdicts, pre-implementation algorithm choice, local line explanation, or an automatic post-implementation gate.
---

# Report Implementation Explainer

## Routing Card
- role: report_primary
- intent_signature: source-anchored implementation explanation or verified readable diff/before-after HTML
- use_when:
  - the user requests a causal implementation artifact or verified changed-line/before-after comparison.
- do_not_use_when:
  - quality/readiness verdicts belong to `report-qualitative` or `report-critical`; approach selection to `analysis-algorithm`; code changes to `workflow-implementation`.
  - a direct answer suffices, no concrete target exists, or the artifact would be automatic after ordinary implementation.
- expected_inputs: selected mode; concrete target/snapshot and production path for `explain`, or an authoritative diff/baseline pair for `compare`
- expected_outputs: Report Canvas `trace`/`spatial` causal explanation or verified `compare` HTML, with calibrated evidence and concise next handoff when applicable
- context_targets:
  must_read:
    - requested target, format, audience, decision purpose, and canonical caller-to-output path
  read_if_needed:
    - accepted intent, focused tests, runtime readback, rationale history, and a material counterexample
    - `references/compare-mode.md` for `compare`
  do_not_load_by_default:
    - full repository/history, unrelated plans, generated mirrors, or broad logs
- risk_profile:
  reads: narrow source, config, tests, traces, and accepted decisions
  writes: one self-contained report HTML by default; no production source or instrumentation mutation
  tools: focused read-only inspection and safe local rendering; new production instrumentation belongs to implementation
  sensitive_resources: deny credentials; redact sensitive runtime data
- entry_scene: FINALIZE

## Modes

- `explain`: use the causal source/runtime workflow below.
- `compare`: read [Compare Mode](references/compare-mode.md), preserve exact verified changed lines, and do not require a causal walkthrough or verdict.

## Canvas Asset Resolution

For every admitted invocation, set `REPORT_SKILL_DIR` to the directory containing this active skill's resolved `SKILL.md`; use the exact `file:` path exposed by the current skill catalog. The bundled contract documents the Codex plugin-cache layout explicitly. Never guess, glob, or select an install/cache version from the working directory.

Require `$REPORT_SKILL_DIR/references/report_canvas_contract.md` and `$REPORT_SKILL_DIR/scripts/report-canvas/render_report.py`. `source/tools/generate_targets.py` projects repository assets; it is not the renderer. If either local file is missing, report an incomplete installed payload and use only the contract's allowed chat fallback.

## Explain Evidence Contract

Pin a commit, diff, branch, release, or clearly labeled current-worktree snapshot. Treat the explainer as a derived index, never evidence or a new source of truth:

1. accepted intent states desired behavior;
2. production source/config/schema establishes the implemented path;
3. runtime readback establishes only what it observed;
4. tests establish only their named contract; rationale/history explains why.

Label material claims `intent_stated`, `source_established`, `runtime_observed`, `inferred`, `hypothetical`, or `unverified`. Do not turn source inspection into runtime behavior or a passing test/interface into operability or release readiness.

Keep status axes separate when relevant: `core_capability` (operation exists), `integration` (real callers reach it), `operability` (a person can control and observe it), and `release` (acceptance/safety/performance/compatibility evidence). Never emit `understood: true` or credit scrolling; source and side-chat use are valid open-book navigation.

## Explain Workflow

- Resolve the skill directory and renderer per `references/report_canvas_contract.md`; never guess an install/cache path. Render `trace`, or `spatial` only from authoritative 3D data. Use only the contract's allowed fallback.
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

Before returning, confirm the selected mode's baseline/snapshot, evidence labels, working links/navigation, and proof ceiling. In `explain`, also confirm separate status axes, applicable counterexample/unknown, no duplicated production logic, and no claim about the reader's mental state.
