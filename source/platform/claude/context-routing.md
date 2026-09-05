# Context Routing — Claude Overlay

This file owns only Claude-specific routing and context guardrails. Skill identity, family, role,
use/exclusion semantics, and conditional context stay in each installed skill's Routing Card.
`.claude/docs/skill_registry.md`, `.claude/docs/skill_routing.md`, and the family files under
`.claude/docs/routing/` are generated lookup views, not semantic inputs.

## Custom Skill Scope

`.claude/skills/.system`, live home runtimes, and plugin caches are app-managed or deployment state.
Repository work changes canonical `source/` assets and uses repository generators; it does not
audit, patch, migrate, route-register, or smoke-test `.system` skills as bundle implementation.

## Mode Separation

- Software implementation, failure diagnosis/repair, scientific research, evidence search, Design,
  Test Design/Implementation, planning, and reporting retain distinct installed owners.
- A development request that mentions a model, experiment, loss, metric, paper, or design noun keeps
  its direct development owner unless the requested deliverable matches another Routing Card.
- First implementation or an explicit production-mechanism replacement remains Implementation;
  only an admitted bounded repair of an already implemented contract belongs to Bug Fix.
- Test Design and Test Implementation are explicit owners. A failing check is evidence, not automatic
  repair or successor authority.

## Resolution And Precedence

Resolve an explicit skill by exact user path, current-session exposure, a repository-local root
declared by project instructions or `project-context.yaml`, then `unresolved`. Explicit selection
wins within the selected card's scope; otherwise choose one narrow primary owner and attach support
or evidence owners only when their conditions are material. Do not scan unrelated home directories,
plugin versions, adjacent repositories, or guessed caches.

For genuine ambiguity, read `.claude/docs/skill_routing.md`, select the smallest matching family,
then read only that family view or exact skill. Never load the whole routing library. Family mode
requires explicit group/family framing or a family name; bare words such as analysis, report, or
plan continue through direct intent matching.

`allow_implicit_invocation` in `agents/openai.yaml` controls Claude-facing discoverability only.
The package generator projects `disable-model-invocation` when that bit is false; neither field
grants authorization or changes the skill's role.

## Context Bundle Contract

Resource Closure is build metadata. Package presence never admits a reference into active context.
The installed Routing Card's `must_read`, `read_if_needed`, and `do_not_load_by_default` prose owns
loading. Start with user intent and one primary owner, load only the minimum condition-matched
reference slice, and do not recover from missing context by loading every skill, document, store, or
chat artifact.

When delegation follows a selected specialist, carry its exact canonical ID. Without one, let the
worker route normally. Plans, Memory, Knowledge, and named Wikis remain separately declared context
sources; persistent writes require their explicit owners and user authority.

## Claude Host Exceptions

- Claude plugin path projection, permission modes, approval prompts, hooks, lifecycle, and tool
  compatibility remain owned by `CLAUDE.md`, hook settings, and the Claude harness. Generated common
  routing views cannot override them.
- Do not classify `/goal`, `/loop`, automation, duration, cost, or agent count. Use
  `plan-execution-handoff` only for durable execution state, and load repeated-work principles only
  for an admitted verifier-steered graph.
- `.claude/docs/work_horizon_model.md` owns artifact altitude and
  `.claude/docs/planning_state_model.md` owns persisted-plan transitions. Neither invokes a chain.
- Router/support/context-cost guards remain conservative: read a targeted family slice, stop after
  selecting the owner, and attach evidence or output modifiers only when the primary task requires
  them.
