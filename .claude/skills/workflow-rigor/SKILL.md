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

If the task matches `do_not_use_when`, attach no rigor mode. `lite` applies only after a behavior-changing primary workflow is already active; it is not a reason to govern harmless text, formatting, or explanation work.

| mode | choose when | added gate |
| --- | --- | --- |
| `lite` | local, reversible, low-coupling change with an observable result | focused direct check; diff review only for remaining uncertainty |
| `standard` | meaningful behavior change, moderate coupling, non-trivial regression surface, or a material semantic claim resting mainly on maker-authored implementation and checks | direct behavior/regression evidence plus one relevant independent review axis when available |
| `strict` | destructive, auth/security, schema/data migration, infra, external-write, broad-refactor, or explicit highest-rigor work | separate independent Contract/Spec and Repository/Constraints passes when available, plus rollback/readback evidence where relevant |

Escalate when evidence widens risk; de-escalate when it proves risk local. Size alone does not require `strict`.

## Workflow
At the primary workflow's checkpoints:

1. `prepare`: select the mode; name each material condition, realistic failure, and deciding evidence.
2. `before side effect`: identify the runtime approval plus rollback/readback signal. This skill grants no permission.
3. `validate`: observe the direct result and smallest risk-specific regression surface.
4. `review`: pin the fixed point and inspect the diff/results on the applicable axes below; the implementation owner resolves or carries findings.
5. `finalize`: match material claims to deciding evidence and expose unresolved conditions.

## Review Axes And Independence

Pin one fixed point before review: the named commit/merge-base or the captured pre-change diff, plus the accepted request/spec/contract that defines intended behavior.

- `Contract/Spec`: check missing or partial requirements, wrong behavior, scope creep, and mismatches against the accepted source.
- `Repository/Constraints`: check repository instructions, architecture/ownership rules, accepted local patterns, compatibility, maintainability, and material defects introduced by the diff. Generic style preference is not authority unless the repository, accepted design, or an observable defect makes it relevant.

Keep the axes separate. A pass on one never masks a failure or unavailable input on the other, and the implementation owner aggregates without merging or reranking their findings.

For `strict`, run each applicable axis as a separate independent read-only review when subagents or equivalent reviewers are available. Give each reviewer the fixed point, raw diff/changed artifacts, and only its own governing sources; do not reveal the intended verdict, the maker's conclusion, or the other review. For `standard`, use at least one independent pass when a material completion claim otherwise depends mainly on maker-authored implementation, tests, or self-review; choose the axis most likely to falsify the claim. `lite` may remain self-reviewed.

If an independent reviewer is unavailable, report that axis as unavailable and lower the result label where it is material; do not call the maker's second pass independent. A review is judgment evidence, not an execution verifier, and it never turns a maker-authored test into an independent product oracle.

Reviewer availability changes execution states such as `batch_complete`, `phase_complete`, or `plan_complete` only when the accepted contract names review as an exit gate. Otherwise it changes the task-level evidence label while the underlying condition states remain governed by their direct evidence.

## Semantic Evidence Gate
- Name what each diff, command, validator, render, interaction, or readback proves. It decides only a matching condition.
- Static checks prove structure; mocks prove their boundary; an agent-authored test is a self-check for its asserted contract, not an independent oracle for an inferred user contract. A test derived from the same mistaken interpretation can pass while the product requirement still fails.
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
- `standard` and `strict`: `review_pass` with fixed point, axis, reviewer independence, findings, and unavailable inputs
- `strict` when relevant: `rollback_or_readback`, `remaining_uncertainty`
- blocked only: `blocked_condition`, `attempted_steps`, `next_action`

Omit empty optional fields. A separately requested report skill may shape presentation without changing these evidence requirements.

## Context Boundary
- Read changed/implicated code, its validation contract, and risk policy. Expand one layer to a nearby owner/rule or failing output only when needed.
- This modifier cannot grant permission, create missing evidence, replace a specialist verifier, or prove behavior outside observed checks.
- Before returning, confirm the mode matches actual risk, checks discriminate material failures without duplicating specialist gates, contradictions remain visible, and claims do not exceed observed surfaces.
