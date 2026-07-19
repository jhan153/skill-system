# Qualitative Evaluation Report Template

Use this full template when the user requests a complete, reusable, or table-heavy qualitative report. For short answers, collapse the same logic into fewer sections.

## 1. Executive Summary

Include:
- overall verdict
- readiness level
- top strengths
- top weaknesses
- highest-priority recommendations

## 2. Evaluation Scope

Include:
- artifact evaluated
- evaluation goal
- intended audience
- criteria used
- assumptions
- exclusions

## 3. Method

Briefly describe:
- how the artifact was reviewed
- what evidence was considered
- how ratings were assigned
- limitations of the review

## 4. Evidence Map

| Criterion | Key Evidence | Interpretation | Confidence |
| --- | --- | --- | --- |

## 5. Findings By Criterion

For each criterion:

### Criterion Name

- Rating:
- Judgment:
- Evidence:
- Interpretation:
- Risk or gap:
- Recommendation:

## 6. Strengths

List the strongest qualities of the artifact. Each strength must include evidence.

## 7. Weaknesses And Risks

List major gaps, risks, ambiguities, and failure modes. Separate critical blockers from minor refinements.

Severity labels:
- Critical: blocks safe or effective use.
- Major: materially reduces quality or reliability.
- Minor: polish or optimization issue.

## 8. Recommendations

| Priority | Recommendation | Rationale | Expected Impact | Effort |
| --- | --- | --- | --- | --- |

Priority values:
- P0: must fix before use.
- P1: high-value improvement.
- P2: useful refinement.
- P3: optional polish.

Effort values:
- Low
- Medium
- High

## 9. Final Judgment

Include:
- final rating or readiness level
- decision recommendation
- remaining uncertainty
- next best action

Readiness levels:
- Not ready
- Needs major revision
- Usable with revisions
- Ready for limited use
- Ready for production or publication

## 10. Limitations

State:
- what could not be evaluated
- what evidence was missing
- what assumptions may affect the judgment
- what would improve confidence in the evaluation

## Compact Evidence Report Template

Use only for explicit `srq` or formal completion-report requests. Do not use this template for vague "보고해줘", "검토해줘", or "요약해줘" requests unless the user also asks for verified evidence separation.

```markdown
Conclusion: <one-line result>

Evidence:
- [type + location] <verified fact 1>
- [type + location] <verified fact 2>
- [type + location] <verified fact 3 or omit>

Action:
- <one concrete completed action or next action>

Verification:
- <command/check and result, only when relevant>
```
