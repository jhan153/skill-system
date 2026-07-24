# Changelog

## 9.4.3

- Added a shared user work contract for direct work, TaskRun, WorkItem, and v3 LoopRun. The contract structures core deliverables, allowed/excluded action classes, verification ownership, interaction mode, local-block continuation, semantic intent identity, and terminal handoff without requiring users to write YAML or learn field names. Skills and workflow guidance preserve explicit user limits ahead of optional validation, quality, and meta procedures.
- Extended the Codex Go harness with a privacy-bounded work-contract projection across prompt submission, planning, tool preflight, permission decisions, compaction, Stop continuation, and session continuation. Excluded or already-deferred plan items are removed without blocking independent required work; approval is denied before UI wait only for unattended Goal/Loop execution that explicitly forbids interaction. Attended and interaction-enabled work keeps normal host approval, user-owned verification ends as `user-verification-needed`, and ordinary direct-task contracts survive Stop until explicit reset or a fresh session.
- Upgraded TaskRun, WorkItem, and LoopRun schemas/evaluators to distinguish core, prerequisite, validation, test, optional-quality, and meta work; record locally deferred actions; reject same-intent retries; reevaluate dependency graphs after a local block; and reserve global `blocked` for the absence of required runnable work.
- Added a shared offline Report Canvas as the default human-facing output for every admitted report-family task across Codex, Claude, and standalone plugins. One canonical typed model supports `decision`, `compare`, `trace`, and optional Three.js `spatial` views with Oblivion dark and Oblivion Hagoromo light themes, progressive evidence drawers, pinned local dependencies, an explicit no-follow-up state, and no change to report ownership or evidence semantics. Generation projects the complete contract and renderer into each `report-*` skill's supported `references/` and `scripts/` boundary, removing undeclared plugin-root and sibling-plugin dependencies. Explicit chat-only/no-file and exact machine/canonical formats remain overrides.
- Hardened the dependency-free Report Canvas renderer to enforce the bundled JSON Schema recursively, reject unsupported future schema keywords rather than drifting open, preserve semantic spatial checks, refuse existing outputs by default, require explicit `--force` replacement, and reject identical input/output paths.
- Added a required maintainer-side `runtime` release profile for canonical Go tests while keeping target-side `core` verification independent of Go and source files. Profile order, builders, and release-required check IDs now have one owner in `verify_bundle.py` instead of a second pipeline copy.
- Tightened the portable default Codex rules so bounded reads remain reusable while Git writes, branch mutation, plugin/runtime changes, direct `curl`, and POSIX shell `-c`/`-lc` command strings require local review. Hooks remain bounded notification/context/response-guard adapters rather than a substitute network proxy or host permission system.
- Reconciled audit gaps found against 9.4.2: Claude skill bodies project host-owned paths, Knowledge/project-context skills have paired routing cases, unsafe context checkpointing is explicit-only, and the affected analysis, design, research, and maintenance handoffs have concrete positive/negative boundaries. The shared registry now owns family entry mapping while host routing owns only group-selection triggers and platform guardrails.
- Added explicit-only `report-implementation-explainer` and `plan-behavior-discovery` skills to the dev plugin. They separate implementation navigation from evidence authority, capability from operability/release, and existing-capability product decisions from greenfield requirements or direct implementation.
- Classified one-question discovery turns as non-persisted `one_shot` work, added validator coverage for both discovery altitudes, reduced the two new instruction bodies, and kept actual model routing/output quality unverified pending fresh forward evidence.
- Cut the unified source/runtime/plugin/eval 9.4.3 release with the local annotated tag `v9.4.3`. Remote push, publication, installation, and live cache mutation remain separate explicit operations.

## 9.4.2

