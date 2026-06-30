---
name: create-skill-pack
description: Manages the lifecycle of user-managed Codex custom skill packs and reference packs. Use when explicitly creating, hardening, migrating, deprecating, registering, or updating metadata and route smoke tests for reusable custom skills.
---

# Create Skill Pack Lifecycle Manager

## Routing Card
- role: primary
- lifecycle_modes:
  - create_new_skill_pack
  - create_reference_pack
  - harden_existing_skill
  - migrate_existing_skill
  - split_or_merge_skill
  - deprecate_skill
  - register_routing
  - update_agent_metadata
  - add_route_smoke_tests
- intent_signature:
  - create user-managed Codex skill pack, reference pack, skill hardening, legacy custom skill migration, custom skill deprecation, routing registration, agent metadata update, route smoke test update
- use_when:
  - the user explicitly asks to create, update, harden, migrate, deprecate, split, merge, register, or add routing tests for a user-managed Codex custom skill/reference pack.
  - an existing custom skill needs lifecycle maintenance across `SKILL.md`, references, docs, `agents/openai.yaml`, or `context-routing.md`.
- do_not_use_when:
  - the target is `.codex/skills/.system` or another system-managed skill namespace.
  - the user only wants to execute an existing skill.
  - the user asks for casual explanation of what skills are.
  - the task is ordinary code review, bug analysis, planning, memory-only update, repo `AGENTS.md`-only rule, or one-turn formatting preference.
- expected_inputs:
  - lifecycle mode, primary skill, target skill id, scope, intended triggers, pack type, validation needs, routing/metadata intent
- expected_outputs:
  - lifecycle result, skill/reference artifacts, routing decision, metadata decision, smoke test decision, validation checklist
- context_targets:
  must_read:
    - current lifecycle request
    - target custom skill files when updating an existing custom skill
  read_if_needed:
    - one or two adjacent user-managed custom skills with similar role
    - `context-routing.md` only when routing registration or trigger conflict is in scope
    - `agents/openai.yaml` only when metadata decision is in scope
  do_not_load_by_default:
    - `.codex/skills/.system`
    - full skill library
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - targeted requirements, target custom skill files, adjacent custom examples when needed
  writes:
    - requested custom skill/reference pack files, metadata, and routing docs only when lifecycle scope requires them
  tools:
    - safe validation/listing commands
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Purpose
This skill is the lifecycle manager for user-managed custom skills in this `.codex` library. It creates new skill/reference packs and maintains existing custom skills so routing, metadata, smoke tests, risk boundaries, recovery rules, and validation stay aligned. `.codex/skills/.system` is Codex app-managed and outside this lifecycle.

## Lifecycle Scope
- Include: user-managed custom skills under `.codex/skills/*` excluding `.system`.
- Exclude: `.codex/skills/.system`, system-managed markers, app-managed skill files, memory-only updates, repo `AGENTS.md`-only rules, and one-turn preferences.
- Do not create, harden, migrate, deprecate, route-register, smoke-test, or patch `.system` skills through this skill.
- For existing skill hardening, `create-skill-pack` is the `primary_skill`; the inspected or patched custom skill is the `target_skill` and must not be treated as the primary execution workflow.

## Lifecycle Modes
- `create_new_skill_pack`: create a new user-managed Codex custom skill pack.
- `create_reference_pack`: create reference/docs only, without `SKILL.md` or agent metadata.
- `harden_existing_skill`: add or correct Routing Card, context targets, Resource/Risk Boundary, Recovery/Context Expansion, Known Limits, validation, or metadata for a custom skill.
- `migrate_existing_skill`: bring a legacy custom skill into the current routing style.
- `split_or_merge_skill`: propose splitting overloaded custom skills or merging near-duplicates; do not delete without explicit approval.
- `deprecate_skill`: mark a custom skill deprecated/superseded, update routing references, and add migration notes; do not delete by default.
- `register_routing`: decide whether to update `context-routing.md` route matrix and route smoke tests for a custom skill.
- `update_agent_metadata`: create or update custom skill `agents/openai.yaml` when metadata is in scope.
- `add_route_smoke_tests`: add or update routing smoke tests for created or modified custom skills.

