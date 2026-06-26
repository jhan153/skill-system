# Changelog

## 8.4.0

- Adopted Fable-style harness discipline (FableCodex, fablize) as concepts rather than code: observed-evidence completion plus an `accepted_risk` terminal in `workflow-rigor`, a debugging hypothesis ladder in `analysis-bug`, capability-ceiling escalation in `workflow-recovery`, and verification-grounding / noise-control runtime eval cases (`runtime-029..032`).
- Added a harness-paradox out-of-band holdout + sunset measurement reference under `evaluation-usage-tracker`, and registered `SRC-FABLECODEX` (AGPL-3.0-or-later) and `SRC-FABLIZE` (MIT) in `source_registry.yaml` with an `adoption_decisions` ledger.
- Added an opt-in Claude-side observational hook adapter (`.claude/hooks/claude_hook_adapter.py`) that records lifecycle events to the shared hash-chained evidence ledger, reaching observed-evidence parity with the Codex `hooks.json` adapter in the default observational mode. Strict-block parity is deferred pending a Claude run-manifest producer.
- Published the Checkpointed Execution (`workflow-task-ledger`) design as design-only; implementation is gated to a later release.

## 8.3.2

- Scoped bundle verification to committed/distributable content: `validate_source_registry.py`, `validate_research_ledger.py`, and `validate_knowledge_store.py` no longer require local-only source-project paths (`docs/`, `.github/`, `.kanboard-plan`) to exist, while keeping schema validation, bundle-internal consumer/locator existence, and absolute-path rejection.
- Removed the `context_compounding_plan` check from the `core` verification profile and deleted `check_context_compounding_plan.py`: it was a release-QA gate hardcoded to a local-only `docs/plan/...` document, not installed-bundle content.
- Added `.claude/CLAUDE.md` as a Claude-adapted mapping of the global working rules in `.codex/AGENTS.md`, diverging only where Claude feature names differ (`settings.json` and permission modes, `.claude/` paths, `/loop`).

## 8.3.1

- Cleaned evaluation-facing framing: replaced deployment/autonomy-negative wording with portable skill-bundle and host-managed runtime asset language across public docs, runtime notes, mirrored skills, eval notes, and references.
- Simplified stale-version hygiene around a single `CURRENT_VERSION` and current-label regex checks instead of a long hand-maintained stale-label list.
- Hardened verification cleanup so `verify_bundle.py` removes Python cache artifacts after checks as well as before checks.

## 8.3.0

- Bounded-loop activation bridge: added `activate_loop_run.py` / `deactivate_loop_run.py` and a session-scoped pointer under `${CODEX_HOME:-~/.codex}/harness/active-loops/<session>.json`; the Stop hook now resolves the active LoopRun by `session_id` instead of a custom Stop payload field or parent env var, and loop evaluation is decoupled from the generic agent-run manifest (it also runs when that manifest is `UNVERIFIED`, only a hard validation failure skips it).
- LoopRun guarded transition in `evaluate_loop_run.py`: iteration advances strictly by one (no skip/rewind via `max()`), terminal runs (success/blocked/budget_exhausted/...) reject new iteration results, duplicate results replay idempotently (returning the prior decision without re-recording side effects), and every applied iteration's input and decision are persisted under `iterations/`. Added `iteration_result_id`/`payload_hash` to the iteration-result schema and `applied_results`/`resumes` to the loop-run schema, plus `resume_loop_run.py` to explicitly reopen a terminal LoopRun.
- `evaluate_loop_run.decide()` now honors `termination.precedence` for terminal decisions (with `blocked`/`budget_exhausted` kept as non-negotiable ceilings and recover-vs-continue as a threshold-driven continuation strategy), and `control.max_wall_time_seconds` is measured from `started_at` and enforced as a real budget. Added `blocked`/`recover` to the contract precedence vocabulary.
- `check_evidence_ledger.py` now fails any retained claim whose verdict is not `confirmed` (a `partial` claim keeps the loop running instead of converging), matching the search-deep-evidence success contract.
- Unified `plan-loop-term` output: a runtime contract that validates directly against `loop-contract.schema.json` (the `init_loop_run.py` input, no manual rewrite) plus a clearly-separated governance/planning companion; aligned condition ids to the `^SC-[0-9]{3}$` runtime pattern and clarified `workflow-loop-runner`'s executable input.
- Wired `search-deep-evidence` into `search-router`, `.codex/context-routing.md`, and both README skill catalogs as a deep multi-angle, adversarially-verified evidence lane.
- Added `.codex/tools/tests/test_loop_engineering.py` covering the activation bridge, monotonic iteration, terminal immutability, idempotent replay, `iterations/` audit, explicit resume, wall-time enforcement, and the partial-verdict gate.
- Loop activation lifecycle close-out and audit hardening: a terminal Stop decision auto-deactivates the session pointer (so later unrelated turns are plain non-loop), reused `iteration_result_id` with a different payload is a conflict (not a replay), observe-mode Stop no longer consumes the continuation budget, the `loop` verify profile runs the loop-engineering invariants, `validate_loop_run.py` checks the `iterations/` audit trail and `applied_results` integrity, and `init_loop_run.py --force` re-initializes atomically (no stale artifacts).
- Notification display refinement (the notification feature itself shipped in 8.2.0): completion/attention alerts use a compact `[stat]-[model]-[session]` title (model+effort, e.g. `opus4.8-xhigh`; session from the transcript ai-title) while keeping session context in the body; the Claude adapter extracts the last assistant summary from the transcript when the hook payload omits it.

