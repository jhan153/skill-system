# Changelog

## 7.2.5

- Added a user-facing, family-grouped Skill Catalog to `README.md` so people can understand the renamed skills by intent without reading the runtime registry first.
- Added `README.ko.md`, a Korean translation of the public README, and linked it from the English README.
- Documented every current skill with a short practical explanation under its family (`analysis`, `design`, `report`, `workflow`, `planning`, `coordination`, `research`, `search`, `memory`, `evaluation`, and `skill_system`).
- Bumped the bundle version label to `7.2.5` across package-facing docs, runtime notes, eval case files, and version-label hygiene checks.

## 7.2.3

- Trimmed the 13 longest skill `description:` fields (`design-frontend`, `report-qualitative`, `plan-spec-curator`, `analysis-codebase`, and the `design-*` surface/gate skills) so the combined skill-listing text fits Claude Code's description budget. Total skill-description text dropped from ~11,862 to ~9,946 chars; all 47 skills now surface for model auto-invocation instead of ~34. Applied on both mirrors and both live installs (`~/.claude/skills`, `~/.codex/skills`); long descriptions are now wrapped in quotes to keep frontmatter YAML valid when they contain punctuation.
- Companion guidance: keep each skill description concise (lead with core use-case plus the do-not-use boundary), consistent with the bundle's progressive-disclosure principle.
- Bumped the bundle version label to `7.2.3` across `README.md`, `TERMS.md`, `.codex/AGENTS.md`, `.claude/CLAUDE.md`, and eval case files; added stale-label detection for `7.2.2`.

## 7.2.2

- Made `check_bundle_hygiene.py` treat git-ignored OS noise (`.DS_Store`, `._*`, `__MACOSX`, `Thumbs.db`) as non-payload: mirror parity and the root `docs/` stray check now ignore those files instead of hard-failing, while real stray files and real mirror content drift still fail (D5).
- Adopted a plan-doc tracking convention (D6): each plan ends with a `Remaining / Next` forward link, and each item is tracked in a single active plan (reconciled the duplicate skill TODOs across the 7.2.0/7.2.1 plans).
- Audited external/user-level alias maps (D7): the live global config still targets pre-rename IDs (e.g., `srq -> /strict-response-quality`); recorded that these update to the renamed IDs after the 7.2.x bundle is installed. No out-of-bundle files were edited.
- Hardened the five lowest-scoring skills (`report-artifact-inventory`, `memory-bank-harness`, `search-router`, `evaluation-usage-tracker`, `memory-bank-ingestion`): added Workflow/Output Contract/decision-tree/schema sections, one `references/*.md` each (output schema, admission decision tree, evidence-lane matrix, usage-summary template, ingestion-packet schema), and positive/negative routing eval cases — on both mirrors. Maturity stays `experimental` (no auto-promotion).
- Bumped the bundle version label to `7.2.2` across `README.md`, `TERMS.md`, `.codex/AGENTS.md`, `.claude/CLAUDE.md`, and eval case files; updated the version-label hygiene check to flag stale `7.2.1` labels.

## 7.2.1

- Added three experimental, explicit-only workflow draft skills on both `.codex` and `.claude`: `workflow-plan-runner` for approved plan/spec/package execution, `workflow-validation` for validation matrices and validation-only runs, and `workflow-recovery` for repeated failure-loop recovery.
- Registered the new workflow skills in both registries, expanded workflow family routing, and added positive/negative routing eval cases for plan/spec execution, validation-only work, and recovery over-trigger prevention.
- Hardened the workflow draft skills after qualitative review: added plan-runner output and fallback contracts, validation risk-tier/check heuristics, recovery repeated-failure thresholds, diagnostic examples, rollback/fallback output alignment, and workflow confusion eval cases.
- Upgraded `report-qualitative` from the old strict-response-quality wrapper into an operational qualitative evaluation report skill, with rubric/template/evidence-mapping/example references, routing/eval cases, and a compact `srq` compatibility mode.
- Hardened `report-qualitative` after qualitative review: compressed trigger metadata, made `srq` compact mode explicit-only, added sensitive-evidence redaction and external-evidence separation, clarified fallback behavior when sibling report skills are unavailable, and added qualitative-diff/negative routing eval cases.
- Set `report-qualitative` to explicit-only (`allow_implicit_invocation: false`) and `experimental` maturity, matching the other report skills' conservative posture until field feedback (F1).
- Added negative routing eval cases: ordinary implementation with no approved plan/spec must not trigger `workflow-plan-runner` (F3); a first-observation failure routes to `analysis-bug`, not `workflow-recovery` (F6).
- Kept the `report_primary` role as-is; it fits the report family's descriptive role convention (`review_gate`/`output_modifier`/`support`) (F5).
- Removed stray `.DS_Store` files so bundle hygiene passes; `.gitignore` already excludes them, and packaging/hygiene runs strip any macOS-regenerated copies (F2).
- Bumped the bundle version label to `7.2.1` across `README.md`, `TERMS.md`, `.codex/AGENTS.md`, `.claude/CLAUDE.md`, and eval case files; updated the version-label hygiene check to flag stale `7.2.0` labels.