- Upgraded the Markdown Knowledge Base contract from flat current records to readable current snapshots with accepted aliases/search terms, embedded typed spatial/causal links, source-traced observation events, and append-only semantic revision history. Literal diffs remain in Git; no separate claim, edge, event, score, Runtime Projection, or Wiki store is introduced.
- Added overlap classification across all Knowledge writers and synchronization/checkpoint paths: same identity updates or observes the existing record, shared-provenance copies do not become independent support, stable changes amend in place, replacements use reciprocal supersession, partial scope uses typed relations, and contradictions remain visible.
- Added bounded graph-style Knowledge reads for why/history/scope/recurrence questions and maintenance operations for relation/history/overlap checks plus transparent recurrence profiles. Observation count, independent verified provenance roots, time range, scopes, unresolved roots, and counterexamples stay separate; they never become confidence, importance, maturity, popularity, or composite frequency scores.
- Made Knowledge storage location-independent: initialization binds approved `knowledge_root` and `knowledge_index` values, records them in `project-context.yaml`, and every bundled reader/writer/maintenance consumer reuses those resolved variables. Relative values resolve from the manifest; exact explicitly approved absolute targets are supported without parent or neighboring-store discovery.
- Removed the orphaned `schemas/knowledge/context-pack.schema.json` from the retired claim/edge pipeline. The generic task Context Pack guidance remains a separate small reading-set contract.
- Added non-executing workflow topology without a duplicate registry authority: Work Horizon owns persistence/artifact altitude, Planning State owns persisted-artifact transitions, and host routing owns the current-turn specialist. Direct stable work remains outside the planning state machine.
- Expanded `project-context-init` into explicit `manifest-init`, guided `bootstrap`, and read-only `doctor` modes. Bootstrap enumerates manifest and store actions separately but accepts all or a subset in one transaction approval, then delegates approved Memory or Knowledge creation without a second approval unless scope changes; ordinary work never auto-initializes context.
- Split risk review into Contract/Spec and Repository/Constraints axes. Material semantic claims that otherwise rest mainly on maker-authored implementation and checks trigger one independent standard pass when available; strict-risk work uses separate independent axes without treating review, authored tests, or repeat self-review as an oracle.
- Added a shared delivery-shape contract: `single_batch` imports no slice ceremony, multi-batch features use `vertical_slice`, wide compatibility changes use `migration_sequence`, and non-feature work uses `evidence_unit`. The contract fabricates no architectural layer and mandates neither TDD nor ticket shape.
- Removed the historical Research Ledger instance and schema from the generated `.codex/research/` runtime payload. Its synthetic validator fixture remains source-only, execution assurance no longer requires a research ledger, and runtime generation prunes the retired target root so installation cannot overwrite live research records.
- Added the version-independent `CLEAN_INSTALL_GUIDE.md` contract. Release-side source regeneration stays in the maintainer build environment, while target-side installation checks the selected commit/tree, bundle identity, and core consistency without requiring Go or Swift. Live app-managed state, user stores, and plugin caches remain protected.
- Retired the public external-source revision/license/adoption ledger and its generated mirrors, validator, research-fixture dependency, and release-gate wiring. Current project decisions remain in the manifest-declared local Knowledge Base, while two independent release checks reject reintroduction of the retired path or structured ledger payload.
- Consolidated the corrected 9.4 work into unified Codex/Claude/plugin bundle identity 9.4.2, directly succeeding 9.3.4. Live home and plugin-cache installation remains a separate explicit operation.

## 9.3.4

- Added a Claude-native Go dispatcher that shares the bounded response guard, project-context resolver, Kanboard lease/stamp implementation, redaction, and OS notification core without reusing the Codex event dispatcher.
- Registered only `SessionStart`, `UserPromptSubmit`, `Stop`, and `Notification` in the host-owned Claude settings template. Hooks use shell-free exec form and are not auto-installed.
- Uses Claude `prompt_id` as the primary turn identity with a hash-only session-sequence fallback for older clients, reads `last_assistant_message` directly, and respects `stop_hook_active` to prevent repeated Stop blocking.
- Routes native Claude notification types for approval, idle, elicitation, background input, and background completion; Stop no longer infers those notification states.
- Removed the Claude Python hook adapter, lifecycle ledger, transcript-derived Output Gate, harness measurement, lifecycle schema, and Python notification stack.
- Added reproducible Claude artifacts for macOS arm64, Windows amd64, and Linux/WSL amd64 plus the packaged macOS Swift overlay. Linux uses `notify-send` when available.
- Made bounded analysis, search, and non-writing research owners implicitly invocable when an implicit router declares them as automatic handoff targets. Heavy report/code/manuscript writers, design evidence gates, rigor modifiers, and explicitly selected Wiki context remain explicit-only.
- Added router invocation contracts and verifier coverage so an automatic handoff target must exist and be implicitly exposed; explicit recommendations must remain explicit-only, and unclassified router references fail validation.
- Projected the canonical `allow_implicit_invocation` bit into each host's native skill contract: Codex keeps `agents/openai.yaml`, while generated Claude skills add `disable-model-invocation: true` only when model invocation is disabled.
- Preserved the existing Codex package paths at `plugins/<name>/skills` and generated paired Claude-native packages at `plugins/claude/<name>/skills` under the same plugin names and versions. Separate package roots prevent each host's default skill discovery from loading the other host's metadata.

## 9.3.3

- Disabled automatic Go VCS build metadata with `-buildvcs=false` so the committed `darwin/arm64` and `windows/amd64` harness binaries remain byte-identical when regenerated after the release commit.
- Removed hard-coded `/private/tmp` writes from Codex verification tooling and tests so the caller's `TMPDIR` policy controls scratch files.
- Regenerated both Go harness artifacts with the unchanged 9.3.2 Go runtime behavior and advanced the unified Codex/Claude/plugin bundle identity to 9.3.3.

## 9.3.2

