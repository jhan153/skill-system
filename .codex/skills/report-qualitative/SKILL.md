---
name: report-qualitative
description: Produce evidence-based qualitative evaluation reports for artifacts, documents, skills, workflows, product specs, implementations, research plans, designs, or operating processes. Use for qualitative assessment, strengths/weaknesses, readiness review, rubric-based evaluation, risk interpretation, and prioritized improvement recommendations. Use compact evidence mode only for explicit `srq` or formal completion-report requests. Not for blocker-first QA gates, readable diffs, artifact inventories, implementation, debugging, telemetry, or purely quantitative benchmarking without qualitative interpretation.
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
  - improvement recommendations
  - explicit-only `srq` or formal evidence-first report requests
- use_when:
  - the user wants a human-readable qualitative report about an artifact's quality, usefulness, readiness, risks, or improvement path.
  - the user asks to evaluate a skill, workflow, plan, document, design, implementation, research artifact, proposal, or operating process.
  - the user explicitly asks for `srq`, `srq로`, `formal report`, or evidence-first completion reporting.
- do_not_use_when:
  - the user wants blocker-first critical review, QA gate verdicts, or failure diagnosis; use `report-critical`.
  - the user wants actual changed lines or before/after diff presentation; use `report-diff`.
  - the user wants a file/artifact inventory or handoff list; use `report-artifact-inventory`.
  - the user wants skill-system eval case review or usage telemetry; use `evaluation-harness` or `evaluation-usage-tracker`.
  - the task is implementation, debugging, or validation execution rather than a report.
- expected_inputs:
  - artifact or artifact slice
  - evaluation goal and intended audience
  - user-provided rubric or default criteria
  - evidence anchors, validation results, or source references when available
- expected_outputs:
  - qualitative report with scope, method, evidence map, criterion findings, risks, recommendations, final judgment, and limitations
  - compact evidence-first report only when legacy `srq`/completion-report mode is explicitly requested
- context_targets:
  must_read:
    - target artifact or the smallest relevant slice
    - user goal, constraints, and requested output shape
  read_if_needed:
    - `references/rubric.md` for score definitions or domain criteria
    - `references/evidence_mapping.md` for evidence map discipline, confidence, and judgment traceability
    - `references/report_template.md` for full report structure
    - `references/examples.md` for prompt/output examples and over-trigger guards
    - validation output, changed file list, or evidence pack
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated plans, reports, or historical artifacts
- risk_profile:
  reads:
    - provided or referenced artifact slices and evidence anchors
  writes:
    - none unless the user explicitly requests a report artifact file
  tools:
    - focused read-only inspection only when evidence is missing and local context is available
  sensitive_resources:
    - credentials default deny; redact secrets, tokens, private keys, passwords, cookies, and sensitive personal data in quoted evidence
- entry_scene:
  - PREPARE

## Purpose
Use this skill to create a structured, evidence-based qualitative evaluation report.

The report must not be a vague opinion. It should:
1. define the evaluation scope,
2. select or adapt evaluation criteria,
3. inspect the artifact,
4. map observable evidence to each criterion,
5. separate observation, inference, judgment, and recommendation,
6. identify strengths, weaknesses, risks, uncertainty, and readiness,
7. provide prioritized, actionable improvements.

## Modes
### A. Qualitative Evaluation Report
Default mode. Use for quality/readiness/risk/usefulness assessment of an artifact.

### B. Compact Evidence Report
Use only for explicit legacy aliases such as `srq`, `srq로`, `formal report`, or completion/handoff reporting where the user wants verified vs unverified separation but not a full qualitative evaluation.

Do not enter compact evidence mode from vague requests such as "검토해줘", "요약해줘", or "보고해줘". Those requests need normal task routing or explicit qualitative-report intent.

## Trigger Shortcuts
- `report-qualitative`
- `정성 평가 리포트`
- `정성평가`
- `qualitative evaluation`
- `rubric-based review`
- `readiness review`
- `srq`
- `srq로`
- `formal report`
- `evidence-first report`

## Required Framing
Before evaluating, identify or infer:
- `artifact`: content, file, code, plan, document, skill, workflow, design, or process to evaluate
- `evaluation_goal`: what the user wants to decide or learn
- `audience`: who will use the report
- `context`: intended use, domain, constraints, and known requirements
- `criteria`: user rubric or default criteria
- `output_preference`: concise report, full report, table-heavy report, executive summary, or compact evidence report

If critical information is missing, ask at most two focused clarification questions. If the evaluation can proceed with assumptions, proceed and list the assumptions explicitly.

## Default Criteria
Use these unless the user provides a custom rubric.

1. Purpose Fit: whether the artifact clearly serves its intended purpose.
2. Structural Clarity: whether the artifact is organized for understanding and use.
3. Evidence and Grounding: whether claims and judgments are traceable to evidence.
4. Practical Usability: whether the artifact can be used in a realistic setting.
5. Risk and Failure Modes: what may reduce quality, reliability, safety, correctness, or adoption.
6. Improvement Leverage: which changes would produce the largest quality gain.

Optional domain criteria:
- Skills or agent workflows: invocation clarity, input/output contract, progressive disclosure, tool/resource boundaries, safety checks, fallback behavior.
- Documents or reports: executive summary quality, argument structure, evidence synthesis, audience fit, completeness, limitations, recommendation traceability.
- Code or implementation: maintainability, correctness risk, readability, error handling, dependency risk, testability, operational safety.
- Research artifacts: research question clarity, methodological validity, evidence quality, novelty, reproducibility, ethical or safety considerations.

Read `references/rubric.md` when a scored or detailed rubric-based report is needed.

