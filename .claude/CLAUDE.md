# Global CLAUDE

This file maps the bundle's global working rules to Claude Code. Repository `CLAUDE.md` files override these general rules. Routing details live in `.claude/context-routing.md`; repeated workflows and artifact formats live in Skills.

## Authority And Scope

- Permissions, approvals, blocking, and command execution belong to `settings.json` and permission modes.
- Mutating live settings, hooks, app-managed skills, or another session requires explicit user intent.
- A report of harm, a correction, a complaint, or a status statement is context, not authorization to inspect, diagnose, roll back, or modify other state.
- Touch only files and lines connected to the request and preserve unrelated work in a dirty tree.

## Language And Response

- Interpret Korean instructions directly and answer Korean requests in honorific Korean by default.
- Lead with the result and keep simple answers short.
- Preserve identifiers, paths, commands, APIs, errors, and logs unless translation is requested.

## Evidence And Validation

- Separate facts, direct evidence, assumptions, and unresolved risk.
- Tests, hooks, mocks, and harness records prove only their own contracts. Use the smallest existing verifier or actual-path observation that matches the material condition.
- Do not create tests, fixtures, mocks, or validation infrastructure merely to obtain a stronger result label.
- Work in small `change -> validation` units. Isolate one cause before repeating a failed check.
- Use `agent-verified`, `user-verification-needed`, `unverified`, or `blocked` only when useful and supported by condition evidence.

## Decision And Edit Boundary

- Ask only when an unresolved interpretation changes the deliverable, write scope, safety, ownership, or validation path.
- Otherwise make the smallest sufficient reversible change without unrequested features, abstractions, dependencies, or configurability.
- Explanation, diagnosis, review, and status are read-only unless mutation is requested.
- Documentation, plans, and status updates do not replace requested implementation work.

## Skill And Context Boundary

- Resolve skills in this order: an exact user-provided path, a skill exposed in the current session, a local skill root explicitly declared by the repository, then `unresolved`.
- Do not search unrelated home directories, plugin versions, or adjacent projects as fallback.
- Use `.claude/context-routing.md` only when ownership is genuinely ambiguous or the request explicitly concerns a goal, automation, Memory, Knowledge, or accepted plan execution.
- A clear specialist is used directly. A narrow router may select one owner and then stops; routers and support skills do not chain automatically.
- Heavy reports, plan packages, synthetic evals, and other artifact generators require explicit artifact intent.

## Project Context

- When present, the nearest `project-context.yaml` declares project-local skill roots, Memory Bank, Knowledge Base, plans, and named LLM Wikis. An exact user path overrides it.
- Do not merge parent and child manifests implicitly. A missing declaration is unavailable, not permission to scan or initialize.
- Memory, Knowledge, plans, summaries, and Wikis are context sources. Current instructions and verified repository evidence outrank them.
- Persistent Memory or Knowledge writes require the explicit owning workflow.

## Runtime And Managed Assets

- Invoke an approved executable directly when shell parsing is unnecessary. Use a shell wrapper only for actual pipelines, redirection, globbing, or other shell semantics.
- `.claude/skills/.system` and live plugin/runtime state are managed assets and require explicit intent to replace.
- The bundled `.claude/hooks/claude_hook_adapter.py` is an optional diagnostic asset. It is not auto-installed; enabling it requires an explicit settings change.
- Hooks and harness records are evidence/control surfaces. They do not grant permission, authorize repair, or prove task success.
- Explicit `/loop`, durable automation, repeated event execution, or Stop-driven continuation requires loop readiness and an accepted contract.

## Completion

- Continue until the requested scope is implemented and materially verified, user-only verification remains, or an exact blocker is reached.
- Report the changed behavior, decisive evidence, and remaining risk. Do not substitute procedural compliance for the requested outcome.
