---
doc_type: phase_group
canonical: false
status: planned
last_validated: 2026-07-10T06:50:28-07:00
last_validated_mode: strict-handoff
strict_validated_at: 2026-07-10T06:50:28-07:00
strict_handoff_validated_at: 2026-07-10T06:50:28-07:00
release_ready: false
phase: "R2 Test Tenant Canary"
phase_order: 3
group_id: "group-6"
title: "Group 6: R2 Eligible Canary and Immediate Rollback"
hard_predecessor: "true"
owned_concerns:
  - r2-canary-implementation-and-evidence
depends_on:
  - group-2
  - group-3
  - group-5
soft_depends_on: []
blocking_interfaces:
  - IF-COMMIT
  - IF-ROUTING
relevant_specs:
  - compatibility-matrix
  - migration-map
  - rollback-plan
  - rollback-trigger
  - release-gate
source_of_truth_for: []
derived_from:
  - "docs/plan/2026-07-10-payment-engine-replacement.md"
---

# Group 6: R2 Eligible Canary and Immediate Rollback

## Purpose
Implement and operate the canonical R2 combination for the approved refundable test-tenant cohort while preserving exact compatibility and the pre-drilled legacy-only rollback path.

## Bounded Outcome And Non-Goals
- Outcome: the R2 release gate evaluates complete routing, parity, financial/event, security, and rollback evidence.
- Non-goals: no non-test-tenant, non-refundable, or broader allocation; no legacy removal.

## Current State
R2 is hard-blocked by refund/timeout datasets, accepted selector design, deploy-free rollback evidence, R1 PASS, exact owners, and an approval event.

## Target State
Only the canonical eligible cohort can select `new-pay`; all P0 oracles pass; rollback returns every subsequent eligible decision to legacy and reconciles in-flight uncertain outcomes.

## Derived Document Notice
This group decomposes R2 implementation/evidence only; canonical compatibility, migration, rollback, and release specs own all rules.

## Referenced Canonical Docs
- `docs/spec/payment-engine-replacement-compatibility-matrix.md`
- `docs/spec/payment-engine-replacement-migration-map.md`
- `docs/spec/payment-engine-replacement-rollback-plan.md`
- `docs/spec/payment-engine-replacement-rollback-trigger.md`
- `docs/spec/payment-engine-replacement-release-gate.md`

## Referenced Canonical IDs
- Compatibility matrix: COMBO-R2-ELIGIBLE, COMBO-R2-INELIGIBLE, unsafe combinations
- Migration map: MIG-001, MIG-002, MIG-003, MIG-004, MIG-005, MIG-006, MIG-007 and R2 sequence
- Rollback plan: RB-SCOPE-R2 and procedure steps 1-6
- Rollback trigger: RT-001, RT-002, RT-003, RT-004, RT-005, RT-006, RT-007
- Release gate: R2 datasets, thresholds, regression rows, and verdict rule

## Dependencies
- hard predecessor: true
- depends_on: group-2, group-3, group-5
- blocking interfaces: IF-COMMIT, IF-ROUTING

## Implementation Digest

### Target Files / Components
- Exact `gateway/` selector, adapter commit orchestration, idempotency logic, and tests.
- `ledger/` posting/reconciliation, `webhooks/` ordering tests, and `ops/` controls/metrics/runbooks.

### Before / After
- Before: legacy serves all authoritative traffic; new engine is shadow-only.
- After: canonical R2 selection may commit through `new-pay`, with legacy for all other selections and an audited no-deploy return to legacy.

### Critical Gap
The selector and rollback path must be demonstrated against retry, timeout, and in-flight commit races; a configuration readback alone is insufficient.

### Concrete First Step
Run CMD-R2 in a safe test environment against synthetic eligible/ineligible boundaries and cross-route idempotency cases; do not request R2 enablement until every routing and side-effect assertion passes.

### Implementation Behavior Oracle
- Scenario/input: approved refund/timeout/idempotency/ledger/webhook datasets, eligibility boundaries, configuration changes, and rollback during in-flight outcomes.
- Expected observation: every selection/effect matches the canonical R2 gate; after the rollback marker, all selections are legacy and each operation has one compatible outcome/effect set.
- Verifier: CMD-R2, CMD-ROLLBACK, and CMD-RELEASE-GATE.
- Evidence destination: R2 route, parity, rollback, security, and release paths in the canonical gate.
- Owner: release operator with payment, ledger, webhook, ops, test, and security sign-off.

## Proposed Changes to Canonical Contracts
- None at package creation. Selector or rollback discoveries require canonical decisions before R2 approval.

## Acceptance Criteria
- [ ] Eligibility and engine selection match the canonical R2 selector for every audited operation.
  - Contract: compatibility matrix and release gate R2 allocation/ineligible rows
  - Evidence: `artifacts/payment-engine-replacement/metrics/r2-route-report.json`
  - Test command: CMD-R2 routing audit
  - Blocking: true
- [ ] Authorization, idempotency, ledger, refund, timeout, and webhook order all pass applicable P0 oracles.
  - Contract: behavior parity BEH-001 through BEH-006 and release gate R2 regression matrix
  - Evidence: reviewed reports under `artifacts/payment-engine-replacement/parity/`
  - Test command: CMD-R2 full parity suite
  - Blocking: true
- [ ] Immediate rollback is demonstrated without deploy, with no post-marker new routes and complete in-flight reconciliation.
  - Contract: rollback plan RB-SCOPE-R2 and trigger RT-006
  - Evidence: `artifacts/payment-engine-replacement/rollback/latest-drill.md`, `latest-routing.json`, and `latest-inflight.md`
  - Test command: CMD-ROLLBACK
  - Blocking: true
- [ ] R2 evidence is security-approved and the canonical release evaluator returns PASS.
  - Contract: security contract and release gate verdict rule
  - Evidence: `artifacts/payment-engine-replacement/release/r2-gate.md`
  - Test command: CMD-RELEASE-GATE with release `R2`
  - Blocking: true

## Prohibited Shortcuts
- Do not widen eligibility, proceed without refund/timeout evidence, retry uncertain operations blindly, or call config readback a completed rollback.

## Exit Gate And Rollback
- Exit only with canonical R2 PASS and rollback control remaining active. R2 PASS begins eligibility for the R3 observation window; it does not authorize legacy removal.
- Any trigger invokes the canonical rollback plan, resets progression, and requires reconciled evidence before a new approval.

## TODO
- [ ] Close all hard predecessors and obtain explicit R2 approval.
- [ ] Execute the canary, rollback drill, parity review, and R2 gate.
