# Changelog

## 7.1.1

- Recut the bundle as a manual drop-in skill bundle.
- Hardened `rules/default.rules` so network, history rewrite, process termination, debugger, host-specific, and live `.codex` mutation commands are not active allow rules.
- Excluded `.codex/config.toml` and `automations/` from the default bundle by policy.
- Moved app-managed `.system` skills into `optional-system-skills-snapshot/` instead of the default copy payload.
- Added a compact Routing Card to `design-to-frontend` while preserving its implementation workflow.
- Narrowed global task result wording so labels apply to concrete user tasks, not the skill system as a whole.
- Added field feedback examples for design, research, and memory over-trigger cases.
- Extended bundle hygiene checks for risky allow rules, config/automation policy, and core `.system` placement.
- Moved Codex runtime docs, eval cases, and tools under `.codex`.
- Added Claude-side runtime folders under `.claude`.
- Removed root-level runtime dependency on `docs/`, `eval/`, `tools`, `.agent-workflow`, and `harness`.
- Retained the 6.0.2-based skill set.
- Retained research cluster routing.
- Reframed 7.0 coordination, eval, and artifact concepts as lightweight support skills.
- Added `skill_maturity` and `improvement_track` to the runtime registry.
- Added runtime usage eval cases for real-use quality observation.
- Added field feedback templates and guidelines.
- Added a small read-only bundle hygiene checker.
- Added `spec-and-plan-curator` for active-context pruning, plan closeout, memory proposal distillation, and stale plan/archive load-policy decisions.
- Narrowed coordination, eval, artifact, and memory agent metadata to explicit invocation to reduce pre-field over-trigger risk.

## Notes

This cut does not add automatic installation, live runtime mutation, deployment management, signoff workflow, rollback workflow, evidence intake/finality workflow, package-cut scoring, or skill-system finality state.