## Evidence Rules
Every major judgment must be traceable to evidence.

Core chain:
`Criterion -> Evidence -> Interpretation -> Judgment -> Recommendation`

Required discipline:
- Quote or reference specific sections, files, lines, logs, examples, or source text when possible.
- Separate `Observed`, `Inferred`, `Risk`, and `Recommendation`.
- Mark missing support as `Not evidenced`.
- Do not quote secrets, credentials, tokens, private keys, passwords, session cookies, or sensitive personal data verbatim. Cite the location and redact the value.
- If sensitive evidence is relevant, describe the evidence category rather than reproducing the sensitive content.
- When external evidence is used, label it as `External evidence` and do not mix it with artifact-grounded evidence.
- Do not infer hidden behavior, hidden intent, or unstated constraints.
- Do not over-penalize missing information if it is outside the artifact's stated scope.
- Do not make a recommendation unless it is traceable to evidence, clearly labeled expert judgment, or a stated user goal.
- If evidence is ambiguous, state the ambiguity and how it affects confidence.

Confidence values:
- High: directly supported by artifact evidence.
- Medium: supported but incomplete or partly inferred.
- Low: weak, ambiguous, or missing evidence.
- Not assessable: evidence is missing or outside provided scope.

Read `references/evidence_mapping.md` when the artifact is large, ambiguous, multi-source, or likely to produce unsupported judgments.

## Workflow
1. Frame: identify artifact type, goal, audience, scope, assumptions, constraints, criteria, and exclusions.
2. Inspect: read the relevant artifact slice and capture strengths, gaps, contradictions, unsupported claims, readiness evidence, and incompleteness evidence.
3. Map Evidence: build a compact evidence map before final judgments.
4. Judge: for each criterion, provide rating or qualitative level, evidence, interpretation, implication, risk/gap, and recommendation.
5. Prioritize: distinguish P0/P1/P2/P3 recommendations and Critical/Major/Minor risks.
6. Report: use the requested output shape or the default qualitative report structure.

## Rating Guidance
Use a 1-5 scale only when useful or requested:
- 1 = Poor: major issues block use.
- 2 = Weak: usable only with substantial revision.
- 3 = Adequate: meets baseline expectations but has clear gaps.
- 4 = Strong: mostly ready, with manageable improvements.
- 5 = Excellent: clear, well-grounded, actionable, and low-risk.

Avoid decimal scores unless explicitly requested. Do not use false precision.

Readiness levels:
- Not ready
- Needs major revision
- Usable with revisions
- Ready for limited use
- Ready for production or publication

## Default Output Contract
For a full qualitative report, use:
1. Executive Summary
2. Evaluation Scope
3. Method
4. Evidence Map
5. Findings by Criterion
6. Strengths
7. Weaknesses and Risks
8. Recommendations
9. Final Judgment
10. Limitations

For concise reports, preserve the same logic but collapse sections:
- Conclusion
- Evidence Map
- Criterion Findings
- Recommendations
- Limitations

Read `references/report_template.md` when the user asks for a full, table-heavy, or reusable report structure.
Read `references/examples.md` when writing or validating prompts for this skill, or when routing ambiguity needs examples.

## Compact Evidence Report Mode
Use this only for explicit `srq`/formal completion-report intent.

Structure:
1. Conclusion: one-line result.
2. Evidence: up to three verified facts with locations.
3. Action: one concrete completed action or next action.
4. Verification: include only for code, workflow, or delivery tasks.

This mode is a compatibility path. Do not let it replace qualitative evaluation when the user asks for assessment, readiness, strengths/weaknesses, or recommendations.
Do not enter this mode from vague requests such as "검토해줘", "요약해줘", or "보고해줘".
Enter this mode only when the user explicitly says `srq`, `srq로`, `formal report`, or asks for a verified completion/evidence report.

## Cross-Skill Resolution
- `report-critical` owns blocker diagnosis, QA gates, severe-risk verdicts, and critical review findings.
- `report-diff` owns changed-line and before/after presentation.
- `report-artifact-inventory` owns artifact lists, verification notes, and handoff inventories.
- `evaluation-harness` owns eval-case review; `evaluation-usage-tracker` owns invocation telemetry.
- `workflow-validation` owns validation matrix design and validation execution. This skill may report validation meaning, but it does not run validation by default.
- `workflow-rigor` owns implementation discipline and completion gates. This skill can report the result only after evidence exists.
- If another named skill is unavailable, do not fail. Handle only the qualitative reporting portion and state that specialized diff, blocker, artifact-inventory, telemetry, or validation handling is out of scope.
- If the user asks to qualitatively evaluate a diff, use this skill for judgment and recommendations, but do not present changed-line diffs unless explicitly requested.

## Resource and Risk Boundary
- Reads: target artifact, explicit evidence pack, validation output, and narrow supporting context.
- Writes: none unless the user explicitly requests a report artifact.
- Tool/process calls: read-only inspection only; no broad validation runs by default.
- Network: none by default. Browse only when the user asks for current/external evidence or high-stakes factual verification requires it.
- Credentials: default deny.
- Evidence quoting: redact sensitive values and cite only the location or evidence category.
- External evidence: label separately from artifact-grounded evidence.
- Destructive actions: out of scope.

## Quality Checklist
Before returning the report, verify:
- Every major judgment has evidence.
- Every criterion has either a finding or a stated reason for insufficient evidence.
- Recommendations are traceable to findings.
- Assumptions and limitations are explicit.
- Scores are not more precise than evidence supports.
- Observations, inferences, risks, and recommendations are separated.
- The final verdict is decision-useful.
- The report does not fail as an opinion piece, score-only output, or abstract recommendation list.
