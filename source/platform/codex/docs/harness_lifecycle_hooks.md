# Codex Harness Lifecycle Hooks

The default Codex harness keeps all eight supported lifecycle events and sends each event to `bin/skill-system-harness`. POSIX invokes the binary directly; Windows uses a bounded `cmd.exe` conditional only to resolve custom `CODEX_HOME` or the default `%USERPROFILE%\.codex` location. No hook uses Python as its base launcher. Hooks do not replace repository instructions, sandboxing, rules, host permissions, or approval policy.

## Event Branches

| Codex event | bounded behavior |
| --- | --- |
| `SessionStart` | Clear correction and work-contract state for a fresh or cleared session; on resume/compaction restore only bounded projections and nearest-manifest context. |
| `UserPromptSubmit` | Mark a field-derived explicit correction and compile high-confidence work-contract signals. Raw prompt text is never persisted. |
| `PreToolUse` | Apply explicit work-contract scope exclusions without treating shell or interpreter command shape as a terminal denial. |
| `PermissionRequest` | Return no hook decision so Codex Auto-review can approve ordinary requests and reject the risky minority without a user-click wait. |
| `PostToolUse` | No-op for policy state; it does not retain tool output or validate task results. |
| `Stop` | Apply the one-shot response guard; convert a forbidden blocking question into bounded local deferral/continuation; retain a direct-task work contract for user continuation; and send one completion or input notification. It never evaluates or continues a task graph. |
| `PreCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |
| `PostCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |

The dispatcher has no hook-event ledger, Agent Run artifact, output-validation gate, reference monitor, harness measurement, execution-admission state, or compact record.

## Command And Approval Boundary

The model uses purpose-built tools and direct executables where possible. It decomposes compound shell work into ordered direct calls only when working directory, data flow, failure ordering, and side effects remain equivalent. Stable local reads, diagnostics, builds, and tests remain sandboxed; `rules/skill-system.rules` does not grant unsandboxed execution from a broad executable prefix. Boundary-crossing commands reach Auto-review, while explicit forbidden rules retain hard stops.

A shell or inline interpreter expression that genuinely needs quoting, expansion, a pipeline, redirection, or evaluator semantics is marked `prompt` and reaches `PermissionRequest`. `PreToolUse` does not deny it merely because of that form. With an effective `on-request` or granular approval policy and `approvals_reviewer = "auto_review"`, the reviewer subagent resolves eligible requests without a user-click dialog; host sandboxing, hard-safety policy, and explicit work-contract exclusions remain authoritative boundaries.

Text creation and edits inside a writable workspace use `apply_patch`. For an explicitly authorized external text target, exact content is first staged with `apply_patch` inside the workspace, then deployed with an auditable direct command through host-supported approval or escalation and read back. The model does not ask the user to repeat already clear task authorization merely to trigger that host mechanism.

Skill System policy does not store a command-attempt ledger or convert a host denial, expiration, or sandbox refusal into a prompt-reentry requirement.

## Work-Contract Enforcement Boundary

The runtime projection contains only schema version, revision, prompt digest, verification owner, interaction mode, execution mode, excluded action classes, current semantic intent, deferred intent keys/classes/reasons, and a bounded continuation count. Raw prompt text, tool input, command text, transcript content, and credentials are never persisted.

`PreToolUse` protects explicit scope regardless of task duration: an excluded validation or meta action does not become permitted because a workflow proposed it. When a plan mixes allowed and excluded work, the hook returns the official non-blocking `permissionDecision: "allow"` plus `updatedInput`, records the removed semantic purposes as deferred, and preserves the remaining plan. It denies only when no in-contract plan item remains or a side-effecting tool still attempts excluded work; arbitrary execution is never rewritten into a false-success no-op.

The work-contract projection does not decide `PermissionRequest`; the host-selected reviewer does. When Auto-review is effective, it evaluates eligible approval prompts for both attended and unattended work. Explicitly excluded or already-deferred actions are removed or denied at `PreToolUse`, before they can become reviewer requests, and the model continues independent runnable nodes. Interaction mode governs blocking questions only. Internal work-contract state errors fail open to the host reviewer without inventing permission.

When one intent is deferred, its purpose—not its surface command—is the deduplication key. A test run cannot be retried as a GUI smoke check or validation wrapper merely by changing tools. The Stop branch asks the model to continue other required runnable work and permits global `blocked` only when the remaining graph has no such work.

A direct-task projection remains active after an ordinary Stop so a same-task user continuation does not silently regain excluded work or agent-owned verification. It is cleared only by an explicit work-contract reset or a fresh/cleared session boundary.

## Independent Branches

- Desktop notification is a notification-only branch. macOS uses the packaged Swift/Cocoa overlay and never `osascript`; all platforms redact external paths and sensitive text before launch. It cannot validate output, sync a board, continue a loop, or change permission decisions.
- Project context resolution reads at most the exact or nearest `project-context.yaml`. It reports locations and existence only and never reads or writes store content.

## Two-Layer Response Guard

Global `AGENTS.md` owns the semantic rule: a complaint, correction, question, or harm report is not action authority, and a correction requires re-evaluating affected conclusions before answering. The runtime guard handles only one narrow end-of-turn failure derived from field reports: after an explicit correction, a response that only acknowledges the correction and promises future action can be blocked once.

The guard does not reject direct explanations, completed actions, or a concrete plan the user requested. A single generic word such as `실수` is not a correction signal, and code fences or file links do not count as a direct resolution. A blocked Stop returns the official `decision: "block"` plus `reason` continuation shape. It stores only a session hash, turn hash, and two booleans; raw prompt and assistant text are never persisted. Missing identity, corrupt state, or internal errors fail open.

## Platform And Deployment Boundary

`hooks.json` is the sole base registration owner; plugins do not register duplicate hooks. `rules/skill-system.rules` owns generated Skill System policy while Codex and the user own `rules/default.rules`. Stop retains its bounded response-guard and notification work only; no child evaluator or continuation process is launched. The runtime contains `darwin/arm64` and `windows/amd64` Go artifacts plus the precompiled macOS overlay, so target machines need no build toolchain. Generation does not install the runtime into a live home or plugin cache.

Claude owns a separate Go dispatcher and four-event registration template. It reuses bounded core packages but not the Codex event dispatcher or hook topology.
