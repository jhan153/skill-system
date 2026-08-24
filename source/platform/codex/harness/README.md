# Codex Go Harness

The default Codex harness is the eight-event map in `../hooks.json` plus generated platform executables in `../bin/`. Source lives under `source/runtime/go` and `source/runtime/swift`; `source/tools/generate_targets.py` builds:

- `bin/skill-system-harness` for `darwin/arm64`
- `bin/skill-system-harness.exe` for `windows/amd64`
- `bin/skill-system-notify-overlay`, a precompiled Swift/Cocoa overlay for `darwin/arm64`

The Go dispatchers are built with `CGO_ENABLED=0`; target machines need neither Go nor a Swift compiler. POSIX hooks invoke the Go dispatcher directly. Windows uses one bounded `cmd.exe` conditional to resolve custom `CODEX_HOME` or its `%USERPROFILE%\.codex` default, then invokes the Go dispatcher.

The dispatcher owns four bounded branches: response correction guard, privacy-safe user work-contract projection/enforcement, desktop notification, and location-only `project-context.yaml` resolution. Each branch fails open and cannot grant another branch's authority.

The work-contract branch persists normalized policy fields and semantic intent digests, never raw prompts or tool inputs. At `PreToolUse`, it non-blockingly rewrites a mixed `update_plan` to remove excluded or already-deferred items while preserving allowed work. It rejects an all-excluded plan or an unexpected side-effecting excluded action only as a last resort and never rewrites execution into a false-success no-op. It changes a `PermissionRequest` decision only when the natural-language projection selects unattended execution and forbids additional interaction. Attended tasks and interaction-enabled Goal/Loop contracts keep normal host approval behavior. A denied or locally blocked purpose is deferred while independent required runnable work continues.

An ordinary Stop retains the direct-task projection for a same-task user continuation. Explicit contract reset or a fresh/cleared session removes it.

macOS notifications use only the packaged Swift overlay; the removed `osascript` path is not a fallback. Notification title/body inputs redact external paths, credentials, long token-like values, and URLs before process launch.

Codex no longer packages the Python diagnostic adapter, hook-event ledger, Agent Run, TaskRun, LoopRun, WorkItem runtime, output gate, Reference Monitor, harness measurement/version comparison, compact record, or their compatibility fixtures. Explicit research/evidence artifacts and Memory Bank event history remain separate owners.

Runtime generation does not install or update a live home, plugin cache, or another session. Claude hook assets are independently owned under `.claude/`.