## Pack Types
- Codex Skill Pack: `.codex/skills/{skill-id}/SKILL.md` + `reference.md` + `docs/document.md`, with optional `agents/openai.yaml`.
- Reference Pack: `.codex/references/{reference-pack-id}/reference.md` + `docs/document.md`; no `SKILL.md` or agent metadata unless later promoted.
- If a reference-only pack is temporarily placed under `.codex/skills/`, it must not include `SKILL.md` or `agents/openai.yaml`, and it must not be route-registered as a skill.
- Do not create `SKILL.md` for reference-only mode unless the user asks to promote it into a real skill.

## Skill Lifecycle Output Contract
When creating or updating a custom skill, output or prepare:
- `lifecycle_mode`
- `primary_skill`
- `target_skill`
- `affected_skill_id`
- `files_to_create`
- `files_to_update`
- `must_read`
- `exclude_as_primary_skill`
- `must_not_route_to`
- `routing_decision`
- `agent_metadata_decision`
- `smoke_test_decision`
- `risk_boundary`
- `validation_checklist`
- `follow_up_review`

Do not silently create routing entries, metadata, or smoke tests unless the user requested lifecycle registration or the workflow requires it. When uncertain, draft the recommendation first.

## Workflow
1. PREPARE - Determine lifecycle mode
   - Select one lifecycle mode and confirm the affected custom skill or reference pack id.
   - Confirm the request is in custom skill lifecycle scope and not `.codex/skills/.system`.
   - Distinguish `primary_skill` from `target_skill`; hardening a skill reads the target but uses `create-skill-pack` as primary.
   - Confirm whether writes, routing registration, metadata, or smoke tests are in scope.
2. ACQUIRE - Read only targeted context
   - Read requested requirements and the target custom skill if updating.
   - Read one or two adjacent user-managed custom skills only if style comparison is needed.
   - Read `context-routing.md` only if routing registration or trigger conflict is in scope.
   - Read `agents/openai.yaml` only if metadata decision is in scope.
   - Do not read `.system`, the full skill library, the full repo, or the full memory bank by default.
3. REASON - Classify role and overlap
   - Classify role as primary, router, execution_modifier, output_modifier, review_gate, memory_operation, or heavy_artifact_generator.
   - Check trigger overlap and whether the request should instead be a skill, reference pack, memory rule, repo `AGENTS.md` update, or one-turn preference.
   - Decide whether the target custom skill should be excluded as primary while being read as an artifact.
4. ACT - Draft or patch artifacts
   - Patch only the required custom `SKILL.md`, `reference.md`, `docs/document.md`, `agents/openai.yaml`, `context-routing.md`, or route smoke tests.
   - Do not patch `.codex/skills/.system`.
5. VERIFY - Run checklist
   - Frontmatter exists; description is under 1024 chars; Routing Card, context targets, Resource/Risk Boundary, Recovery/Context Expansion, Known Limits, Validation, metadata policy, route matrix/smoke tests, trigger guards, host paths, and secret hygiene are aligned.
6. RECOVER - If mismatch found
   - Fix only the mismatched artifact.
   - Do not rewrite all skill files or load all skills.
   - Return to scheduling if the task is not custom skill lifecycle work.
7. FINALIZE - Report lifecycle result
   - Summarize created/updated files, routing decision, metadata decision, smoke tests added or skipped, validation, and remaining manual review.

## Research Cluster Lifecycle Note
For 6.0 Research Cluster work, use source archives such as `codex-research-lifecycle.zip` only as source material. Create narrow user-managed custom skills, add `agents/openai.yaml` with `allow_implicit_invocation: false`, keep reference-only packs under `.codex/references/`, register only cluster-level routing in `context-routing.md`, and put detailed research routes in `research-routing.md`. Do not make this skill responsible for paper search, evidence judgment, hypothesis generation, experiment blueprint decisions, statistical conclusions, or manuscript claims.

## Routing Registration Decision
Update `context-routing.md` only when the new or modified custom skill should be discoverable as a primary, router, modifier, review gate, output modifier, memory operation, or heavy artifact generator; the user explicitly asks to register routing; trigger overlap or smoke-test coverage requires it; or a custom skill is deprecated, superseded, merged, split, or renamed.

