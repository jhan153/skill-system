---
name: workflow-dependency-upgrade
description: Upgrade one dependency, runtime, framework, SDK, package, or lockfile with bounded migration and evidence from the canonical dependency state and actual selected path.
---

# Workflow Dependency Upgrade

## Routing Card
- role: primary
- intent_signature:
  - dependency/package/framework/SDK/runtime/lockfile upgrade; 의존성 업그레이드; 패키지 업데이트
- use_when:
  - the requested implementation centers on upgrading, pinning, replacing, or migrating dependency state and only the compatibility changes it requires.
- do_not_use_when:
  - ordinary feature work, choice analysis without edits, comments/docs-only work, validation-only planning, or security/release verdicts is primary.
- expected_inputs:
  - target and desired version/policy, package manager, canonical manifests/lockfiles, affected integrations, and allowed process/network boundary
- expected_outputs:
  - bounded dependency-state and migration changes, selected-version/path evidence, scoped validation, unresolved conditions, and rollback
- context_targets:
  must_read:
    - request, canonical manifests/lockfiles, current resolution, and affected production config/call sites
  read_if_needed:
    - authoritative release/migration contract, dependency graph, build/CI output, generated code, or actual integration readback
    - `references/execution_item_contract.md` when a concrete compatibility failure is delegated to Bug Fix and the upgrade owner must consume repair/review/Known Bug items
    - `references/execution_assurance_contract.md` when the upgrade has material maker/checker separation or auth/security, schema/data, infrastructure, external-write, destructive, or broad-migration risk
    - `workflow-implementation` paradigm references as non-owning shape context when the requested/required migration names a paradigm or implementation model; `workflow-dependency-upgrade` remains the migration owner
  do_not_load_by_default:
    - full repo/memory, unrelated dependency trees/reports, credentials, or raw production data
- risk_profile:
  reads: dependency state, integration path, authoritative contract, and validation output
  writes: scoped manifests/lockfiles plus only required config and production migration
  tools: package-manager resolution/update and condition-matched build/runtime checks
  sensitive_resources: deny credentials; network, private registries, lifecycle scripts, and destructive cleanup require their governing boundary
- entry_scene:
  - PREPARE

## Core Cards

- consumes after delegated repair or review: `references/core-execution-items-v1/cards/code_review_result.md`, `references/core-execution-items-v1/cards/deferred_item.md`, `references/core-execution-items-v1/cards/bug_fix_result.md`, `references/core-execution-items-v1/cards/known_bug_candidate.md`, `references/core-execution-items-v1/cards/known_bug_record.md`

## Workflow
1. Bind the target, requested range/policy, package manager, canonical files, non-goals, and material success conditions. Distinguish a version/behavior upgrade from an explicitly structural lockfile-only request.
2. Trace the current selected version and representative production use path through config, imports/call sites, every internal representation, unavoidable external translation, generated state, and runtime resolution. Use a user/public/canonical/external contract for required behavior; agent-authored tests may record that contract but do not create it.
3. Apply the canonical dependency change and every required lockfile, config, and production call-site migration directly. Canonical dependency state is real progress even when no code migration is required; interface/mock/test-only work is not. Keep one authoritative resolution and internal contract, update all in-scope consumers, and do not preserve an old package/source, adapter, shim, dual model, or fallback to make the diff smaller. An unmodifiable external SDK edge may use only thin stateless validation/translation to one canonical value or typed failure.
4. Validate each material condition with matching evidence: review lockfile graph churn, confirm the actually selected version, run compiler/build checks where applicable, and read back a representative actual integration when calls or runtime behavior are affected. A deterministic metadata-only lockfile request may use structural diff plus package-manager readback when those directly cover the user condition.
5. Apply `references/execution_assurance_contract.md` only when its trigger is material; preserve the upgrade owner and reuse equivalent compatibility review/readback instead of duplicating it.
6. Preserve every unresolved `fail`, `needs_review`, `unverified`, or `blocked` condition. Complete only the conditions directly covered; otherwise correct or roll back the scoped change and state the next evidence-producing action.

## Upgrade Rules
- Preserve the complete migration with the least conceptual machinery. Prefer direct calls, concrete types, existing package/runtime primitives, and composition; reject Clean Code-style wrapper/service/interface layers introduced only to isolate the upgrade or enable mocks.
- Preserve explicit user/canonical paradigm and implementation-shape conditions. Detailed `workflow-implementation` references are non-owning context; this workflow retains dependency migration ownership.
- Do not broaden a single-target request or accept unexplained transitive shifts. Required peer, engine, type, install, migration, or runtime-resolution failures remain failures; narrower tests cannot turn them into warnings.
- Required canonical/actual version mismatch or missing input fails closed. Remove stale cache, duplicate source, or legacy fallback and confirm the intended path rather than reporting manifest success.
- Run networked installs, private-registry access, or lifecycle scripts only when allowed. If they cannot run, an explicitly requested reversible manifest edit may remain partial, but installed/resolved status stays unverified and completion is false.
- Generated lockfiles must match the requested package manager and scope. Missing authoritative migration guidance stays explicit unless compiler and actual-path evidence directly establish the affected contract.

## Output Contract
Return only applicable fields: target/scope, changed canonical state and migrations, selected-version/path evidence, lockfile review, condition-scoped validation, unresolved conditions, rollback, and next action. Do not claim an upgrade from manifest text, mocks, agent-authored tests, or command exit alone.

## Cross-Skill Boundaries
- `workflow-implementation` owns unrelated feature work and accepted production-mechanism replacement; `analysis-algorithm` owns choice-only analysis; `workflow-source-maintenance` owns comment-only work in `comment_sync`; `report-critical` owns security/release verdicts; `analysis-performance` owns bottleneck diagnosis; the current task owner or named domain verifier owns validation-only requests. A concrete compatibility failure uses one assigned `workflow-bug-fix` intervention at a time only after bounded same-contract semantic admission; this upgrade owner consumes the attempt/review evidence and carries any final Known Bug.
- `workflow-implementation` paradigm references may constrain migration shape without transferring primary ownership.
