# Behavior Decision Record

Persist this shape only inside the associated Execution Handoff package.

When material working state is needed, keep hard constraints and soft preferences distinct in
Accepted constraints and link their authority/source. Use Current behavior/anchors for evidence
status and any dynamic refresh condition. Affected scope names every actual downstream dependent:
other decision rows, artifact readiness/status, Next Human-Operable Slice, and Handoff selections.
After a correction, invalidate and recompute those derived fields from refreshed evidence; preserve
unrelated decided rows. If readiness is affected, keep the record `active` until the next user path,
observable contract, cancel/failure/recovery behavior, recommended owner, and consumed decision IDs
have been re-evaluated. These annotations do not promote assumed,
delegated, stale, or open input to decided behavior or create another persistence path.

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
