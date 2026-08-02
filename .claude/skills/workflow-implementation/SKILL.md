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
  - the user wants a causal source/runtime explanation of existing code; use `report-implementation-explainer`.
  - an existing capability's product-facing behavior is still undecided and the user asks to resolve it; use `plan-behavior-discovery`.
  - the request is pure analysis, planning, review, validation-only, or other report generation.
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
    - `.claude/docs/delivery_slice_contract.md` when any requested change needs multiple executable batches, including a wide migration or non-feature decomposition
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
- Preserve the active user work contract before applying this workflow: core deliverables, allowed/excluded action classes, verification owner, interaction mode, continuation behavior, and stop terms. This workflow may fill an unspecified field but cannot reactivate an excluded test/validation/meta action or take verification back from the user.
- Implementation means the requested source, runtime config/build, or executable behavior. Plans, docs, mocks, interfaces, or tests alone are not completion unless they are the whole requested deliverable.
- Keep canonical source selection, domain policy, fallback, and failure behavior in the module that owns them. Adapters may translate shape; they must not silently choose those policies.
- Surface a missing or mismatched required/canonical input as a failing outcome or explicit user decision. Do not catch it into a placeholder, warning, legacy/lower-quality fallback, or success-looking partial result.

## Workflow
1. Compile explicit natural-language scope into the active work contract and classify the next actions as core, required prerequisite, optional validation/quality, or meta work.
2. State the observable success condition and one material negative or edge case.
3. Inspect the smallest real caller-to-output path, including the canonical source or policy owner when selection is involved.
4. Change that owner path with the smallest coherent diff. If more than one batch is necessary, name the `delivery_shape`: `vertical_slice` for feature behavior, `migration_sequence` for a wide mechanical compatibility change, or `evidence_unit` for non-feature work. A `single_batch` does not activate the delivery-slice contract. Reuse local patterns before adding a layer or dependency.
5. Observe the changed path only when agent verification is owned and allowed, using one existing verifier, direct observation, or focused smoke check that can expose the realistic failure. Add a regression test only when the user requested tests or the existing test system can cover a specific anchored regression without new framework, mock, fixture-family, or dependency work. When the user owns verification, skip this action and preserve `user-verification-needed`.
6. Inspect the diff for scope creep, accidental churn, missed callers, and policy-owning wrappers.
7. Report each material condition as evidenced, user-only, or unresolved.

## Evidence Gate
- Match each completion claim to the condition and surface the evidence actually covers. Structural checks prove structure; mocks prove the mocked boundary; agent-authored tests are regression/self-check evidence, not an independent semantic oracle.
- Require actual-path readback for source selection, migration, media/data transforms, adapters, and external boundaries. A lower-scope pass cannot replace it.
- A required `fail`, `needs_review`, `unverified`, or `blocked` condition stays open until evidence from that same condition resolves it.
- If direct observation needs unavailable GUI, credentials, or external state, return task state `user-verification-needed` or `unverified`; do not add a surrogate path and call it complete.
- If an optional verifier or permission is unavailable, defer that semantic intent and continue independent required implementation. Do not retry it as another command, GUI path, wrapper, probe, or new test; use `blocked` only when no required runnable work remains.
- If no suitable verifier exists, keep the implementation scope complete but lower its evidence label. Do not create validation-only work or repeat an unchanged check to promote the label.
- If a material semantic completion claim otherwise depends mainly on code and checks produced by the same agent, use the `workflow-rigor` standard independent review pass when available. This review does not replace direct condition evidence or become a second implementation owner.
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
