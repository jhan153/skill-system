# Qualitative Evaluation Rubric

Use this reference when the user asks for a scored, rubric-based, readiness, or table-heavy qualitative report.

## Core Criteria

| Criterion | 1 - Poor | 2 - Weak | 3 - Adequate | 4 - Strong | 5 - Excellent |
| --- | --- | --- | --- | --- | --- |
| Purpose Fit | Purpose is absent or contradictory. | Purpose is vague or only partly aligned. | Purpose is understandable but not fully operationalized. | Purpose is clear and mostly aligned with artifact design. | Purpose, audience, and success conditions are explicit and well aligned. |
| Structural Clarity | Disorganized; hard to use. | Some structure exists but important parts are missing or misplaced. | Basic structure works with noticeable gaps. | Structure is logical and easy to follow. | Structure is clean, complete, and optimized for use. |
| Evidence and Grounding | Claims are mostly unsupported. | Some evidence exists but traceability is weak. | Main claims have partial support. | Most judgments are well supported by evidence. | Claims, judgments, and recommendations are consistently traceable to evidence. |
| Practical Usability | Not usable without redesign. | Usable only with major interpretation by the user. | Usable for simple cases. | Usable in realistic settings with minor gaps. | Ready for repeated use with clear inputs, outputs, and edge-case handling. |
| Risk and Failure Modes | Serious unaddressed risks. | Major risks are visible but unmanaged. | Some risks are identified. | Most likely risks are identified and mitigated. | Risks, boundaries, safeguards, and fallback paths are explicit. |
| Improvement Leverage | No clear path to improve. | Recommendations are vague or too broad. | Some useful improvements are identified. | Recommendations are specific and prioritized. | Recommendations are high-leverage, evidence-based, and implementation-ready. |

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
- Maintainability
- Correctness risk
- Readability
- Error handling
- Dependency risk
- Testability
- Operational safety

### Research Artifacts
- Research question clarity
- Methodological validity
- Evidence quality
- Novelty
- Reproducibility
- Ethical or safety considerations
