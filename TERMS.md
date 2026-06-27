# 8.5.0 Terms

## version_cut

A version cut is a named snapshot of Skill System artifacts for a compatibility line. It records the current structure, guidance, and validation targets for that line.

## skill_system_bundle

A Skill System bundle is a portable set of skills, docs, eval cases, tools, and integration source. Host runtime configuration remains under the user's local policy and explicit choices.

## runtime_canonical

The location that an agent should treat as the source of runtime guidance.

- Codex: `.codex/docs`, `.codex/eval`, `.codex/tools`
- Claude: `.claude/docs`, `.claude/eval`
- Root: packaging documents only

## runtime_config_policy

Runtime configuration and automation assets, including `.codex/config.toml` and `automations`, are host-managed. Preserve existing local settings unless the user explicitly chooses to replace them.

The Codex hook files are project-local evidence/control surfaces. They run under project trust, hook trust, sandboxing, approval policy, and rules.

## app_managed_system_skills

`.codex/skills/.system` is app-managed. Optional snapshots under `optional-system-skills-snapshot/` are comparison material and require explicit user intent before replacing an existing runtime `.system` folder.

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

Usage examples that help observe skill behavior in real tasks and collect improvement evidence.

## field_feedback

Human notes from real use. Feedback can update maturity, routing examples, negative cases, docs, or skill text in the next version cut.

## Host-Managed Or External Assets

Runtime config such as `.codex/config.toml`, automations, app-managed system skills, release/signoff processes, rollback operations, and local third-party runtimes are governed by their owning host or workflow.
