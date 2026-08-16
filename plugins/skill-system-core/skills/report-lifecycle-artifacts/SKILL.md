---
name: report-lifecycle-artifacts
description: Package explicitly requested lifecycle artifacts and traceability across requirements, design, implementation, validation, security, release, and retrospective, with a Report Canvas trace index as the default human-facing entry point.
---

# Report Lifecycle Artifacts

## Routing Card
- role: report_primary
- intent_signature: lifecycle/SDLC artifacts, 개발 산출물, WBS/HLD/LLD/QA/security/release, traceability matrix
- use_when:
  - The user explicitly requests a lifecycle package, planned shells, or evidence-backed normalization.
  - Lifecycle records must be linked in a formal traceability matrix.
- do_not_use_when:
  - Do not use for implementation, planning, `docs/plan` sync, validation execution, critique-only review, or memory promotion.
  - Changed files plus validation notes use `plan-task-handoff`; blocker-first QA critique uses `report-critical`.
  - Missing evidence does not cancel explicit packaging; preserve the unresolved result.
- expected_inputs: package scope or sources; evidence anchors for result claims
- expected_outputs: Report Canvas `trace` HTML index plus the requested canonical artifact pack, traceability matrix, condition-scoped statuses, and gaps
- context_targets:
  must_read:
    - packaging request, included sources, and evidence for claimed results
  read_if_needed:
    - `references/artifact-tiering.md` and only the relevant templates
    - `$REPORT_SKILL_DIR/references/report_visual_authoring.md` when a packaged 3D/math/graphics artifact must be seen
    - narrow plan, specification, or validation files in scope
  do_not_load_by_default:
    - full repository, memory bank, plan inventory, unrelated logs, or generated mirrors
- risk_profile:
  reads: provided artifacts and named evidence
  writes: one self-contained report HTML by default; canonical lifecycle files only within the explicitly requested package scope
  sensitive_resources: deny credentials; redact secrets
- entry_scene: PREPARE

## Package Contract

Use the smallest requested tier; full packs stay explicit-only. Never execute implementation or validation.

Canonical artifacts, when present: `requirements-discovery-record`, `requirements-contract`, `delivery-architecture-package`, `implementation-design-record`, `implementation-evidence-record`, `verification-and-quality-report`, `security-risk-review`, `release-readiness-report`, `delivery-retrospective`, and `lifecycle-traceability-matrix`.

Modes: `planned_artifacts`, `design_artifacts`, `verification_artifacts`, `closeout_artifacts`, and `full_lifecycle_pack`.

## Semantic Completion Gate

Report package construction separately from every lifecycle result. For `planned` or `not_executed` results, state: `Package completion does not imply implementation completion.` Other results may remain `evidence_unavailable`, `needs_review`, `user_verification_needed`, `blocked`, or `fail`.

Use `evidence_unavailable` when the required oracle or actual-path evidence is absent despite agent tests or mocks; reserve `not_executed` for intentionally unrun work and `needs_review` for available evidence awaiting judgment.

For each material result, record:

- source condition and claim;
- evidence scope: `structural`, `runtime`, `semantic`, or `user-only`;
- oracle origin: user decision, canonical source, external contract, formal invariant, observed behavior, or agent-authored;
- reference, freshness, and status.

Use `agent-verified` only when evidence directly covers the condition at its required scope. Command exits, artifact presence, hooks, schemas, and harnesses prove only their contract. An agent-authored test may preserve an established oracle; it cannot invent one and become independent semantic proof. When only mocks pass, state: `Mocks prove only the mock boundary`, then name the required real path.

Source selection, migration, media/data transforms, external boundaries, and adapters require actual-path execution and material output readback. Preserve canonical-source or required-input mismatches as failure or explicit unresolved decisions; never report silent fallback as success.

Never lower an unresolved status because a narrower check passed. Change the same condition only with resolution/readback evidence or the required user decision.

If the exact condition is structural, such as a matrix with valid stable links, a structural check may close only that condition. Planned-shell delivery may be package-complete while represented results remain planned or not executed.

## Canvas Asset Resolution

For every admitted invocation, set `REPORT_SKILL_DIR` to the directory containing this active skill's resolved `SKILL.md`; use the exact `file:` path exposed by the current skill catalog. The bundled contract documents the Codex plugin-cache layout explicitly. Never guess, glob, or select an install/cache version from the current working directory.

Require `$REPORT_SKILL_DIR/references/report_canvas_contract.md` and `$REPORT_SKILL_DIR/scripts/report-canvas/render_report.py`. `source/tools/generate_targets.py` only projects repository assets and is not the report renderer. If either local file is missing, report an incomplete installed payload and use the contract's allowed chat fallback; do not search sibling plugins, unrelated checkouts, alternate global skill roots, or app-managed system skills for substitutes.

## Traceability And Output

Prefer stable IDs: `REQ-*`, `AC-*`, `WBS-*`, `HLD-*`, `LLD-*`, `TEST-*`, `SEC-*`, `REL-*`, and `RETRO-*`.

Return only needed sections: `artifact_scope`, `source_artifacts`, `artifact_pack`, `traceability_matrix`, `evidence_status`, `gaps`, and `handoff_targets`. Link completed claims to condition-scoped evidence.

Persist the requested canonical artifacts in their required formats. Read `$REPORT_SKILL_DIR/references/report_canvas_contract.md` and render the primary human-facing entry point with `$REPORT_SKILL_DIR/scripts/report-canvas/render_report.py` as Report Canvas `trace` HTML whose nodes identify the canonical artifacts and condition-scoped evidence. Declare `trace_kind: lifecycle` and set every node's typed `lifecycle_status` to the preserved lifecycle result while keeping node `status` limited to evidence confidence; the renderer rejects a lifecycle trace that omits either contract. Never collapse the two axes into label/detail prose. If the inspectable visual gate fires for a packaged 3D/math/graphics artifact, also emit a `spatial` report from `references/report_visual_authoring.md` rather than restyling the trace. Never edit Canvas CSS/JS. Return only a concise chat receipt with package status and the Canvas link. Use chat-only output only when the user explicitly prohibits file creation, the host has no safe artifact surface, or the resolved installed payload is incomplete. Canvas is navigation over the package, not the package or proof of lifecycle completion.

## Owner Boundaries

- `plan-requirements-discovery`: elicitation; `plan-requirements-brief`: requirements contracts.
- `plan-long-term-package`: heavy phase planning; `plan-short-term-docs`: active implementation design/status sync.
- `workflow-plan-runner`: plan execution; `workflow-validation`: validation strategy/execution.
- `plan-task-handoff`: small task-local inventories; `report-critical`: blocker-first critique.
