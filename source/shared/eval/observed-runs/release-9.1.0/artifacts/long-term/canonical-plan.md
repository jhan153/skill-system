---
doc_type: canonical_dated_plan
canonical: true
status: planning
last_validated: 2026-07-10T06:50:28-07:00
last_validated_mode: strict-handoff
strict_validated_at: 2026-07-10T06:50:28-07:00
strict_handoff_validated_at: 2026-07-10T06:50:28-07:00
release_ready: false
implementation_status: planning-only
source_of_truth_for:
  - execution-status
  - approval-state
  - todo-status
  - blocked-items
derived_from:
  - "PLANNING_BRIEF.md"
---

# Payment Engine Replacement Package

## 1) Task Overview
- purpose: provide a resumable, canonical three-release plan for replacing `legacy-pay` with `new-pay` while preserving six named compatibility surfaces and PCI-safe evidence.
- scope: evidence discovery, compatibility characterization, engine boundaries, R1 shadow authorization, R2 eligible canary with rollback, R3 clean-window validation and legacy retirement.
- non-scope: production code/config changes, traffic enablement, runtime validation, implementation approval, raw payment/trace data, and inferred vendor-specific interfaces.
- plan_package: `docs/plan/PaymentEngineReplacement`
- archetype: `backend-service`
- modifiers: `strict-behavior-parity, legacy-parity, rollback-required, cross-session-handoff, data-sensitive, security-sensitive`
- domain_context: `docs/plan/PaymentEngineReplacement/domain-ingest-summary.md`
- planning_state: base `active_plan`; overlay `package_planned` after bundled package validation; not `implementation_ready`

### Artifact Manifest
- canonical_plan: `docs/plan/2026-07-10-payment-engine-replacement.md`
- package_root: `docs/plan/PaymentEngineReplacement/README.md`
- phase_docs: seven stable group paths under `Evidence Baseline`, `R1 Shadow Authorization`, `R2 Test Tenant Canary`, and `R3 Legacy Retirement`
- contract_docs: the 16 `docs/spec/payment-engine-replacement-*.md` files listed by the package README; this is the de-duplicated union for the selected archetype/modifiers
- domain_ingest_summary: `docs/plan/PaymentEngineReplacement/domain-ingest-summary.md` (derived from the brief and repository outline; no prior report was available)
- validation_modes: default, `--strict`, `--quality-lint`, and `--strict-handoff`; write a stamp only after a passing applicable run

### Authority Summary
- scope/priority/parity target: capability map
- interfaces/boundaries: API, data, integration, mapping, compatibility, observability, and security contracts by concern
- release sequence: migration map
- release thresholds/datasets/verdict: release gate
- rollback procedure/conditions: rollback plan and rollback trigger
- current status/approval/TODO/blockers: this dated plan
- navigation/decomposition: derived README, handoff index, and group docs