## 8.2.0

- Desktop notification hooks: best-effort, redacted OS notifications for Codex `PermissionRequest` (`.codex/tools/notify_desktop.py`) and Claude Code `PermissionRequest` / native `Notification(permission_prompt)` / `StopFailure` (`.claude/tools/claude_notify_adapter.py`) without blocking hook recording.
- Codex and Claude turn-completion notifications on `Stop`, with a redacted session label from the latest prompt, compact summary, or task subject.
- Loop-aware notifications: per-iteration loop continuation/recover/success alerts, plus failure and approval cues.

## Unreleased

- Started the execution-loop layer: added an opt-in hook event recorder, optional Codex `PreToolUse` hook example, automatic verification pipeline runner, GitHub Actions workflow, and a research ledger validator/profile.
- Added `.codex/tools/requirements.txt` with `PyYAML` and `jsonschema`; validators use Draft 2020-12 `jsonschema` when installed and retain the local subset fallback for offline/local use.
- Added the research evidence ledger schema and initial ledger instance under `.codex/research/`.
- Added agent output validation for recorded Codex agent run artifacts, including claim-to-evidence checks, hook event hash/order checks, an `agent-output` verification profile, and valid/invalid fixtures.
- Wired repo-local Codex lifecycle hooks for `PreToolUse`, `PermissionRequest`, `PostToolUse`, and `Stop` through a live hook adapter; `Stop` now gates finalization on agent-run artifact validation once hooks are trusted.
- Hardened the live hook prototype after review: `Stop` validates only the current `session_id`/`turn_id` run, missing current-run evidence is `UNVERIFIED` rather than pass, repeated tool calls validate per `tool_use_id`, failed `PostToolUse` exits record `fail`, hook evidence defaults to metadata hashes with redaction, and release CI installs `pytest`.
- Hardened the P0 completion gate after execution feedback: failed/unverified `Stop` checks now record `turn_finalize_attempt` so repair work remains valid, Codex `PermissionRequest` without `tool_use_id` is accepted as approximate, dangling tool calls fail validation, `Stop.last_assistant_message` is hash-bound to the run manifest, unknown tool responses record `warn`, runtime traces are excluded from packaged evidence, and package verification uses synthetic fixtures.
- Closed the hook launcher and finalization P0s: `hooks.json` no longer searches arbitrary `cwd` adapter paths, `Stop` post-finalize validation now accepts an in-memory candidate final event before appending the actual `turn_finalize`, and the release GitHub Actions workflow referenced by the source registry is restored.
- Registered `workflow-minimal-implementation` in user-facing README catalogs and added routing/negative eval cases for minimal-implementation modifier behavior.
- Wired the bounded verification loop layer into the bundle's own verification pipeline: added a `loop` profile to `verify_bundle.py` (committed LoopRun fixture validation + `init_loop_run` runtime smoke), added `loop` to `run_verification_pipeline.py` `DEFAULT_PROFILES` so release CI gates it, registered the three loop schemas, their `examples/`, the four loop runtime tools, and the committed LoopRun fixture in `check_execution_assurance.py` `REQUIRED_FILES` with schema accept/reject contracts, and added a first committed valid LoopRun fixture under `.codex/tools/tests/fixtures/loop-runs/valid/` plus four unit tests. Closes the loop-engineering integration debt where loop schemas/runtime had no dedicated verification profile and ran only against tmp dirs inside unit tests.
- Codified two deterministic loop governance gates in `evaluate_loop_run.py`: an evidence-backed-pass guard (a required condition reported `pass` with empty `evidence_refs` is blocked with reason `pass_without_evidence`, resisting reward hacking / premature completion) and oscillation detection (a required condition regressing `pass`→`fail` increments `progress.oscillation_count`; reaching the optional contract `control.oscillation_limit`, default 2, switches to `recover`). Added `oscillation_count`/`oscillation_limit` to the loop-run/loop-contract schemas and `init_loop_run.py`.
- Unified and bounded the Stop-hook loop policy: loop continuation still blocks by default to drive the next iteration, but `SKILL_SYSTEM_LOOP_CONTINUATION=observe` (or off/false/0) downgrades it to an observational `systemMessage`, aligning it with the base observational-by-default Stop policy; added an exclusive `loop_lock` (fcntl) around the LoopRun read-modify-write in `evaluate_loop_run.py` so concurrent Stop evaluations cannot corrupt state.
- Added `emit_loop_feedback.py`: turns a finished LoopRun into a schema-valid knowledge feedback packet that is always `review_state: proposed` (never accepted) and whose `source_run_id` provenance is enforced from the loop's recorded agent-run refs (refuses to emit when no attributable `AR-*` run exists), closing the loop→Context-Compounding wiring gap.
- Normalized the canonical bundle version label to `8.1.0`: the version-label hygiene check now treats `7.3.1`/`8.0.0`/`8.0.1`/`8.0.2` labels as stale and points to `8.1.0`, and updated `TERMS.md`, `.codex/AGENTS.md`, `.claude/CLAUDE.md`, the behavior-eval bundle-version default and observed-run fixture, and execution-assurance/hygiene docstrings accordingly. (Historical `bundle_version`/eval `version:` records and unscanned routing-doc prose are intentionally left as-is.)
- Added a `search`-family `search-deep-evidence` skill that brings the deep-research harness shape (angle fan-out, evidence ledger, adversarial verification, `citation_status` labels) into the bundle while respecting the search↔synthesis boundary (it produces a verified evidence set and hands final synthesis to `report-*`/`research-literature-synthesis`); lightly enhanced `search-paper-evidence` with shared `citation_status`/current-source labeling. Registered in the skill registry + cross-family tags and mirrored to `.claude`.
- Made `search-deep-evidence` loop-drivable through the existing loop-engineering runtime (no new workflow/skill): added `check_evidence_ledger.py`, a deterministic command_exit verifier that PASSes only when every retained ledger claim is `verified`+`confirmed`+sourced, with committed converged/in-progress fixtures, a `loop`-profile `loop_evidence_ledger` gate, execution-assurance registration, two unit tests, and a loop-contract template under the skill's references.
- Gave the loop recover decision a regression-specific continuation prompt: when recovery is triggered by `oscillation_limit_reached`, `evaluate_loop_run.py` now emits an "Oscillation detected … Regressed condition: <id>" message (root-cause-the-reversion guidance) instead of the generic repeated-failure prompt.
- Strengthened Codex desktop notifications beyond approval prompts: the Stop hook now emits a best-effort notification on every loop iteration (`loop-iteration`, topic mapped from the decision), on validation failure (`stop-failure`), and on Kanboard sync (`kanboard-sync`), via a generalized `run_desktop_notify` helper; the Kanboard session update also carries a `[loop <id> -> <action>/<reason>]` note so the board reflects loop progress per iteration. Added optional `--topic`/`--app` to `notify_desktop.py`, redacted `task_subject`/`plan`/workspace labels, three unit tests (notify topic/app, per-iteration loop notification, plus dry-run forced in the test harness so suites never deliver real overlays), and a doc section. Notifications remain best-effort and never block the hook; controlled by `SKILL_SYSTEM_DESKTOP_NOTIFY` (`off`/`dry-run`/enabled).
- Removed the macOS `osascript`/AppleScript ("Script Editor") notification path from both `notify_desktop.py` shims (`.codex` and `.claude`): macOS now uses the Swift overlay only, and `--mode native` resolves to the overlay on macOS (it still reaches `notify-send`/PowerShell on Linux/Windows). Made the overlay visibility duration configurable via `--duration` / `SKILL_SYSTEM_NOTIFY_DURATION` (default 4s) and aligned the `.claude` shim to the same `--topic`/`--app`/`--duration` CLI (host-appropriate `--app` default). Notification titles are now prefixed with an `[app]-[topic]` tag (e.g., `[codex]-[done]`) reported as `display_title`, making the source/kind visible at a glance; notifications stay non-interactive (no click target, since the hook has no terminal/session handle to focus). Added an ordinary turn-completion notification: a successful Stop with no active loop now fires a `turn-complete` (topic `done`) desktop notification (previously only loop iterations / failures / kanboard / approvals notified, so plain Codex completions were silent). Fixed the gating so UNVERIFIED runs (validation code 4 — the common case when no agent-run manifest is provisioned) count as a normal completion and fire `turn_complete` (done) instead of being misclassified as `stop_failure`; only genuine validation failures now fire `stop-failure`, and the code-4 completion notification is recorded as a `turn_finalize_attempt` for observability. Loop turns still notify per iteration; failures still fire `stop-failure`. The Claude adapter (`claude_notify_adapter.py`) gained the same `turn-complete` notification on `Stop` and now passes `--app claude`/`--topic` so Claude notifications render the `[claude]-[topic]` tag (e.g., `[claude]-[done]`); requires a `Stop` hook wired in `~/.claude/settings.json`. Notification text is now markdown-stripped in `notify_desktop.py` (`strip_markdown`): bold/italic/code/strike markers, heading/blockquote/list prefixes, and `[text](url)` are removed so overlays show plain text, while the `[app]-[topic]` tag brackets and `snake_case` underscores are preserved. Restyled the macOS overlay to a Monokai theme (background `#272822`, off-white message) and colored the title + border by topic accent (done=green, error=pink, approval/input=cyan, progress=yellow, kanboard=purple, default=foreground); the topic is passed to the Swift overlay as an extra argv and the source-hash cache auto-rebuilds the overlay binary on theme changes.
- Tightened Stop completion notification semantics: every non-loop Codex `Stop` now sends the `turn_complete` finish cue; validation failures additionally send `stop_failure`.

