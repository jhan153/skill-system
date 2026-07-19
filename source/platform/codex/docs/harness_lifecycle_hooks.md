# Codex Harness Lifecycle Hooks

The default Codex harness keeps all eight supported lifecycle events and sends each event to `bin/skill-system-harness`. POSIX invokes the binary directly; Windows uses a bounded `cmd.exe` conditional only to resolve custom `CODEX_HOME` or the default `%USERPROFILE%\.codex` location. No hook uses Python as its base launcher. Hooks do not replace repository instructions, sandboxing, rules, host permissions, or approval policy.

## Event Branches

| Codex event | bounded behavior |
| --- | --- |
| `SessionStart` | Clear correction state for a fresh/cleared session, conditionally sync a declared Kanboard plan, and report only the nearest manifest location summary. |
| `UserPromptSubmit` | Mark a field-derived explicit correction and add compact correction context; ordinary prompts are no-op. |
| `PreToolUse` | No-op. It records and decides nothing. |
| `PermissionRequest` | Send an independent desktop approval notification and leave the host decision unchanged. |
| `PostToolUse` | No-op. It records and validates nothing. |
| `Stop` | Apply the one-shot response guard, evaluate only an active LoopRun, conditionally sync a declared Kanboard plan, and send one completion/input/loop notification. |
| `PreCompact` | No-op. |
| `PostCompact` | No-op. |

The dispatcher has no hook-event ledger, Agent Run artifact, output-validation gate, reference monitor, harness measurement, or compact record. Idle Pre/PostTool and Compact events decode one bounded JSON object and return without a child process, network access, or file write.

## Independent Branches

- Desktop notification is a notification-only branch. macOS uses the packaged Swift/Cocoa overlay and never `osascript`; all platforms redact external paths and sensitive text before launch. It cannot validate output, sync a board, continue a loop, or change permission decisions.
- Kanboard runs only when the current workspace has `.kanboard-plan.yml` and the relevant plan fingerprint changed. An atomic workspace-specific pending lease prevents overlapping workers; the detached Go worker must present the lease token, waits for the integration result, releases the lease, and writes the normalized mode/fingerprint stamp only after exit 0 with an unchanged plan. `dry_run` and `dry-run` share one persisted mode. A crashed lease is reclaimable after 120 seconds; the worker itself is bounded to 60 seconds. The worker is absent from the unconfigured/unchanged path.
- LoopRun reads only the exact active pointer or explicit run directory. It invokes the existing evaluator only for an active run; inactive Stop events do not scan run directories.
- Project context resolution reads at most the exact or nearest `project-context.yaml`. It reports locations and existence only and never reads or writes store content.

## Two-Layer Response Guard

Global `AGENTS.md` owns the semantic rule: a complaint, correction, question, or harm report is not action authority, and a correction requires re-evaluating affected conclusions before answering. The runtime guard handles only one narrow end-of-turn failure derived from field reports: after an explicit correction, a response that only acknowledges the correction and promises future action can be blocked once.

The guard does not reject direct explanations, completed actions, or a concrete plan the user requested. A single generic word such as `실수` is not a correction signal, and code fences or file links do not count as a direct resolution. A blocked Stop returns the official `decision: "block"` plus `reason` continuation shape. It stores only a session hash, turn hash, and two booleans; raw prompt and assistant text are never persisted. Missing identity, corrupt state, or internal errors fail open.

## Platform And Deployment Boundary

`hooks.json` is the sole base registration owner; plugins do not register duplicate hooks. The Stop host timeout is 12 seconds, longer than the active-only LoopRun evaluator's 8-second bound; other events retain a 3-second host timeout. The runtime contains `darwin/arm64` and `windows/amd64` Go artifacts plus the precompiled macOS overlay, so target machines need no build toolchain. Generation does not install the runtime into a live home or plugin cache.

Claude owns a separate Go dispatcher and four-event registration template. It reuses bounded core packages but not the Codex event dispatcher, LoopRun branch, or hook topology.
