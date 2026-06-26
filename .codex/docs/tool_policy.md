# Tool / Permission Operating Catalog

This catalog is a human-readable operating layer over `.codex/rules/default.rules`
and `.codex/schemas/tools/tool-policy.schema.json`. It does not grant permission,
override sandboxing, or replace host approval policy.

## Decision Classes

| class | meaning | default action |
| --- | --- | --- |
| `routine` | Local, reversible, task-scoped observation or validation with bounded output. | allow when host policy allows |
| `risky` | Can mutate workspace/runtime state, access network/browser/session state, or has broad output or side effects. | ask or require explicit approval |
| `blocked` | Destructive, credential-seeking, policy-bypassing, or out-of-scope action without explicit user intent and recovery boundary. | deny or stop |

Use the smallest class that matches the actual invocation. A tool name alone is
not enough; classify by arguments, target, side effects, and current user intent.

## Operating Catalog

| tool class | routine when | risky when | blocked when |
| --- | --- | --- | --- |
| local read/search | `rg`, `sed`, `nl`, `git diff`, or schema inspection scoped to relevant files. | Broad scans over private/runtime state or large logs. | Reading credentials, unrelated private files, or raw memory/transcripts without explicit need. |
| local process/check | Tests, linters, validators, dry-runs, or local build commands with no network or destructive side effect. | Long-running builds, generated artifacts, host GUI, debugger attach, process termination, or writes outside expected outputs. | Commands that bypass sandbox/approval or execute untrusted downloaded code. |
| filesystem write | Requested source/doc/test edits inside the workspace. | Bulk rewrites, generated files, runtime state, config, or migration output. | Protected paths, app-managed `.system` replacement, unrelated config, or write scope not tied to the request. |
| destructive cleanup | Targeted cleanup of artifacts created by the current task after inspection. | Recursive deletion, git index mutation, branch deletion, or history-changing commands. | `git reset --hard`, broad `git clean`, deleting user work, or deleting outside approved scope. |
| network | Fetching cited docs or narrow public sources required for the task. | Package installs, remote git, APIs, large downloads, authenticated sites, or sending task data. | Credential exfiltration, uploading private files, unapproved external writes, or bypassing auth/paywalls. |
| browser / GUI | Read-only inspection of a user-requested page or local app verification. | Form submission, downloads, login/session-dependent actions, comments/messages, purchases, permission prompts. | Sending sensitive data or changing account/state without explicit action-time authorization. |
| MCP / connector | Read-only project or issue metadata needed for routing/evidence. | Creating/updating remote issues, PRs, cards, docs, or automations. | Mutating external systems without exact target, approval, and rollback/handoff boundary. |
| credential / secret | Not routine. | Reading a named local credential only when the user explicitly authorizes that credential and destination. | Printing, storing, or transmitting secrets unnecessarily; searching broadly for secrets. |

## Agent Use

- Treat this catalog as preflight guidance and reporting vocabulary.
- Prefer `routine` checks before requesting risky actions.
- Mark missing approval, missing runtime support, or blocked host capability as
  `unverified` instead of inventing success.
- Record postconditions as evidence: exit code, changed files, network target,
  browser readback, or user approval reference.
- Do not weaken `.codex/rules/default.rules`; this catalog explains intent,
  while rules and host policy enforce the boundary.

## Representative Policy Files

Examples under `.codex/schemas/tools/examples/` show how to express common
tool classes in the schema:

- `tool-policy.exec-command.yaml`
- `tool-policy.network.yaml`
- `tool-policy.destructive.yaml`
- `tool-policy.browser-mcp.yaml`
