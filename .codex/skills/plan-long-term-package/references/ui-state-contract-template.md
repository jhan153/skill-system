---
doc_type: ui_state_contract
canonical: true
status: draft
last_validated: Unverified
source_of_truth_for:
  - ui-state
  - cta-rules
  - error-state
derived_from: []
---

# {{SLUG}} UI State Contract

## Purpose

## State ID Naming Rule
- Use stable ids such as `empty`, `material_loaded`, `align_ready`, `error_alignment_failed`
- Do not redefine ids in phase/group docs

## Canonical State IDs

| State ID | State Name | Meaning | Entry Condition | Exit Condition | Side Effects | Terminal? |
| --- | --- | --- | --- | --- | --- | --- |

## Transitions
```mermaid
flowchart LR
```

## Error States
| State ID | Trigger | User-visible behavior | Recovery | Retry / Recovery Invariant |
| --- | --- | --- | --- | --- |

## CTA Visibility / Enabled Rules
| CTA | Visible In | Enabled In | Blocked By |
| --- | --- | --- | --- |

## Notes
- No other planning document may redefine this state list.