- Reconstructed the Codex eight-event base harness as cross-compiled Go executables for `darwin/arm64` and `windows/amd64`; POSIX calls Go directly, while Windows uses only a bounded `cmd.exe` conditional to honor custom `CODEX_HOME` with the default fallback.
- Restored the precompiled Swift/Cocoa macOS notification overlay with no `osascript` fallback, and reinstated notification path/credential/token/URL redaction before launch.
- Corrected the Stop continuation contract to `decision: "block"` plus `reason`, raised only the Stop host timeout above the active LoopRun bound, made Kanboard stamp only a successful stable worker result, and narrowed correction/direct-resolution heuristics so generic `실수`, code fences, and file links cannot trigger or bypass the guard alone.
- Added an atomic, token-owned Kanboard pending lease per workspace so concurrent SessionStart/Stop events cannot queue overlapping sync workers. Worker leases expire after 120 seconds versus the 60-second execution bound, are released on handled exits, and gate Windows stamp replacement as well. Normalized `dry_run` to `dry-run` before both stamp comparison and worker execution.
- Kept desktop notifications, declared-plan Kanboard sync, and active-only LoopRun as independent conditional branches. Idle tool/compact events perform no child process, network access, growing ledger scan, or file write.
- Combined the unchanged Global `AGENTS.md` authority/depth rules with a bounded field-derived correction guard. Persistent guard state contains only a session hash, turn hash, and two booleans; raw prompts, responses, commands, and tool data are not stored.
- Added a common location-only `project-context.yaml` resolver plus explicit `project-context-init` and `project-context-update` skills. Memory, Knowledge, plans, and named LLM Wiki contents remain under their specialist owners and are never collected by hooks.
- Removed the Codex Python hook adapter/base prototype, lifecycle/hash-chain ledger, Agent Run, Agent Output Gate, Reference Monitor, Recovery Guard, harness measurement/version comparison, compact records, historical release replay packages, and their exclusive schemas, docs, fixtures, tests, and verification profiles. Task/Research/Evidence ledgers, Memory Bank events, Kanboard, and LoopRun remain.
- Separated Claude's preserved opt-in hook ledger dependency into `.claude/tools` so the Claude adapter no longer borrows Codex runtime files. Plugins do not register duplicate base hooks.
- Advanced the unified bundle identity to 9.3.2. This source change does not install into a home runtime or live plugin cache.

## 9.3.1

- Split platform harness ownership at the canonical source boundary. Codex and Claude now have independent global instructions and `context-routing.md` files; portable skills, docs, eval contracts, and schemas remain shared.
- Kept the compact 9.3 Codex routing model and restored Claude's proven 9.2.1 structured decision/execution model, adapted only to the current Memory, Knowledge, Wiki, repository-skill, and non-scenario-gating contracts.
- Added independent `runtime-codex` and `runtime-claude` generation and parity checks. The aggregate `runtime` target remains the unified release path.
- Removed the separate active harness-protocol version selector. The optional receipt monitor now uses `SKILL_SYSTEM_REFERENCE_MONITOR=1` and reports the current bundle version; harness changes advance the single bundle version and tag.
- Advanced canonical bundle identity to 9.3.1 without installing or modifying a live home runtime.

## 9.3.0

- Replaced broad default lifecycle interception with an empty Codex hook map and compact global Codex/Claude rules. Harm reports, corrections, complaints, and status messages remain context rather than authorization for investigation or mutation.
- Reduced routing to direct explicit/clearly matching specialists plus at most one narrow router when owners genuinely compete. Exact skill paths and repository declarations outrank exposed-session skills; undeclared home and adjacent repositories are not fallback search roots.
- Added a portable `project-context.yaml` contract for repository-relative Memory Bank, Knowledge Base, plans, skill roots, and named LLM Wiki paths. Missing entries mean unavailable and do not initialize or discover stores.
- Simplified Memory Bank to append-only events plus compact current/archive/meta reflection for cross-session goals, rules, recurring mistakes, and proven practices. Removed packet ingestion, maturity/confidence/recurrence/usage/satisfaction scoring, Stop writes, and automatic complaint capture.
- Replaced the claim/edge/Runtime Projection Knowledge pipeline with a generic artifact-linked Markdown Knowledge Base lifecycle, five explicit category record skills, accepted-plan synchronization, and a separate explicit read-only LLM Wiki context skill.
- Added a bounded `project-context-checkpoint` for explicit commit or closeout requests. It writes only clear current-task durable items to one existing declared store, never initializes stores, duplicates facts, mutates Wikis, or writes home/global context.
- Kept authored scenarios as non-authoritative regression material and removed obsolete ingestion/projection cases instead of adding a 9.3 scenario suite. Advanced canonical bundle identity to 9.3.0 without installing, deploying, tagging, committing, or pushing it.

## 9.2.3

- Stopped routing every skill authoring or update request through the app-managed system `skill-creator`. Repository skill changes stay with the current task implementation owner; system `skill-creator` is reserved for explicit invocation or new personal-skill creation.
- Remapped the retired `create-skill-pack` model alias to direct task ownership with optional `skill-system-repo-adapter` integration instead of an automatic external-system handoff.
- Removed the unsupported `displayName` key from generated Claude plugin manifests while preserving Codex interface metadata, allowing all six local plugins to validate and install in both clients.
- Advanced the active bundle identity to 9.2.3 without adding scenario, maturity, telemetry, or user-record machinery.

