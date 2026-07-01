---
name: create-skill-pack
description: Maintains Skill System source skills, role plugin packages, routing metadata, eval smoke tests, and runtime companion payloads. Use when explicitly creating, hardening, migrating, deprecating, registering, or updating reusable Skill System skills or plugin package membership.
---

# Create Skill Pack Lifecycle Manager

## Routing Card
- role: primary
- lifecycle_modes:
  - create_source_skill_pack
  - create_reference_or_runtime_companion_pack
  - harden_existing_skill
  - migrate_existing_skill
  - split_or_merge_skill
  - deprecate_skill
  - register_routing
  - update_agent_metadata
  - update_plugin_membership
  - add_route_smoke_tests
- intent_signature:
  - Skill System source skill creation, skill hardening, skill migration, deprecation, route registration, plugin membership, generated target sync, runtime companion payload update
- use_when:
  - the user explicitly asks to create, update, harden, migrate, deprecate, split, merge, register, package, or add routing tests for a reusable Skill System skill.
  - the task touches `source/skills`, `source/plugins`, generated `.codex` or `.claude` runtime mirrors, generated `plugins/skill-system-*` packages, or local marketplace install guidance.
  - an existing Skill System skill needs lifecycle maintenance across `SKILL.md`, references, docs, `agents/openai.yaml`, routing docs, eval cases, or plugin package membership.
- do_not_use_when:
  - the target is `.codex/skills/.system`, `~/.codex/plugins/cache`, or another app-managed/plugin-cache namespace.
  - the user only wants to execute an existing skill, not modify or package it.
  - the user asks for casual explanation of what skills are.
  - the task is ordinary code review, bug analysis, implementation, planning, memory-only update, repo `AGENTS.md`-only rule, or one-turn formatting preference.
- expected_inputs:
  - lifecycle mode, target skill id, source scope, intended triggers, plugin role package, runtime companion impact, validation needs, routing/metadata intent
- expected_outputs:
  - lifecycle result, source artifacts, plugin membership decision, generated-target decision, routing decision, metadata decision, smoke-test decision, validation checklist
- context_targets:
  must_read:
    - current lifecycle request
    - target `source/skills/{skill-id}` files when updating an existing Skill System skill
  read_if_needed:
    - one or two adjacent source skills with similar role
    - `source/shared/context-routing.md` when routing registration or trigger conflict is in scope
    - `source/shared/docs/skill_registry.md` when registry/family/maturity is in scope
    - `source/plugins/*.yaml` when plugin membership is in scope
    - `agents/openai.yaml` when metadata decision is in scope
  do_not_load_by_default:
    - `.codex/skills/.system`
    - live `$HOME/.codex` or `$HOME/.claude`
    - generated plugin cache directories
    - full skill library
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - targeted source skill files, adjacent examples, routing docs, registry, eval cases, and plugin manifests when needed
  writes:
    - Skill System source files and generated targets only within lifecycle scope
  tools:
    - source generation, focused search, route/eval validation, bundle verification, and bundle hygiene
  sensitive_resources:
    - credentials default deny; local home runtime and plugin cache are deployment targets, not source of truth
- entry_scene:
  - PREPARE

## Purpose
This skill is the lifecycle manager for the Skill System bundle. It creates and hardens reusable skills in the canonical `source/` tree, keeps role plugin packages aligned, and regenerates `.codex`, `.claude`, and `plugins/` targets when source changes require it.

## Source Of Truth
- Edit canonical skill content under `source/skills/{skill-id}/`.
- Edit shared routing, registry, eval cases, and schemas under `source/shared/`.
- Edit platform-specific runtime companion payloads under `source/platform/{codex,claude}/`.
- Edit role plugin membership under `source/plugins/*.yaml`.
- Treat `.codex/`, `.claude/`, and `plugins/skill-system-*` as generated targets. Regenerate them from source instead of hand-editing them, except for emergency inspection.
- Treat live homes such as `~/.codex`, `~/.claude`, and plugin caches as install/deployment targets, not implementation workspaces.

## Lifecycle Scope
- Include: Skill System source skills, references, docs, agent metadata, shared routing/registry/eval files, plugin membership manifests, and generated runtime/plugin targets.
- Exclude: `.codex/skills/.system`, app-managed skills, plugin cache content, host-local config, automations, credentials, memory-only updates, repo `AGENTS.md`-only rules, and one-turn preferences.
- Do not create, harden, migrate, deprecate, route-register, smoke-test, or patch `.system` skills through this skill.
- For existing skill hardening, `create-skill-pack` is the `primary_skill`; the inspected or patched skill is the `target_skill` and must not be treated as the primary execution workflow.

