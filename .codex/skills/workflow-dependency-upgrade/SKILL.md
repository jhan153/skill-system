---
name: workflow-dependency-upgrade
description: Implementation workflow for dependency, package, runtime, framework, SDK, or lockfile upgrades. Use when Codex must update versions, handle breaking changes, migrate APIs/config, refresh lockfiles, and validate compatibility without turning the task into a broad rewrite.
---

# Workflow Dependency Upgrade

## Routing Card
- role: primary
- intent_signature:
  - dependency upgrade
  - package upgrade
  - framework upgrade
  - SDK upgrade
  - lockfile update
  - runtime upgrade
  - 의존성 업그레이드
  - 패키지 업데이트
- use_when:
  - the user asks to upgrade, pin, replace, or migrate dependencies, runtimes, SDKs, frameworks, packages, or lockfiles.
  - compatibility, breaking changes, or generated lockfile updates are part of the work.
  - the implementation should be limited to dependency-related changes and required call-site fixes.
- do_not_use_when:
  - the task is ordinary feature work with no dependency change; use `workflow-implementation`.
  - the user asks only to evaluate dependency choices without modifying files; use `analysis-algorithm` or direct analysis.
  - a dependency change caused a repeated failure loop; use `workflow-recovery`.
  - the task is a security review or release verdict only; use `report-critical`.
- expected_inputs:
  - target dependency, runtime, SDK, framework, package, or manifest
  - desired version/range or upgrade policy
  - relevant package manager and validation expectations
- expected_outputs:
  - upgrade scope, manifest/lockfile changes, migration fixes, validation result, rollback/fallback, and remaining compatibility risks
- context_targets:
  must_read:
    - current upgrade request
    - package/runtime manifests and lockfiles
    - relevant source call sites or config touched by the dependency
  read_if_needed:
    - release notes or migration guide when provided or locally available
    - CI/build/test docs
    - generated code or type errors after upgrade
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated dependency trees
    - broad architecture reports
- risk_profile:
  reads:
    - manifests, lockfiles, dependency-related source/config, validation output, and migration docs
  writes:
    - WRITE_CODEBASE for manifests, lockfiles, required config, and call-site compatibility fixes
  tools:
    - CALL_PROCESS for package-manager commands, install/update, build, test, lint, typecheck, and smoke checks
  sensitive_resources:
    - credentials default deny; private registries, network fetches, scripts with side effects, and destructive cleanups require explicit boundary review
- entry_scene:
  - PREPARE

## Purpose
- Upgrade dependencies with bounded blast radius.
- Pair manifest/lockfile changes with required compatibility fixes.
- Validate the dependency surface rather than broadening into unrelated cleanup.

## Workflow
1. Identify the package manager, manifests, lockfiles, target dependency, and desired version/range.
2. Define the upgrade scope and non-goals.
3. Inspect current usage and compatibility-sensitive call sites.
4. Apply the smallest dependency change:
   - manifest version/range
   - lockfile refresh
   - required config or call-site migration
5. Run targeted validation:
   - install/update result
   - build/typecheck
   - focused tests for touched integration
   - smoke check when runtime behavior changes
6. Review generated lockfile churn for unexpected package shifts.
7. Report rollback/fallback when validation fails or the upgrade is too broad.

## Upgrade Rules
- Do not run broad package upgrades when one dependency was requested.
- Do not commit generated lockfile churn without checking whether it matches the requested scope.
- Do not bypass peer dependency, engine, or type errors without explaining the compatibility risk.
- Treat package-manager lifecycle scripts, private registries, and network installs as boundary-sensitive.
- Do not run networked package-manager commands or lifecycle-script-triggering installs unless the user or host policy has allowed network/process side effects for the current task.
- If package install/update cannot run safely, edit only manifest-compatible changes and mark lockfile/install validation as `user_verification_needed`.
- If migration docs are unavailable, mark the gap `Unverified` and rely on compiler/tests/runtime evidence.

## Output Contract
Return only the sections needed:
- `upgrade_scope`
- `changed_artifacts`
- `migration_fixes`
- `validation`
- `lockfile_review`
- `rollback_or_fallback`
- `remaining_risks`
- `next_step`

## Cross-Skill Boundaries
- `workflow-implementation` owns ordinary code changes not centered on dependency upgrades.
- `analysis-performance` owns performance bottleneck diagnosis before choosing dependency changes for speed.
- `workflow-recovery` owns repeated same-signature failures after upgrade attempts.
- `report-critical` owns security/release verdicts and blocker reviews.
- `workflow-validation` owns validation-only matrices for upgrade plans when installed or explicitly requested.

## Invocation Examples
Positive:
- "React 버전 올리고 깨지는 call site까지 고쳐줘."
- "이 SDK를 최신 minor로 올리고 lockfile 검증해줘."
- "Node runtime 업그레이드에 필요한 config와 테스트를 맞춰줘."

Negative:
- "어떤 라이브러리를 쓸지 비교해줘." -> `analysis-algorithm`
- "패키지 업데이트 후 같은 테스트가 계속 실패해." -> `workflow-recovery`
- "의존성 보안 위험을 리뷰해줘." -> `report-critical`
