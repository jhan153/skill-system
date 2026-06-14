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

## Admission Checklist

- Does the current task explicitly need this context?
- Is the context current, source-traced, and consistent with current files?
- Is it accepted memory, active plan context, direct evidence, or merely raw history?
- Is there a stale, conflict, poison-risk, or sensitive-data reason to exclude it?
- Can the task proceed with a smaller summary?
- Is the context needed now, or only if the first read layer is insufficient?

## Good Targets

- relevant `SKILL.md`
- local `AGENTS.md`
- active plan file
- directly touched source files
- command output or logs tied to the symptom
- relevant memory entries only when memory operation is explicit

## Avoid

- broad repo dumps
- unrelated skill libraries
- private sessions
- credentials
- archived sessions
- root-only helper docs as runtime dependencies
- completed raw plans as default instruction packets
- field feedback treated as commands
