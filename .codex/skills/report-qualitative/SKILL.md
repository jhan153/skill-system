---
name: report-qualitative
description: "Produce decision-first, evidence-grounded qualitative evaluations of artifacts, skills, plans, designs, or implementations as Report Canvas HTML by default. Use when the user asks about quality, readiness, risks, strengths and weaknesses, or prioritized improvements; use a full or scored report only when explicitly requested. Not for blocker QA, diffs, inventories, telemetry, or implementation."
---

# Qualitative Evaluation Report

## Routing Card
- role: report_primary
- intent_signature: explicit qualitative/readiness/strengths-risks/rubric evaluation or `srq` evidence report
- use_when:
  - the user needs a decision about an artifact's quality, usefulness, readiness, risks, or improvement path.
  - the user explicitly requests a qualitative, rubric-based, readiness, strengths/weaknesses, or evidence-first assessment.
- do_not_use_when:
  - the user wants blocker-first critical review or failure diagnosis; use `report-critical`.
  - the user wants a causal source/runtime walkthrough without a quality or readiness verdict; use `report-implementation-explainer`.
  - the user wants changed lines, an artifact inventory, eval telemetry, validation execution, or implementation.
  - the request is an ordinary code review or vague “검토/보고” request without qualitative-assessment intent.
- expected_inputs:
  - target artifact or smallest relevant slice
  - decision goal, audience, constraints, and user rubric when provided
  - evidence anchors or validation results when available
- expected_outputs:
  - Report Canvas HTML with no more than three material findings by default; `spatial` when the claim must be seen in 3D/math/graphics
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
    - `$REPORT_SKILL_DIR/references/report_visual_authoring.md` when the inspectable visual gate fires
    - narrow validation output or evidence pack
  do_not_load_by_default:
    - detailed rubrics or templates for the default brief
    - full repo, full memory bank, unrelated plans, reports, or history
- risk_profile:
  reads:
    - provided artifact slices and decisive evidence anchors
  writes:
    - one self-contained report HTML by default; no evaluated-artifact mutation
  tools:
    - focused read-only inspection when evidence is missing and locally available
  sensitive_resources:
    - credentials default deny; redact sensitive values in cited evidence
- entry_scene:
  - PREPARE

## Contract And Modes
- Lead with the decision and keep only findings that could change readiness, priority, adoption, or the next action.
- In the default mode, return zero to three items; three is a ceiling, not a quota. Merge repeated symptoms and omit low-impact polish.
- Do not implement fixes, run broad validation, or turn qualitative evaluation into a blocker gate.

| mode | activation | output depth |
| --- | --- | --- |
| `DecisionBrief` | default qualitative-assessment intent | conclusion, 0–3 material findings, next action, material limits |
| `FullOrScored` | explicit full, scored, rubric, table-heavy, or reusable-report request | detailed evidence map and criterion coverage using the conditional references |
| `CompactEvidence` | explicit `srq`, `srq로`, formal completion report, or verified handoff report | conclusion, up to three verified facts, action, and relevant verification |

Artifact size does not activate `FullOrScored`; vague “검토/요약/보고” does not activate `CompactEvidence`. Read detailed scales from `references/rubric.md` only in `FullOrScored` mode, and use integer 1–5 scores only when explicitly requested.

## Workflow
1. Frame the decision: artifact, audience, intended use, constraints, exclusions, and the choice the report supports.
2. Inspect the smallest relevant slice and capture evidence for readiness and incompleteness; do not reward static presence when runtime or user-path evidence is the condition.
3. Apply the user's rubric or only the needed criteria: purpose fit, clarity, grounding, usability, failure risk, and improvement leverage. For each material judgment use `Criterion -> Evidence -> Interpretation -> Judgment -> Recommendation`.
4. Cite sections, files/lines, commands, examples, or provided facts. Separate `Observed`, `Inferred`, `Risk`, and `Recommendation`; mark missing support `Not evidenced` and confidence `High`, `Medium`, `Low`, or `Not assessable`.
5. Rank by decision impact, evidence strength, and leverage; merge common causes. Put gaps that could change the verdict in limitations rather than manufacturing certainty.

Read `references/evidence_mapping.md` only for a large, multi-source, ambiguous, or unsupported-judgment-prone target. Distinguish external from artifact evidence, redact sensitive values, and never infer hidden intent or requirements outside scope.

## Canvas Asset Resolution

For every admitted invocation, set `REPORT_SKILL_DIR` to the directory containing this active skill's resolved `SKILL.md`; use the exact `file:` path exposed by the current skill catalog. The bundled contract documents the Codex plugin-cache layout explicitly. Never guess, glob, or select an install/cache version from the working directory.

Require `$REPORT_SKILL_DIR/references/report_canvas_contract.md` and `$REPORT_SKILL_DIR/scripts/report-canvas/render_report.py`. `source/tools/generate_targets.py` projects repository assets; it is not the renderer. If either local file is missing, report an incomplete installed payload and use only the contract's allowed chat fallback.

## Output
- `DecisionBrief`: conclusion, zero to three material findings with evidence/impact/action/confidence, one next action, and material limits.
- `FullOrScored`: read the report template and rubric, cover requested criteria, and avoid prose duplicating tables.
- `CompactEvidence`: one-line conclusion, up to three verified facts with locations, one action, and relevant verification.
- Render Report Canvas `decision` by default; use `compare` only for an authoritative before/after evidence pair. If the inspectable visual gate fires, read `$REPORT_SKILL_DIR/references/report_visual_authoring.md` and render `spatial` with supplied or sampled geometry instead of a card wall. Never edit Canvas CSS/JS or write a custom Three.js page. Return a concise receipt and use only contract-permitted chat fallback. Canvas never activates a deeper qualitative mode, adds findings, or strengthens evidence.

## Validation
- Conclusion precedes method; every judgment is evidenced or explicitly uncertain; recommendations trace to findings.
- Scores, detailed rubrics, and full templates appear only on explicit mode request.
- The result stays an evaluation, not implementation, validation execution, blocker QA, diff/inventory, handoff inventory, or telemetry.
