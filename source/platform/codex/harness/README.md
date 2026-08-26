# Codex Go Harness

The default Codex harness is the eight-event map in `../hooks.json` plus generated platform executables in `../bin/`. Codex owns the independent `source/runtime/go/codex` module; shared baseline behavior was distributed into that module and Codex alone adds execution admission. `source/tools/generate_targets.py` builds:

- `bin/skill-system-harness` for `darwin/arm64`
- `bin/skill-system-harness.exe` for `windows/amd64`
- `bin/skill-system-notify-overlay`, a precompiled Swift/Cocoa overlay for `darwin/arm64`

The Go dispatchers are built with `CGO_ENABLED=0`; target machines need neither Go nor a Swift compiler. POSIX hooks invoke the Go dispatcher directly. Windows uses one bounded `cmd.exe` conditional to resolve custom `CODEX_HOME` or its `%USERPROFILE%\.codex` default, then invokes the Go dispatcher.

The dispatcher owns five bounded branches: execution admission, response correction guard, privacy-safe user work-contract projection/enforcement, desktop notification, and location-only `project-context.yaml` resolution. Each branch has one policy owner and cannot grant another branch's authority.

The execution-admission branch compiles each `UserPromptSubmit` into turn-local effect and target grants without persisting prompt or command text. `PreToolUse` rewrites only a safely reducible `sh`/`bash`/`zsh -c/-lc` wrapper; rejects opaque shell and inline interpreter evaluators such as `python3 -c`, `node -e`, and `osascript -e` before they can create an approval prompt; rejects shell-based repository text authoring in favor of `apply_patch`; and stops unchanged duplicate attempts. Auditable script and module entrypoints remain eligible for ordinary effect/target classification. `PermissionRequest` auto-allows a host escalation when the current turn already grants the same effect and target, exposes at most one interactive prompt for a new semantic purpose, and immediately denies that gap in `dontAsk` or plan mode. `PostToolUse` closes the attempt and advances the workspace generation after a successful write so changed-state readback and validation may run again.

Execution state is bounded to normalized grant names, target fingerprints, tool/purpose digests, status, and a generation counter. A denied or expired purpose is terminal for the current turn; the model is told not to retry it through another command form or spend a follow-up loop analyzing approval mechanics. This is admission control, not an event ledger, command history, or learned global allowlist.

The work-contract branch persists normalized policy fields and semantic intent digests, never raw prompts or tool inputs. At `PreToolUse`, it non-blockingly rewrites a mixed `update_plan` to remove excluded or already-deferred items while preserving allowed work. It rejects an all-excluded plan or an unexpected side-effecting excluded action only as a last resort and never rewrites execution into a false-success no-op. It changes a `PermissionRequest` decision only when the natural-language projection selects unattended execution and forbids additional interaction. Attended tasks and interaction-enabled Goal/Loop contracts keep normal host approval behavior. A denied or locally blocked purpose is deferred while independent required runnable work continues.

An ordinary Stop retains the direct-task projection for a same-task user continuation. Explicit contract reset or a fresh/cleared session removes it.

macOS notifications use only the packaged Swift overlay; the removed `osascript` path is not a fallback. Notification title/body inputs redact external paths, credentials, long token-like values, and URLs before process launch.

Codex no longer packages the Python diagnostic adapter, hook-event ledger, Agent Run, TaskRun, LoopRun, WorkItem runtime, output gate, Reference Monitor, harness measurement/version comparison, compact record, or their compatibility fixtures. Explicit research/evidence artifacts and Memory Bank event history remain separate owners.

`rules/skill-system.rules` is the only Skill System-owned Codex rule file. Codex and its TUI own `rules/default.rules`; runtime generation and installation must preserve it. `config.toml.fragment` declares the one host-owned key that an explicitly authorized installer merges into `config.toml`: `allow_login_shell = false`, so omitted shell calls are non-login and explicit login-shell requests are rejected.

Runtime generation does not install or update a live home, plugin cache, user `default.rules`, or another session. Claude hook assets are independently owned under `.claude/`.
