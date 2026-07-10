---
doc_type: phase_group
canonical: false
status: planned
last_validated: 2026-07-10T06:50:28-07:00
last_validated_mode: strict-handoff
strict_validated_at: 2026-07-10T06:50:28-07:00
strict_handoff_validated_at: 2026-07-10T06:50:28-07:00
release_ready: false
phase: "Evidence Baseline"
phase_order: 1
group_id: "group-1"
title: "Group 1: Service and Evidence Discovery"
hard_predecessor: "false"
owned_concerns:
  - source-and-evidence-discovery
depends_on: []
soft_depends_on: []
blocking_interfaces:
  - IF-AUTH-NORMALIZED
  - IF-SHADOW
relevant_specs:
  - capability-map
  - api-contract
  - integration-contract
  - agent-handoff-index
source_of_truth_for: []
derived_from:
  - "docs/plan/2026-07-10-payment-engine-replacement.md"
  - "docs/plan/PaymentEngineReplacement/domain-ingest-summary.md"
---

# Group 1: Service and Evidence Discovery

## Purpose
Recover the actual source outline, endpoint inventory, test/build entrypoints, component owners, and safe authorization evidence needed to replace `Unverified` planning claims with source-backed contract rows.

## Bounded Outcome And Non-Goals
- Outcome: one sanitized discovery bundle identifies exact implementation surfaces and runnable validation commands for later groups.
- Non-goals: no engine adapter, traffic, logging, routing, schema, or production configuration change.
- Stop immediately if inspecting or copying evidence would place PCI-scoped card data, credentials, or raw payment payloads in repository artifacts.

## Current State
Only `PLANNING_BRIEF.md` and this package are present. The brief reports `gateway/`, `ledger/`, `webhooks/`, `ops/`, an endpoint inventory, and one week of sampled authorization traces, but their paths and contents are unavailable here.

## Target State
The active implementation repository has a source outline, ownership list, exact interface/test command manifest, and approved authorization-evidence provenance record. Canonical contracts are updated from those sources before Group 2 opens.

## Derived Document Notice
This document decomposes work only. Update the referenced canonical spec before treating a discovered scope, interface, or rule as accepted.

## Referenced Canonical Docs
- `docs/spec/payment-engine-replacement-capability-map.md`
- `docs/spec/payment-engine-replacement-api-contract.md`
- `docs/spec/payment-engine-replacement-integration-contract.md`
- `docs/spec/payment-engine-replacement-security-contract.md`
- `docs/spec/payment-engine-replacement-agent-handoff-index.md`

## Referenced Canonical IDs
- capability map: CAP-001, CAP-002, CAP-003, CAP-004, CAP-005, CAP-006, CAP-007, CAP-008, CAP-009
- `docs/spec/payment-engine-replacement-api-contract.md`: API-AUTH, API-REFUND, API-LEDGER, API-WEBHOOK, API-ROUTING
- `docs/spec/payment-engine-replacement-integration-contract.md`: IF-AUTH-NORMALIZED, IF-SHADOW, IF-COMMIT, IF-ROUTING, IF-PARITY-EVIDENCE
- `docs/spec/payment-engine-replacement-agent-handoff-index.md`

## Dependencies
- hard predecessor: false
- depends_on: none
- blocking interfaces to investigate: IF-AUTH-NORMALIZED, IF-SHADOW

## Implementation Digest

### Target Files / Components
- Discovery targets: `gateway/`, `ledger/`, `webhooks/`, `ops/`, repository test/build configuration, endpoint inventory, authorization trace manifest.
- Planning updates after evidence review: API, data, integration, parity, security, and release contracts plus the canonical dated plan.

### Before / After
- Before: component and evidence existence is user-reported but not repository-observed.
- After: exact paths, owners, interface symbols, safe evidence locations, and commands are listed in `artifacts/payment-engine-replacement/contracts/` without payment payload values.

### Critical Gap
No production source or evidence artifact is currently available under the approved repository root.

### Concrete First Step
From the implementation repository root, run `pwd && rg --files gateway ledger webhooks ops | sort` and save the path-only result to `artifacts/payment-engine-replacement/contracts/source-outline.txt`; if any named directory is absent, stop and record that blocker in the canonical dated plan.

### Implementation Behavior Oracle
- Scenario/input: inspect only paths, schemas, command definitions, and approved metadata.
- Expected observation: all named components and each logical interface have an exact source pointer; no payment payload or card data is copied.
- Verifier: source-outline assertions plus the organization-approved sensitive-data scanner.
- Evidence destination: `artifacts/payment-engine-replacement/contracts/` and `artifacts/payment-engine-replacement/security/planning-artifact-scan.txt`.
- Owner: implementing agent with service/security review.

## Proposed Changes to Canonical Contracts
- None at package creation. Source discoveries must update the owning canonical contract before downstream use.

## Acceptance Criteria
- [ ] The reported component layout and interface entrypoints are mapped.
  - Contract: integration contract IF-AUTH-NORMALIZED through IF-PARITY-EVIDENCE
  - Evidence: `artifacts/payment-engine-replacement/contracts/source-outline.txt` and `interface-inventory.md`
  - Test command: `test -s artifacts/payment-engine-replacement/contracts/source-outline.txt && rg -n "gateway/|ledger/|webhooks/|ops/" artifacts/payment-engine-replacement/contracts/source-outline.txt`
  - Blocking: true
- [ ] Endpoint inventory provenance and exact logical API mappings are reviewed without payload values.
  - Contract: API contract API-AUTH through API-ROUTING
  - Evidence: `artifacts/payment-engine-replacement/contracts/endpoint-inventory-review.md`
  - Test command: `test -s artifacts/payment-engine-replacement/contracts/endpoint-inventory-review.md && rg -n "API-AUTH|API-REFUND|API-LEDGER|API-WEBHOOK|API-ROUTING" artifacts/payment-engine-replacement/contracts/endpoint-inventory-review.md`
  - Blocking: true
- [ ] Authorization sample provenance, sanitization status, owner, and permitted use are accepted.
  - Contract: security contract CTRL-001, CTRL-002, CTRL-006
  - Evidence: `artifacts/payment-engine-replacement/security/authorization-evidence-review.md`
  - Test command: run the organization-approved sensitive-data scanner and require zero findings in the discovery bundle
  - Blocking: true
- [ ] Exact repository-native commands for Groups 2-7 are recorded.
  - Contract: release gate regression matrix
  - Evidence: `artifacts/payment-engine-replacement/contracts/command-manifest.md`
  - Test command: `test -s artifacts/payment-engine-replacement/contracts/command-manifest.md && rg -n "CMD-CONTRACT|CMD-R1|CMD-R2|CMD-R3" artifacts/payment-engine-replacement/contracts/command-manifest.md`
  - Blocking: true

## Prohibited Shortcuts
- Do not infer missing source paths, copy raw traces, or treat document presence as interface/runtime evidence.

## Exit Gate And Fallback
- Exit only when all four acceptance rows pass and canonical `Unverified` interface entries are reconciled from source.
- If source/evidence access remains unavailable, keep the package `planning-only`; the fallback is a blocker report, not inferred contracts or production work.

## TODO
- [ ] Obtain the implementation repository/source checkout and evidence locations.
- [ ] Produce the discovery bundle and update canonical contracts first.
