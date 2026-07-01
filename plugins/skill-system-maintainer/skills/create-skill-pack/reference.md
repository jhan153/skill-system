# create-skill-pack Reference

## Overview
Use this reference for Skill System bundle lifecycle work: source skill creation, hardening, migration, metadata, plugin package membership, routing registration, eval smoke tests, generated target sync, and deprecation notes.

The canonical implementation workspace is `source/`. Generated `.codex/`, `.claude/`, and `plugins/` outputs mirror source and should not drift.

## Scope Guard
- Include: `source/skills/*`, `source/shared/*`, `source/platform/{codex,claude}/*`, and `source/plugins/*.yaml` when the user asks for Skill System skill/package lifecycle work.
- Exclude: `.codex/skills/.system/**`, live `$HOME/.codex`, live `$HOME/.claude`, plugin caches, host-local config, automations, credentials, repo `AGENTS.md`-only rules, memory-only updates, and one-turn preferences.
- Do not audit, patch, migrate, deprecate, route-register, smoke-test, or add metadata to `.system` skills through `create-skill-pack`.
- Existing skill hardening uses `create-skill-pack` as `primary_skill`; the inspected or patched skill is `target_skill`.

## Lifecycle Mode Table
| Mode | Use when | Writes |
| --- | --- | --- |
| `create_source_skill_pack` | A reusable Skill System behavior needs a new canonical skill. | `source/skills/{skill-id}/` and optional registry/routing/eval/plugin membership. |
| `create_reference_or_runtime_companion_pack` | Docs, schemas, hooks, tools, or platform runtime files are needed without a new skill. | `source/shared/` or `source/platform/{codex,claude}/`. |
| `harden_existing_skill` | A source skill lacks routing, risk, recovery, limits, validation, output contract, examples, or metadata alignment. | Targeted source sections/files only. |
| `migrate_existing_skill` | An older skill should match the current source/plugin architecture. | Targeted migration edits and generated target sync. |
| `split_or_merge_skill` | Skills are overloaded or duplicate. | Proposal first; no deletion by default. |
| `deprecate_skill` | A skill is superseded or should stop routing. | Deprecation notes, routing/eval updates, and plugin membership changes when approved. |
| `register_routing` | A skill should enter the route matrix, registry, or smoke tests. | `source/shared/context-routing.md`, `source/shared/docs/skill_registry.md`, and eval cases. |
| `update_agent_metadata` | Skill metadata is missing or stale. | `source/skills/{skill-id}/agents/openai.yaml`. |
| `update_plugin_membership` | A skill should move between role packages or be added to one. | `source/plugins/{role}.yaml`, then generated `plugins/`. |
| `add_route_smoke_tests` | Trigger behavior needs regression checks. | `source/shared/eval/*.yaml` and route smoke tests. |

## Pack Type Decision Table
| User intent | Pack type |
| --- | --- |
| Reusable Skill System behavior with triggers | Source Skill Pack under `source/skills/{skill-id}/` |
| Role package distribution | Plugin membership in `source/plugins/{role}.yaml` |
| Runtime hooks/tools/rules/schemas/docs/eval | Runtime Companion Payload under `source/shared/` or `source/platform/` |
| Local home deployment | Install/mirror operation, not source lifecycle, unless explicitly requested |
| One-turn preference | No pack |
| Project-specific convention | Repo `AGENTS.md` or project docs |
| Persistent preference/rule | Memory operation, not this skill |
| `.system` or plugin cache request | Out of scope; do not patch or lifecycle-manage |

## Role Decision Table
| Role | Owns |
| --- | --- |
| `primary` | Main task execution or lifecycle operation |
| `router` | Chooses a primary skill, no writes |
| `execution_modifier` | Evidence/risk/validation rigor during implementation |
| `output_modifier` | Final presentation shape |
| `review_gate` | QA, blocker, risk, validation review |
| `memory_operation` | Persistent memory mutation/inspection |
| `heavy_artifact_generator` | Explicit report/package artifacts only |