## 9.2.2

- Removed the skill maturity system from the active bundle: registry maturity values and review rules, maturity guidance, field-feedback persistence schemas/YAML/gates/reports, their validator and report-generator Python tools, and the `evaluation-usage-tracker` skill.
- Removed field-feedback and frozen skill-diet comparisons from the required core gate. Historical changelog and baseline artifacts remain historical records, not active quality or release authorities.
- Limited field feedback to problems the user explicitly reports in conversation. The bundle adds no automatic prompt, transcript, usage, identifier, or telemetry collection.
- Narrowed `evaluation-harness` to explicitly requested maintenance of existing eval cases and stated that scenario results do not establish field quality.
- Advanced active bundle identity to 9.2.2 while leaving the independently versioned opt-in harness protocol unchanged.

## 9.2.1

- Continued the immutable local `v9.2.0` cut with bounded conditional reference disclosure across six design skills: `design-frontend`, `design-visual-regression`, `design-tokens`, `design-a11y-audit`, `design-component-mapper`, and `design-layout-translator`. Main bodies keep routing selectors, semantic decisions, evidence ceilings, and fail-closed behavior; detailed schemas, policies, and procedures are selected only for applicable tasks.
- Against `v9.2.0`, the six main bodies move from 6,162 to 5,524 words (-638) and from 47,072 to 42,349 UTF-8 bytes (-4,723). Main bodies plus their Markdown references move from 10,410 to 9,960 words (-450) and from 78,661 to 75,477 bytes (-3,184), so the result is not reported as deletion achieved by merely moving prose.
- Per-skill main/main-plus-Markdown-reference word deltas are: `design-frontend` -202/-202, `design-visual-regression` -151/-130, `design-tokens` -113/-16, `design-a11y-audit` -69/-31, `design-component-mapper` -47/-47, and `design-layout-translator` -56/-24.
- Kept narrow direct token and component decisions in the main skills while reserving normalization schemas and component-contract matrices for multi-category, export, artifact, or persisted-record work. Canonical conflicts remain unresolved without declared authority; catalog availability still does not prove reuse; `unmapped` still does not authorize fallback; consumer/app-surface readback remains required for the claims it covers.
- Corrected the unreleased opt-in harness 9.2.1 semantics before tagging: the reference monitor now reports freshness and integrity status for a predeclared verifier receipt only. It no longer parses or authorizes task result labels, emits validation codes or Stop reissues, feeds LoopRun, or suppresses independently enabled Agent Run, Kanboard, notification, or ordinary output-validation paths. Internal monitor observation errors become `unavailable` metadata at the adapter boundary instead of aborting those paths. The monitor itself adds no verifier command or subprocess.
- Fresh read-only forward observations covered the `design-visual-regression` and `design-frontend` admission boundaries and retained scoped fail-closed outcomes. No fresh host-admission receipt was collected for `design-tokens`, `design-a11y-audit`, `design-component-mapper`, or `design-layout-translator`; their actual admission effect remains `unverified`. Generated parity, core checks, and existing tests prove only their stated contracts, not universal six-skill behavioral equivalence or user-visible quality.
- Added no new test suite, schema, skill, or adapter for the disclosure work. Existing behavior cases remain regression surfaces rather than an independent user-quality oracle.
- Advanced active bundle identity to 9.2.1 without relabeling the separately versioned harness. Bundle 9.2.1, opt-in harness protocol 9.2.1, and historical harness 9.2.0 retain independent version meanings.

## 9.2.0

- Local release cut for the completed instruction-surface diet. The release commit is tagged `v9.2.0` locally; neither the tag nor the bundle is pushed, installed, or deployed by this cut.
- Reduced all 66 canonical skill bodies from 49,513 whitespace-delimited words to 39,820 (-9,693, -19.58%) and from 372,882 UTF-8 bytes to 310,450 (-62,432, -16.74%). These measurements exclude YAML frontmatter and are instruction-surface measurements, not billed-token estimates.
- Resolved all 38 T9 merge/delete candidates as 32 merges and 6 deletions, with zero reference moves and zero retained-unverified dispositions. The broader owned inventory, including existing references, moved from 132,280 to 122,482 words and from 1,196,415 to 1,133,065 bytes.
- Kept `design-frontend` implicit activation bounded to applicable product-interface work, and restored the repository adapter handoff boundary so translation does not absorb source, policy, or fallback ownership.
- Kept quality claims bounded: generated-target agreement, release/core checks, and the recorded forward comparisons prove only their covered contracts, not universal equivalence for every skill or user task.
- Preserved harness protocol identity independently from bundle identity. Harness 9.2.0 remains the prior evaluated candidate, while harness 9.2.1 remains the current opt-in verifier-authority candidate; this bundle release does not relabel either protocol.
- Advanced the active canonical plugin/eval/runtime identity to 9.2.0. Historical 9.1.1 release evidence, the unpublished 9.1.2 pre-diet baseline, and harness-version fixtures retain their original identities.

