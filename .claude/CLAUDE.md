# Claude Runtime Notes

This folder mirrors the 7.2.0 manual drop-in skill bundle for Claude-side use.

## Boundary

- `.claude/skills` contains the skill texts.
- `.claude/docs` contains runtime guidance copied from `.codex/docs`.
- `.claude/eval` contains usage-quality cases copied from `.codex/eval`.
- `optional-system-skills-snapshot/.claude/skills/.system` is review-only and is not part of the default copy payload.
- Root files are packaging guidance only.

## Use Rules

- Treat this as a manual bundle.
- Do not install or mutate live settings automatically.
- Do not use package scoring or skill-system finality state.
- Keep runtime usage cases as real-use quality examples.
- Use skill maturity conservatively.
- Do not replace existing runtime config, automations, or app-managed system skills by default.