## 2) Changed File List
- [x] `docs/plan/2026-07-10-payment-engine-replacement.md`
- [x] `docs/plan/PaymentEngineReplacement/README.md`
- [x] `docs/plan/PaymentEngineReplacement/domain-ingest-summary.md`
- [x] `docs/plan/PaymentEngineReplacement/Evidence Baseline/Group1-Service-Baseline.md`
- [x] `docs/plan/PaymentEngineReplacement/Evidence Baseline/Group2-Api-And-Data-Contracts.md`
- [x] `docs/plan/PaymentEngineReplacement/Evidence Baseline/Group3-Dependency-And-Boundary-Map.md`
- [x] `docs/plan/PaymentEngineReplacement/R1 Shadow Authorization/Group4-Execution-Surface.md`
- [x] `docs/plan/PaymentEngineReplacement/R1 Shadow Authorization/Group5-Observability-And-Failure-Contract.md`
- [x] `docs/plan/PaymentEngineReplacement/R2 Test Tenant Canary/Group6-Stability-Refactor.md`
- [x] `docs/plan/PaymentEngineReplacement/R3 Legacy Retirement/Group7-Validation-And-Release.md`
- [x] `docs/spec/payment-engine-replacement-agent-handoff-index.md`
- [x] `docs/spec/payment-engine-replacement-api-contract.md`
- [x] `docs/spec/payment-engine-replacement-behavior-parity-contract.md`
- [x] `docs/spec/payment-engine-replacement-capability-map.md`
- [x] `docs/spec/payment-engine-replacement-compatibility-matrix.md`
- [x] `docs/spec/payment-engine-replacement-data-contract.md`
- [x] `docs/spec/payment-engine-replacement-integration-contract.md`
- [x] `docs/spec/payment-engine-replacement-migration-map.md`
- [x] `docs/spec/payment-engine-replacement-observability-contract.md`
- [x] `docs/spec/payment-engine-replacement-old-new-mapping.md`
- [x] `docs/spec/payment-engine-replacement-parity-contract.md`
- [x] `docs/spec/payment-engine-replacement-release-gate.md`
- [x] `docs/spec/payment-engine-replacement-rollback-plan.md`
- [x] `docs/spec/payment-engine-replacement-rollback-trigger.md`
- [x] `docs/spec/payment-engine-replacement-security-contract.md`
- [x] `docs/spec/payment-engine-replacement-source-of-truth-policy.md`

## 3) Change Summary
- what: created canonical contracts plus concern-based, predecessor-linked phase groups for discovery, R1, R2, and R3.
- why: another agent must be able to resume without converting unavailable source/runtime facts into false requirements or release evidence.

### Claim Ledger
| Claim ID | Statement | Grade | Source / Evidence | Planning Impact | Status |
| --- | --- | --- | --- | --- | --- |
| CL-001 | The requested deliverable is a cross-session package replacing `legacy-pay` with `new-pay` over three releases. | `verified-source` | `PLANNING_BRIEF.md:3,15` | package shape and sequence | accepted |
| CL-002 | R1 shadows authorization without changing customer-visible behavior. | `verified-source` | `PLANNING_BRIEF.md:7` | R1 scope and parity gate | accepted |
| CL-003 | R2 applies to 10% of refundable test-tenant traffic and requires immediate rollback. | `verified-source` | `PLANNING_BRIEF.md:8` | R2 scope and rollback gate | accepted |
| CL-004 | R3 may retire legacy only after 30 days with no unexplained parity failures. | `verified-source` | `PLANNING_BRIEF.md:9` | R3 observation gate | accepted |
| CL-005 | PCI-scoped card data may not enter new logs or planning artifacts. | `verified-source` | `PLANNING_BRIEF.md:10` | security/data/observability contracts | accepted |
| CL-006 | Authorization result, idempotency, ledger postings, refund state, timeout behavior, and webhook order are compatibility surfaces. | `verified-source` | `PLANNING_BRIEF.md:11` | P0 scope and oracles | accepted |
| CL-007 | The implementation repository has `gateway/`, `ledger/`, `webhooks/`, and `ops/`. | `verified-source` | `PLANNING_BRIEF.md:12` | target component hypotheses | accepted for discovery; runtime presence unverified |
| CL-008 | A static endpoint inventory and one week of sampled authorization traces exist. | `verified-source` | `PLANNING_BRIEF.md:13` | Group 1/2 evidence inputs | accepted for discovery; path/safety open |
| CL-009 | Refund and timeout traces are unavailable. | `verified-source` | `PLANNING_BRIEF.md:13` | hard R2 evidence blockers | accepted |
| CL-010 | Planning docs are not runtime validation or implementation completion. | `verified-source` | `PLANNING_BRIEF.md:15` | state/release boundary | accepted |
| CL-011 | Production source, prior reports, tests, and runtime artifacts are absent from this approved planning repository. | `observed-runtime` | `find . -maxdepth 3 -type f` on 2026-07-10; domain ingest summary | Group 1 active discovery/blocker | accepted |
| CL-012 | `backend-service` is the narrow primary archetype; six modifiers supply parity, rollback, handoff, data, and security contracts. | `inferred` | skill archetype catalog plus CL-001/003/005/006 | artifact manifest only | accepted |
| CL-013 | “Immediate rollback” should mean no deploy plus zero `new-pay` selections after an effective marker. | `decision-needed` | conservative planning proposal derived from CL-003 | proposed R2 gate and drill | open; must be accepted before R2 |
| CL-014 | The R2 deterministic selector key/algorithm and audit population are unspecified. | `decision-needed` | missing from brief/source | blocks IF-ROUTING and R2 | open |
| CL-015 | No P0 behavior difference is pre-approved. | `inferred` | CL-002/004/006; no exception provided | zero-tolerance parity policy | accepted as planning default; exceptions require decision |
| CL-016 | Post-R3 response must be a separately accepted fallback or forward-fix plan because R2 rollback may no longer exist. | `decision-needed` | retirement risk from CL-004 | blocks IF-RETIRE/R3 approval | open |
| CL-017 | Named service, test, release, security, data, ledger, webhook, and ops owners are unavailable. | `observed-runtime` | no owner/source artifacts in repository | blocks handoff sign-off and release approval | open |

