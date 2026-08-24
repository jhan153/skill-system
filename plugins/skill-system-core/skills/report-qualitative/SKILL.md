---
name: report-qualitative
description: Produce an explicitly requested qualitative evaluation of an artifact, system, design, plan, or implementation using user-supplied, collaboratively elicited, or explicitly delegated criteria. Treat metrics as evidence rather than quality verdicts. Deliver content-first Markdown by default and optional matching HTML on explicit html/both or spatial intent. Not for blocker QA, metric inventories, diffs, validation execution, or implementation.
---

# Qualitative Evaluation Report

## Routing Card
- role: report_primary
- intent_signature: explicit qualitative fitness, strengths/weaknesses, tradeoff, or improvement-priority report
- use_when:
  - the user asks whether a target is fit for an intended purpose or requests a qualitative judgment under stated or delegated criteria
- do_not_use_when:
  - blocker-first QA or failure diagnosis is primary
  - the output is only metrics/counts, changed lines, telemetry, validation execution, or implementation
  - vague `검토/보고` wording provides no qualitative decision intent
- expected_inputs: bounded target, decision goal, stakeholder/use context, criterion authority, evidence anchors, and delivery mode
- expected_outputs: criterion-grounded Markdown evaluation; optional HTML projection with identical judgments
- context_targets:
  must_read:
    - target or smallest relevant slice
    - decision goal, constraints, criterion authority, and requested delivery mode
    - `references/report_delivery_contract.md`
  read_if_needed:
    - `references/quality-evaluation-method.md` when criteria need elicitation or delegated selection
    - `references/evidence_mapping.md` for large, ambiguous, or multi-source targets
    - `references/rubric.md` only for an explicitly ordinal or rubric-heavy report
    - `references/report_template.md` only for an explicitly full or reusable report
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when inspectable spatial evidence is material
  do_not_load_by_default:
    - rubrics/templates when a brief is sufficient, full repository/history, unrelated plans/reports, or generic example catalogs
- risk_profile:
  reads: bounded target and decisive evidence anchors
  writes: one Markdown report and only the explicitly selected optional HTML projection; never the evaluated artifact
  tools: focused read-only inspection when locally available evidence is decision-changing
  sensitive_resources: credentials denied; redact sensitive evidence
- entry_scene: PREPARE

## Delivery And Ownership

Apply `references/report_delivery_contract.md`. Markdown owns the substantive evaluation. HTML may
improve navigation but cannot add criteria, findings, scores, or certainty. A missing renderer does
not affect the evaluation result.

This skill evaluates; it does not implement fixes, run broad validation, edit Plan/Handoff, select
a successor, or become a blocker gate. A Plan-assigned evaluation closes only its named condition.

## Evaluation Contract

- Record criterion origin as `supplied`, `elicited`, `accepted_proposal`, `delegated`, or
  `assumed`. User-supplied or accepted criteria outrank model/repository preferences.
- Every criterion needs an observable indicator, evidence need, and context-specific yardstick.
  Generic quality attributes are candidate vocabulary, never an automatic checklist.
- LOC, complexity, coverage, latency, failure counts, and benchmark values are observations until
  the target context and yardstick give them meaning.
- Default to zero to three decision-material findings. Three is a ceiling, not a quota. Expand only
  for an explicitly full report.

Modes:

- `DecisionBrief`: default conclusion, material findings/tradeoffs, one action, and limitations.
- `FullOrRubric`: only on explicit full, reusable, table-heavy, or rubric intent.

## Workflow

1. Bind target, decision, stakeholder perspective, intended use/lifecycle, responsibilities,
   expected changes/failures, constraints, exclusions, criterion authority, and delivery mode.
2. Resolve criterion authority before judging. If user priorities could change the criteria, ask
   one bounded round of up to three independent questions and stop before creating an evaluation.
   If selection is explicitly delegated, propose only the smallest context-grounded set.
3. Inspect the smallest relevant slice plus one result-changing counterexample, boundary, or
   tradeoff. Load evidence mapping only when the target actually needs it.
4. Build each finding as `Criterion -> Observation -> Interpretation -> Impact -> Judgment ->
   Recommendation`. Separate observed, inferred, risk, and recommendation content.
5. Mark unsupported judgment `not_evidenced` and confidence `high`, `medium`, `low`, or
   `not_assessable`. Never average ordinal ratings or imply interval precision.
6. Produce Markdown first. If HTML is selected, project the same criteria/findings/evidence and
   render once without adding dashboard filler or a second evaluation pass.

## Output Contract

For `DecisionBrief`, return the decision, criterion origins, zero to three material findings, one
next action, and material limits. For `FullOrRubric`, add only the accepted criterion/yardstick map,
evidence map, detailed findings, counterexamples/tradeoffs, and limitations.

Return the Markdown link first and optional HTML link second. The closing action is a recommendation,
not a workflow transition. Stop after delivery.