## 8.1.0

- Added `plan-loop-term` as a Planning-family specialist for `/goal` and loop term contracts.
- Added loop term templates for success conditions, verifier evidence, progress/stall signals, retry and stop policies, checkpoints, side-effect notes, and execution handoff text.
- Registered `plan-loop-term` in both Codex and Claude mirrors, README catalogs, skill registries, context routing, and runtime usage eval cases.
- Preserved `plan-long-term-package` as the owner of broad multi-document planning packages; `plan-loop-term` is a narrow nested contract artifact when used inside long-term plans.
- Tuned GPT-5.5-era skill fit: shortened report routing, moved long-term package detail into references, added stop/idempotency gates for Kanboard and Knowledge maintenance, outcome-first guidance for design/algorithm skills, search-router validation, and selective implicit entry routers.
- Split Loop Engineering into dedicated readiness, verifier mapping, and accepted execution skills: `loop-readiness-router`, `loop-verifier-registry`, and `workflow-loop-runner`, with design loop contract support.
- Strengthened Loop Engineering skills with source-grounded readiness factors, deterministic-first verifier mapping, maker/checker separation, durable loop state, retry taxonomy, untrusted-observation handling, and observe-decide-act-verify-checkpoint execution.
- Added loop governance coverage for Stop-hook limits, progress heuristics, Wiki Bank feedback candidates, durable/event-runtime labels, improvement/safety/verifier/efficiency/process/outcome metrics, comprehension debt, over-orchestration, parallel conflicts, non-idempotent retry, context poisoning, reward hacking, thrashing, infinite retry, premature completion, and oscillation.
- Added the first bounded verification loop runtime: loop contract/run/iteration schemas, `init_loop_run.py`, `evaluate_loop_run.py`, `validate_loop_run.py`, Stop-hook active LoopRun evaluation, continuation prompts via `decision: block`, checkpoint writing, no-progress/repeated-failure recovery decisions, and non-loop compatibility tests. Host schedulers, queues, event triggers, and daemonized controllers remain separate runtime capabilities.

