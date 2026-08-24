# Qualitative Evaluation Report Template

Use this full template when the user requests a complete, reusable, or table-heavy qualitative report. For short answers, collapse the same logic into fewer sections.

## 1. Executive Summary

Include:
- the decision the evaluation supports
- one-line qualitative conclusion
- up to three decision-changing findings
- the highest-leverage next action
- material evidence limits

## 2. Evaluation Contract

Include:
- artifact evaluated
- decision goal and stakeholder perspective
- intended use and lifecycle
- responsibilities, expected changes, and material failures when relevant
- constraints and accepted yardsticks
- criterion origin: supplied, elicited, accepted proposal, delegated, or assumed
- exclusions
- narrow assumptions that cannot change the criteria

## 3. Method

Briefly describe:
- how the artifact was reviewed
- what evidence was considered
- how criteria and scenarios were selected
- how observations were interpreted against yardsticks
- limitations of the review

## 4. Evidence Map

| Criterion | Origin | Scenario / Yardstick | Observation or Measurement | Evidence | Interpretation | Confidence |
| --- | --- | --- | --- | --- | --- | --- |

## 5. Findings By Criterion

For each criterion:

### Criterion Name

- Scenario and yardstick:
- Observation or measurement:
- Evidence location:
- Interpretation:
- Decision impact:
- Counterexample or boundary condition:
- Judgment: Meets / Mostly meets / Partially meets / Does not meet / Not assessable
- Recommendation:
- Confidence and limitation:

## 6. Material Strengths

List only strengths that affect the decision. Each strength needs the same observation, interpretation, boundary, and evidence discipline as a weakness. Omit this section when none is material.

## 7. Weaknesses And Risks

List major gaps, risks, ambiguities, and failure modes. Keep a suspected risk separate from an observed defect.

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
- whether and under what conditions the target fits the stated purpose
- the decision recommendation when requested
- remaining uncertainty
- next best action

Use a readiness label only when the evaluation contract supplies a readiness decision and yardstick. Do not infer production or publication readiness from artifact structure alone.

## 10. Limitations

State:
- what could not be evaluated
- what evidence was missing
- what assumptions may affect the judgment
- what would improve confidence in the evaluation

## Qualitative Scale Note

When the user explicitly requests numeric scores, include the descriptive anchors used for each criterion and retain the finding text. Never compute an overall average unless the user supplies a valid aggregation rule and explains its decision meaning.

## Compact Evidence Report Template

Use only for an explicitly full, reusable, table-heavy, or rubric-based qualitative report. Do not
use this template for vague "보고해줘", "검토해줘", or "요약해줘" requests.

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
