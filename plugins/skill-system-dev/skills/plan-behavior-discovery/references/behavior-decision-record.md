# Behavior Decision Record

Persist this shape only inside the associated Execution Handoff package.

```markdown
---
kind: behavior_decision_record
plan_id: <associated plan id>
status: active | decision_ready
source_refs: []
---

# <Capability> Behavior Decisions

## Capability Snapshot

- **Actor / path:**
- **Current behavior status:** runtime_observed | source_established | inferred | unverified
- **Current behavior anchors:**
- **Accepted constraints:**

## Decision Ledger

| ID | Scenario | Current behavior / anchors | Choice | Status | Observable contract | Affected scope | Decision source |
|---|---|---|---|---|---|---|---|
| BD-001 |  |  |  | decided / assumed / delegated / open |  |  |  |

## Next Human-Operable Slice

- **User path:**
- **Observable success:**
- **Cancel / failure / recovery behavior:**

## Open Deferrals And Productization Gaps

- none

## Handoff

- **Recommended owner:**
- **Consumed decision IDs:**
```

Set `status: decision_ready` only when the next human-operable slice is exact and no unrecorded
behavior blocker remains. Plan compilation may consume only ledger rows whose status is `decided`.