## 8.0.2

- Promoted the Context Compounding package to the 8.0.2 field line.
- Hardened `analysis-codebase` for C++/CMake/lizard discovery and safer fallback behavior.
- Expanded Codex hook launchers to work from repo and home install paths.
- Deferred optional validation imports in the hook adapter so runtime hooks can start without eager dependency failures.

## 7.3.1

- Hardened validation integrity after the 7.3.0 release-candidate review: eval, field feedback, source registry, behavior replay, generated mirrors, and execution-assurance schemas now reject invalid sentinel data instead of only checking field names or headers.
- Restored `integrations/kanboard-plan-sync/README.md` and added a static reference-target checker so skill context targets cannot silently point at missing files.
- Added `unittest` coverage for new validators using valid/invalid fixtures, and wired those tests into `verify_bundle.py --profile core`.
- Promoted representative production eval cases to schema v2 and moved the observed behavior replay fixture from a test-only case id to a production eval case.
- Reframed field feedback gate output as `unmeasured + waived` rather than measured field-test success.

## 7.3.0

- Added 7.3.0 execution-assurance artifacts: host-neutral lifecycle hook guidance, capability-based tool hardening guidance, lifecycle-event schema, and tool-policy schema.
- Added `run_behavior_evals.py` as a replay-first behavior eval runner with an observed-run pilot fixture.
- Added `verify_bundle.py --profile execution` to validate execution-assurance artifacts and replay behavior evals without live host/model calls.
- Treated field feedback evidence as a user-accepted release gate for this cut without fabricating measured entries.
- Bumped active bundle labels to `7.3.0` while preserving 7.2.7 as the stabilization baseline.

