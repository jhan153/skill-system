---
doc_type: handoff_index
canonical: false
status: procedural
last_validated: Unverified
last_validated_mode: none
strict_validated_at: Unverified
strict_handoff_validated_at: Unverified
release_ready: false
source_of_truth_for: []
derived_from:
  - "{{CANONICAL_PLAN_PATH}}"
{{DERIVED_FROM_SPECS}}
---

# {{SLUG}} Agent Handoff Index

## Current Canonical Plan Path
- `{{CANONICAL_PLAN_PATH}}`

## Active Blockers
- `Unverified`

## Human Quickstart
1. Read Current Canonical Plan Path.
2. Read Active Blockers.
3. Read the active group document.
4. Read only that group's relevant specs before coding.

## Read Order
1. `{{CANONICAL_PLAN_PATH}}`
{{READ_ORDER}}

## Implementation Start Checklist
- [ ] canonical dated plan read
{{CHECKLIST}}

## Update Rules
- scope change -> capability map
- state change -> UI state contract
- boundary change -> integration contract
- threshold change -> release gate
- execution status -> canonical dated plan

## Prohibited Shortcuts
- Do not trust README for status
- Do not redefine UI states outside the UI state contract
- Do not downgrade P0 scope without a decision record
- Do not open implementation while hard predecessors are incomplete

## Last Validated At
- `Unverified`
