---
doc_type: release_gate
canonical: true
status: draft
last_validated: Unverified
source_of_truth_for:
  - release-thresholds
  - pass-fail
derived_from: []
---

# {{SLUG}} Release Gate

## Purpose

## Gate Inputs
| Gate Input ID | Source Gate | Required? | Aggregation Rule | Owner |
| --- | --- | --- | --- | --- |
{{GATE_INPUT_ROWS}}

## Upstream Gates
| Upstream Gate | Contract Doc | Pass Condition | Blocks Release? |
| --- | --- | --- | --- |
{{UPSTREAM_GATE_ROWS}}

## Datasets
| Dataset | Version | Source | Split | Frozen? | Purpose | Size | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Numeric Thresholds
| Metric | Threshold | Unit | Comparator | Measurement Method | Baseline | Fail Severity | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Regression Matrix
| Scenario | Expected Result | Pass Condition | Owner | Automation Status |
| --- | --- | --- | --- | --- |

## Rollback Triggers
| Trigger | Severity | Action |
| --- | --- | --- |

## Waivers
| Waiver ID | Reason | Expires On | Approved By |
| --- | --- | --- | --- |

## Evidence Artifacts
| Artifact | Path | Produced By |
| --- | --- | --- |

## Verdict Rule
- PASS only if all required thresholds, scenarios, evidence artifacts, and blocking upstream gates pass.