## Template Handling Rule
The templates below are scaffolding for patches, not content to paste into final answers.

- Never leave angle-bracket placeholders, blank dummy fields, `TODO`, `TBD`, or `placeholder` text in generated source artifacts.
- For analysis/review requests, report concrete findings and cite files/lines instead of outputting the whole template.
- For creation/migration requests, replace placeholders with task-specific values or remove the field with an explicit skip reason.
- For route/eval examples, use realistic user requests and real skill ids; use `expected_route_class` when there is no single primary skill.
- Before finalizing, run a focused placeholder search over changed non-reference files.

Suggested focused check:

```bash
rg -n '<[^>]+>|TODO|TBD|FIXME|placeholder|dummy|더미' <changed-files>
```

Do not apply that check blindly to this `reference.md`; the template section intentionally contains placeholders.

## Trigger Guard Examples
- Good: `새 Skill System source skill pack 만들어줘`, `기존 스킬 Routing Card 보강해줘`, `이 스킬 deprecated 처리하고 plugin membership도 정리해줘`.
- Guard: `.system 스킬도 보강해줘` is out of custom lifecycle scope.
- Guard: `스킬이란 뭐야?` is conceptual explanation, not lifecycle work.
- Guard: `analysis-bug로 분석해줘` executes that skill; it does not update the skill pack.
- Guard: `기존 analysis-bug 스킬 보강해줘` reads `analysis-bug` as `target_skill`; it does not execute it as `primary_skill`.
- Guard: `이번 답변만 짧게 해줘` is one-turn preference, not memory or skill creation.

## Generation Flow
After source edits:

```bash
python3 source/tools/generate_targets.py --target runtime
python3 source/tools/generate_targets.py --target plugins
```

Then validate:

```bash
python3 source/platform/codex/tools/verify_bundle.py --root . --profile core --format text
```

From the project parent, also run:

```bash
python3 tools/check_bundle_hygiene.py Skill-System
```

## Routing Registration Decision
Update `source/shared/context-routing.md` and relevant eval cases only when:
- the new or modified skill should be discoverable as a primary, router, modifier, review gate, output modifier, memory operation, or heavy artifact generator.
- the user explicitly asks to register routing.
- trigger overlap or smoke-test coverage requires a route update.
- a skill is deprecated, superseded, merged, split, or renamed.

Do not update routing when:
- the task is runtime companion only.
- the change is typo/editing cleanup.
- the skill is not intended for routing.
- the target is `.system` or plugin cache content.
- the user asks only for a proposal and not patches.

## Agent Metadata Decision
Create or update `source/skills/{skill-id}/agents/openai.yaml` when:
- a source skill is created.
- a skill changes role, trigger, lifecycle scope, or plugin membership.
- a heavy artifact generator, memory operation, output modifier, review gate, router, or lifecycle manager needs explicit invocation policy.

Default source policy for conservative skills:

```yaml
policy:
  invocation_surface: explicit_procedure
  allow_implicit_invocation: false
  may_own_execution: true
```

Use `support_only` and `may_own_execution: false` only when the skill never owns a user request. If route/eval cases expect the skill as `expected_primary_skill`, it should not be marked support-only.

Codex plugin packages sanitize source-only policy fields and keep only host-supported fields such as `allow_implicit_invocation`. That generated difference is expected.

## Agent Metadata Template
```yaml
interface:
  display_name: "<Display Name>"
  short_description: "<Specific purpose>"
  default_prompt: |
    Use $<skill-id> only when <specific explicit intent>.

    Do not activate for <nearby non-goals>.

policy:
  invocation_surface: explicit_procedure
  allow_implicit_invocation: false
  may_own_execution: true
```

