# Evidence Mapping

Use this reference when the evaluation target is large, ambiguous, multi-source, or likely to produce unsupported judgments.

## Core Contract

Every major judgment must follow this chain:

```text
Criterion -> Evidence -> Interpretation -> Judgment -> Recommendation
```

Do not skip directly from criterion to judgment. A qualitative report fails when it becomes:
- an opinion piece without evidence,
- a score table without reasons,
- or an abstract recommendation list without traceability.

## Required Evidence Map

Use a compact map before final findings:

| Criterion | Evidence | Interpretation | Confidence |
| --- | --- | --- | --- |

Evidence can be:
- source text or section reference
- file path and line reference
- code behavior or command output
- validation result
- data table or metric
- provided user context
- absence of expected information, marked as `Not evidenced`

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
2. What evidence supports or weakens the judgment?
3. What interpretation follows from that evidence?
4. What is the practical implication?
5. What action would improve the artifact?

## Failure Prevention

| Failure Type | Prevention Rule |
| --- | --- |
| Opinion-only report | Require an evidence map and criterion findings. |
| Score-only report | Pair rating with evidence, interpretation, implication, and recommendation. |
| Abstract recommendations | Attach priority, rationale, expected impact, and effort. |
| Overconfident report | Use confidence labels and limitations. |
| Missing-evidence confusion | Mark `Not evidenced` instead of guessing. |