## 9.1.2

- Unpublished, non-deployed source baseline for the 9.2.0 instruction-surface diet. The latest published release and release tag remain `v9.1.1`; this cut is not installed, deployed, pushed, or tagged as `v9.1.2`.
- Hardened design execution around product-family profile discovery, fail-closed family rules, app-surface proof for approved component reuse, explicit UX decision handling, and rejection of fake or inert interaction mutations.
- Separated exact-target fidelity from product-family coherence so visual evidence cannot silently substitute one claim for the other, and added nine artifact-bound host-assisted design behavior cases plus focused positive/negative routing coverage.
- Froze the 66 canonical skill bodies before pruning at 49,502 whitespace-delimited body words and 372,785 UTF-8 body bytes, excluding YAML frontmatter. Full `SKILL.md` files total 52,199 words and 394,611 bytes; Routing Cards account for 15,220 body words. These measurements are comparison surfaces, not billed-token estimates.
- Advanced active source/plugin/eval defaults to 9.1.2 and regenerated runtime/plugin targets. The historical `release_forward_cases.yaml`, `release-9.1.1` observed runs, 9.1.1 fixtures, and their `solar-911-*` identities remain explicitly 9.1.1 and are rejected if relabeled as 9.1.2 evidence.

## 9.1.1

- Patch release over `v9.1.0` for routing correctness, evidence durability, and fail-closed validation. The 66-skill partition is unchanged; this release does not add a new feature family.
- Made the five high-frequency dev routing descriptions host-neutral (`analysis-performance`, `workflow-{implementation,bug-fix,dependency-upgrade,refactor-safely}`) and added a canonical 66-skill metadata regression gate that rejects host product names in frontmatter descriptions while leaving legitimate host-specific body guidance untouched.
- Replaced the shared global temp hook ledger fallback with durable, hashed per-run storage under `${CODEX_HOME:-~/.codex}/harness/hook-ledgers/<run-key>/hook-events.jsonl`. Explicit `SKILL_SYSTEM_HOOK_LEDGER` and agent-run manifest paths retain priority; Codex session/turns and Claude sessions no longer share one verifier input. Raw Codex session/turn identity is hashed without lossy filename sanitization, preventing distinct IDs such as `session/a` and `session?a` from merging. Ledger-family measurement aggregation, `0600` files/locks, `0700` run directories, and separate `agent_output_gate_mode` / `recovery_guard_mode` status fields were added. Existing global temp ledgers are not migrated, merged, or deleted automatically; consumers of `$TMPDIR/skill-system-hook-events.jsonl` must select a concrete per-run file, a ledger-family root, or retain an explicit override.
- Changed C/C++ codebase-analysis gating intentionally: any report containing included C/C++ files now records `architecture.c_cpp_semantic_depth: Not evidenced` and fails with `c_cpp_structural_evidence=not_evidenced`; include/build coupling can no longer yield PASS. The current collector does not yet emit or ingest a compilation-aware symbol/class/call index, so affected reports cannot regain PASS until that capability is added.
- Added a final-manifest default cap of 20 to `plan-long-term-package`, enforced before the first package mkdir/write. Higher caps require an explicit nonempty reason and a canonical projected path/count record; modifier `0/0` deltas are marked `absorbed-by-archetype`; empty ingest summaries are omitted; `--canonical-only` then `--derived-only` supports canonical-first staged materialization without overwriting canonical artifacts. Derived materialization now exact-matches the recorded archetype, modifiers, ordered manifest, phase topology, ingest binding, and cap record, and restores bound ingest sources instead of silently degrading or admitting stale/unbound input.
- Removed the expiring Kanboard verifier exception. When `pytest` is unavailable, the integration profile now runs the bundled stdlib `unittest discover` suite as a required check instead of SKIP; the current suite contains 97 tests.
- Compatibility impact: previously passing C/C++ reports may now FAIL, oversized long-term package initialization may be rejected before writing, no-input packages no longer contain `domain-ingest-summary.md`, and environments without `pytest` now execute rather than skip Kanboard tests. These are deliberate safety corrections, not silent behavior-preserving changes.
- Added five fresh `gpt-5.6-sol` forward-regression cases for host-neutral bug-fix routing, C/C++ fail-closed reporting, bounded staged long-term packages, durable ledger/mode separation, and the Kanboard unittest fallback. Release evidence remains SHA-256-bound, host/model-attested, independently reviewed, and time-windowed.
- Moved the canonical bundle identity to 9.1.1 across all six plugin manifests, eval manifests, runtime defaults, README/Terms/current audit labels, release checks, and hygiene policy. The identity gate requires the exact six unique canonical/generated/Claude/Codex marketplace plugin names and rejects misnamed manifests, duplicate or extra entries, and wrong local source paths; regenerated runtime/plugin targets remain mandatory before tagging.

