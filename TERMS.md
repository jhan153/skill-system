# 10.2.3 Terms

## version_cut

A version cut is a named snapshot of Skill System artifacts for a compatibility line. It records the current structure, guidance, and validation targets for that line.

## skill_system_bundle

A Skill System bundle is a portable set of skills, docs, schemas, tools, and integration source. Host runtime configuration remains under the user's local policy and explicit choices.

## runtime_canonical

The location that an agent should treat as the source of runtime guidance.

- Codex: `.codex/AGENTS.md`, `.codex/docs`, `.codex/bin`
- Claude: `.claude/CLAUDE.md`, `.claude/docs`, `.claude/bin`
- Grok: `.grok/AGENTS.md`, `.grok/docs`, `.grok/bin` (common Go harness; Orca owns lifecycle)
- Antigravity: `.antigravity/GEMINI.md`, `.antigravity/docs`, `.antigravity/bin` (staged common Go harness;
  deployment maps it to the host's actual global root and Orca owns lifecycle)
- Root: packaging documents only

## runtime_config_policy

Runtime configuration and automation assets, including `.codex/config.toml` and `automations`, are host-managed. Preserve existing local settings unless the user explicitly chooses to replace them.

Codex `rules/default.rules` is also host/user-managed because Codex appends persistent TUI
approvals there. Skill System owns only `rules/skill-system.rules`; generation and installation
must preserve `default.rules` and its backups.

The default Codex hook map keeps eight lifecycle events and invokes the generated Go harness directly on POSIX. Windows uses one bounded environment-path resolver so custom `CODEX_HOME` and the default home both work. Hook registration, live home installation, and project-local overrides remain under explicit runtime policy; plugins do not add a duplicate base hook map.

## project_context_manifest

`project-context.yaml` declares manifest-relative locations, or exact explicitly approved absolute locations, for optional project Memory Bank, Knowledge Base, plans, skill roots, and named LLM Wikis. A missing entry means that context source is unavailable; it does not authorize parent, home, or adjacent-repository discovery. Knowledge operations bind `knowledge_root` and `knowledge_index` once and consume those variables instead of a fixed directory. Explicit `manifest-init`, `bootstrap`, and `doctor` modes keep declaration, target existence, and content initialization separate.

## workflow_topology

Non-executing navigation composed from existing authorities. Work Horizon decides persistence and artifact altitude, Planning State admits transitions for persisted planning artifacts, and host routing retains the current-turn owner. It is not a registry table, skill chain, or orchestrator.

## delivery_shape

The batching form selected only when execution decomposition is needed: `single_batch`, `vertical_slice`, `migration_sequence`, or `evidence_unit`. The choice follows actual dependency and observation paths and does not require TDD or irrelevant architectural layers.

## memory_bank_and_knowledge_base

Memory Bank preserves cross-session goals, working rules, recurring mistakes, and proven practices. Knowledge Base preserves accepted project domain, design, algorithm, architecture, code-review, and decision knowledge as current Markdown snapshots with typed links, semantic revisions, and source-traced observations. It may derive separate recurrence dimensions from explicit events and provenance roots; neither store uses maturity, confidence, importance, usage, popularity, satisfaction, or composite recurrence scores.

## llm_wiki

An LLM Wiki is an optional named read-only context source. It is selected explicitly and navigated through its own guide, index, search, graph, or backlink conventions; it is not a default Knowledge Base projection.

## app_managed_system_skills

`.codex/skills/.system` is app-managed. Optional snapshots under `optional-system-skills-snapshot/` are comparison material and require explicit user intent before replacing an existing runtime `.system` folder.

## improvement_track

The next practical work needed to improve a skill after an explicit user report or request.

## runtime_usage_eval

Authored regression examples that can check their declared syntax and routing contract. They are not field-quality evidence.

## implicit_invocation

Model-visible selection of a skill from clear natural-language intent without requiring an explicit skill alias. It does not grant write, side-effect, persistence, external-state, or lifecycle authority beyond the user's request and the selected skill's guardrails.

## workflow_prototype

One isolated runnable artifact built to discriminate an explicit unresolved UI, interaction, state, or logic question before production implementation. It is decision evidence rather than production proof and remains runnable until the decision owner observes it or an authorized cleanup trigger fires.

## field_feedback

A behavior or problem the user explicitly reports in conversation. The bundle does not automatically collect or persist prompts, transcripts, usage, or user identifiers.

## Host-Managed Or External Assets

Runtime config such as `.codex/config.toml`, automations, app-managed system skills, release/signoff processes, rollback operations, and local third-party runtimes are governed by their owning host or workflow.
