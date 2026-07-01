---
name: report-lifecycle-artifacts
description: Create or update formal product/software lifecycle artifact packages by mapping requirements discovery records, requirements contracts, delivery architecture packages, implementation design records, implementation evidence, test/QC/QA artifacts, security review, release readiness, retrospective, and traceability matrices. Use only when explicitly requested.
---

# Report Lifecycle Artifacts

## Routing Card
- role: report_primary
- intent_signature:
  - lifecycle artifacts
  - SDLC artifacts
  - product lifecycle documents
  - 개발 산출물
  - 요구사항 WBS HLD LLD QA 보안 릴리즈 회고
  - traceability matrix
- use_when:
  - the user explicitly asks for lifecycle deliverables, SDLC/product-development documents, or evidence-backed artifact packaging.
  - discovery records, requirements contracts, architecture packages, implementation design records, implementation evidence, validation evidence, or release evidence must be mapped into a formal artifact pack.
  - a traceability matrix is needed across requirements, acceptance criteria, WBS, design, tests, security, release, and retrospective items.
- do_not_use_when:
  - the user wants direct implementation, casual planning, small TODOs, active `docs/plan` status sync, validation execution alone, critique-only review, or memory promotion.
  - the user only wants changed files and validation notes; use `report-artifact-inventory`.
  - the user wants blocker-first QA critique; use `report-critical`.
  - evidence for result artifacts is unavailable and the user expects completion claims.
- expected_inputs:
  - one or more lifecycle source artifacts or explicit request to create planned artifact shells
  - evidence references for implementation, validation, QA, security, or release claims when result status is requested
  - desired artifact tier or package scope when available
- expected_outputs:
  - lifecycle-artifact-pack
  - lifecycle-traceability-matrix
  - explicit status labels for planned, not executed, evidence unavailable, user verification needed, or agent-verified items
- context_targets:
  must_read:
    - current artifact packaging request
    - provided lifecycle source artifacts or artifact pointers
    - evidence anchors for any completed result claims
  read_if_needed:
    - `references/artifact-tiering.md`
    - relevant artifact templates under `references/`
    - narrow plan/spec/validation files explicitly included in the package
  do_not_load_by_default:
    - full repo
    - full memory bank
    - all plan packages
    - unrelated validation logs
    - generated runtime mirrors unless packaging generated target evidence is explicitly requested
- risk_profile:
  reads:
    - provided artifacts, approved plans/specs, and evidence anchors
  writes:
    - none by default; write lifecycle artifact files only when explicitly requested
  tools:
    - local file reads and optional artifact scaffold script when requested
  sensitive_resources:
    - credentials default deny; redact secrets from evidence excerpts and artifact outputs
- entry_scene:
  - PREPARE

## Purpose
- Normalize product/software lifecycle documents into one coherent artifact package.
- Preserve traceability from requirements through release and retrospective.
- Keep evidence-backed result reporting honest.

## Artifact Spine
Use these canonical artifact names when present:
- `requirements-discovery-record`
- `requirements-contract`
- `delivery-architecture-package`
- `implementation-design-record`
- `implementation-evidence-record`
- `verification-and-quality-report`
- `security-risk-review`
- `release-readiness-report`
- `delivery-retrospective`
- `lifecycle-traceability-matrix`

## Evidence Rules
- Do not mark tests, QC, QA, security, or release readiness as complete without evidence.
- If evidence is missing, use one of:
  - `planned`
  - `not_executed`
  - `evidence_unavailable`
  - `user_verification_needed`
  - `blocked`
- Separate plan status from result status.
- Trace every completed result claim to a command, file, artifact, review, or user-provided evidence reference.

## Modes
- `planned_artifacts`: requirements, scope, WBS, milestones, HLD/LLD-style package shells.
- `design_artifacts`: delivery architecture package and implementation design record normalization.
- `verification_artifacts`: test, QC, QA, and validation evidence packaging.
- `closeout_artifacts`: security review, release readiness, known issues, rollback notes, and retrospective.
- `full_lifecycle_pack`: explicit full package from discovery through retrospective.

## Output Contract
Return only the sections needed:
- `artifact_scope`
- `source_artifacts`
- `artifact_pack`
- `traceability_matrix`
- `evidence_status`
- `gaps`
- `handoff_targets`

## Traceability Contract
Prefer stable IDs:
- `REQ-*` requirements
- `AC-*` acceptance criteria
- `WBS-*` work breakdown items
- `HLD-*` architecture/package decisions
- `LLD-*` implementation design records
- `TEST-*` test/verification items
- `SEC-*` security review items
- `REL-*` release gate items
- `RETRO-*` retrospective follow-ups

## Cross-Skill Boundaries
- `plan-requirements-discovery` owns requirements elicitation.
- `plan-requirements-brief` owns requirements contracts and PRD/SRS-lite distillation.
- `plan-long-term-package` owns heavy phase/package planning.
- `plan-short-term-docs` owns active `docs/plan` implementation design and status sync.
- `workflow-plan-runner` owns executing approved plans/specs.
- `workflow-validation` owns validation strategy and validation execution.
- `report-artifact-inventory` owns small task-local artifact inventories.
- `report-critical` owns blocker-first QA critique.

## Known Limits
- This skill packages and reports lifecycle artifacts; it does not execute implementation.
- It cannot prove runtime behavior without validation evidence.
- Full lifecycle packages are heavy and should remain explicit-only.
