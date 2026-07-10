---
doc_type: release_gate
canonical: true
status: draft
last_validated: 2026-07-10T06:50:28-07:00
last_validated_mode: strict-handoff
strict_validated_at: 2026-07-10T06:50:28-07:00
strict_handoff_validated_at: 2026-07-10T06:50:28-07:00
release_ready: false
source_of_truth_for:
  - release-thresholds
  - pass-fail
derived_from: []
---

# payment-engine-replacement Release Gate

## Purpose

Own the measurable pass/fail criteria for R1 shadowing, R2 10% refundable test-tenant routing, and R3 legacy retirement. Document validation does not satisfy any runtime gate.

## Gate Inputs
| Gate Input ID | Source Gate | Required? | Aggregation Rule | Owner |
| --- | --- | --- | --- | --- |
| GI-001 | capability-map | true | Every P0 capability has a contract and no unapproved descoping. | Planning/release owner |
| GI-002 | api-contract | true | Exact interfaces and error semantics are characterized and tests pass. | Gateway owner |
| GI-003 | data-contract | true | Data authority, side effects, and safe evidence schema are approved and tested. | Data/ledger owners |
| GI-004 | integration-contract | true | All interfaces blocking the target release are resolved with runtime or test evidence. | Integration owner |
| GI-005 | observability-contract | true | Required signals, alerts, and evidence artifacts exist and are reviewed. | Ops owner |
| GI-006 | behavior-parity-contract | true | Every release-applicable behavior oracle passes. | Test/surface owners |
| GI-007 | parity-contract | true | Required datasets and comparator reports have zero unexplained failures. | Test owner |
| GI-008 | old-new-mapping | true | Every behavior-bearing mapping is explicit and validated. | Gateway owner |
| GI-009 | compatibility-matrix | true | Only the release-supported combination is enabled. | Release owner |
| GI-010 | rollback-plan | true | Release-applicable rollback drill passes. | Release operator |
| GI-011 | rollback-trigger | true | Triggers and alerts are configured and tested. | Ops/release owners |
| GI-012 | source-of-truth-policy | true | Validator confirms no authority drift. | Planning owner |
| GI-013 | agent-handoff-index | true | Evidence/read-order/active status pointers are current. | Planning owner |
| GI-014 | migration-map | true | All release predecessors and rollback hooks are closed. | Migration owner |
| GI-015 | security-contract | true | All release-applicable controls pass with zero sensitive-data findings. | Security owner |

## Upstream Gates
| Upstream Gate | Contract Doc | Pass Condition | Blocks Release? |
| --- | --- | --- | --- |
| api-contract | docs/spec/payment-engine-replacement-api-contract.md | release-blocking contract passes | true |
| data-contract | docs/spec/payment-engine-replacement-data-contract.md | release-blocking contract passes | true |
| observability-contract | docs/spec/payment-engine-replacement-observability-contract.md | release-blocking contract passes | true |
| behavior-parity-contract | docs/spec/payment-engine-replacement-behavior-parity-contract.md | release-blocking contract passes | true |
| parity-contract | docs/spec/payment-engine-replacement-parity-contract.md | release-blocking contract passes | true |
| old-new-mapping | docs/spec/payment-engine-replacement-old-new-mapping.md | release-blocking contract passes | true |
| compatibility-matrix | docs/spec/payment-engine-replacement-compatibility-matrix.md | release-blocking contract passes | true |
| rollback-plan | docs/spec/payment-engine-replacement-rollback-plan.md | release-blocking contract passes | true |
| rollback-trigger | docs/spec/payment-engine-replacement-rollback-trigger.md | release-blocking contract passes | true |
| source-of-truth-policy | docs/spec/payment-engine-replacement-source-of-truth-policy.md | release-blocking contract passes | true |
| agent-handoff-index | docs/spec/payment-engine-replacement-agent-handoff-index.md | release-blocking contract passes | true |
| migration-map | docs/spec/payment-engine-replacement-migration-map.md | release-blocking contract passes | true |
| security-contract | docs/spec/payment-engine-replacement-security-contract.md | release-blocking contract passes | true |

## Datasets
| Dataset | Version | Source | Split | Frozen? | Purpose | Size | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DS-AUTH | Version assigned after secure ingest | Reported one-week sampled authorization traces; exact path/sanitization `Unverified` | Characterization plus held-out regression split defined before R1 | no | Authorization result/error parity | `Unverified` | Trace/test owner |
| DS-AUTH-LIVE-R1 | R1 release window | Sanitized shadow observations | All eligible R1 shadow observations | no | R1 live parity and side-effect proof | release-dependent | Ops/test owners |
| DS-REFUND | Version assigned on creation | Sanitized refundable test-tenant scenarios; not yet available | Characterization plus held-out regression split | no | Refund state/financial-effect parity before R2 | missing | Payment/test owners |
| DS-TIMEOUT | Version assigned on creation | Sanitized traces or approved synthetic failure-injection scenarios; not yet available | Boundary and held-out regression cases | no | Timeout/retry/uncertain-result parity before R2 | missing | Ops/test owners |
| DS-IDEMP | Version assigned in Phase 0 | Synthetic first/replay/conflict cases across routing/rollback | Full P0 matrix | no | Exactly-once behavior | `Unverified` | Gateway/test owners |
| DS-WEBHOOK | Version assigned in Phase 0 | Synthetic/sanitized committed P0 flows | Full P0 sequence matrix | no | Event order and duplicate policy | `Unverified` | Webhook/test owners |
| DS-R3-DAILY | One record per UTC day | Reviewed sanitized parity/health/security rollups | 30 consecutive daily records | no | Legacy retirement observation window | 30 records minimum | Release owner |

