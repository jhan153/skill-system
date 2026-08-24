# Plan Question Document Template

```markdown
---
kind: question_document
plan_id: <associated plan id or null>
status: awaiting_response | answered | superseded
answer_owner: <name or role>
source_refs: []
downstream_consumer: plan-requirements-discovery | plan-requirements-brief | <other explicit owner>
---

# <Topic>: information needed from <recipient role>

## Request Contract

- **Decision this supports:** <What becomes decidable after the response>
- **Requested from:** <Name or role>
- **Response needed by:** <Date or “no fixed deadline”>
- **Expected effort:** <Estimate or “not specified”>
- **Response owner after receipt:** <Who will interpret and apply the answers>

## Minimum Context

<Only the background required for this recipient to understand the request.>

## Response Guidance

Please mark each answer as confirmed, uncertain, unavailable, or owned by someone else. Partial answers and links to an authoritative source are useful.

## <Decision or information group>

### 1. <One answerable question>

**Requested answer shape:** <choice | short text | list | link/source | approval condition>

**Response:**

>

**Confidence or source, when relevant:**

>

## Missing Constraint Or Owner

Is there a constraint, exception, source, or responsible person this document should have asked about?

>
```

## Internal Coverage Readback

Keep this mapping outside the recipient-facing document unless traceability is explicitly requested:

| Needed-back id | Downstream use | Primary question | Response shape | Status |
| --- | --- | --- | --- | --- |
| NB-001 |  |  |  | covered / missing / duplicate |

Delivery is ready only when every `needed_back` entry has one primary question and no question lacks a downstream use.