## 4) Risks
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Missing source/evidence is mistaken for a finished design. | Incorrect interfaces or unsafe implementation. | Group 1 is the only active group; later groups have hard predecessors. |
| Raw traces or vendor errors leak PCI-scoped data. | Compliance/security incident and persistent repository exposure. | Allowlist schemas, synthetic leak tests, approved scans, and stop/delete/restrict procedure. |
| Shadow execution commits effects. | Duplicate financial or webhook outcomes in R1. | Decision-only boundary plus authoritative-store/event reconciliation and rollback trigger. |
| R2 eligibility/allocation or rollback is ambiguous. | Out-of-scope customer traffic or failed recovery. | Keep CL-013/014 open and R2 blocked until accepted design and drill evidence exist. |
| Missing refund/timeout datasets hide incompatibility. | Unsafe R2 promotion. | No waiver; produce approved datasets and passing oracles. |
| Legacy is removed before clean evidence or response planning. | Irreversible outage/regression. | 30-consecutive-day gate, IF-RETIRE blocker, explicit approval, and post-removal validation. |

## 5) Validation Procedure

### Agent Validation
```bash
python3 /Users/master/repo/software/skill-system/Skill-System/source/skills/plan-long-term-package/scripts/validate_phase_plan_package.py --root . --package PaymentEngineReplacement --slug payment-engine-replacement --dated-plan docs/plan/2026-07-10-payment-engine-replacement.md --archetype backend-service --modifiers "strict-behavior-parity,legacy-parity,rollback-required,cross-session-handoff,data-sensitive,security-sensitive"
python3 /Users/master/repo/software/skill-system/Skill-System/source/skills/plan-long-term-package/scripts/validate_phase_plan_package.py --root . --package PaymentEngineReplacement --slug payment-engine-replacement --dated-plan docs/plan/2026-07-10-payment-engine-replacement.md --archetype backend-service --modifiers "strict-behavior-parity,legacy-parity,rollback-required,cross-session-handoff,data-sensitive,security-sensitive" --strict --quality-lint
python3 /Users/master/repo/software/skill-system/Skill-System/source/skills/plan-long-term-package/scripts/validate_phase_plan_package.py --root . --package PaymentEngineReplacement --slug payment-engine-replacement --dated-plan docs/plan/2026-07-10-payment-engine-replacement.md --archetype backend-service --modifiers "strict-behavior-parity,legacy-parity,rollback-required,cross-session-handoff,data-sensitive,security-sensitive" --strict-handoff
python3 /Users/master/repo/software/skill-system/Skill-System/source/skills/plan-long-term-package/scripts/validate_phase_plan_package.py --root . --package PaymentEngineReplacement --slug payment-engine-replacement --dated-plan docs/plan/2026-07-10-payment-engine-replacement.md --archetype backend-service --modifiers "strict-behavior-parity,legacy-parity,rollback-required,cross-session-handoff,data-sensitive,security-sensitive" --strict --quality-lint --write-validation-stamp
```

