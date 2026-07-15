---
name: workflow-implementation
description: Primary workflow for direct software implementation. Use when the user requests production code, API, script, config, build, or explicitly scoped test changes from current requirements. Do not use for behavior-preserving refactors, concrete bug fixes, approved plan execution, repeated failure recovery, or analysis/validation-only work.
---

# Workflow Implementation

## Routing Card
- role: primary
- intent_signature:
  - direct implementation
  - code change
  - add tests
  - implement feature
  - 구현
- use_when:
  - the user asks for a concrete code, test, script, API, config, or build change.
  - requirements are sufficient for a current-turn implementation slice.
  - the task is ordinary development work not already owned by a narrower specialist.
- do_not_use_when:
  - the user asks to execute an approved plan/spec/package; use `workflow-plan-runner`.
  - the user asks to fix a concrete failure or failing test; use `workflow-bug-fix`.
  - the user asks for behavior-preserving rename, move, extract, collapse, simplify, or restructure work; use `workflow-refactor-safely`.
  - the same failure has repeated after an attempted fix; use `workflow-recovery`.
  - the request is pure analysis, planning, review, validation-only, or report generation.
- expected_inputs:
  - requested behavior or change
  - relevant repository files and existing local patterns
  - explicit constraints, non-goals, and validation expectations when available
- expected_outputs:
  - scoped production-path change, condition-bound evidence, remaining gaps, and user-verification needs
- context_targets:
  must_read:
    - current implementation request
    - repository instructions such as `AGENTS.md`
    - target files or nearest existing patterns for the requested behavior
  read_if_needed:
    - adjacent callers, canonical data/source owner, package manifest, or validation contract
    - active plan only when explicitly referenced as task input
  do_not_load_by_default:
    - full repo
    - full memory bank
    - broad architecture reports
    - unrelated plans or transcripts
- risk_profile:
  reads:
    - targeted source, callers, tests, configs, manifests, and observed output
  writes:
    - WRITE_CODEBASE for the requested implementation scope
  tools:
    - CALL_PROCESS for focused build, test, lint, typecheck, smoke, or static validation commands
  sensitive_resources:
    - credentials default deny; destructive, network, data, or external-side-effect work requires explicit boundary review
- entry_scene:
  - PREPARE

## Contract
- Own ordinary coding work from requirement through the production-path change and its evidence.
- Implementation means the requested source, runtime config/build, or executable behavior. Plans, docs, mocks, interfaces, or tests alone are not completion unless they are the whole requested deliverable.
- Keep canonical source selection, domain policy, fallback, and failure behavior in the module that owns them. Adapters may translate shape; they must not silently choose those policies.
- Surface a missing or mismatched required/canonical input as a failing outcome or explicit user decision. Do not catch it into a placeholder, warning, legacy/lower-quality fallback, or success-looking partial result.

## Workflow
1. State the observable success condition and one material negative or edge case.
2. Inspect the smallest real caller-to-output path, including the canonical source or policy owner when selection is involved.
3. Change that owner path with the smallest coherent diff; reuse local patterns before adding a layer or dependency.
4. Observe the changed path with one existing verifier, direct observation, or focused smoke check that can expose the realistic failure. Add a regression test only when the user requested tests or the existing test system can cover a specific anchored regression without new framework, mock, fixture-family, or dependency work.
5. Inspect the diff for scope creep, accidental churn, missed callers, and policy-owning wrappers.
6. Report each material condition as evidenced, user-only, or unresolved.

## Evidence Gate
- Match each completion claim to the condition and surface the evidence actually covers. Structural checks prove structure; mocks prove the mocked boundary; agent-authored tests are regression/self-check evidence, not an independent semantic oracle.
- Require actual-path readback for source selection, migration, media/data transforms, adapters, and external boundaries. A lower-scope pass cannot replace it.
- A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until evidence from that same condition resolves it.
- If direct observation needs unavailable GUI, credentials, or external state, return `user_verification_needed` or `unverified`; do not add a surrogate path and call it complete.
- If no suitable verifier exists, keep the implementation scope complete but lower its evidence label. Do not create validation-only work or repeat an unchanged check to promote the label.
- After the same failure survives a targeted change, hand the failing slice to `workflow-recovery`.

## Output Contract
Return only the sections needed:
- `implementation_scope`
- `changed_artifacts`
- `validation`
- `review_notes`
- `user_verification_needed`
- `unverified_gaps`
- `next_step`
