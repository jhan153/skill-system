# Context Pack Guidelines

Context packs are task-specific reading sets. They should stay small and relevant.

## Shape

```yaml
context_pack:
  task:
  primary_skill:
  must_read:
  read_if_needed:
  do_not_load_by_default:
  validation_context:
  risk_boundary:
  admitted:
  excluded:
  unresolved_questions:
```

## Rules

- Start with the user request, active files, and the selected primary skill.
- Prefer source files, active plans, and direct evidence over broad history.
- Add one layer at a time when context is missing.
- Do not load every skill, every memory card, every previous plan, or full chat history by default.
- Keep `do_not_load_by_default` explicit for large, sensitive, stale, or unrelated material.
- Treat root packaging documents as human guidance, not runtime source material.
- Treat completed or superseded plans as background evidence, not active instructions.
- Include field feedback only as observed usage evidence, not as a direct runtime instruction.
- Prefer short source-traced summaries over raw transcripts or full old plan text.

## Cache-Friendly Ordering

Order context from stable to volatile so repeated turns can reuse the stable prefix:

1. Stable: repo rules, selected route summary, selected `SKILL.md`, stable validation policy.
2. Semi-stable: active plan, selected source files, selected reference index or catalog.
3. Volatile: current date/time, newest user clarification, latest command output, transient logs, screenshots, or external observations.

Do not put volatile command output, timestamps, or fresh logs before stable routing and policy context unless the current task is only to inspect that output.

## Recoverable Facts And Durable Context

- Reference an authoritative file or deterministic lookup instead of freezing its current value into agent instructions when that lookup is cheap.
- Preserve information whose value is in the reasoning: decisions, constraints, failure modes, costly observations, and operational caveats.
- Verify that every reference is available from the installed runtime. A pointer outside the recipient's reachable surface is missing context, not compression.
- When prose and its referenced authority disagree, follow the authority and route correction of the obsolete prose through its owning maintenance workflow.

## Reference Admission

- Load indexes, catalogs, or routing cards before large reference folders.
- Admit only the reference needed for the current decision or artifact.
- Keep template/reference admission to 1-3 files per expansion step unless the user explicitly requested a broad package.
- Record why a large reference set is needed before reading it.
- Prefer `read_if_needed` over eager `must_read` for templates, examples, and historical packages.

## Token-Cost Notes

- Context-surface scores are advisory; they are not billing-token measurements.
- Favor late reference loading over deleting useful skill instructions.
- Optimize repeated work by keeping stable context stable and appending volatile evidence later.
- If quality and cost conflict, preserve routing, risk boundary, and validation evidence first.

## Admission Checklist

- Does the current task explicitly need this context?
- Is the context current, source-traced, and consistent with current files?
- Is it accepted memory, active plan context, direct evidence, or merely raw history?
- Is there a stale, conflict, poison-risk, or sensitive-data reason to exclude it?
- Can the task proceed with a smaller summary?
- Is the context needed now, or only if the first read layer is insufficient?
- Can stable context be placed before volatile observations to improve cache reuse?
- Can an index or summary replace raw template/reference loading for this turn?

## Good Targets

- relevant `SKILL.md`
- local `AGENTS.md`
- active plan file
- directly touched source files
- selected reference index or one selected template
- command output or logs tied to the symptom
- relevant memory entries only when memory operation is explicit

## Avoid

- broad repo dumps
- unrelated skill libraries
- all references/templates for a high-fanout skill
- private sessions
- credentials
- archived sessions
- root-only helper docs as runtime dependencies
- completed raw plans as default instruction packets
- field feedback treated as commands
