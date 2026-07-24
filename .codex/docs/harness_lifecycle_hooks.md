# Codex Harness Lifecycle Hooks

The default Codex harness keeps all eight supported lifecycle events and sends each event to `bin/skill-system-harness`. POSIX invokes the binary directly; Windows uses a bounded `cmd.exe` conditional only to resolve custom `CODEX_HOME` or the default `%USERPROFILE%\.codex` location. No hook uses Python as its base launcher. Hooks do not replace repository instructions, sandboxing, rules, host permissions, or approval policy.

## Event Branches

| Codex event | bounded behavior |
| --- | --- |
| `SessionStart` | Clear correction/work-contract state for a fresh or cleared session; on resume/compaction restore only bounded work-contract and nearest-manifest context; conditionally sync a declared Kanboard plan. |
| `UserPromptSubmit` | Mark a field-derived explicit correction and compile high-confidence natural-language work-contract signals into a privacy-safe runtime projection; ordinary prompts are no-op. |
| `PreToolUse` | Rewrite a mixed `update_plan` non-blockingly to remove excluded/already-deferred items; reject an all-excluded plan or an unexpected side-effecting action only as a last resort; otherwise leave the tool decision unchanged. |
| `PermissionRequest` | Deny before UI wait only for an active unattended Goal/Loop that forbids interaction, recording that semantic intent as deferred. All attended and interaction-enabled work sends the notification and leaves the host decision unchanged. |
| `PostToolUse` | No-op. It records and validates nothing. |
| `Stop` | Apply the one-shot response guard; convert a forbidden blocking question into bounded local deferral/continuation; evaluate only an active LoopRun; retain a direct-task work contract for user continuation; clear it after a terminal LoopRun; conditionally sync a declared Kanboard plan; and send one completion/input/loop notification. |
| `PreCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |
| `PostCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |

The dispatcher has no hook-event ledger, Agent Run artifact, output-validation gate, reference monitor, harness measurement, or compact record. Idle PostTool events decode one bounded JSON object and return without a child process, network access, or file write.

## Work-Contract Enforcement Boundary

The runtime projection contains only schema version, revision, prompt digest, verification owner, interaction mode, execution mode, excluded action classes, current semantic intent, deferred intent keys/classes/reasons, and a bounded continuation count. Raw prompt text, tool input, command text, transcript content, and credentials are never persisted.

`PreToolUse` protects explicit scope regardless of task duration: an excluded validation or meta action does not become permitted because a workflow proposed it. When a plan mixes allowed and excluded work, the hook returns the official non-blocking `permissionDecision: "allow"` plus `updatedInput`, records the removed semantic purposes as deferred, and preserves the remaining plan. It denies only when no in-contract plan item remains or a side-effecting tool still attempts excluded work; arbitrary execution is never rewritten into a false-success no-op. This action-scope enforcement is separate from approval policy. `PermissionRequest` changes the host decision only when both conditions hold:

1. the explicit natural-language projection or accepted active v3 LoopRun contract selects `unattended_goal_loop`; and
2. the work contract forbids additional interaction.

An attended task is not converted into an unattended task merely because the user prefers fewer questions. Likewise, an unattended Goal/Loop that explicitly allows interaction keeps the normal host approval UI. Internal state errors fail open to the host policy rather than broadening automatic denial.

When one intent is deferred, its purpose—not its surface command—is the deduplication key. A test run cannot be retried as a GUI smoke check or validation wrapper merely by changing tools. The Stop branch asks the model to continue other required runnable work and permits global `blocked` only when the remaining graph has no such work.

A direct-task projection remains active after an ordinary Stop so a same-task user continuation does not silently regain excluded work or agent-owned verification. It is cleared only by an explicit work-contract reset, a fresh/cleared session boundary, or terminal LoopRun cleanup.

## Independent Branches

- Desktop notification is a notification-only branch. macOS uses the packaged Swift/Cocoa overlay and never `osascript`; all platforms redact external paths and sensitive text before launch. It cannot validate output, sync a board, continue a loop, or change permission decisions.
- Kanboard runs only when the current workspace has `.kanboard-plan.yml` and the relevant plan fingerprint changed. An atomic workspace-specific pending lease prevents overlapping workers; the detached Go worker must present the lease token, waits for the integration result, releases the lease, and writes the normalized mode/fingerprint stamp only after exit 0 with an unchanged plan. `dry_run` and `dry-run` share one persisted mode. A crashed lease is reclaimable after 120 seconds; the worker itself is bounded to 60 seconds. The worker is absent from the unconfigured/unchanged path.
- LoopRun reads only the exact active pointer or explicit run directory. It invokes the existing evaluator only for an active run; inactive Stop events do not scan run directories.
- LoopRun v3 carries the same work contract into condition classification. Local `blocked`/`deferred` conditions are recorded in `deferred_actions`; independent required conditions continue. `user_verification_needed` is a terminal handoff, not verifier success.
- Project context resolution reads at most the exact or nearest `project-context.yaml`. It reports locations and existence only and never reads or writes store content.

## Two-Layer Response Guard

Global `AGENTS.md` owns the semantic rule: a complaint, correction, question, or harm report is not action authority, and a correction requires re-evaluating affected conclusions before answering. The runtime guard handles only one narrow end-of-turn failure derived from field reports: after an explicit correction, a response that only acknowledges the correction and promises future action can be blocked once.

The guard does not reject direct explanations, completed actions, or a concrete plan the user requested. A single generic word such as `실수` is not a correction signal, and code fences or file links do not count as a direct resolution. A blocked Stop returns the official `decision: "block"` plus `reason` continuation shape. It stores only a session hash, turn hash, and two booleans; raw prompt and assistant text are never persisted. Missing identity, corrupt state, or internal errors fail open.

## Platform And Deployment Boundary

`hooks.json` is the sole base registration owner; plugins do not register duplicate hooks. The Stop host timeout is 12 seconds, longer than the active-only LoopRun evaluator's 8-second bound; other events retain a 3-second host timeout. The runtime contains `darwin/arm64` and `windows/amd64` Go artifacts plus the precompiled macOS overlay, so target machines need no build toolchain. Generation does not install the runtime into a live home or plugin cache.

Claude owns a separate Go dispatcher and four-event registration template. It reuses bounded core packages but not the Codex event dispatcher, LoopRun branch, or hook topology.
