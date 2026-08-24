# Qualitative Evaluation Rubric

Use this reference when the user asks for a detailed, rubric-based, ordinal, readiness, or table-heavy qualitative report. Read `quality-evaluation-method.md` first when criteria are not already accepted.

## Selection Rule

Do not apply a fixed universal rubric. Preserve user-supplied or elicited criteria first; use the following candidate dimensions only when the user delegates selection or asks for suggestions. They are not mandatory sections:

- purpose and responsibility fit
- correctness and invariant preservation
- change locality and contract stability
- failure behavior, recovery, and diagnosis
- usability, predictability, feedback, and misuse resistance
- operational cost, scalability, and resource behavior
- compatibility and dependency resilience
- evidence quality and repeatable verifiability
- practical usability and improvement leverage

## Semantic Yardstick

Prefer semantic ordinal judgments:

| Judgment | Meaning |
| --- | --- |
| Meets | The criterion is supported across its material scenario and checked boundary condition. |
| Mostly meets | The intended use is supported with a bounded non-blocking gap. |
| Partially meets | The target works only under material conditions or needs a significant improvement. |
| Does not meet | Observed evidence contradicts the required response or yardstick. |
| Not assessable | Required evidence or an authoritative yardstick is unavailable. |

If the user explicitly requests a 1–5 scale, define every value with criterion-specific descriptive anchors first. Treat it as ordinal: do not average values, claim equal intervals, or replace findings with a composite score.

## Evidence Confidence

| Confidence | Meaning |
| --- | --- |
| High | Directly supported by artifact text, code, data, logs, source references, or explicit user context. |
| Medium | Supported by partial evidence plus reasonable inference. |
| Low | Ambiguous, incomplete, or weakly supported. |
| Not assessable | Evidence is missing or outside the provided scope. |

## Severity Labels

| Severity | Meaning |
| --- | --- |
| Critical | Blocks safe, correct, or effective use. |
| Major | Materially reduces quality, reliability, trust, or adoption. |
| Minor | Does not block use but should be improved. |
| Polish | Improves clarity, style, or maintainability. |

## Recommendation Priority

| Priority | Meaning |
| --- | --- |
| P0 | Must fix before serious use. |
| P1 | High-value improvement that materially changes quality or confidence. |
| P2 | Useful refinement with moderate impact. |
| P3 | Optional polish. |

## Domain Criteria

These lists help discover candidates after the evaluation contract is bound. Never apply every item merely because the target belongs to a domain.

### Skills Or Agent Workflows
- Invocation clarity
- Input/output contract
- Progressive disclosure
- Tool and resource boundaries
- Permission and safety checks
- Fallback and recovery behavior
- Routing conflict handling

### Documents Or Reports
- Executive summary quality
- Argument structure
- Evidence synthesis
- Audience fit
- Completeness
- Limitations
- Recommendation traceability

### Code Or Implementation
- Responsibility and invariant preservation
- Expected-change locality
- Contract and ownership clarity
- Error and invalid-state behavior
- Dependency and compatibility resilience
- Diagnosis and verification support
- Operational and safety constraints

### Research Artifacts
- Research question clarity
- Methodological validity
- Evidence quality
- Novelty
- Reproducibility
- Ethical or safety considerations

## Tradeoff Rule

Every material positive or negative judgment must preserve a result-changing boundary condition when one exists. A structure can satisfy one quality obligation while weakening another; do not convert a preferred mechanism into a universal quality rule.
