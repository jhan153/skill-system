# 7.2.3 Terms

## version_cut

A version cut is a new manual bundle snapshot. It does not mean the skill system is finished, approved, or globally correct.

## manual_drop_in_skill_bundle

A manual drop-in skill bundle is copied by the user. It does not mutate live settings, install itself, or manage the user's runtime.

## runtime_canonical

The location that an agent should treat as the source of runtime guidance.

- Codex: `.codex/docs`, `.codex/eval`, `.codex/tools`
- Claude: `.claude/docs`, `.claude/eval`
- Root: packaging documents only

## runtime_config_policy

The bundle intentionally excludes `.codex/config.toml` so a manual copy does not overwrite the user's existing runtime config.

`automations/` are also excluded from 7.2.3 core because this bundle is not an automatic runtime loop.

## app_managed_system_skills

`.codex/skills/.system` is app-managed. It is not part of the default copy payload. A snapshot may be provided under `optional-system-skills-snapshot/` for manual review, but it should not overwrite an existing runtime `.system` folder unless the user explicitly chooses that.

## skill_maturity

A conservative label for how ready a skill is in real use.

Allowed values:

- `skeleton`
- `usable`
- `field_tuned`
- `experimental`
- `deprecated`

## improvement_track

The next practical work needed to improve a skill. It can mention routing precision, better examples, context trimming, output shape, or field feedback.

## runtime_usage_eval

Usage examples that help observe skill behavior in real tasks. They are not package approval, release scoring, or proof that a skill is complete.

## field_feedback

Human notes from real use. Feedback can update maturity, routing examples, negative cases, docs, or skill text in the next version cut.

## bundle_hygiene_check

A small read-only sanity check for structure and obvious packaging mistakes. It must not install, fix, generate reports, mutate live settings, or score real skill quality.

## Removed From 7.2.3 Core

7.2.3 core excludes automatic install flow, promotion flow, release flow, signoff workflow, rollback flow, evidence intake flow, evidence closure flow, package-cut scoring, runtime config replacement, automations, default `.system` payload, and skill-system finality modeling.
