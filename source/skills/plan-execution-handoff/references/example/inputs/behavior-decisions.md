---
kind: behavior_decision_record
plan_id: example-csv-export
status: decision_ready
source_refs:
  - request:example-csv-export
---

# CSV Export Behavior Decisions

## Capability Snapshot

- **Actor / path:** report screen user / current table export
- **Current behavior status:** source_established
- **Current behavior anchors:** `report/view/ReportScreen.cpp:120`
- **Accepted constraints:** preserve row order and UTF-8 output

## Decision Ledger

| ID | Scenario | Current behavior / anchors | Choice | Status | Observable contract | Affected scope | Decision source |
|---|---|---|---|---|---|---|---|
| BD-001 | Export current report table | No active export path | Add CSV export from the current table | decided | Downloaded CSV matches visible row order and UTF-8 content | report screen export | product owner |

## Next Human-Operable Slice

- **User path:** report screen → export CSV
- **Observable success:** downloaded CSV matches the current table
- **Cancel / failure / recovery behavior:** failed export leaves the current report unchanged

## Open Deferrals And Productization Gaps

- none

## Handoff

- **Recommended owner:** plan-execution-handoff
- **Consumed decision IDs:** BD-001
