# Test Decision Record

Use this template only for a package-bound `plan-test-discovery` result. Omit optional sections that
have no content; do not copy conversation transcripts.

```markdown
---
kind: test_discovery_record
plan_id: <plan-id>
status: active | decision_ready | stopped_with_open_questions
artifact_owner: plan-test-discovery
downstream_consumer: workflow-test-design
authority_owner: <human-or-canonical-owner>
source_refs:
  - <source-or-observation-ref>
---

# <Target> Test Decisions

## Target Snapshot

- **SUT / actual path or accepted external-contract boundary:**
- **Implementation/prototype snapshot or contract revision:**
- **Blocked Test Design conditions:**
- **Source evidence and representative observations when empirical:**

## Decision Ledger

| ID | Request ID | Blocked condition IDs | Judgment | Evidence | Selected decision | Authority / source | Status | Accepted uncertainty | Test Design scope |
|---|---|---|---|---|---|---|---|---|---|
| `TD-001` | `TDR-001` | `TC-003` | ... | ... | ... | ... | `decided` | ... | ... |

## Rejected Oracles Or Baselines

- <candidate and why it must not be reused>

## Downstream Readiness

- **ready_for_test_design:** true / false
- **consumable decision IDs:**
- **open blockers:**
- **continuation:** resume_same_node / plan_revision / new_plan
```

`awaiting_human_event` belongs to Handoff lifecycle state and never appears as this artifact's
status. Current implementation output remains observation unless a named authority decides to
accept it for an exact scope.
