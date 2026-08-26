# Codex Harness Lifecycle Hooks

The default Codex harness keeps all eight supported lifecycle events and sends each event to `bin/skill-system-harness`. POSIX invokes the binary directly; Windows uses a bounded `cmd.exe` conditional only to resolve custom `CODEX_HOME` or the default `%USERPROFILE%\.codex` location. No hook uses Python as its base launcher. Hooks do not replace repository instructions, sandboxing, rules, host permissions, or approval policy.

## Event Branches

| Codex event | bounded behavior |
| --- | --- |
| `SessionStart` | Clear correction, execution-admission, and work-contract state for a fresh or cleared session; on resume/compaction restore only bounded projections and nearest-manifest context. |
| `UserPromptSubmit` | Mark a field-derived explicit correction; compile turn-local execution effect/target grants; and compile high-confidence work-contract signals. Raw prompt text is never persisted. |
| `PreToolUse` | Normalize a safely reducible shell wrapper; reject opaque shell/inline-interpreter evaluators, shell-based repository text authoring, and unchanged duplicate attempts; then apply work-contract scope exclusions. |
| `PermissionRequest` | Auto-allow authority already granted by the current turn; expose one normal prompt for a genuinely new purpose; deny that gap immediately in `dontAsk`/plan mode; and preserve the stricter work-contract denial. |
| `PostToolUse` | Close the bounded execution attempt and advance its workspace generation after a successful write. It does not retain tool output or validate task results. |
| `Stop` | Apply the one-shot response guard; convert a forbidden blocking question into bounded local deferral/continuation; retain a direct-task work contract for user continuation; and send one completion or input notification. It never evaluates or continues a task graph. |
| `PreCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |
| `PostCompact` | Reinject the bounded active work-contract projection without storing compacted conversation text. |

The dispatcher has no hook-event ledger, Agent Run artifact, output-validation gate, reference monitor, harness measurement, or compact record. Execution admission stores only bounded grants, fingerprints, digests, attempt status, and generation; it launches no child process and performs no network access.

## Execution Admission Boundary

Execution admission answers one question: does the pending command request authority already granted by this user turn, and is its execution form safe to preserve? Stable local reads, diagnostics, builds, and tests need no per-command prompt. Explicit install, sync, process-launch, network, cleanup, publication, or termination wording grants only the corresponding effect and declared target for that turn. An ambiguous or broader target is not inferred from a command name.

`PreToolUse` may rewrite `sh`/`bash`/`zsh -c/-lc` only when removing the wrapper preserves one directly classifiable command or plain command chain with no expansion, positional arguments, or redirection. A surviving shell evaluator, or an inline general-purpose interpreter such as `python3 -c`, `node -e`, `ruby -e`, `perl -e`, `osascript -e`, or PowerShell `-Command`, is denied before `PermissionRequest`; representative forms are also forbidden by `rules/skill-system.rules` without creating a UI prompt. Absolute/versioned executable names and an `env` prefix do not bypass `PreToolUse`. Direct script files and named module entrypoints remain classifiable. Shell syntax is not itself a risk class: an authorized operational workflow may run directly, while repository text authoring through `tee`, in-place editors, stdin-fed interpreters, or writer redirection is denied in favor of `apply_patch`.

`PermissionRequest` recomputes the same effect, target, and semantic-purpose key from the canonical tool input. If the turn grant covers them, it returns `behavior: "allow"` and no approval UI appears. Otherwise an interactive mode may surface that purpose once. `dontAsk` and plan mode deny immediately, and a second equivalent request is terminal. `bypassPermissions` removes the host wait for a structurally valid command but never overrides malformed input, broad destructive targets, or work-contract exclusions.

The per-session state contains no raw prompt, command, patch, tool response, transcript, URL, credential, or absolute target. Exact paths are compared through normalized path fingerprints. The latest 64 attempts are bounded by turn and workspace generation; a successful `apply_patch` or other admitted workspace write advances the generation so same-command readback may run against changed state.

## Work-Contract Enforcement Boundary

The runtime projection contains only schema version, revision, prompt digest, verification owner, interaction mode, execution mode, excluded action classes, current semantic intent, deferred intent keys/classes/reasons, and a bounded continuation count. Raw prompt text, tool input, command text, transcript content, and credentials are never persisted.

`PreToolUse` protects explicit scope regardless of task duration: an excluded validation or meta action does not become permitted because a workflow proposed it. When a plan mixes allowed and excluded work, the hook returns the official non-blocking `permissionDecision: "allow"` plus `updatedInput`, records the removed semantic purposes as deferred, and preserves the remaining plan. It denies only when no in-contract plan item remains or a side-effecting tool still attempts excluded work; arbitrary execution is never rewritten into a false-success no-op. This action-scope enforcement is separate from execution admission. When admission has already established that a command is authorized, it may remove the host wait without weakening an exclusion. Otherwise `PermissionRequest` changes the host decision under the work contract only when both conditions hold:

1. the explicit natural-language projection selects `unattended_goal_loop`; and
2. the work contract forbids additional interaction.

An attended task is not converted into an unattended task merely because the user prefers fewer questions. Likewise, an unattended Goal/Loop that explicitly allows interaction keeps the normal host approval UI. Internal state errors fail open to the host policy rather than broadening automatic denial.

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