## Numeric Thresholds
| Metric | Threshold | Unit | Comparator | Measurement Method | Baseline | Fail Severity | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 customer-visible `new-pay` authoritative routes | 0 | operations | exact | Routing audit for full R1 window | Legacy-only | critical | Legacy remains authority. |
| R1 new-engine commit side effects | 0 | ledger/refund/webhook effects | exact | Counters plus authoritative-store reconciliation | Legacy-only | critical | Decision-only shadow invariant. |
| R1 unexplained P0 parity failures | 0 | failures | exact | Approved comparator over DS-AUTH and live observations | `Unverified` | critical | Explanations require canonical decision; no implicit tolerance. |
| R2 configured eligible allocation | 10.0 | percent | exact config plus deterministic-selector audit | Readback config and verify every audited selection against approved selector | 0% new | critical | Cohort key/algorithm is decision-needed before R2. |
| R2 ineligible new-engine routes | 0 | operations | exact | Full release routing audit by tenant/refund eligibility classification | 0 | critical | No non-test or non-refundable scope. |
| R2 unexplained P0 parity failures | 0 | failures | exact | All applicable comparator reports and release observations | R1 evidence | critical | Includes all six compatibility surfaces. |
| R2 post-rollback new-engine routes | 0 | operations | exact after effective marker | Routing audit plus synthetic probes | `Unverified` | critical | Rollback requires no deploy. |
| PCI/secret/raw-payload findings in new logs or planning/evidence artifacts | 0 | findings | exact | Approved automated scan plus reviewed samples | `Unverified` | critical/security | Applies before and throughout R1-R3. |
| R3 clean observation window | 30 | consecutive calendar days | exact | One accepted DS-R3-DAILY record per UTC day; reset after any unexplained P0 failure | 0 days | critical | Starts only after R2 gate passes. |
| R3 unexplained P0 parity failures | 0 | failures over 30-day window | exact | Daily rollup plus full P0 regression at end | R2 evidence | critical | Any failure resets the clock after remediation. |

## Regression Matrix
| Scenario | Expected Result | Pass Condition | Owner | Automation Status |
| --- | --- | --- | --- | --- |
| Authorization decision/error boundaries | New normalized result equals legacy. | Zero unexplained mismatches on DS-AUTH and release-applicable observations. | Gateway/test owners | planned; source command discovery blocked |
| Idempotent replay across engine/rollback changes | Same result and one side-effect set. | Zero result/cardinality mismatches on DS-IDEMP. | Gateway/test owners | planned |
| Ledger posting | Same normalized posting multiset. | Zero unexplained posting differences. | Ledger/test owners | planned |
| Refund transitions | Same eligibility, path, terminal state, and effect. | DS-REFUND exists, is approved, and has zero unexplained differences. | Payment/test owners | blocked: dataset missing |
| Timeout/retry/uncertain result | Same mapped classes and one effect set. | DS-TIMEOUT exists, is approved, and has zero unmapped/unexplained outcomes. | Ops/test owners | blocked: dataset missing |
| Webhook sequence | Same causal order and duplicate policy. | Zero sequence/duplicate-policy violations on DS-WEBHOOK. | Webhook/test owners | planned |
| R1 no-commit shadow | New engine commits nothing. | Exactly zero new-engine financial/event effects. | Gateway/ledger/webhook owners | planned |
| R2 eligibility/allocation | Only approved cohort selects new. | 10.0% configured allocation; zero selector deviations; zero ineligible routes. | Gateway/ops owners | blocked: selector decision |
| R2 rollback | Next decisions after effective marker use legacy without deploy. | 0% readback and zero post-marker new routes; in-flight reconciliation complete. | Release operator | blocked: control discovery/drill |
| Security | No forbidden data in new outputs/artifacts. | Zero scanner findings and approved control review. | Security owner | planned |
| R3 retirement | Observation and regression gates remain clean. | 30 consecutive accepted days and all P0 regressions pass. | Release owner | blocked until R2 pass |

## Rollback Triggers
| Trigger | Severity | Action |
| --- | --- | --- |
| Any threshold above fails. | critical or stated severity | Apply the matching canonical rollback trigger and keep the release failed. |
| Required evidence is missing, unsafe, stale, or unreviewed. | release-blocking | Do not enable/promote; produce safe evidence. |
| A blocking interface/owner/decision remains open. | release-blocking | Do not enable/promote; resolve in canonical contract/dated plan. |

## Waivers
| Waiver ID | Reason | Expires On | Approved By |
| --- | --- | --- | --- |
| WAIVER-NONE | No waiver is pre-approved for P0 parity, PCI safety, R2 scope/rollback, or the R3 30-day window. | not applicable | not applicable |

## Evidence Artifacts
| Artifact | Path | Produced By |
| --- | --- | --- |
| Contract/interface inventory | `artifacts/payment-engine-replacement/contracts/` | Gateway/integration owners |
| Parity comparator reports | `artifacts/payment-engine-replacement/parity/` | Test/surface owners |
| Security control reports | `artifacts/payment-engine-replacement/security/` | Security owner |
| Routing/allocation evidence | `artifacts/payment-engine-replacement/metrics/r2-route-report.json` | Ops owner |
| Rollback drill/event evidence | `artifacts/payment-engine-replacement/rollback/` | Release operator |
| Release decisions and R3 daily records | `artifacts/payment-engine-replacement/release/` | Release owner |

## Verdict Rule
- PASS only if all required thresholds, scenarios, evidence artifacts, and blocking upstream gates pass.
- R1 PASS authorizes shadow observation only; it does not authorize customer traffic on `new-pay`.
- R2 PASS authorizes only the 10.0% eligible cohort and requires the rollback control to remain available.
- R3 PASS requires 30 consecutive accepted days and an approved post-removal fallback/forward-fix decision; document validation alone never passes a runtime release gate.
