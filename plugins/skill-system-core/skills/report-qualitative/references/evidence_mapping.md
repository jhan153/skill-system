# Evidence Mapping

Use this reference when the evaluation target is large, ambiguous, multi-source, or likely to produce unsupported judgments.

## Core Contract

Every major judgment must follow this chain:

```text
Criterion -> Observation/Measurement -> Context/Yardstick
-> Interpretation -> Impact -> Judgment -> Recommendation
```

Do not skip directly from criterion to judgment. A qualitative report fails when it becomes:
- an opinion piece without evidence,
- a score table without reasons,
- or an abstract recommendation list without traceability.

## Required Evidence Map

Use a compact map before final findings:

| Criterion | Observation / Measurement | Evidence | Context / Yardstick | Interpretation | Judgment | Confidence |
| --- | --- | --- | --- | --- | --- | --- |

Evidence can be:
- source text or section reference
- file path and line reference
- code behavior or command output
- validation result
- data table or metric
- provided user context
- absence of expected information, marked as `Not evidenced`

## Measurement Boundary

Measurements are observations, not self-interpreting quality judgments.

- LOC does not establish maintainability.
- complexity does not establish comprehensibility or defect risk without path and change context.
- coverage does not establish correctness or test quality.
- dependency count does not establish harmful coupling.
- failure or participant frequency does not establish cause or generality beyond the observed sample.

Interpret a measurement only after naming the responsibility, scenario, affected stakeholder, and context-specific yardstick. A metric-only inventory belongs to its direct analysis owner, not this qualitative report.

Do not reproduce sensitive values as evidence. Redact the value and cite only the location or evidence category.

## Evidence Language

Use these labels to keep facts and judgment separate:

- `Observed:` facts visible in the artifact or evidence pack.
- `Inferred:` reasonable interpretation based on partial evidence.
- `Not evidenced:` missing or unsupported evidence.
- `Risk:` possible negative outcome.
- `Recommendation:` specific next action.

## Confidence

| Confidence | Use When |
| --- | --- |
| High | Direct evidence supports the finding. |
| Medium | Partial evidence supports the finding, but interpretation is needed. |
| Low | Evidence is weak, ambiguous, stale, or incomplete. |
| Not assessable | Evidence is missing or outside the provided scope. |

## Evidence Boundaries

- Do not infer hidden behavior, hidden intent, or unstated requirements.
- Do not penalize missing information when it is outside the artifact's stated scope.
- Do not treat user claims as verified artifact evidence unless the claim itself is the artifact being evaluated.
- Do not use external knowledge as proof unless the user requested external verification or the source is included in the evidence pack.
- When external evidence is used, label it as `External evidence` and keep it separate from artifact-grounded evidence.
- Do not quote secrets, credentials, tokens, private keys, passwords, session cookies, or sensitive personal data verbatim.
- If sensitive evidence matters to the judgment, describe the evidence class and cite the location with the sensitive value redacted.
- If a criterion cannot be judged, report `Not assessable` and explain what evidence would be needed.

## Evaluation Questions

For each criterion, answer:
1. What is being judged?
2. What was observed or measured, and where?
3. What context and yardstick give that observation quality meaning?
4. What interpretation follows, including a counterexample or boundary condition?
5. What is the practical implication for the decision?
6. What action would improve the target?

## Failure Prevention

| Failure Type | Prevention Rule |
| --- | --- |
| Opinion-only report | Require an evidence map and criterion findings. |
| Score-only report | Pair rating with evidence, interpretation, implication, and recommendation. |
| Metric-as-verdict | Require target context and a criterion-specific yardstick before interpretation. |
| Abstract recommendations | Attach priority, rationale, expected impact, and effort. |
| Overconfident report | Use confidence labels and limitations. |
| Missing-evidence confusion | Mark `Not evidenced` instead of guessing. |