Do not update `context-routing.md` when the task is reference-only, typo/editing cleanup, not intended for routing, targets `.system`, or asks only for a proposal rather than patches.

## Agent Metadata Decision
Create or update `agents/openai.yaml` when a user-managed custom skill is created; a custom skill changes role, trigger, or lifecycle scope; or a heavy artifact generator, memory operation, output modifier, review gate, or lifecycle manager needs explicit invocation policy. Skip metadata for reference-only packs, `.system` skills, docs-only notes, one-turn preferences, and repo `AGENTS.md`-only rules. Default custom skill policy is `allow_implicit_invocation: false`; do not enable implicit invocation without explicit user approval and route smoke-test coverage.

## Default Skill Sections
New skill packs should include these AI-facing sections unless the user explicitly asks for a reference-only pack:
- `## Routing Card`
- `## Purpose`
- `## When To Apply`
- `## When Not To Apply`
- `## Workflow`
- `## Resource and Risk Boundary`
- `## Recovery and Context Expansion`
- `## Known Limits`
- `## Validation`
- `## Anti-Patterns`

## Resource and Risk Boundary
- Reads: requested requirements, target custom skill files, selected adjacent custom examples, and routing/metadata files only when in scope.
- Writes: requested custom skill/reference pack files, metadata, routing docs, or smoke tests only within lifecycle scope.
- Tool/process calls: safe validation/listing commands only.
- Network access: none by default.
- Credential access: default deny.
- Generated artifacts: custom skill pack docs, reference docs, optional metadata, and routing notes.
- Destructive actions: deleting skills is out of scope unless explicitly requested and separately approved.
- Required checkpoints: lifecycle mode, custom scope, primary vs target skill, trigger specificity, routing decision, metadata decision, smoke test decision, and validation checklist.

## Recovery and Context Expansion
- If lifecycle mode is unclear, ask one focused question or draft the recommended mode.
- If the target is `.system`, stop lifecycle routing and report that it is app-managed and out of scope.
- If role is unclear, classify the custom skill before writing triggers.
- If existing style is unclear, read one or two adjacent custom skills rather than the full skill library.
- If routing conflict is unclear, read `context-routing.md` route matrix and smoke tests only.
- If validation fails, read only the failing section and checklist before expanding.
- Never recover by loading `.system`, all skills, all memory, or unrelated repo files at once.

## Validation
- Confirm frontmatter has `name` and a specific `description` under 1024 chars.
- Confirm `.codex/skills/.system` was not modified and custom skill scope excludes `.system`.
- Confirm `primary_skill` and `target_skill` are distinguished for hardening/migration/deprecation requests.
- Confirm Routing Card fields and context target subfields are complete.
- Confirm Resource/Risk Boundary, Recovery/Context Expansion, Known Limits, and Validation exist for skill packs.
- Confirm reference-only packs do not create `SKILL.md`, `agents/openai.yaml`, or route registration unless promoted.
- Confirm `agents/openai.yaml` exists or is intentionally skipped, and policy matches routing risk.
- Confirm route matrix and smoke tests are updated or intentionally skipped.
- Confirm route smoke tests use auditable fields such as `target_skill`, `exclude_as_primary_skill`, and `must_not_route_to` where appropriate.
- Confirm no wildcard ambiguity, free-form expected skill names, broad unguarded triggers, hardcoded single-host reusable paths, secrets, or unrelated file changes were introduced.

## Anti-Patterns
- Treating `.codex/skills/.system` as a custom skill lifecycle target.
- Creating a skill for a one-turn preference.
- Updating `context-routing.md` for a skill that has no reusable invocation intent.
- Route-registering a reference-only pack as a skill.
- Turning ordinary code review, bug diagnosis, planning, or memory updates into skill lifecycle work.
- Overloading `SKILL.md` with long templates that belong in `reference.md`.
- Deleting or replacing existing skills during deprecation without explicit approval.

## Known Limits
- Lifecycle contracts do not guarantee runtime triggering; validate against route smoke tests.
- Metadata and route entries can under-activate when conservative policies are used.
- Split, merge, and deprecation decisions may need user review before writes.
- Generated examples may need host/tool adaptation before publication.
