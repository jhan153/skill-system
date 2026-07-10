---
name: report-qualitative
description: "Produce decision-first, evidence-grounded qualitative evaluations of artifacts, skills, plans, designs, or implementations. Use when the user asks about quality, readiness, risks, strengths and weaknesses, or prioritized improvements; use a full or scored report only when explicitly requested. Not for blocker QA, diffs, inventories, telemetry, or implementation."
---

# Qualitative Evaluation Report

## Routing Card
- role: report_primary
- intent_signature:
  - qualitative evaluation report
  - 정성 평가 리포트
  - evidence-based assessment
  - strengths and weaknesses
  - readiness review
  - rubric-based review
  - explicit-only `srq` or formal evidence-first report requests
- use_when:
  - the user needs a decision about an artifact's quality, usefulness, readiness, risks, or improvement path.
  - the user explicitly requests a qualitative, rubric-based, readiness, strengths/weaknesses, or evidence-first assessment.
- do_not_use_when:
  - the user wants blocker-first critical review or failure diagnosis; use `report-critical`.
  - the user wants changed lines, an artifact inventory, eval telemetry, validation execution, or implementation.
  - the request is an ordinary code review or vague “검토/보고” request without qualitative-assessment intent.
- expected_inputs:
  - target artifact or smallest relevant slice
  - decision goal, audience, constraints, and user rubric when provided
  - evidence anchors or validation results when available
- expected_outputs:
  - a decision brief with no more than three material findings by default
  - a full/scored report only on explicit request
  - a compact evidence report only for explicit `srq` or formal completion-report intent
- context_targets:
  must_read:
    - target artifact or smallest relevant slice
    - user goal, constraints, and requested output shape
  read_if_needed:
    - `references/evidence_mapping.md` for large, ambiguous, or multi-source targets
    - `references/rubric.md` for explicitly scored or detailed criterion reports
    - `references/report_template.md` for full, table-heavy, or reusable reports
    - `references/examples.md` only for routing or prompt validation
    - narrow validation output or evidence pack
  do_not_load_by_default:
    - detailed rubrics or templates for the default brief
    - full repo, full memory bank, unrelated plans, reports, or history
- risk_profile:
  reads:
    - provided artifact slices and decisive evidence anchors
  writes:
    - none unless the user explicitly requests a report file
  tools:
    - focused read-only inspection when evidence is missing and locally available
  sensitive_resources:
    - credentials default deny; redact sensitive values in cited evidence
- entry_scene:
  - PREPARE

## Operating Contract
- Make the result useful for a decision, not merely comprehensive.
- Lead with the judgment. Keep only findings that could change readiness, priority, adoption, or the next action.
- Treat three material findings as a ceiling in the default mode, not a quota. Omit low-impact polish and repeated symptoms.
- Do not implement fixes, run broad validation, or turn the report into a blocker gate.

## Modes

| mode | activation | output depth |
| --- | --- | --- |
| `DecisionBrief` | default qualitative-assessment intent | conclusion, 0–3 material findings, next action, material limits |
| `FullOrScored` | explicit full, scored, rubric, table-heavy, or reusable-report request | detailed evidence map and criterion coverage using the conditional references |
| `CompactEvidence` | explicit `srq`, `srq로`, formal completion report, or verified handoff report | conclusion, up to three verified facts, action, and relevant verification |

Do not infer `FullOrScored` from the size of the artifact. Do not infer `CompactEvidence` from vague “검토해줘”, “요약해줘”, or “보고해줘”.

## Evaluation Kernel
Use the user's rubric when present. Otherwise choose only the criteria needed for the decision from:

- purpose fit
- structural clarity
- evidence and grounding
- practical usability
- risk and failure modes
- improvement leverage

Use this chain for every material judgment:

`Criterion -> Evidence -> Interpretation -> Judgment -> Recommendation`

Read `references/rubric.md` for detailed scales and domain criteria only in `FullOrScored` mode. Use a 1–5 score only when explicitly requested; avoid decimals.

## Workflow
1. Frame the decision: identify the artifact, audience, intended use, constraints, exclusions, and what choice the report should support. Infer safe details and disclose only assumptions that affect the verdict.
2. Inspect the smallest relevant artifact slice. Capture evidence for both readiness and incompleteness; do not reward static presence when runtime or user-path evidence is what matters.
3. Build a compact evidence map before judging. Keep it internal in `DecisionBrief`; emit it only when it materially helps or the user requests the full form.
4. Rank candidate findings by decision impact, evidence strength, and improvement leverage. Merge common causes and retain at most three in `DecisionBrief`.
5. State the decision first, then findings and actions. Put missing evidence in limitations rather than manufacturing certainty.

## Evidence Discipline
- Cite a section, file/line, command result, example, or provided fact for every material finding when available.
- Separate `Observed`, `Inferred`, `Risk`, and `Recommendation`; mark absent support `Not evidenced`.
- Use confidence `High`, `Medium`, `Low`, or `Not assessable` according to evidence strength.
- Do not infer hidden behavior, intent, or requirements, and do not penalize information outside the artifact's stated scope.
- Label external evidence separately from artifact-grounded evidence.
- Redact secrets and sensitive personal data; cite the location or evidence class, not the value.
- A recommendation must address an observed gap, a stated goal, or clearly labeled expert judgment.

Read `references/evidence_mapping.md` only when the target is large, multi-source, ambiguous, or prone to unsupported judgments.

## Output Contracts

### DecisionBrief (default)
1. `Conclusion`: decision, readiness, and the main reason in one or two sentences.
2. `Material findings`: zero to three items, ordered by impact. Each item contains judgment, decisive evidence, decision impact, recommended action, and confidence.
3. `Next action`: the single highest-leverage step; add up to two more only when independent and necessary.
4. `Limitations`: only missing evidence or assumptions that could change the conclusion.

Do not add separate strengths, weaknesses, evidence-map, or score sections when they would repeat the same findings.

### FullOrScored
Read `references/report_template.md` and, when scoring or domain criteria are requested, `references/rubric.md`. Cover all requested criteria, but keep the executive decision first and avoid duplicate prose around tables.

### CompactEvidence
Use only for the explicit aliases above:

1. `Conclusion`: one-line result.
2. `Evidence`: up to three verified facts with locations.
3. `Action`: one completed or next action.
4. `Verification`: only for code, workflow, or delivery tasks.

This compatibility mode does not replace qualitative assessment when the user asks for readiness, strengths/weaknesses, risks, or improvements.

## Boundaries
- `report-critical` owns blocker diagnosis and QA verdicts.
- `report-diff` owns changed-line and before/after presentation.
- `coordination-handoff` owns handoff inventories.
- `evaluation-harness` and `evaluation-usage-tracker` own eval cases and telemetry.
- `workflow-validation` owns check design and execution; this skill reports only the meaning of existing results.
- If a specialized owner is unavailable, return only the qualitative portion and state the limitation.

## Validation
- The conclusion appears before methodology or detail.
- The default report contains no more than three material findings.
- Every material judgment is evidence-backed or explicitly uncertain.
- Recommendations trace to findings and are ordered by decision impact.
- Scores and detailed rubrics appear only when explicitly requested.
- Full templates and detailed references were loaded only for the mode that needs them.
- The response remains an evaluation report, not implementation, validation execution, diff output, or telemetry.