## 9.1.0

- Release lineage: `v9.0.2` is the latest published tag before this release. The prior `9.0.4` current labels described this uncommitted release work and were not a published release; this cut advances that work directly to 9.1.0.
- Completed a current-canonical 66-skill quality pass: reduced duplicated/fixed-format skill instructions, bounded all UI metadata descriptions, made analysis depth proportional, added a shared replay-safe Memory Bank mutation contract, corrected live Knowledge Context Pack routing/budget guidance, and separated each research stage's decision oracle. Search evidence now tracks acquisition, source identity, evidence basis, and claim relation independently; the ledger verifier accepts supported, contradicted, mixed, or explicitly insufficient outcomes instead of rewarding confirmation-only ledgers or majority-vote claim deletion.
- Added a release-bound `gpt-5.6-sol` forward-evaluation gate covering codebase semantic comparison, long-term package planning, sparse-corpus research ideation, and a trivial direct read. The gate requires all release cases, a fixed evidence window, exact model identity, schema-valid cases, SHA-256-bound raw/review artifacts, and an independent qualitative review. All four behavior cases passed; the long-term package run's host-reported 187,493-token total is retained as a non-billing cost advisory for further contract/admission narrowing.
- Added a low-context Codex Recovery Guard: the default `SKILL_SYSTEM_RECOVERY_GUARD=observe` mode records `would_audit` without prompt injection or blocking; opt-in `SKILL_SYSTEM_RECOVERY_GUARD=audit` performs one bounded Stop audit per correction episode. It arms only after compaction or long/repeated activity, detects correction + recovery rhetoric + missing progress evidence independently, keeps active LoopRun primary, never persists raw conversation text, and reports recovery audit/block rates separately.
- Hardened the Codex hook harness against self-certification and ambiguous terminal state: `agent-verified` can no longer rely on `manual_check` or its own final report, schema-v2 command claims require matching preflight/result receipts, unsupported hook events fail closed, hash-chain verification is explicit, external Kanboard sync is opt-in, and one `Stop` records exactly one finalize or finalize-attempt outcome. Ledger migration is forward-only for new evidence: existing schema-v1 fixtures remain read-compatible and need not be rewritten, while new live records and new fixtures must use schema v2 with `run_id`, monotonic `seq`, `prev_event_hash`, `event_hash`, request/context/finalization events, and command claims bound to matching tool lifecycle receipts.
- Consolidated the skill surface from 71 to 66 skills. Migration: `design-mobile-screen`, `design-dashboard`, and `design-section-web` move to conditional `design-frontend` profiles; `coordination-brief`, `coordination-multi-agent`, and task-local `report-artifact-inventory` move to `coordination-handoff`; the repository-only `create-skill-pack` adapter is renamed to `skill-system-repo-adapter`.
- Added the Planning Determinism state model as shared planning-family guidance, tying planning skills to explicit states, events, invariants, and invalid-transition routing/eval coverage.
- Added token-cost surface cleanup guidance: cache-friendly context ordering, selected-reference admission, analyzer advisory metrics, unit coverage, and routing/negative eval guards against full-library loading and support-skill over-attachment.
- Deferred the Claude-specific standalone manifest, path-neutral routing, and runtime-companion parity follow-up to 9.1.1; 9.1.0 does not claim that additional Claude compatibility work.
- Fixed README timeline ordering so late 8.x entries appear before 9.x releases, then added the 9.1.0 current-release row.
- Moved the canonical bundle version identity to 9.1.0 across plugin/eval manifests, `DEFAULT_BUNDLE_VERSION`, the Claude platform header, Terms, README current pointers, tests, and hygiene policy. `.codex`, `.claude`, and plugin packages remain generated targets and must be regenerated and integrity-checked from these canonical sources before release.

## 9.0.2

- Template-hygiene and output-quality maintenance cut after 9.0.1.
- Removed toy C++ before/after examples from the short-term plan template (`plan-short-term-docs/references/plan-template.md`) and the `plan-short-term-docs` evidence rule; before/after code evidence now uses the change's actual language with no placeholder/toy code.
- Propagated the `plan-short-term-docs` diagram policy to `workflow-rigor` and `report-critical`: Mermaid only for actual runtime/control-flow/concurrency/component-boundary/class-design/data-model concerns, and plan lifecycle, approval flow, and agent workflow are not default plan diagrams.
- Made the long-term `ui-state-contract` transition diagram conditional on real transitions (no shipped empty `flowchart LR` block); kept the phase-plan-package self-test in sync.
- Converted `analysis-codebase` `report.py` unverified fallback diagrams (subsystem/path/class/metric) to plain text notices instead of meaningless placeholder diagrams; evidence-backed diagrams are unchanged.
- Bumped the bundle version to 9.0.2 across plugin/eval manifests, `DEFAULT_BUNDLE_VERSION`, the Claude platform header, and README current pointers; regenerated `.codex`/`.claude`/plugin targets and re-verified integrity.

