---
name: evaluation-harness
description: Reviews Skill System eval cases and observed routing/output behavior as usage-quality evidence, without turning eval review into release readiness or package validation.
---

# Evaluation Harness

## Routing Card
- role: primary
- intent_signature:
  - runtime usage eval
  - routing case review
  - negative routing review
  - usage quality case
  - manual result capture
  - eval smoke test consistency
- use_when:
  - the user asks to inspect, improve, or summarize `.codex/eval` or `source/shared/eval` usage cases.
  - routing, negative routing, context, memory, handoff, design, research, or maintainer eval cases need consistency review.
  - observed behavior from real or dry-run requests should be captured as usage-quality evidence.
- do_not_use_when:
  - the user wants release governance, readiness signoff, broad bundle validation, or package publish approval.
  - the request is ordinary code execution unrelated to eval cases.
  - the work would create deployment, signoff, operational recovery, or evidence-finality machinery.
  - the user asks for invocation counts or usage telemetry from a ledger; use `evaluation-usage-tracker`.
- expected_inputs:
  - eval cases from `.codex/eval/*.yaml` or `source/shared/eval/*.yaml`
  - `.codex/docs/skill_registry.md` or `source/shared/docs/skill_registry.md`
  - observed behavior only when the user supplies it or asks for a manual capture
- expected_outputs:
  - concise findings in the current response or an explicitly requested usage-quality note
  - filled manual result capture only when observation data exists
  - candidate eval/routing/registry/skill-text changes
  - no generated report directory
  - no readiness decision
  - no live settings mutation
- context_targets:
  must_read:
    - targeted eval case files
    - skill registry when family, maturity, or expected routing is involved
  read_if_needed:
    - `context-routing.md`
    - `research-routing.md`
    - target `SKILL.md` only when a finding maps to skill text
    - field-feedback YAML records only when real-use friction is in scope
  do_not_load_by_default:
    - live `$HOME/.codex`
    - live `$HOME/.claude`
    - plugin caches
    - archived sessions
    - raw transcripts
    - credentials
- risk_profile:
  reads:
    - local bundle eval, registry, routing, and selected skill files only
  writes:
    - none unless the user explicitly asks to edit eval/routing/registry/skill files
  tools:
    - optional read-only eval validation and focused search
  sensitive_resources:
    - credentials default deny; do not ingest raw prompts or transcripts
- entry_scene:
  - PREPARE

## Boundary
- Runtime usage eval is for observing skill quality in real use and dry-run cases.
- Eval review can propose improvements, but it is not release readiness, package validation, or critical signoff.
- Field feedback is stored as YAML records under `field-feedback/`, not a single Markdown file.

## Workflow
1. Select a small representative case set from `.codex/eval` or `source/shared/eval`.
2. Compare expected primary/supporting skills with observed behavior from a real request, dry run, or supplied case data.
3. If observation data exists, fill the manual result capture fields with concrete values.
4. If observation data is missing, report the missing data instead of emitting a blank capture template.
5. Map each finding to candidate changes in eval cases, routing docs, registry notes, field-feedback YAML, or skill text.
6. Keep the result focused on usage-quality observations and improvement candidates.

## Manual Result Capture Fields
Use this shape only when the fields can be filled. Do not paste it as a blank dummy template.

```yaml
result_capture:
  case_id:
  request_date:
  evaluator:
  observed_primary_skill:
  observed_supporting_skills: []
  context_overload: false
  unexpected_trigger: []
  missing_trigger: []
  output_shape_match: true
  friction:
  follow_up_change:
  verification: unverified
```

Allowed `verification` values:
- `agent-verified`
- `user-verification-needed`
- `unverified`

## Result Mapping
- `unexpected_trigger` -> add or adjust `negative_routing_cases.yaml`, then consider `context-routing.md` trigger guard changes.
- `missing_trigger` -> add or adjust `routing_cases.yaml`, then consider `SKILL.md` description or Routing Card changes.
- `context_overload` -> tighten `context_pack_guidelines.md`, skill-local `read_if_needed`, or `do_not_load_by_default`.
- `output_shape_match: false` -> update skill-local expected outputs or usage eval expected shape.
- `friction` -> add a field-feedback YAML record only when the friction was observed in real use.

## Output Contract
Return only the sections needed:
- `case_scope`
- `observed_behavior`
- `routing_mismatches`
- `context_mismatches`
- `output_shape_mismatches`
- `candidate_changes`
- `manual_capture`
- `validation`
- `remaining_gaps`

Use `manual_capture` only when observation data is available. Otherwise, say which fields are missing.

## Cross-Skill Boundaries
- `evaluation-usage-tracker` owns metadata-only invocation count summaries.
- `report-critical` owns release/readiness/QA verdicts.
- `workflow-validation` owns validation plans for implementation changes.
- `create-skill-pack` owns lifecycle edits after eval findings identify a concrete skill/package change.
- `report-qualitative` owns formal qualitative reports; this skill stays case-review oriented.

## Validation
- Eval cases must stay YAML-parseable.
- Result capture is evidence for improvement, not readiness.
- A single dry run can update a case; maturity changes require repeated field feedback or one severe routing failure.
- Do not output blank dummy capture fields as if they were observed data.
- Do not read or store raw prompts, secrets, transcripts, or private logs.

## Known Limits
- Eval cases model expected routing behavior; they do not prove runtime installation state.
- Observed behavior can be model/runtime-version dependent and should be labeled when not directly verified.
- Field feedback records are qualitative evidence and do not automatically change maturity.
