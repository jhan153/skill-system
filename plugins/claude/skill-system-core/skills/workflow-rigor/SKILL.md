---
name: workflow-rigor
description: Risk-proportional evidence, review, and completion control for behavior-changing work.
disable-model-invocation: true
---

# Workflow Rigor

## Routing Card
- role: execution_modifier
- intent_signature:
  - `strict-evidence`, `strict-reporting`, `execution-strict`, `evidence-workflow`, `실행통제`
- use_when:
  - implementation or another behavior-changing task needs risk-proportional proof, checker separation, rollback, or readback.
- do_not_use_when:
  - pure Q&A, harmless edits, or formatting-only work; or the primary workflow already provides the same gates.
- expected_inputs:
  - primary workflow, scope, material conditions/risks, and evidence surfaces
- expected_outputs:
  - mode/risk basis, condition evidence, review, and uncertainty
- context_targets:
  must_read:
    - request, primary workflow scope, and planned/actual changed files
  read_if_needed:
    - risk-specific policy, validation contract, or failing output
  do_not_load_by_default:
    - full repo, memory, unrelated plans/reports, or policy copies
- risk_profile:
  reads: targeted evidence for the selected mode
  writes: none directly; the primary workflow owns mutation
  tools: risk-targeted checks, readback, and read-only review
  sensitive_resources: credentials default deny; runtime policy owns approvals and side effects
- entry_scene:
  - PREPARE

## Modifier Contract
- Attach rigor requirements to the primary workflow; do not re-plan or reimplement its task.
- Runtime policy remains authoritative; this skill controls only proof depth, checker separation, and completion claims.
- Select mode from consequence, coupling, reversibility, and verification difficulty—not file count or task duration.
- Add only checks that discriminate a realistic material failure. Reuse equivalent specialist gates.

## Modes

| mode | choose when | added gate |
| --- | --- | --- |
| `lite` | local, reversible, low-coupling change with an observable result | focused direct check; diff review only for remaining uncertainty |
| `standard` | meaningful behavior change, moderate coupling, or non-trivial regression surface | direct behavior/regression evidence plus self-review or independent review |
| `strict` | destructive, auth/security, schema/data migration, infra, external-write, broad-refactor, or explicit highest-rigor work | independent read-only review when useful plus rollback/readback evidence where relevant |

Escalate when evidence widens risk; de-escalate when it proves risk local. Size alone does not require `strict`.

## Workflow
At the primary workflow's checkpoints:

1. `prepare`: select the mode; name each material condition, realistic failure, and deciding evidence.
2. `before side effect`: identify the runtime approval plus rollback/readback signal. This skill grants no permission.
3. `validate`: observe the direct result and smallest risk-specific regression surface.
4. `review`: inspect the diff/results at the selected mode; the implementation owner resolves or carries findings.
5. `finalize`: match material claims to deciding evidence and expose unresolved conditions.

For `strict`, use an independent read-only reviewer when useful. Do not seed its verdict; review does not replace condition evidence.

## Semantic Evidence Gate
- Name what each diff, command, validator, render, interaction, or readback proves. It decides only a matching condition.
- Static checks prove structure; mocks prove their boundary; an agent-authored test is a self-check for its asserted contract, not an independent oracle for an inferred user contract.
- A lower-scope pass, clean review, or command exit cannot override conflicting runtime evidence, a missing artifact, stale output, or an uncovered required condition. Fix a conflict in its actual production owner and repeat the same deciding observation.
- Separate `validation_agent` (observed) from `validation_user` (user-only/unavailable, or `N/A` with reason). Name the exact user observation; GUI, credentialed, private-service, and unavailable conditions stay `user-verification-needed` or `unverified`.
- Mark accepted risk only with approver, reason, affected condition, and revisit point.

## Escalation and Stop
- If the same failure survives an intervention, hand its slice to `workflow-recovery`; do not stack speculative patches.
- Stop when the next required proof needs missing access, approval, external state, or user-only observation.
- When blocked, return the exact blocked condition, up to three attempted steps, and one next action.
- Never downgrade contradictory or missing evidence to completion because a lower-scope check passed.

## Output Contract
Return fields, not a second workflow narrative:

- all modes: `mode`, `risk_basis`, `scope`, `changed_files`, `decisive_evidence`, `validation_agent`, `validation_user`
- `standard` and `strict`: `review_pass`
- `strict` when relevant: `rollback_or_readback`, `remaining_uncertainty`
- blocked only: `blocked_condition`, `attempted_steps`, `next_action`

Omit empty optional fields. A separately requested report skill may shape presentation without changing these evidence requirements.

## Context Boundary
- Read changed/implicated code, its validation contract, and risk policy. Expand one layer to a nearby owner/rule or failing output only when needed.
- This modifier cannot grant permission, create missing evidence, replace a specialist verifier, or prove behavior outside observed checks.
- Before returning, confirm the mode matches actual risk, checks discriminate material failures without duplicating specialist gates, contradictions remain visible, and claims do not exceed observed surfaces.