## 7.2.0

- Added a `family` grouping layer (Phase A): appended a `family` column to `skill_registry.md` (last column; maturity stays column 3) and a Group Alias Map (display names, interim entries, aliases, cross-family tags) for the 11 families; mirrored to both `.codex`/`.claude`.
- Added a Group Alias Routing section to both `context-routing.md` mirrors (explicit framing-token trigger guard, family->entry table, evidence<->research boundary) plus positive/negative group-routing eval cases with an `expected_family` field.
- Extended `check_bundle_hygiene.py` with `check_family_consistency`, scoped `check_registry` to the Registry section so the Group Alias Map table is not mis-parsed, and allowed `docs/plan/` planning artifacts while still forbidding other root `docs/` runtime content.
- Authored three new experimental, explicit-only skills (Phase B) and registered them on both mirrors: `search-router` (cross-domain evidence routing, role `router`, no writes), `memory-bank-ingestion` (approved closeout-packet promotion into durable memory), and `evaluation-usage-tracker` (metadata-only invocation telemetry).
- Applied the family-stem hard rename (Phase C): renamed 26 skill IDs to match their family (for example `deep-analysis-workflow`->`analysis-router`, `strict-evidence-driven-reporting-workflow`->`workflow-rigor`, `agent-critical-review`->`report-critical`, design family to `design-<noun>`) atomically across skill directories, registry, routing docs, eval cases, and `agents/openai.yaml` on both mirrors. ID-only mechanical rename; `strict-response-quality`->`report-qualitative` did not change behavior (the qualitative-report redefinition stays a separate later change).
- Bumped the bundle version label to `7.2.0` across `README.md`, `TERMS.md`, `.codex/AGENTS.md`, `.claude/CLAUDE.md`, and eval case files; updated the version-label hygiene check accordingly. Re-ran bundle hygiene (PASS) with zero residual old IDs.

## 7.1.2

- Added an implementation completion gate so implementation, bug fix, refactor, UI, and test-repair requests cannot be completed with Markdown-only or plan-only edits unless documentation-only work was explicitly requested.
- Clarified that active plans are implementation input and optional status trackers, not substitutes for source/test/config/build changes.
- Added a runtime eval case for `이 플랜대로 구현해줘` to catch plan-edit-only regressions.
- Synced the implementation completion gate into the Claude mirror (`.claude/context-routing.md`, `runtime_usage_cases.yaml`, `plan-doc-workflow`, `strict-evidence-driven-reporting-workflow`) so Codex and Claude runtimes match.
- Narrowed `design-to-frontend` to explicit-only (`allow_implicit_invocation: false`) until real-use design field feedback justifies implicit invocation; it remains the routed primary for concrete design implementation. Every user-managed skill now declares its implicit-invocation policy.
- Extended `check_bundle_hygiene.py` with `.codex`/`.claude` mirror parity, eval skill-reference integrity, agent-metadata policy-line, role<->risk-profile consistency (routers declare no writes; heavy artifact generators stay non-implicit), Routing Card field-order, and version-label checks (read-only).
- Added a version-label hygiene check and normalized stray `7.1`-style bundle version labels while preserving the historical version timeline.

## 7.1.1

- Recut the bundle as a manual drop-in skill bundle.
- Hardened `rules/default.rules` so network, history rewrite, process termination, debugger, host-specific, and live `.codex` mutation commands are not active allow rules.
- Excluded `.codex/config.toml` and `automations/` from the default bundle by policy.
- Moved app-managed `.system` skills into `optional-system-skills-snapshot/` instead of the default copy payload.
- Added a compact Routing Card to `design-to-frontend` while preserving its implementation workflow.
- Narrowed global task result wording so labels apply to concrete user tasks, not the skill system as a whole.
- Added field feedback examples for design, research, and memory over-trigger cases.
- Extended bundle hygiene checks for risky allow rules, config/automation policy, and core `.system` placement.
- Moved Codex runtime docs, eval cases, and tools under `.codex`.
- Added Claude-side runtime folders under `.claude`.
- Removed root-level runtime dependency on `docs/`, `eval/`, `tools`, `.agent-workflow`, and `harness`.
- Retained the 6.0.2-based skill set.
- Retained research cluster routing.
- Reframed 7.0 coordination, eval, and artifact concepts as lightweight support skills.
- Added `skill_maturity` and `improvement_track` to the runtime registry.
- Added runtime usage eval cases for real-use quality observation.
- Added field feedback templates and guidelines.
- Added a small read-only bundle hygiene checker.
- Added `spec-and-plan-curator` for active-context pruning, plan closeout, memory proposal distillation, and stale plan/archive load-policy decisions.
- Narrowed coordination, eval, artifact, and memory agent metadata to explicit invocation to reduce pre-field over-trigger risk.

## Notes

This cut does not add automatic installation, live runtime mutation, deployment management, signoff workflow, rollback workflow, evidence intake/finality workflow, package-cut scoring, or skill-system finality state.