### User Validation
1. Confirm whether CL-013 is the intended operational meaning of “immediate rollback.”
2. Supply/authorize the implementation source and safe evidence locations so Group 1 can replace `Unverified` entries.
3. Confirm the R2 selector decision owner and post-R3 fallback/forward-fix owner before those phases open.

## 6) Questions and Answers

### 질의
- Q-001: Where are the production source, endpoint inventory, and sampled authorization trace manifest?
  - status: `open`
  - answer: unavailable in this repository
  - evidence: domain ingest summary
- Q-002: Who owns gateway, ledger/refund, webhooks, ops, testing, security/data, and release approval?
  - status: `open`
  - answer: `Unverified`
  - evidence: no owner artifact available
- Q-003: What deterministic key/algorithm defines the R2 selection and audit population?
  - status: `open`
  - answer: `decision-needed`
  - evidence: CL-014
- Q-004: Are any normalized P0 differences intentionally allowed?
  - status: `open`
  - answer: none are pre-approved; any exception requires a canonical decision
  - evidence: CL-015
- Q-005: Does “immediate rollback” accept the proposed no-deploy/post-marker definition?
  - status: `open`
  - answer: `decision-needed`
  - evidence: CL-013
- Q-006: What fallback or forward-fix procedure remains after legacy removal?
  - status: `open`
  - answer: `decision-needed`
  - evidence: CL-016
- Q-007: Who will produce and approve sanitized refund and timeout datasets?
  - status: `open`
  - answer: owner and method are `Unverified`
  - evidence: CL-009/017

## 7) TODO
- [x] `done` — select archetype/modifiers and freeze artifact manifest.
- [x] `done` — define authority map, claim ledger, canonical contracts, and measurable release gates.
- [x] `done` — decompose discovery, R1, R2, and R3 into predecessor-linked groups.
- [ ] `blocked` — execute Group 1; source/evidence locations and owners are unavailable.
- [ ] `blocked` — execute Groups 2-5 until Group 1 and applicable predecessors close.
- [ ] `blocked` — open R2 until refund/timeout evidence, selector decision, rollback definition/control, R1 PASS, and approval exist.
- [ ] `blocked` — open R3 until R2 PASS, 30-day evidence, IF-RETIRE response decision, and approval exist.

## 8) Implementation Transition Status
- current_status: `planning-only`
- planning_state: `active_plan + package_planned` after package validator pass
- implementation_transition_marker: `PACKAGE_PLANNED_NOT_IMPLEMENTATION_READY`
- code_mutation_allowed: `not approved`
- hard_predecessor_gate: `blocked on Group 1 source/evidence access`
- active_phase: `Evidence Baseline`
- active_group: `group-1 — Service and Evidence Discovery`

## 9) Approval Gate
- current_status: `pending`
- approval_phrase: none
- approved_at: `Unverified`
- approver: `Unverified`

## 10) Progress Log
- 2026-07-10 America/Los_Angeles: admitted explicit package intent; inspected the brief and repository outline without network access.
- 2026-07-10 America/Los_Angeles: selected `backend-service` plus six risk modifiers; scaffolded the de-duplicated contract set and four-phase/seven-group package.
- 2026-07-10 America/Los_Angeles: filled canonical contracts first, then reconciled derived README, handoff, ingest, and group docs; no production code or runtime config changed.

## Active Implementation Card
- Active group: `docs/plan/PaymentEngineReplacement/Evidence Baseline/Group1-Service-Baseline.md`
- Goal: recover exact source/evidence paths, owners, interfaces, and safe runnable commands.
- Must read: domain ingest summary; capability, API, integration, security, source-of-truth, and handoff specs.
- Blocking contracts: IF-AUTH-NORMALIZED, IF-SHADOW, API discovery rows, security evidence-use approval.
- First file to inspect: implementation repository path list for `gateway/`, `ledger/`, `webhooks/`, and `ops/`.
- First artifact to produce: `artifacts/payment-engine-replacement/contracts/source-outline.txt`.
- Stop condition: source/evidence unavailable or inspection would copy prohibited data.
