# Claude Runtime Notes

This folder mirrors the 8.3.1 Skill System runtime material for Claude-side use.

## Boundary

- `.claude/skills` contains the skill texts.
- `.claude/docs` contains runtime guidance copied from `.codex/docs`.
- `.claude/eval` contains usage-quality cases copied from `.codex/eval`.
- `optional-system-skills-snapshot/.claude/skills/.system` contains comparison material for app-managed system skills.
- Root files are packaging guidance only.

## Use Rules

- Mutating live settings requires explicit user intent.
- Keep runtime usage cases as real-use quality examples.
- Use skill maturity conservatively.
- Preserve existing runtime config, automations, and app-managed system skills unless the user explicitly requests replacement.
