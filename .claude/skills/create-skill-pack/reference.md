# create-skill-pack Reference

## Overview
Use this reference for user-managed Codex custom skill lifecycle work: creation, hardening, migration, metadata, routing registration, smoke tests, and deprecation notes. `.codex/skills/.system` is Codex app-managed and outside this lifecycle.

## Scope Guard
- Include: `.codex/skills/*` user-managed custom skills, excluding `.system`.
- Exclude: `.codex/skills/.system/**`, system-managed markers, app-managed skill files, repo `AGENTS.md`-only rules, memory-only updates, and one-turn preferences.
- Do not audit, patch, migrate, deprecate, route-register, smoke-test, or add metadata to `.system` skills through `create-skill-pack`.
- Existing skill hardening uses `create-skill-pack` as `primary_skill`; the inspected or patched custom skill is `target_skill`.

## Skill Lifecycle Mode Table
| Mode | Use when | Writes |
| --- | --- | --- |
| `create_new_skill_pack` | A reusable custom Codex behavior needs a new skill. | New custom skill directory and optional metadata. |
| `create_reference_pack` | Only reusable docs/templates are needed. | `.codex/references/{reference-pack-id}/reference.md` and `docs/document.md` only. |
| `harden_existing_skill` | A custom skill lacks routing, risk, recovery, limits, validation, or metadata alignment. | Targeted sections/files only. |
| `migrate_existing_skill` | A legacy custom skill should match current Routing Card style. | Targeted migration edits and notes. |
| `split_or_merge_skill` | Custom skills are overloaded or duplicate. | Proposal first; no deletion by default. |
| `deprecate_skill` | A custom skill is superseded or should stop routing. | Deprecation/migration notes and routing references. |
| `register_routing` | A custom skill should enter the route matrix or smoke tests. | `context-routing.md` only. |
| `update_agent_metadata` | Custom skill metadata is missing or stale. | `agents/openai.yaml`. |
| `add_route_smoke_tests` | Trigger behavior needs regression checks. | `context-routing.md` smoke tests. |

## Pack Type Decision Table
| User intent | Pack type |
| --- | --- |
| Reusable behavior with triggers | Codex Skill Pack under `.codex/skills/{skill-id}/` with `SKILL.md` |
| Templates/reference only | Reference Pack under `.codex/references/{reference-pack-id}/` |
| Temporary reference under `skills/` | No `SKILL.md`, no metadata, no route registration |
| One-turn preference | No pack |
| Project-specific convention | Repo `AGENTS.md` or project docs |
| Persistent preference/rule | Memory operation, not this skill |
| `.system` skill request | Out of scope; do not patch or lifecycle-manage |

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

## Trigger Guard Examples
- Good: `새 Codex 스킬 팩 만들어줘`, `기존 스킬 Routing Card 보강해줘`, `이 스킬 deprecated 처리해줘`.
- Guard: `.system 스킬도 보강해줘` is out of custom lifecycle scope.
- Guard: `스킬이란 뭐야?` is conceptual explanation, not lifecycle work.
- Guard: `analysis-bug로 분석해줘` executes that skill; it does not update the skill pack.
- Guard: `기존 analysis-bug 스킬 보강해줘` reads `analysis-bug` as `target_skill`; it does not execute it as `primary_skill`.
- Guard: `이번 답변만 짧게 해줘` is one-turn preference, not memory or skill creation.

## Routing Registration Decision
Update `context-routing.md` only when:
- the new or modified custom skill should be discoverable as a primary, router, modifier, review gate, output modifier, memory operation, or heavy artifact generator.
- the user explicitly asks to register routing.
- trigger overlap or smoke-test coverage requires a route update.
- a custom skill is deprecated, superseded, merged, split, or renamed.

Do not update `context-routing.md` when:
- the task is reference-only.
- the change is only typo/editing cleanup.
- the skill is not intended for routing.
- the target is `.system`.
- the user asks only for a proposal and not patches.

## Agent Metadata Decision
Create or update `agents/openai.yaml` when:
- a user-managed custom skill is created.
- a custom skill changes role, trigger, or lifecycle scope.
- a heavy artifact generator, memory operation, output modifier, review gate, or lifecycle manager needs explicit invocation policy.

Do not create metadata when:
- the pack is reference-only.
- the target is `.system`.
- the change is docs-only.
- the request is a one-turn preference.
- the request belongs only in repo `AGENTS.md`.

Default policy for user custom skills:
```yaml
policy:
  allow_implicit_invocation: false
```
Do not enable implicit invocation without explicit user approval and route smoke-test coverage.

## Agent Metadata Template
```yaml
interface:
  display_name: "<Display Name>"
  short_description: "<Specific purpose>"
  default_prompt: |
    Use $<skill-id> only when <specific explicit intent>.

    Do not activate for <nearby non-goals>.

policy:
  allow_implicit_invocation: false
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
- [ ] `.codex/skills/.system` was not modified, counted, or treated as removable OS/editor residue.
- [ ] Custom skill counts and audits exclude `.system`.
- [ ] Frontmatter has `name` and specific `description` under 1024 chars.
- [ ] `primary_skill` and `target_skill` are distinguished for hardening/migration/deprecation requests.
- [ ] `SKILL.md` is compact and links to `reference.md`/`docs/document.md` for long material.
- [ ] Routing Card has all standard fields.
- [ ] `context_targets` include `must_read`, `read_if_needed`, and `do_not_load_by_default`.
- [ ] Resource/Risk Boundary and Recovery/Context Expansion exist.
- [ ] Known Limits and Validation sections exist for skill packs.
- [ ] Reference-only packs do not create `SKILL.md`, metadata, or routing registration unless promoted.
- [ ] Agent metadata exists or has an explicit skip reason.
- [ ] Route matrix and smoke tests are updated or intentionally skipped.
- [ ] Smoke tests use auditable fields such as `target_skill`, `exclude_as_primary_skill`, and `must_not_route_to` where appropriate.
- [ ] Wildcard expectations are avoided unless explicitly documented.
- [ ] Free-form expected skill names are replaced with `expected_route_class` where needed.
- [ ] Broad triggers are guarded.
- [ ] Reusable examples avoid hardcoding one host path.
- [ ] No secrets, tokens, credentials, or private values are added.

## Anti-Patterns
- Treating `.system` as a user custom skill.
- Generic descriptions such as "helps with docs".
- Missing validation section.
- Docs and `SKILL.md` describing different behavior.
- Broad trigger aliases without guards.
- Full library scans for a single skill update.
- Silent route matrix or metadata edits when lifecycle registration was not requested.
- Route-registering a reference-only pack as a skill.
- Deleting skills during migration/deprecation without explicit approval.

## Research Cluster Source Decomposition
- Treat broad source archives as source material, not installable monolithic skills.
- Do not create `.codex/skills/codex-research-lifecycle/`.
- Split evidence search, synthesis, ideation, blueprint, scaffold, analysis, writing, and peer review into narrow skills.
- Add `agents/openai.yaml` with `allow_implicit_invocation: false` for every new custom skill.
- Put reference-only packs such as speech-enhancement research under `.codex/references/`, not `.codex/skills/`.
- Keep `.codex/context-routing.md` thin and put detailed research routes in `.codex/research-routing.md`.
- Do not use `create-skill-pack` to decide actual research claims, citations, hypotheses, experiment design, statistical conclusions, or manuscript content.