## 9.0.1

- Expanded the `skill-system-dev` engineering role beyond the initial 9.0.0 cut with concrete execution-owner and analysis skills: `analysis-architecture-deepening`, `analysis-codebase-design`, `analysis-domain-modeling`, `analysis-performance`, `workflow-implementation`, `workflow-bug-fix`, `workflow-dependency-upgrade`, `workflow-refactor-safely`, `workflow-source-maintenance`, and `workflow-comment-maintenance`. Skill count 58 → 68.
- Added `workflow-source-maintenance` (post-development source cleanup, evidence-gated dead-code pruning, source diet) and `workflow-comment-maintenance` (behavior-preserving comment/docstring/TODO-FIXME sync) as separate primaries, with explicit boundaries against `workflow-implementation`, `workflow-refactor-safely`, and each other.
- Added `source_maintenance_execution` and `comment_maintenance_execution` work-horizon execution modes, plus routing-matrix rows, registry entries, family aliases, and runtime/negative routing eval coverage for the new skills.
- Regenerated the `.codex`/`.claude` runtime targets and the `skill-system-dev` plugin from `source/`; integrity re-verified byte-identical and the full verification pipeline passes.

## 9.0.0

- Introduced a neutral canonical `source/` tree (`skills/`, `shared/`, `platform/{codex,claude}/`, `plugins/`, `mirror-meta.json`, `tools/`) as the single source of truth, replacing hand-maintained `.codex` / `.claude` dual trees.
- Added `source/tools/generate_targets.py` and `source/tools/check_generated_targets.py`: `.codex` and `.claude` are now generated runtime targets, reproduced byte-identically from `source/` (verbatim shared payload, mirror-from-canonical with frozen timestamps, and platform overlay).
- Cutover: `.codex` / `.claude` are generated-only and carry a `.generated` do-not-edit marker; integrity is enforced by regeneration (`check_generated_targets.py --baseline`) rather than a stored checksum manifest.
- Shared the platform-agnostic JSON schema definitions to the Claude target (`.claude/schemas`), closing the one genuine runtime-scaffolding mirror gap; codex-specific items (research routing, harness README, the codex-tool-referencing schema example, `notify_desktop.py` variants) stay platform-native.
- Added initial role-based Codex plugin packages under `plugins/` (`skill-system-{core,dev,design,research,quality,maintainer}`), each with `.codex-plugin/plugin.json` and its member skills; the 58 skills are partitioned with full, disjoint coverage.

## 8.5.1

- Added the Work Horizon model to separate `one_shot`, `task_ticket`, `short_plan`, `long_plan`, `loop_overlay`, and `cross_horizon` work without introducing queue/runtime automation.
- Added plan/workflow metadata: `work_horizon`, `planning_altitude`, and `execution_mode` now distinguish tactical plan artifacts, strategic packages, loop contracts, lifecycle curation, plan batch execution, loop convergence, checkpoint ledgers, and support/intervention facets.
- Added `check_work_horizon_policy.py` and unit coverage, wired into the core verification profile with `.codex`/`.claude` metadata parity checks.
- Added routing docs and runtime eval cases for the key boundary: `workflow-task-ledger` is the task/ticket state layer between one-shot and short-plan artifacts, while WorkItem remains the lifecycle envelope.

## 8.5.0

- Added WorkItem lifecycle governance as a schema-bound state model for `triage -> explore -> ready -> implement -> verify -> review -> closed`, with explicit `blocked` handling, source/owner metadata, state history, evidence refs, findings, and next action.
- Added `work-item.schema.json`, a canonical example, `validate_work_item.py`, and unit tests. Core verification now validates the canonical WorkItem example, and execution assurance tracks the WorkItem schema/tool/test artifacts.
- Linked WorkItem to checkpointed execution without replacing it: `task-run.schema.json` and `task_ledger.py init` now support optional `work_item_ref`, while `TaskRun` remains the execution-slice ledger and WorkItem remains the parent lifecycle state.
- Documented the WorkItem boundary in `.codex` and `.claude` runtime docs and `workflow-task-ledger`: WorkItem is not a queue runtime, scheduler, Kanboard source of truth, autonomous worker, or LoopRun replacement.

## 8.4.4

- Added invocation-surface policy metadata to skill agent manifests, classifying skills as `explicit_procedure`, `selective_router`, `evidence_gate`, or `support_only` while preserving the existing Routing Card roles.
- Added `check_invocation_surface_policy.py` to verify invocation-surface / implicit-invocation consistency and `.codex` / `.claude` policy parity in the core verification profile.
- Added `analyze_context_surface.py` as an advisory, report-only context-surface analyzer so likely context leakage can be inspected without creating a release-blocking budget gate.
- Extended field feedback with optional `harness_improvement_candidate` metadata and documented friction-signal maturity review guidance without introducing automatic maturity scoring.
- Kept WorkItem lifecycle as an 8.5.0 horizon concept; no queue runtime, scheduler, worker, Kanboard state mapping, or LoopRun transition runtime is introduced in this cut.

