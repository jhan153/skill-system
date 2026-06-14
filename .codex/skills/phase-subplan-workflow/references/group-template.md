---
doc_type: phase_group
canonical: false
status: draft
last_validated: Unverified
last_validated_mode: none
strict_validated_at: Unverified
strict_handoff_validated_at: Unverified
release_ready: false
phase: "{{PHASE_NAME}}"
phase_order: {{PHASE_ORDER}}
group_id: "{{GROUP_ID}}"
title: "{{GROUP_TITLE}}"
hard_predecessor: "{{HARD_PREDECESSOR}}"
owned_concerns: []
depends_on:
{{DEPENDS_ON}}
soft_depends_on:
{{SOFT_DEPENDS_ON}}
blocking_interfaces:
{{BLOCKING_INTERFACES}}
relevant_specs:
{{RELEVANT_SPECS_FM}}
source_of_truth_for: []
derived_from:
  - "{{CANONICAL_PLAN_PATH}}"
---

# {{GROUP_TITLE}}

## Purpose
{{GROUP_PURPOSE}}

## Current State
{{GROUP_CURRENT_STATE}}

## Target State
{{GROUP_TARGET_STATE}}

## Derived Document Notice
- This document is a **derived decomposition document**.
- It must not redefine canonical contracts.
- If a contract changes, update the canonical document first.

## Referenced Canonical Docs
{{REFERENCED_CANONICAL_DOCS}}

- Full required spec list lives in the package README.

## Referenced Canonical IDs
- capability ids:
- state ids:
- interface ids:
- release gate ids:

## Dependencies
- hard predecessor: {{HARD_PREDECESSOR}}
- depends_on: {{DEPENDS_ON_INLINE}}
- soft_depends_on: {{SOFT_DEPENDS_ON_INLINE}}
- blocking_interfaces: {{BLOCKING_INTERFACES_INLINE}}

## Implementation Digest
### Target Files / Components
{{TARGET_COMPONENTS}}

### Main Responsibilities
{{RESPONSIBILITIES}}

### Before / After
#### Before
```text
{{BEFORE_STRUCTURE}}
```

#### After
```text
{{AFTER_STRUCTURE}}
```

### Critical Gap
- {{CRITICAL_GAP}}

### First Implementation Step
- {{FIRST_STEP}}

## Proposed Changes to Canonical Contracts
- If this group discovers a needed contract change, record the proposal here and update the canonical doc before treating it as final.

## Acceptance Criteria
- [ ] Relevant canonical contracts are updated with evidence-backed, domain-specific rows for this group.
  - Contract: `{{PRIMARY_CONTRACT}}`
  - Evidence: `docs/plan/{{PACKAGE_DIR_NAME}}/domain-ingest-summary.md`
  - Test command: `{{GROUP_VALIDATION_COMMAND}}`
  - Blocking: true

## Prohibited Shortcuts
{{PROHIBITED_SHORTCUTS}}

## TODO
- [ ] Replace derived ingest bullets with verified source-backed contract rows where this group owns the work.
- [ ] Add or update one evidence artifact path for each release-blocking acceptance criterion.
