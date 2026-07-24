# Codex Go Harness

The default Codex harness is the eight-event map in `../hooks.json` plus generated platform executables in `../bin/`. Source lives under `source/runtime/go` and `source/runtime/swift`; `source/tools/generate_targets.py` builds:

- `bin/skill-system-harness` for `darwin/arm64`
- `bin/skill-system-harness.exe` for `windows/amd64`
- `bin/skill-system-notify-overlay`, a precompiled Swift/Cocoa overlay for `darwin/arm64`

The Go dispatchers are built with `CGO_ENABLED=0`; target machines need neither Go nor a Swift compiler. POSIX hooks invoke the Go dispatcher directly. Windows uses one bounded `cmd.exe` conditional to resolve custom `CODEX_HOME` or its `%USERPROFILE%\.codex` default, then invokes the Go dispatcher.

The dispatcher owns six bounded branches: response correction guard, privacy-safe user work-contract projection/enforcement, desktop notification, declared Kanboard plan synchronization, active-only LoopRun evaluation, and location-only `project-context.yaml` resolution. Each branch fails open and cannot grant another branch's authority.

The work-contract branch persists normalized policy fields and semantic intent digests, never raw prompts or tool inputs. At `PreToolUse`, it non-blockingly rewrites a mixed `update_plan` to remove excluded or already-deferred items while preserving allowed work. It rejects an all-excluded plan or an unexpected side-effecting excluded action only as a last resort and never rewrites execution into a false-success no-op. It changes a `PermissionRequest` decision only when the natural-language or accepted v3 LoopRun projection selects unattended execution and forbids additional interaction; LoopRun activation alone is insufficient. Attended tasks and interaction-enabled Goal/Loop contracts keep normal host approval behavior. A denied or locally blocked purpose is deferred while independent required runnable work continues.

An ordinary Stop retains the direct-task projection for a same-task user continuation. Explicit contract reset, a fresh/cleared session, or terminal LoopRun cleanup removes it.

macOS notifications use only the packaged Swift overlay; the removed `osascript` path is not a fallback. Notification title/body inputs redact external paths, credentials, long token-like values, and URLs before process launch. Kanboard atomically acquires one workspace-specific pending lease before queueing a detached Go worker. The worker verifies its owner token, releases the lease on every handled exit, and records a fingerprint only after the integration exits successfully and the plan remains unchanged. A crashed worker's lease becomes reclaimable after 120 seconds, beyond the 60-second worker timeout. `dry_run` is normalized to the persisted `dry-run` mode before stamp comparison.

Codex no longer packages the Python diagnostic adapter, hook-event ledger, Agent Run, output gate, Reference Monitor, harness measurement/version comparison, compact record, or their compatibility fixtures. The explicit TaskRun, Research/Evidence ledgers, Memory Bank event history, and LoopRun runtime are separate owners and remain available.

Runtime generation does not install or update a live home, plugin cache, or another session. Claude hook assets are independently owned under `.claude/`.
