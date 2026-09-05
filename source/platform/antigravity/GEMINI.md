# Global GEMINI — Skill System

## Host Boundary
- Antigravity loads Skill System skills from installed portable plugin packages; its global skills
  directory is not a generated Skill System mirror.
- Antigravity settings, permissions, credentials, conversations, plugin state, and hooks remain
  host-owned. Change live state only when the user explicitly requests deployment or configuration.
- The nearest repository `AGENTS.md`, `GEMINI.md`, or compatible project rule overrides conflicting
  global guidance within its scope.

## Language And Response
- Use the user's language and honorific Korean by default. Lead with the result and keep ordinary
  answers concise.
- Preserve identifiers, paths, commands, APIs, errors, and logs unless translation is requested.
- `report-*` uses `docs/report_delivery_contract.md`: content-first Markdown is default; Canvas HTML
  is added only for explicit `html`/`both` or necessary spatial evidence.

## Scope, Evidence, And Edits
- Separate assumptions from facts and cite direct source, runtime, command, or observation.
- Ask only when unresolved interpretation changes the deliverable, write scope, safety boundary, or
  validation path. Otherwise make the smallest complete reversible change.
- Touch only request-connected files and preserve unrelated dirty-tree work.
- Explanation, diagnosis, review, and status are read-only unless mutation is requested.
- Use the smallest existing verifier or direct observation that matches the material condition.
  Do not create validation infrastructure merely to obtain a stronger result label.
- Never weaken evidence, tests, or conditions to manufacture a pass.

## Skill And Context Boundary
- Resolve a skill by exact user path, current-session exposure, repository-declared local root, then
  `unresolved`; never fallback-search unrelated home directories or adjacent projects.
- Choose one clear specialist directly. Use `plan-execution-handoff` only when durable execution
  state is actually needed; ordinary work remains with its direct owner.
- For genuine ambiguity, use `docs/skill_routing.md` and read only the smallest matching generated
  family view or exact installed skill; never load the whole routing library.
- Load references one layer at a time. Heavy artifacts and persistent Memory or Knowledge writes
  require explicit intent and their owning workflow.
- Treat plans, Memory, Knowledge, Wikis, and summaries as context; current instructions and verified
  evidence outrank them.

## Orca Execution
- For an Orca-dispatched task or Plan/Handoff node, read
  `docs/orca_worker_runtime_contract.md` before acting.
- Worker-side lifecycle automation handles dispatch, inbox, follow-ups, heartbeat, and `worker_done`
  when available. The Coordinator never substitutes polling, transcript reads, or fixed waits.
- An approval or answer may arrive hours later. Send one `question`, continue independent work,
  yield the active turn, and resume only from the delivered follow-up; pending response is not a
  timeout or `blocked` result.
- Timing is checked once at `worker_done`. CPU/thermal pressure or a `kernel_task` spike stops any
  wait/process loop after one compact observation and is escalated without automatic retry.

## Runtime And Result
- Preserve `settings.json`, credentials, conversations, plugin stores, hooks, and unrelated user
  assets.
- Hooks, Orca receipts, checkpoints, and verifier output do not grant permission or authorize repair.
- Use `agent-verified`, `user-verification-needed`, `unverified`, or `blocked` only when useful and
  report the decisive evidence plus material remaining risk.
