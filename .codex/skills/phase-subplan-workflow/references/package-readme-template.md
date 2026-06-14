---
doc_type: plan_package_readme
canonical: false
status: derived
last_validated: Unverified
last_validated_mode: none
strict_validated_at: Unverified
strict_handoff_validated_at: Unverified
release_ready: false
source_of_truth_for: []
derived_from:
  - "{{CANONICAL_PLAN_PATH}}"
{{DERIVED_FROM_SPECS}}
{{DOMAIN_INGEST_DERIVED_FROM}}
---

# {{PACKAGE_TITLE}}

## Purpose
- Planning package entrypoint for `{{PACKAGE_TITLE}}`
- Navigation only
- Domain ingest summary: `{{DOMAIN_CONTEXT_PATH}}`

## Derived Status Notice
- This README is a **derived navigation document**.
- Do not trust this file for execution status, approval state, TODO truth, or canonical scope.
- The canonical authority for status is: `{{CANONICAL_PLAN_PATH}}`

## Human Quickstart
1. Read this section for orientation only.
2. Read the Active Implementation Card.
3. Open the active phase/group doc.
4. Open only the relevant specs listed by that group.
5. If domain details look thin, open `{{DOMAIN_CONTEXT_PATH}}` before editing contracts.
6. Use Canonical Read Order when changing scope, state, interfaces, or gates.

## Domain Context Inputs
- Derived ingest summary: `{{DOMAIN_CONTEXT_PATH}}`
- This file is derived evidence, not canonical truth.
- Use it to fill Purpose, Current State, Target State, Acceptance Criteria, and TODOs with domain-specific content.

## Canonical Documents
{{CANONICAL_DOCS_TABLE}}

## Archetype
- archetype: `{{ARCHETYPE}}`
- modifiers: `{{MODIFIERS}}`

## Active Implementation Card
- Active group: `{{ACTIVE_GROUP}}`
- Goal: `{{ACTIVE_GOAL}}`
- Must read: `{{ACTIVE_MUST_READ}}`
- Blocking contracts: `{{ACTIVE_BLOCKING_CONTRACTS}}`
- First file to inspect: `{{ACTIVE_FIRST_FILE}}`
- First artifact to produce: `{{ACTIVE_FIRST_ARTIFACT}}`
- Stop condition: `{{ACTIVE_STOP_CONDITION}}`

## Target Module Structure
```mermaid
{{TARGET_MODULE_STRUCTURE}}
```

## Phase Index
{{PHASE_INDEX}}

## Group Index
{{GROUP_INDEX}}

## Dependency Graph
```mermaid
{{DEPENDENCY_GRAPH}}
```

## Spec Docs
{{SPEC_INDEX}}

## Canonical Read Order
1. `{{CANONICAL_PLAN_PATH}}`
{{READ_ORDER}}

## Validation Commands
```bash
{{VALIDATION_COMMANDS}}
```

## Notes
- This README should not contain checklists or execution status.
- If this file conflicts with a canonical document, update this file.