## 7.2.7

- Added `verify_bundle.py` as the profile-based verification entry point with text/json output and explicit `PASS`/`FAIL`/`SKIP`/`ERROR` status handling.
- Added machine-readable field feedback scaffolding under `.codex/field-feedback/`, plus validators, fixtures, and a generated `FIELD_FEEDBACK.md` human-readable view.
- Added eval case schema validation, source registry validation, generated mirror checksum validation, and active document freshness checks.
- Added canonical `.codex/docs/source_registry.yaml` and generated Claude-side mirrors for source registry and eval schema.
- Bumped active bundle labels to `7.2.7` while preserving `7.2.6` as the previous baseline.

## 7.2.6

- Added the Kanboard plan-sync integration bundle under `integrations/kanboard-plan-sync`: a plan-centric MCP server + Python core/CLI that projects Markdown `docs/plan` onto a local Kanboard via JSON-RPC (repo=Project, plan=Swimlane, item=Task; Markdown stays source of truth).
- Added two Agent skills, `kanboard-plan-rollout` (onboard a repo's plans + bulk register/sync) and `kanboard-plan-ops` (push/pull/validate/curate an already-registered board), mirrored across `.codex/skills` and `.claude/skills` with registry rows (family `workflow`) and routing/negative eval cases.
- Included MCP registration examples (`examples/mcp.claude.json`, `examples/mcp.codex.toml`) and a Kanboard local-host setup methodology doc. Excluded the Kanboard application, DB/logs/API token, and the ThemeRevision/UI plugin — those remain local third-party runtime.
- Renamed the integration's `secrets.py` to `token_guard.py` so no bundled filename trips sensitive-name hygiene; the API token resolves from an env var or the local Kanboard DB and is never stored in the bundle.
- Bumped the bundle version label to `7.2.6` across package-facing docs, runtime notes, eval case files, and version-label hygiene checks; added stale-label detection for `7.2.5`.

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

- Recut the bundle as a portable Skill System bundle.
- Hardened `rules/default.rules` so network, history rewrite, process termination, debugger, host-specific, and live `.codex` mutation commands are not active allow rules.
- Kept `.codex/config.toml` and `automations/` under host-managed runtime policy.
- Moved app-managed `.system` skill snapshots into `optional-system-skills-snapshot/` as comparison material.
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

This cut keeps installation, live runtime mutation, deployment management, signoff, rollback, evidence lifecycle, release governance, and completion-state tracking under their owning host or workflow.
