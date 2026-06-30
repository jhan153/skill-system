---
name: workflow-implementation
description: Primary workflow for direct software implementation and refactoring. Use when the user asks Codex to build, change, refactor, add tests, wire APIs, update scripts, or make repo code/config changes from current requirements rather than from an approved plan package or repeated failure loop.
---

# Workflow Implementation

## Routing Card
- role: primary
- intent_signature:
  - direct implementation
  - code change
  - refactor
  - add tests
  - implement feature
  - 구현
  - 리팩터링
- use_when:
  - the user asks for a concrete code, test, script, API, config, or build change.
  - requirements are sufficient for a current-turn implementation slice.
  - the task is ordinary development work not already owned by a narrower specialist.
- do_not_use_when:
  - the user asks to execute an approved plan/spec/package; use `workflow-plan-runner`.
  - the user asks to fix a concrete failure or failing test; use `workflow-bug-fix`.
  - the same failure has repeated after an attempted fix; use `workflow-recovery`.
  - the request is pure analysis, planning, review, validation-only, or report generation.
- expected_inputs:
  - requested behavior or change
  - relevant repository files and existing local patterns
  - explicit constraints, non-goals, and validation expectations when available
- expected_outputs:
  - scoped implementation, changed artifacts, focused validation result, review notes, remaining gaps, and user-verification needs
- context_targets:
  must_read:
    - current implementation request
    - repository instructions such as `AGENTS.md`
    - target files or nearest existing patterns for the requested behavior
  read_if_needed:
    - package manifests, build/test docs, or validation contract
    - adjacent helper APIs and call sites
    - active plan only when the user explicitly references it as task input
  do_not_load_by_default:
    - full repo
    - full memory bank
    - broad architecture reports
    - unrelated plans or transcripts
- risk_profile:
  reads:
    - targeted source, tests, configs, manifests, and validation output
  writes:
    - WRITE_CODEBASE for the requested implementation scope
  tools:
    - CALL_PROCESS for focused build, test, lint, typecheck, smoke, or static validation commands
  sensitive_resources:
    - credentials default deny; destructive, network, data, or external-side-effect work requires explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Own ordinary coding work from requirement to verified diff.
- Keep implementation concrete: source, test, runtime config/build, or executable scaffold changes.
- Attach analysis, minimality, rigor, validation, or recovery only when their narrower trigger is present.

## Activation
- Primary for direct "implement", "add", "refactor", "wire", "update tests", or "change this behavior" requests.
- Attach `workflow-minimal-implementation` when abstraction, dependency, file-count, or boilerplate pressure appears.
- Attach `workflow-rigor` for medium/high-risk changes.
- Attach `workflow-validation` when check selection is the narrow concern.
- Use `workflow-bug-fix` instead when the task starts from a failing behavior that must be fixed.

## Workflow
1. Define the requested behavior and observable success condition.
2. Inspect the smallest relevant code surface and existing local pattern.
3. Choose the smallest coherent change shape and validation target.
4. Edit only files tied to the requested behavior.
5. Run the focused validation that can catch the realistic failure mode.
6. Inspect the diff for scope creep, accidental churn, and missed call sites.
7. Report changed artifacts, validation evidence, user checks, and remaining gaps.

## Implementation Rules
- Prefer existing helpers, patterns, and repo conventions over new abstractions.
- Add tests when the behavior is non-trivial, shared, or regression-prone and the repo has a clear test style.
- Do not treat documentation, TODOs, plans, or reports as implementation completion unless the user explicitly requested only those artifacts.
- Do not broaden from a local implementation to a framework, package, generated scaffold, or cross-module rewrite without evidence that the current requirement needs it.
- If a required behavior cannot be implemented safely from the available context, report the missing input rather than inventing it.

## Validation Rules
- Pick the narrowest meaningful command or manual check for the changed behavior.
- Prefer targeted tests over broad suites unless the change touches shared behavior or the repo convention requires the broader check.
- Separate `agent_verified`, `user_verification_needed`, and `unverified` evidence in the final report.
- If validation fails with the same signature after a targeted fix, hand off to `workflow-recovery`.

## Output Contract
Return only the sections needed:
- `implementation_scope`
- `changed_artifacts`
- `validation`
- `review_notes`
- `user_verification_needed`
- `unverified_gaps`
- `next_step`

## Cross-Skill Boundaries
- `workflow-plan-runner` owns approved plan/spec/package execution order.
- `workflow-bug-fix` owns concrete failure repair.
- `workflow-recovery` owns repeated failure-loop intervention.
- `analysis-codebase-design` owns module-boundary and deep-module design judgment before or after implementation.
- `workflow-minimal-implementation` owns YAGNI pressure; it does not replace implementation ownership.
- `workflow-rigor` owns evidence depth and completion discipline for risky changes.
- `workflow-validation` owns validation-only work and check matrices.
- `design-frontend` owns concrete visual UI implementation when the visual/design surface is primary.

## Invocation Examples
Positive:
- "이 API 필드 추가하고 테스트도 맞춰줘."
- "이 모듈을 기존 패턴대로 리팩터링해줘."
- "스크립트 옵션 하나 추가하고 검증까지 해줘."

Negative:
- "이 버그 원인만 분석해줘." -> `analysis-bug`
- "같은 테스트가 또 실패해. fake fix 말고 격리하자." -> `workflow-recovery`
- "이 승인된 plan package Phase 2를 실행해." -> `workflow-plan-runner`
