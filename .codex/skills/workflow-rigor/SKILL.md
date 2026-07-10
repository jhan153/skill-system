---
name: workflow-rigor
description: Mode-based execution control for evidence-first implementation, scoped reporting, split validation, and review on medium/high-risk changes.
---

# Workflow Rigor

## Routing Card
- role: execution_modifier
- intent_signature:
  - `strict-evidence`, `strict-reporting`, `execution-strict`, `evidence-workflow`, `실행통제`
- use_when:
  - implementation, refactor, behavior-changing config/docs, or medium/high-risk changes need stronger proof and checker separation.
  - destructive, auth/security, schema/data, infra, external-side-effect, or cross-module work is in scope.
- do_not_use_when:
  - pure Q&A, brainstorming, harmless edits, or output formatting without execution risk.
  - the primary workflow already provides equivalent risk-specific gates and the user did not request extra rigor.
- expected_inputs:
  - selected primary workflow
  - change scope, consequence/coupling risk, and intended success signal
  - available validation and review surfaces
- expected_outputs:
  - selected mode and risk basis
  - decisive evidence, split validation, required review, and remaining uncertainty
- context_targets:
  must_read:
    - current request and primary workflow scope
    - planned or actual changed files when implementation is active
  read_if_needed:
    - risk-specific policy, validation contract, or failing output
  do_not_load_by_default:
    - full repo, full memory bank, unrelated plans, reports, or generic policy copies
- risk_profile:
  reads:
    - targeted evidence for the selected mode
  writes:
    - none directly; the primary workflow owns mutation
  tools:
    - targeted checks and read-only review tied to material risk
  sensitive_resources:
    - credentials default deny; runtime policy owns approvals and side-effect permission
- entry_scene:
  - PREPARE

## Modifier Contract
- Attach rigor requirements to the primary workflow; do not re-plan or reimplement its task.
- Runtime approval, sandbox, network, and protected-path policy remain authoritative. This skill controls proof depth, checker separation, and completion claims only.
- Select mode from consequence, coupling, reversibility, and verification difficulty—not file count or task duration.
- Add only checks that can expose a realistic failure mode. Equivalent gates already supplied by a specialist are reused, not duplicated.

## Modes

| mode | choose when | added gate |
| --- | --- | --- |
| `lite` | local, reversible, low-coupling change with an observable success signal | focused check; diff review only if uncertainty remains |
| `standard` | meaningful behavior change, moderate coupling, or non-trivial regression surface | explicit regression check plus self-review or independent review |
| `strict` | destructive work, auth/security, schema/data migration, infra, external writes, broad refactor, or explicit highest rigor | independent read-only review when available, plus rollback/readback evidence where relevant |

Escalate when new evidence widens consequence or coupling. De-escalate when discovery proves the risk local; do not keep `strict` merely because the work is large.

## Checkpoints
At the primary workflow's existing checkpoints, attach only these decisions:

1. `prepare`: select mode, name material risks, define observable success and required evidence.
2. `before side effect`: identify the applicable runtime approval and the rollback/readback signal; do not invent a parallel approval policy.
3. `validate`: run the narrow behavior check and the smallest risk-specific regression check.
4. `review`: perform the mode's required review against the diff and observed results; the implementation owner resolves or explicitly carries findings.
5. `finalize`: compare every completion claim with decisive evidence and report remaining uncertainty.

For `strict`, use an independent read-only reviewer when available and genuinely useful. The implementation owner retains integration and does not leak its expected verdict into the review prompt.

## Evidence Gate
- Accept observed diffs, command results, validator/verifier output, rendered behavior, or connector readback.
- Prefer a few decisive proofs over transcripts; name the surface each check covers.
- Separate `validation_agent` (actually observed) from `validation_user` (manual/runtime work still needed, or `N/A` with reason).
- A pass cannot override a conflicting diff, failed check, missing artifact, stale result, or uncovered required condition.
- GUI, credentialed, private-service, or unavailable-environment checks remain `user-verification-needed` or `unverified` until observed.
- Mark accepted risk only with approver, reason, affected condition, and revisit point.

## Escalation and Stop
- If the same stable failure survives an intervention, hand the failing slice to `workflow-recovery`; do not stack speculative patches.
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
- Read only changed/implicated code, the applicable validation contract, and risk-specific policy.
- If evidence is insufficient, expand one layer to the nearby module rule, source outline, or failing output; never load all repo docs, memory, or skills as recovery.
- This modifier cannot grant permission, create missing evidence, replace a specialist verifier, or prove behavior outside observed checks.

## Validation
- Mode matches consequence, coupling, reversibility, and verification difficulty.
- Added checks target material failure modes and do not duplicate specialist gates.
- Agent and user validation are separated, with contradictions kept visible.
- `standard`/`strict` review and relevant `strict` rollback/readback evidence are present or explicitly unavailable.
- Completion claims do not exceed the surfaces actually observed.
- Primary workflow scope and runtime permission policy remain unchanged.
