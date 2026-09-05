# Context Routing — Codex Overlay

This file owns only Codex-specific routing and context guardrails. Skill identity, family, role,
use/exclusion semantics, and conditional context stay in each installed skill's Routing Card.
`docs/skill_registry.md`, `docs/skill_routing.md`, and `docs/routing/*.md` are deterministic views
generated from those cards; they are lookup aids, never a second semantic owner.

## Resolution And Lookup

Resolve a requested skill in this order:

1. exact path supplied by the user;
2. skill exposed or installed in the current session;
3. repository-local skill root explicitly declared by the nearest project instructions or
   `project-context.yaml`;
4. `unresolved`.

An exact path controls discovery only and does not broaden the selected skill's scope. Unknown or
stale IDs stay unresolved; never scan unrelated home directories, plugin versions, adjacent
repositories, or guessed caches for a replacement.

For a clear natural-language match, select the narrow installed skill directly. When specialists
genuinely compete, read `docs/skill_routing.md`, choose the smallest matching family, then read only
that family file or the exact skill. Never load the complete routing library. Enter family mode only
for explicit group/family framing or an explicit family name, not a bare domain word.

## Codex Invocation Boundary

- `agents/openai.yaml` controls Codex discoverability and implicit invocation. It grants no write,
  persistence, permission, or external-state authority.
- User-explicit skill selection wins only inside the selected Routing Card's declared role and
  scope. The current task owner keeps ordinary work when no skill is needed.
- Pass an already selected canonical skill ID to delegated workers. Without an upstream selection,
  let the worker route normally.
- App-managed `.codex/skills/.system`, live home state, and plugin caches are outside repository
  routing ownership unless the user explicitly requests that live operation.

## Context Admission

Resource Closure in canonical source is build metadata. It makes a declared resource available in
the package but never admits it into the current context. The installed Routing Card's `must_read`,
`read_if_needed`, and `do_not_load_by_default` prose remains the loading authority. Start with the
minimum task and owner context, load a conditional reference only when its stated condition holds,
and never load every packaged file to prove closure.

Plans, Memory, Knowledge, and named Wikis are context sources, not routing fallbacks. Their exact
path/declaration and owning skills govern access; persistent mutation requires explicit user intent.

## Codex Host Exceptions

- Do not invoke a classifier for `/goal`, duration, automation, or repeated wording.
  `plan-execution-handoff` applies only when durable execution state is actually needed, and its
  repeated-work profile applies only when verifier evidence will steer later actions more than once.
- Codex permissions, Auto-review, sandboxing, tool paths, hooks, lifecycle, and Stop behavior remain
  owned by `AGENTS.md`, `rules/`, `hooks.json`, and the Codex harness. A shared routing projection
  cannot override them.
- When the user asks which flow comes next, `docs/work_horizon_model.md` owns artifact altitude and
  `docs/planning_state_model.md` owns persisted-plan transitions. Neither document starts a skill
  chain.
- Test, review, assurance, reporting, Memory, and Knowledge owners attach only when their installed
  Routing Card and the current request admit them; topic similarity alone is insufficient.
