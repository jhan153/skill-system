---
name: workflow-validation
description: Designs or runs focused validation plans for completed or planned changes. Use when the user asks for validation strategy, test/smoke/manual-check selection, verification matrices, or validation-only execution; attach as support during implementation when validation is the narrow concern.
---

# Workflow Validation

## Routing Card
- role: execution_modifier
- intent_signature:
  - validation plan
  - verification matrix
  - smoke test selection
  - 검증 계획
  - 검증만
  - 테스트/스모크/수동확인 매트릭스
- use_when:
  - the user asks how to validate an implementation, migration, plan, or changed artifact.
  - the user asks to run validation only after implementation is already complete.
  - an active implementation workflow needs a narrow validation support layer.
- do_not_use_when:
  - the user is asking to implement the change, not design or run validation.
  - the request is skill-system runtime usage eval; use `evaluation-harness`.
  - the user asks for critical verdicts, blockers, or risk review; use `report-critical`.
  - one obvious command is explicitly requested and no validation strategy is needed.
- expected_inputs:
  - changed files, planned change, or artifact under validation
  - success criteria, acceptance criteria, or risk boundary
  - available test/build/lint/smoke commands when known
- expected_outputs:
  - validation scope, check matrix, command/manual split, expected signal, status, and unverified gaps
- context_targets:
  must_read:
    - current validation request
    - changed artifact or plan/spec slice under validation
  read_if_needed:
    - repo validation contract
    - package scripts, test docs, or CI config
    - active plan/spec only when referenced as the validation source
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated test suites
    - eval cases unrelated to the target artifact
- risk_profile:
  reads:
    - target artifact, validation docs, and command output
  writes:
    - none by default; only update explicitly requested validation docs or tests
  tools:
    - CALL_PROCESS for targeted non-destructive checks when command purpose is clear
  sensitive_resources:
    - credentials default deny; external systems and destructive checks require explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Turn vague "검증해줘" requests into a scoped validation matrix.
- Separate agent-run checks from user/manual checks.
- Prevent validation work from becoming package approval, critical review, or broad repo audit.

## Activation
- Primary when the user's actual goal is validation planning or validation-only execution.
- Support when `workflow-plan-runner`, `workflow-rigor`, implementation work, or a plan/spec execution needs a validation layer.
- Do not displace the implementation owner.

## Workflow
1. Define the validation target and success criteria.
2. Classify checks as static, unit, integration, smoke, visual/manual, or environment-dependent.
3. Pick the smallest check set that gives meaningful confidence for the risk.
4. Run targeted commands only when safe and relevant.
5. Record passed, failed, skipped, blocked, and `Unverified` checks separately.
6. Recommend exactly one next validation action when confidence is still insufficient.

## Risk-Tier Check Sets
- Low risk: static/schema check or one targeted unit check; no broad suite unless the change touches shared behavior.
- Medium risk: static plus targeted unit/integration check; add smoke check when runtime behavior changes.
- High risk: targeted static/unit/integration plus smoke or manual check; require rollback/fallback note for release-affecting changes.

Do not use risk tier to inflate validation. Pick the narrowest set that can detect the realistic failure mode.

## Change-Type Heuristics
| Change type | Minimum useful checks |
| --- | --- |
| Config or schema | schema/config validation, startup smoke, default-value check |
| API or contract | contract test, integration smoke, caller compatibility check |
| UI or visual behavior | component/unit check when available, browser smoke, screenshot/manual visual check |
| Migration or data transform | dry-run or fixture migration, rollback check, data shape assertion |
| Build/runtime config | build command, startup smoke, environment variable/default check |
| Test-only change | failing-test reproduction when possible, targeted test run, assertion quality review |
| Documentation-only change | link/path check or no runtime validation; mark behavior as not exercised |

## Support Handoff
When attached to `workflow-plan-runner`, return validation results in batch terms:
- batch id or change intent
- check selected and why
- agent-run result
- user/manual result needed
- unverified gap
- next validation action

## Output Contract
Return only the sections needed:
- `validation_target`
- `risk_boundary`
- `risk_tier`
- `checks_to_run`
- `agent_verified`
- `user_verification_needed`
- `unverified_gaps`
- `next_validation_action`

## Cross-Skill Boundaries
- `workflow-rigor` owns execution rigor and completion gates for implementation.
- `workflow-plan-runner` owns plan/spec-driven implementation order.
- `workflow-recovery` owns repeated failure-loop recovery.
- `evaluation-harness` owns skill-system eval case review, not product validation.
- `report-critical` owns QA verdicts and blocker findings.

## Known Limits
- Validation can only confirm the covered behavior and environment.
- Missing commands, credentials, GUI access, or external services remain `Unverified`.
- Passing checks do not prove full release readiness unless the release gate explicitly says so.

## Invocation Examples
Positive:
- "이 변경을 어떻게 검증할지 validation matrix만 짜줘."
- "이 UI 변경은 어떤 smoke/manual check가 필요해?"
- "구현은 끝났고 검증만 실행해줘."

Negative:
- "이 플랜대로 구현해줘." -> `workflow-plan-runner`
- "이 테스트 하나만 다시 실행해줘." -> direct command, no validation matrix
- "이 결과가 release-ready인지 비판적으로 판단해줘." -> `report-critical`