## Route Smoke Test Template
```yaml
- request: "<realistic user request>"
  expected_primary_skill: "<skill-id or null>"
  expected_mode: "<lifecycle mode if relevant>"
  target_skill: "<skill being inspected or modified, if any>"
  expected_attachments: []
  must_read:
    - "<specific file/doc required by this route>"
  read_if_needed:
    - "<one-layer expansion target>"
  must_not_route_to:
    - "<skill that should not be selected or attached>"
  exclude_as_primary_skill:
    - "<target skill that may be read but must not own execution>"
  expected_default_exclude:
    - "<context or workflow excluded by default>"
  expected_route_class: "<class when no single primary skill is expected>"
  notes: "<ambiguity or guard>"
```

## Deprecation Note Template
```md
## Deprecation
- Status: deprecated | superseded
- Replacement: `<skill-id>`
- Reason:
- Migration path:
- Routing impact:
- Plugin membership impact:
- Do not delete without explicit user approval.
```

## Migration Note Template
```md
## Migration Note
- Source skill:
- Target style/version:
- Changed sections:
- Routing changes:
- Metadata changes:
- Plugin membership changes:
- Generated targets synced:
- Smoke tests added:
- Remaining manual review:
```

## Routing Card Template
```md
## Routing Card
- role: primary | router | execution_modifier | output_modifier | review_gate | memory_operation | heavy_artifact_generator
- intent_signature:
  - <specific trigger or intent>
- use_when:
  - <when this skill owns the task>
- do_not_use_when:
  - <nearby task this skill should not steal>
- expected_inputs:
  - <required inputs>
- expected_outputs:
  - <deliverables>
- context_targets:
  must_read:
    - <minimal required context>
  read_if_needed:
    - <one-layer expansion target>
  do_not_load_by_default:
    - full repo
    - full memory bank
- risk_profile:
  reads:
    - <read scope>
  writes:
    - <write scope or none>
  tools:
    - <tool/process scope>
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE
```

## Validation Checklist
- [ ] Canonical edits were made under `source/`, not directly in live home or plugin cache.
- [ ] `.codex/skills/.system` was not modified, counted, or treated as removable OS/editor residue.
- [ ] Frontmatter has `name` and specific `description` under 1024 chars.
- [ ] `primary_skill` and `target_skill` are distinguished for hardening/migration/deprecation requests.
- [ ] `SKILL.md` is compact and links to `reference.md`, `references/`, or `docs/document.md` for long material.
- [ ] Routing Card has all standard fields.
- [ ] `context_targets` include `must_read`, `read_if_needed`, and `do_not_load_by_default`.
- [ ] Resource/Risk Boundary and Recovery/Context Expansion exist.
- [ ] Known Limits, Validation, Anti-Patterns, and Output Contract exist for skill packs.
- [ ] Runtime companion payloads do not create `SKILL.md`, metadata, or route registration unless promoted into a real skill.
- [ ] Agent metadata exists or has an explicit skip reason.
- [ ] Plugin membership exists or has an explicit skip reason.
- [ ] Route matrix, registry, and eval smoke tests are updated or intentionally skipped.
- [ ] Smoke tests use auditable fields such as `target_skill`, `exclude_as_primary_skill`, and `must_not_route_to` where appropriate.
- [ ] Wildcard expectations are avoided unless explicitly documented.
- [ ] Free-form expected skill names are replaced with `expected_route_class` where needed.
- [ ] Broad triggers are guarded.
- [ ] Reusable examples avoid hardcoding one host path.
- [ ] Generated runtime/plugin targets were synced when source changes require it.
- [ ] No unresolved dummy placeholders, secrets, tokens, credentials, or private values are added.

## Anti-Patterns
- Treating `.system`, live home runtime, or plugin cache content as source.
- Generic descriptions such as "helps with docs".
- Missing validation section or output contract.
- Docs and `SKILL.md` describing different behavior.
- Broad trigger aliases without guards.
- Full library scans for a single skill update.
- Silent route matrix, metadata, plugin membership, or generated-target edits when lifecycle registration was not requested.
- Route-registering runtime companion payload as a skill.
- Deleting skills during migration/deprecation without explicit approval.