## Lifecycle Modes
- `create_source_skill_pack`: create a new canonical Skill System source skill.
- `create_reference_or_runtime_companion_pack`: create source docs, references, schemas, hooks, tools, or platform runtime companion payload without pretending it is a skill.
- `harden_existing_skill`: add or correct Routing Card, context targets, Resource/Risk Boundary, Recovery/Context Expansion, Known Limits, validation, examples, or metadata for a source skill.
- `migrate_existing_skill`: bring an older skill into the current plugin/source-of-truth style.
- `split_or_merge_skill`: propose splitting overloaded skills or merging near-duplicates; do not delete without explicit approval.
- `deprecate_skill`: mark a skill deprecated/superseded, update routing references, eval cases, plugin membership, and migration notes; do not delete by default.
- `register_routing`: decide whether to update `source/shared/context-routing.md`, registry entries, and route/eval smoke tests.
- `update_agent_metadata`: create or update `source/skills/{skill-id}/agents/openai.yaml`.
- `update_plugin_membership`: add, move, or remove a skill from `source/plugins/{role}.yaml` and regenerate role packages.
- `add_route_smoke_tests`: add or update routing/eval cases for created or modified skills.

## Pack Types
- Source Skill Pack: `source/skills/{skill-id}/SKILL.md` plus optional `reference.md`, `docs/document.md`, `references/`, and `agents/openai.yaml`.
- Role Plugin Package: generated `plugins/skill-system-{role}/` membership from `source/plugins/{role}.yaml`.
- Runtime Companion Payload: shared or platform-specific hooks, tools, rules, schemas, evals, docs, and routing files under `source/shared/` or `source/platform/`.
- Local Install Target: live `~/.codex`, `~/.claude`, or plugin cache content. Inspect only when the user explicitly asks to deploy or diagnose installation.

## Output Contract
When creating or updating a source skill, return only the sections needed:
- `lifecycle_mode`
- `primary_skill`
- `target_skill`
- `affected_skill_id`
- `source_files_to_create`
- `source_files_to_update`
- `plugin_membership_decision`
- `generated_targets_to_sync`
- `routing_decision`
- `agent_metadata_decision`
- `smoke_test_decision`
- `risk_boundary`
- `validation_checklist`
- `follow_up_review`

Do not silently create routing entries, metadata, plugin membership, generated targets, or smoke tests unless the user requested lifecycle registration or the workflow requires it. When uncertain, draft the recommendation first.

## Template Handling
- Templates in `reference.md` are scaffolding, not final answers.
- Do not paste dummy angle-bracket placeholders into user-facing output or generated artifacts.
- For analysis/review requests, report concrete gaps instead of dumping entire templates.
- For creation/migration patches, replace every placeholder with concrete task-specific content or omit the field with an explicit reason.
- Before finalizing source changes, search changed non-reference artifacts for unresolved placeholders.

## Workflow
1. PREPARE - Determine lifecycle mode
   - Select one lifecycle mode and confirm the affected source skill, reference/runtime payload, or plugin package.
   - Confirm the request is in Skill System lifecycle scope and not app-managed `.system` or plugin-cache content.
   - Distinguish `primary_skill` from `target_skill`; hardening a skill reads the target but uses `create-skill-pack` as primary.
   - Confirm whether writes, routing registration, plugin membership, generated sync, metadata, or smoke tests are in scope.
2. ACQUIRE - Read targeted context
   - Read requested requirements and the target `source/skills/{skill-id}` files when updating.
   - Read one or two adjacent source skills only if style comparison is needed.
   - Read `source/shared/context-routing.md` only if routing registration or trigger conflict is in scope.
   - Read `source/shared/docs/skill_registry.md` only if family, maturity, or registry language is in scope.
   - Read `source/plugins/*.yaml` only if plugin membership is in scope.
   - Do not read live home runtime, plugin caches, `.system`, full skill library, full repo, or full memory bank by default.
3. REASON - Classify role and overlap
   - Classify role as primary, router, execution_modifier, output_modifier, review_gate, memory_operation, or heavy_artifact_generator.
   - Check trigger overlap and whether the request should instead be a source skill, runtime companion payload, memory rule, repo `AGENTS.md` update, or one-turn preference.
   - Decide whether the target skill should be excluded as primary while being read as an artifact.
4. ACT - Draft or patch artifacts
   - Patch only required source skill files, references, docs, metadata, routing docs, registry entries, eval cases, plugin membership manifests, or runtime companion source files.
   - Regenerate runtime/plugin targets from source when source changes require it.
   - Do not hand-patch `.codex/skills/.system`, plugin cache files, or host-local config.
5. VERIFY - Run checklist
   - Confirm frontmatter, Routing Card, context targets, risk boundary, recovery, limits, output contract, metadata policy, route/eval cases, plugin membership, generated targets, placeholder cleanup, host paths, and secret hygiene.
6. RECOVER - If mismatch found
   - Fix only the mismatched artifact.
   - Do not rewrite all skill files or load all skills.
   - Return to scheduling if the task is not lifecycle work.
