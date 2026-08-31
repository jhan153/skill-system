# Codex Go Harness

The default Codex harness is the eight-event map in `../hooks.json` plus generated platform executables in `../bin/`. Codex owns the independent `source/runtime/go/codex` module, which contains the distributed common harness baseline and Codex-specific hook delivery. `source/tools/generate_targets.py` builds:

- `bin/skill-system-harness` for `darwin/arm64`
- `bin/skill-system-harness.exe` for `windows/amd64`
- `bin/skill-system-notify-overlay`, a precompiled Swift/Cocoa overlay for `darwin/arm64`

The Go dispatchers are built with `CGO_ENABLED=0`; target machines need neither Go nor a Swift compiler. POSIX hooks invoke the Go dispatcher directly. Windows uses one bounded `cmd.exe` conditional to resolve custom `CODEX_HOME` or its `%USERPROFILE%\.codex` default, then invokes the Go dispatcher.

The dispatcher owns four bounded branches: response correction guard, privacy-safe user work-contract projection/enforcement, desktop notification, and location-only `project-context.yaml` resolution. Each branch has one policy owner and cannot grant another branch's authority.

The model prefers purpose-built direct tools and decomposes compound shell work into ordered direct calls when doing so preserves semantics. Stable local reads, diagnostics, builds, and tests run inside the sandbox without a Skill System rule granting unsandboxed execution from an executable prefix alone. A shell or inline interpreter expression that genuinely needs evaluator semantics reaches Codex `PermissionRequest` instead of being terminated by `PreToolUse` merely because of its form. Under an effective `on-request` or granular approval policy, the host's `approvals_reviewer = "auto_review"` setting routes eligible requests to the reviewer subagent rather than a user-click dialog; rules, sandboxing, and hard-safety policy retain the final boundary.

Workspace text changes use `apply_patch`. For an explicitly authorized external text target, the model stages exact content in the writable workspace and uses an auditable direct deployment command through host-supported approval or escalation, followed by readback. A clear user request is not re-requested in different wording merely to reach host approval.

The work-contract branch persists normalized policy fields and semantic intent digests, never raw prompts or tool inputs. At `PreToolUse`, it non-blockingly rewrites a mixed `update_plan` to remove excluded or already-deferred items while preserving allowed work. It rejects an all-excluded plan or an unexpected side-effecting excluded action only as a last resort and never rewrites execution into a false-success no-op. `PermissionRequest` is a deliberate no-op in this harness: the host-selected reviewer owns approval decisions, and an effective Auto-review configuration removes user-click waits while explicit exclusions are removed before they become runnable and independent DAG work continues.

An ordinary Stop retains the direct-task projection for a same-task user continuation. Explicit contract reset or a fresh/cleared session removes it.

macOS notifications use only the packaged Swift overlay; the removed `osascript` path is not a fallback. Notification title/body inputs redact external paths, credentials, long token-like values, and URLs before process launch.

Codex no longer packages the Python diagnostic adapter, hook-event ledger, Agent Run, TaskRun, LoopRun, WorkItem runtime, output gate, Reference Monitor, harness measurement/version comparison, compact record, or their compatibility fixtures. Explicit research/evidence artifacts and Memory Bank event history remain separate owners.

`rules/skill-system.rules` is the only Skill System-owned Codex rule file. Codex and its TUI own `rules/default.rules`; runtime generation and installation must preserve it. `config.toml.fragment` selects `approvals_reviewer = "auto_review"` only for an explicitly authorized runtime installation and does not override `allow_login_shell`.

Runtime generation does not install or update a live home, plugin cache, user `default.rules`, or another session. Claude hook assets are independently owned under `.claude/`.
