# Runtime Terms

## manual drop-in

The user unpacks the bundle and copies files manually. The bundle does not install itself or modify live runtime state.

## runtime canonical

Codex runtime material lives inside `.codex`.

- `.codex/docs`: runtime guidance
- `.codex/eval`: usage-quality cases
- `.codex/tools`: small read-only sanity tools

Claude runtime material lives inside `.claude`.

## root packaging layer

Root files explain the bundle to a human. Root files are not runtime dependencies.

## runtime config policy

This bundle intentionally excludes `.codex/config.toml` to preserve the user's existing runtime config. It also excludes `automations/` because 7.1 core is a manual drop-in skill bundle, not an automatic runtime loop.

Review `.codex/rules/default.rules` against local policy before copying it.

## app-managed system skills

`.codex/skills/.system` is app-managed and is not part of the default copy payload. Optional snapshots belong under `optional-system-skills-snapshot/` and must not overwrite an existing runtime `.system` folder without explicit user intent.

## skill maturity

Maturity is a conservative use-readiness label. Allowed values are `skeleton`, `usable`, `field_tuned`, `experimental`, and `deprecated`.

## improvement track

Improvement track is the next specific work needed to improve a skill. It is not a status calculation.

## runtime usage eval

Runtime usage eval cases are examples for observing skill behavior in real use. They do not approve the bundle and do not prove skill quality.

## field feedback

Field feedback is real-use observation collected for future skill text, routing, maturity, or eval updates.

## bundle hygiene

Bundle hygiene checks only structure and obvious packaging mistakes. It is read-only and does not make quality decisions.

## 7.1 Core Boundary

7.1 core keeps skills, routing docs, maturity docs, usage cases, feedback guidance, and a small sanity checker.

7.1 core excludes install automation, live runtime mutation, deployment/signoff workflows, rollback flow, evidence intake/finality workflows, package scoring, runtime config replacement, automations, default `.system` payload, and skill-system finality modeling.
