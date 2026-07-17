# 9.3.0 Terms

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

The default Codex hook map is empty. Hook adapters are optional project-local evidence/control surfaces and may be enabled only by explicit project/runtime policy.

## project_context_manifest

`project-context.yaml` declares repository-relative locations for optional project Memory Bank, Knowledge Base, plans, skill roots, and named LLM Wikis. A missing entry means that context source is unavailable; it does not authorize parent, home, or adjacent-repository discovery.

## memory_bank_and_knowledge_base

Memory Bank preserves cross-session goals, working rules, recurring mistakes, and proven practices. Knowledge Base preserves accepted project domain, design, algorithm, architecture, code-review, and decision knowledge linked to canonical artifacts. Neither uses maturity, confidence, recurrence, usage, or satisfaction scores.

## llm_wiki

An LLM Wiki is an optional named read-only context source. It is selected explicitly and navigated through its own guide, index, search, graph, or backlink conventions; it is not a default Knowledge Base projection.

## app_managed_system_skills

`.codex/skills/.system` is app-managed. Optional snapshots under `optional-system-skills-snapshot/` are comparison material and require explicit user intent before replacing an existing runtime `.system` folder.

## improvement_track

The next practical work needed to improve a skill after an explicit user report or request.

## runtime_usage_eval

Authored regression examples that can check their declared syntax and routing contract. They are not field-quality evidence.

## field_feedback

A behavior or problem the user explicitly reports in conversation. The bundle does not automatically collect or persist prompts, transcripts, usage, or user identifiers.

## Host-Managed Or External Assets

Runtime config such as `.codex/config.toml`, automations, app-managed system skills, release/signoff processes, rollback operations, and local third-party runtimes are governed by their owning host or workflow.