## 8.4.3

- Updated live bootstrap finalization so a structured final report's `result_label` and `C-###` task claims synchronize back into `run.yaml` instead of leaving the manifest bound to the bootstrap placeholder claim.
- Kept the finalization sync evidence-bound: structured final reports can record user-verification-needed outcomes without inventing an agent-verified result.

## 8.4.2

- Added opt-in live agent-run manifest bootstrap (`.codex/tools/init_agent_run.py`) so current-turn `run.yaml`, final report, bootstrap evidence, and context pack can be created before Stop validation.
- Wired Codex `UserPromptSubmit` / `SessionStart` to bootstrap live manifests and `Stop` to finalize the manifest from the final assistant message when `SKILL_SYSTEM_AGENT_RUN_BOOTSTRAP=1` is set. Default behavior remains off.
- Added a tool/permission operating catalog plus representative network, destructive, and browser/MCP policy examples.
- Added an orchestration capability contract with schema and example so cron, webhook, queue, automation, and event-trigger claims remain evidence-bound instead of implied by LoopRun, hooks, or Kanboard.
- Connected orchestration capability checks into loop-readiness guidance, routing smoke tests, registry notes, README catalogs, and Claude mirrors.

## 8.4.1

- Added Claude-side strict-block parity: an opt-in transcript-based observed-vs-claimed Stop gate (`SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict`) in `.claude/hooks/claude_hook_adapter.py` that blocks a stop when the final message claims `agent-verified` but a tool result errored with no later success. Pure decision logic, fail-open transcript parsing, and a `stop_hook_active` re-block guard.
- Added the `workflow-task-ledger` skill (Checkpointed Execution): a resume-safe step/finding ledger for multi-turn work between one-shot and a LoopRun, with observed `evidence_refs` (not free text), an `accepted_risk` terminal, and a completion gate (all required steps complete + final verification pass + zero open findings). Ships `schemas/task/task-run.schema.json`, `tools/task_ledger.py`, unit tests, a `checkpointed_task` classification in `loop-readiness-router`, and registry/eval entries.
- Added out-of-band harness-paradox measurement: `analyze_harness_measurement.py` (deterministic 80/20 holdout, per-arm gate-fire/block/finalize-fail rates, `harness_paradox_fail_delta`, and sunset). Both hook adapters tag `turn_finalize` events and treat the off arm as a gate-off baseline (opt-in `SKILL_SYSTEM_HARNESS_MEASUREMENT=1`, default off, so baseline behavior is unchanged).
- Scope note: "harness parity" here means Claude/Codex contradiction-gate parity (observed-vs-claimed). It does not add a quick/normal/deep task classifier, risk flags, a bounded max-block ceiling, or an automated revert/re-instruction outcome collector because the system already has routers, risk boundaries, recovery, and LoopRun.

## 8.4.0

- Added local observed-evidence completion with an `accepted_risk` terminal in `workflow-rigor`, a debugging hypothesis ladder in `analysis-bug`, capability-ceiling escalation in `workflow-recovery`, and verification-grounding/noise-control runtime eval cases (`runtime-029..032`).
- Added a harness-paradox out-of-band holdout and sunset measurement reference under `evaluation-usage-tracker`; this historical measurement machinery was later removed.
- Added an opt-in Claude-side observational hook adapter (`.claude/hooks/claude_hook_adapter.py`) that records lifecycle events to the shared hash-chained evidence ledger, reaching observed-evidence parity with the Codex `hooks.json` adapter in the default observational mode. Strict-block parity is deferred pending a Claude run-manifest producer.
- Published the Checkpointed Execution (`workflow-task-ledger`) design as design-only; implementation is gated to a later release.

## 8.3.2

- Scoped bundle verification to committed/distributable content: research and Knowledge validators no longer require unrelated local-only source-project paths (`docs/`, `.github/`, `.kanboard-plan`) to exist, while keeping schema validation, bundle-internal consumer/locator existence, and absolute-path rejection.
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
- Closed the hook launcher and finalization P0s: `hooks.json` no longer searches arbitrary `cwd` adapter paths, `Stop` post-finalize validation now accepts an in-memory candidate final event before appending the actual `turn_finalize`, and the release GitHub Actions workflow is restored.
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

- Hardened validation integrity after the 7.3.0 release-candidate review: eval, field feedback, behavior replay, generated mirrors, and execution-assurance schemas now reject invalid sentinel data instead of only checking field names or headers.
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
- Added eval case schema validation, generated mirror checksum validation, and active document freshness checks.
- Added a generated Claude-side mirror for the eval schema.
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
