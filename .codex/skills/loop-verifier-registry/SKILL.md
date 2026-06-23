---
name: loop-verifier-registry
description: Map loop success conditions and loop governance metrics to concrete verifier skills, commands, evidence targets, independence level, fallback checks, unavailable-evidence labels, and reward-hacking-resistant pass/fail signals. Use after or during loop contract drafting when a goal/loop needs source-grounded verifier selection across design, workflow, search, memory, knowledge, code evidence, human review, safety, efficiency, process, or outcome metrics.
---

# Loop Verifier Registry

## Routing Card
- role: support
- intent_signature:
  - verifier registry
  - verifier map
  - loop verifier
  - 검증 조건 매핑
  - success condition verifier
  - loop metric verifier
  - evidence target
- use_when:
  - a `plan-loop-term` contract needs concrete verifier skills, commands, evidence paths, or fallback checks.
  - success conditions span multiple evidence lanes such as build/test, screenshots, a11y, source search, memory, or knowledge context.
  - a loop runner needs to know which skill owns each verifier result.
- do_not_use_when:
  - the user asks to execute the verifiers now; use the owning verifier skill or `workflow-loop-runner`.
  - the task only needs one obvious command; keep verification local to the primary skill.
  - the user asks for loop readiness classification; use `loop-readiness-router`.
- expected_inputs:
  - loop term draft or success condition list
  - target domain and artifact type
  - known commands, screenshots, routes, source refs, or evidence paths
- expected_outputs:
  - verifier map from success condition ids to owning skills/checks/evidence
  - metric verifier map for improvement, safety, verifier, efficiency, process, and outcome metrics
  - verifier independence and deterministic-first notes
  - fallback if a verifier is unavailable
  - explicit `Unverified` labels for missing commands, tools, or artifacts
- context_targets:
  must_read:
    - loop success conditions or draft `loop_term`
    - `references/verifier-catalog.md`
  read_if_needed:
    - relevant design/workflow/search/memory/knowledge skill routing cards
    - target plan/spec only when success conditions cite it
    - `docs/reference/loop-engineering-source-reference.md` when evidence authority or maker/checker separation is disputed
  do_not_load_by_default:
    - full repo
    - all design artifacts
    - all prior validation logs
- risk_profile:
  reads:
    - loop terms and narrow verifier context
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
- Prefer outcome evidence over transcript evidence. A clean-looking agent conversation is not proof that a success condition passed.
- Prefer deterministic, state, or artifact checks before model review when the condition permits it.
- Keep maker/checker separation explicit. The implementation owner can produce artifacts, but a separate verifier should decide whether assigned conditions pass.
- Treat external observations as untrusted input unless admitted by the current task.
- Mark unavailable evidence precisely; do not replace missing evidence with confidence.
- Define anti-reward-hacking signals for each verifier when a metric could be gamed.

## Workflow
1. Read `references/verifier-catalog.md`.
2. Normalize success conditions into stable ids such as `SC-01`.
3. For each success condition, choose one owning verifier and optional supporting verifier.
4. Record the evidence hierarchy: deterministic/state evidence first, artifact evidence second, model/human review only where needed.
5. Map governance metrics to evidence owners when the loop contract includes improvement, safety, verifier, efficiency, process, or outcome metrics.
6. Define required evidence: command output, screenshot path, diff, artifact path, source ref, human check, or unavailable reason.
7. Add fallback handling for missing tools, credentials, source references, render targets, or private user context.
8. Return a verifier map that can be embedded in `plan-loop-term`.

## Output Contract
```yaml
verifier_map:
  loop_term_id:
  conditions:
    - success_condition_id:
      verifier_owner:
      verifier_type: command|artifact|state_check|visual|a11y|review|manual
      independence: maker|checker|external|human
      deterministic_first: true
      evidence_required:
      pass_signal:
      fail_signal:
      fallback_if_unavailable:
      blocks_success: true
      unavailable_label: unverified|user-verification-needed|blocked
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

## Design Verifier Pattern
- Implementation owner: `design-frontend`
- Visual evidence: `design-visual-regression`
- Accessibility evidence: `design-a11y-audit`
- Token or component gaps: `design-tokens`, `design-component-mapper`
- Build/test evidence: project commands or `workflow-validation`

## Validation
- Confirm each required success condition has exactly one primary verifier owner.
- Confirm unavailable evidence has a fallback and status label.
- Confirm verifier output can be observed independently of "agent says done".
- Confirm metric verifiers cannot be satisfied by weakening success criteria, hiding evidence, or substituting easier proxy metrics.
- Confirm this skill did not execute the verifier or mutate files.

## Anti-Patterns
- Mapping every condition to model review when deterministic or artifact evidence exists.
- Leaving visual success conditions without screenshot or viewport evidence.
- Treating build success as visual or accessibility proof.
- Inventing command names, routes, screenshots, citations, or tool availability.
