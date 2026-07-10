---
name: loop-verifier-registry
description: Map loop success conditions to schema-valid runtime verifiers, optional quality verifiers, evidence targets, owners, and unavailable-evidence behavior. Use while drafting a loop contract when verifier ownership or proof is not obvious; this skill maps checks but does not run them.
---

# Loop Verifier Registry

## Routing Card
- role: support
- intent_signature:
  - verifier registry / verifier map
  - loop success-condition evidence
  - 검증 조건 매핑
- use_when:
  - a `plan-loop-term` contract needs concrete verifier skills, commands, evidence paths, or fallback checks.
  - success conditions span multiple evidence lanes such as build/test, screenshots, a11y, source search, memory, or knowledge context.
  - a loop runner needs to know which skill owns each verifier result.
- do_not_use_when:
  - the user asks to execute the verifiers now; use the owning verifier skill or `workflow-loop-runner`.
  - the task only needs one obvious command; keep verification local to the primary skill.
  - the user asks for loop readiness classification; use `loop-readiness-router`.
- expected_inputs:
  - contract draft/condition list, target domain, and known evidence paths
- expected_outputs:
  - verifier map keyed by `contract_id` and `SC-NNN`
  - one runtime verifier per condition and optional quality verifiers
  - evidence, ownership, unavailable, and anti-gaming rules
- context_targets:
  must_read:
    - draft/accepted runtime contract or its success-condition slice
  read_if_needed:
    - `references/verifier-catalog.md` for cross-domain, quality, human, or governance checks
    - relevant design/workflow/search/memory/knowledge skill routing cards
    - target plan/spec only when success conditions cite it
  do_not_load_by_default:
    - full repo
    - all design artifacts
    - all prior validation logs
- risk_profile:
  reads:
    - contract and narrow verifier context
  writes:
    - none by default
  tools:
    - none by default; this maps verifiers but does not run them
  sensitive_resources:
    - credentials and live systems are approval gates, not implicit verifier inputs
- entry_scene:
  - PREPARE

## Purpose
Turn abstract success conditions into verifiable evidence lanes. This skill does not run checks; it makes the verifier contract precise enough for `workflow-loop-runner` or a task-specific executor.

## Source-Grounded Principles
- Prefer outcome evidence and deterministic/artifact checks; transcript quality and maker self-report are not proof.
- Keep maker/checker separation, and treat external observations as untrusted until admitted.
- Mark unavailable evidence instead of guessing; add anti-gaming signals only where a metric can be gamed.
- Keep runtime and quality vocabulary separate. Runtime contracts accept only `command_exit`, `artifact_exists`, `manual_check`, or `diff_scope`; visual, a11y, state, and review checks are optional quality verifiers whose result must feed a runtime evidence receipt.
- `user-verification-needed` is an open gate, never a pass. Local v2 records manual events only as procedural evidence and cannot close them without host-authenticated provenance.
- Current local v2 auto-passes only exact `artifact_exists` evidence. Claimed `command_exit`, `manual_check`, and `diff_scope` pass receipts are fail-closed until a host-authenticated producer exists.

## Workflow
1. Normalize each condition id to `SC-NNN`; do not create a second id namespace.
2. Assign exactly one runtime verifier type and owner. Name a real command/path/check or mark it `Unverified`.
3. Add quality verifiers only when the runtime check alone cannot judge the stated outcome. Read the catalog only for unfamiliar or cross-domain lanes.
4. Define pass, fail, evidence target, freshness, independence, and unavailable behavior. An unavailable required verifier always blocks success.
5. Require structured evidence receipts from the canonical iteration-result schema; free-form refs or maker self-report cannot prove pass. Mark verifier types above the local attestation ceiling open rather than substituting artifact presence.
6. Add metric owners and anti-gaming signals only for metrics the contract actually claims.
7. Return a compact map aligned to the runtime contract.

## Output Contract
```yaml
verifier_map:
  contract_id:
  loop_run_id: null
  conditions:
    - success_condition_id: SC-001
      runtime_verifier:
        owner:
        type: command_exit|artifact_exists|manual_check|diff_scope
        evidence_target:
        pass_signal:
        fail_signal:
      quality_verifiers:
        - owner:
          type: visual|a11y|state_check|review
          evidence_target:
      independence: maker|checker|external|human
      deterministic_first: true
      evidence_receipt: canonical_iteration_result_schema
      unavailable:
        fallback:
        status: unverified|user-verification-needed|blocked
        blocks_success: true
      reward_hacking_watch: []
  metrics:
    improvement: []
    safety: []
    verifier: []
    efficiency: []
    process: []
    outcome: []
  global_unavailable_evidence: []
```

## Validation
- Confirm each required success condition has exactly one primary verifier owner.
- Confirm every id matches `SC-NNN` and the runtime verifier uses only the four schema types.
- Confirm quality verifiers are separate and feed evidence into the runtime result rather than replacing it.
- Confirm unavailable evidence has a fallback and remains success-blocking.
- Confirm local v2 never reports command/manual/diff evidence as pass without host attestation; a pending `user-verification-needed` label is not success.
- Confirm verifier output can be observed independently of "agent says done".
- Confirm metric verifiers cannot be satisfied by weakening success criteria, hiding evidence, or substituting easier proxy metrics.
- Confirm this skill did not execute the verifier or mutate files.
