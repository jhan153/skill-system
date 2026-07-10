# Package Core Invariants

Read this only after explicit multi-document package intent is confirmed. It is the compact authoring kernel; templates and detailed mechanics remain conditional.

## Authority

- Scope, interfaces, state, parity targets, and release criteria each have exactly one canonical `docs/spec/` owner.
- Current execution/approval/TODO state belongs only to the canonical dated plan.
- README and phase/group docs are derived navigation and decomposition; conflicts are corrected from the canonical owner outward.

## Claim Ledger

Record every statement that changes scope, architecture, dependency order, acceptance, or release readiness.

| Field | Required meaning |
| --- | --- |
| `claim_id` | stable `CL-NNN` identifier |
| `statement` | one falsifiable or decision-bearing claim |
| `grade` | `verified-source`, `observed-runtime`, `inferred`, or `decision-needed` |
| `source` | file/line, command artifact, accepted decision, or explicit missing source |
| `impact` | contracts, phases, or gates affected |
| `status` | `accepted`, `open`, or `rejected` |

`inferred` and `decision-needed` claims may guide discovery but cannot define a blocking contract or release pass without an explicit decision or stronger evidence.

## Manifest

Freeze the selected archetype/modifiers, canonical dated plan, package root, phase docs, canonical contracts, ingest summary, and validation modes before loading templates. Generate only the de-duplicated archetype/modifier/universal contract set.

## Phase Readiness

A phase is implementation-ready only when each blocking outcome has:

- a canonical contract owner and target implementation surface
- a discriminating oracle: scenario/input, observable expected result, verifier/command, evidence destination, and owner
- hard predecessors and unresolved decisions made explicit
- rollback/fallback for risky changes

Document existence, heading presence, code-count similarity, or framework-language difference can prove structure only. They cannot pass logic, parity, lifecycle, performance, accessibility, or UX behavior.

## Release Truth

- A release gate passes only from its declared evidence and thresholds.
- Derived rollups never upgrade an open claim, missing oracle, or failed upstream gate.
- Validation stamps record a successful validator run; they do not substitute for runtime or user-visible evidence.