7. FINALIZE - Report lifecycle result
   - Summarize source files changed, generated targets synced, plugin membership, routing/metadata/smoke decisions, validation, and remaining manual review.

## Generation And Validation
- Runtime targets: `python3 source/tools/generate_targets.py --target runtime`.
- Plugin packages: `python3 source/tools/generate_targets.py --target plugins`.
- Core verification: `python3 source/platform/codex/tools/verify_bundle.py --root . --profile core --format text`.
- Bundle hygiene from the project parent: `python3 tools/check_bundle_hygiene.py Skill-System`.
- Use focused route/eval validation when routing or eval cases changed.

## Cross-Skill Boundaries
- `workflow-source-maintenance` owns ordinary code cleanup; this skill owns Skill System skill/package lifecycle cleanup.
- `workflow-implementation`, `workflow-bug-fix`, and `workflow-refactor-safely` own application code changes.
- `evaluation-harness` owns eval-case quality review after route cases exist.
- `evaluation-usage-tracker` owns metadata-only invocation summary analysis, not lifecycle edits.
- `report-critical` may review a draft but does not own skill lifecycle writes.
- System-provided `skill-creator` may own platform-specific personal skill creation when explicitly requested and exposed by the runtime; this skill owns the Skill System bundle.

## Resource and Risk Boundary
- Reads: targeted source skill files, selected adjacent examples, routing/registry/eval files, plugin manifests, and generation tools only when in scope.
- Writes: Skill System source files and generated targets only within lifecycle scope.
- Tool/process calls: generation, validation, focused search, and hygiene commands only.
- Network access: none by default.
- Credential access: default deny.
- Generated artifacts: `.codex`, `.claude`, and `plugins` targets generated from source.
- Destructive actions: deleting skills or removing plugin membership is out of scope unless explicitly requested and separately approved.
- Required checkpoints: lifecycle mode, source scope, primary vs target skill, trigger specificity, plugin membership, generated-target decision, routing decision, metadata decision, smoke test decision, and validation checklist.

## Recovery and Context Expansion
- If lifecycle mode is unclear, ask one focused question or draft the recommended mode.
- If the target is `.system` or plugin cache content, stop lifecycle routing and report that it is app-managed/deployment state.
- If role is unclear, classify the source skill before writing triggers.
- If existing style is unclear, read one or two adjacent source skills rather than the full skill library.
- If routing conflict is unclear, read `source/shared/context-routing.md` and relevant eval cases only.
- If validation fails, read only the failing section and checklist before expanding.
- Never recover by loading live home runtime, plugin caches, `.system`, all skills, all memory, or unrelated repo files at once.

## Validation
- Confirm frontmatter has `name` and a specific `description` under 1024 chars.
- Confirm app-managed `.system`, live home runtime, host-local config, and plugin caches were not modified.
- Confirm `primary_skill` and `target_skill` are distinguished for hardening/migration/deprecation requests.
- Confirm Routing Card fields and context target subfields are complete.
- Confirm Resource/Risk Boundary, Recovery/Context Expansion, Known Limits, Validation, and Output Contract exist for source skill packs.
- Confirm runtime companion payloads are not route-registered as skills unless a real skill is created.
- Confirm `agents/openai.yaml` exists or is intentionally skipped, and source-only policy fields match routing risk.
- Confirm plugin membership in `source/plugins/*.yaml` is updated or intentionally skipped.
- Confirm route matrix, registry, and eval smoke tests are updated or intentionally skipped.
- Confirm route smoke tests use auditable fields such as `target_skill`, `exclude_as_primary_skill`, and `must_not_route_to` where appropriate.
- Confirm generated `.codex`, `.claude`, and `plugins` targets were synced when source changes require it.
- Confirm no unresolved dummy placeholders, wildcard ambiguity, free-form expected skill names, broad unguarded triggers, hardcoded single-host reusable paths, secrets, or unrelated file changes were introduced.

## Anti-Patterns
- Treating `.codex/skills/.system`, live `~/.codex`, live `~/.claude`, or plugin cache content as source.
- Creating a skill for a one-turn preference.
- Updating routing docs for a skill that has no reusable invocation intent.
- Route-registering runtime companion payload as a skill.
- Turning ordinary code review, bug diagnosis, planning, or memory updates into skill lifecycle work.
- Copying dummy template placeholders into final artifacts.
- Hand-editing generated `.codex`, `.claude`, or `plugins` targets while leaving source stale.
- Deleting or replacing existing skills during deprecation without explicit approval.

## Known Limits
- Lifecycle contracts do not guarantee runtime triggering; validate against route and eval smoke tests.
- Plugin manifests keep only the fields supported by each host schema; source agent metadata may contain richer internal policy fields than plugin packages expose.
- Metadata and route entries can under-activate when conservative policies are used.
- Split, merge, deprecation, and plugin membership decisions may need user review before writes.
- Generated examples may need host/tool adaptation before publication.
