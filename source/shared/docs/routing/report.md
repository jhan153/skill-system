# Report & Review Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `report-critical`

- role: report_primary
- family: report
- intent_signature: explicit blocker report, critical review report, risk report, QA gate report
- use_when:
  - the user explicitly requests a critical/blocker/risk/QA report or an accepted Plan assigns that report condition
- do_not_use_when:
  - the request is ordinary failure diagnosis, ordinary code review, qualitative evaluation, implementation, or an automatic completion check
  - `검토해` or `문제가 뭐야` appears without critical-report, risk, blocker-report, or QA-gate intent
- expected_inputs: bounded target, report decision, material criteria, audience, and evidence anchors
- expected_outputs: content-first Markdown with a calibrated blocker or QA result; optional matching HTML projection
- context_targets:
  must_read:
    - smallest target/evidence slice that can answer the report decision
    - stated goal, material criteria, and requested delivery mode
    - `references/report_delivery_contract.md`
  read_if_needed:
    - active Plan or policy only when it supplies a material criterion
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when inspectable spatial evidence is material
  do_not_load_by_default:
    - full chat history, full repository, generic benchmark/reference lists, unrelated plans, or another worker transcript
- risk_profile:
  reads: bounded target, criteria, and decisive evidence
  writes: one Markdown report and only the explicitly selected optional HTML projection; never the reviewed artifact
  tools: focused read-only verification only when a material claim needs it
  sensitive_resources: credentials denied; redact sensitive evidence
- entry_scene: PREPARE

## `report-implementation-explainer`

- role: report_primary
- family: report
- intent_signature: explicit implementation explanation report or verified changed-lines/before-after report
- use_when:
  - the user requests a durable causal implementation explanation or readable verified comparison
- do_not_use_when:
  - a direct local answer is sufficient, no concrete target exists, or the artifact would be automatic after implementation
  - quality/readiness judgment, approach selection, or production changes are primary
- expected_inputs: selected mode, concrete snapshot, decision purpose, audience, production path or authoritative diff pair, and delivery mode
- expected_outputs: content-first Markdown explanation/comparison; optional matching trace, compare, or spatial HTML
- context_targets:
  must_read:
    - target snapshot, requested mode, audience/decision purpose, and canonical caller-to-output path or diff pair
    - `references/report_delivery_contract.md`
  read_if_needed:
    - focused tests, runtime readback, accepted intent, rationale history, and one material counterexample
    - `references/compare-mode.md` for compare mode
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when inspectable spatial evidence is material
  do_not_load_by_default:
    - full repository/history, unrelated plans, generated mirrors, broad logs, or another worker transcript
- risk_profile:
  reads: bounded source, config, tests, traces, accepted decisions, or authoritative diff
  writes: one Markdown report and only the explicitly selected optional HTML projection; never production code or instrumentation
  tools: focused read-only inspection and optional local rendering
  sensitive_resources: credentials denied; redact sensitive runtime data
- entry_scene: PREPARE

## `report-lifecycle-artifacts`

- role: report_primary
- family: report
- intent_signature: explicit lifecycle artifact package, SDLC traceability index, selected delivery evidence package
- use_when:
  - the user explicitly requests packaging or normalization of named lifecycle artifacts and their evidence links
- do_not_use_when:
  - implementation, planning, status tracking, validation execution, critique, task-local inventory, or automatic closeout is primary
  - source artifacts do not exist and the request is merely to create generic planned shells
- expected_inputs: selected source artifacts, package scope, result/evidence authority, destination, and delivery mode
- expected_outputs: Markdown lifecycle index, selected artifact links/normalizations, traceability matrix, preserved gaps/statuses, and optional matching HTML trace
- context_targets:
  must_read:
    - explicit package scope, selected source artifacts, and evidence supporting represented results
    - `references/report_delivery_contract.md`
  read_if_needed:
    - `references/artifact-tiering.md` only to bound an explicitly requested package
    - `references/traceability-matrix-schema.md` for a persisted matrix
    - applicable requirements, Plan/Handoff, Core execution-item cards, review, validation, security, release, or retrospective artifacts named by the request
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when packaged spatial evidence must be inspected
  do_not_load_by_default:
    - full repository, plan inventory, memory store, unrelated logs, generic templates, or generated mirrors
- risk_profile:
  reads: explicitly selected artifacts and condition-matched evidence
  writes: requested Markdown index/matrix, bounded normalization of selected artifacts, and only the selected optional HTML projection
  tools: local readback and optional report rendering; no implementation, validation, release, or external publication
  sensitive_resources: credentials denied; redact secrets and audience-sensitive data
- entry_scene: PREPARE

## `report-qualitative`

- role: report_primary
- family: report
- intent_signature: explicit qualitative fitness, strengths/weaknesses, tradeoff, or improvement-priority report
- use_when:
  - the user asks whether a target is fit for an intended purpose or requests a qualitative judgment under stated or delegated criteria
- do_not_use_when:
  - blocker-first QA or failure diagnosis is primary
  - the output is only metrics/counts, changed lines, telemetry, validation execution, or implementation
  - vague `검토/보고` wording provides no qualitative decision intent
- expected_inputs: bounded target, decision goal, stakeholder/use context, criterion authority, evidence anchors, and delivery mode
- expected_outputs: criterion-grounded Markdown evaluation; optional HTML projection with identical judgments
- context_targets:
  must_read:
    - target or smallest relevant slice
    - decision goal, constraints, criterion authority, and requested delivery mode
    - `references/report_delivery_contract.md`
  read_if_needed:
    - `references/quality-evaluation-method.md` when criteria need elicitation or delegated selection
    - `references/evidence_mapping.md` for large, ambiguous, or multi-source targets
    - `references/rubric.md` only for an explicitly ordinal or rubric-heavy report
    - `references/report_template.md` only for an explicitly full or reusable report
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when inspectable spatial evidence is material
  do_not_load_by_default:
    - rubrics/templates when a brief is sufficient, full repository/history, unrelated plans/reports, or generic example catalogs
- risk_profile:
  reads: bounded target and decisive evidence anchors
  writes: one Markdown report and only the explicitly selected optional HTML projection; never the evaluated artifact
  tools: focused read-only inspection when locally available evidence is decision-changing
  sensitive_resources: credentials denied; redact sensitive evidence
- entry_scene: PREPARE
