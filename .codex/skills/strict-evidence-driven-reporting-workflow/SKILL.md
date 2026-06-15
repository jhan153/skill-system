---
name: strict-evidence-driven-reporting-workflow
description: Mode-based execution control for evidence-first implementation, scoped reporting, split validation, and review on medium/high-risk changes.
---

# Strict Evidence-Driven Reporting Workflow

## Routing Card
- role: execution_modifier
- intent_signature:
  - `strict-evidence`, `strict-reporting`, `execution-strict`, `evidence-workflow`, `실행통제`
- use_when:
  - implementation, refactor, behavior-changing docs/config updates, or medium/high-risk changes need stronger evidence and validation discipline.
  - destructive, auth/security, schema/data, infra, external-side-effect, or cross-module changes are in scope.
- do_not_use_when:
  - pure Q&A, brainstorming, small harmless edits, or formal output formatting without execution risk.
- expected_inputs:
  - selected primary workflow
  - change scope and risk boundary
  - validation contract or command purpose
- expected_outputs:
  - selected rigor mode, evidence, changed files, split validation, review status, remaining uncertainty
- context_targets:
  must_read:
    - current request and selected primary skill output
    - changed files or planned write scope when implementation is active
  read_if_needed:
    - repo validation contract
    - risk-specific policy or module docs
    - failing output for recovery
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated plans or reports
- risk_profile:
  reads:
    - targeted evidence for the selected mode
  writes:
    - WRITE_CODEBASE only after scope and validation context are clear
  tools:
    - CALL_PROCESS for targeted checks only
  sensitive_resources:
    - credentials default deny; network and destructive actions require explicit boundary review
- entry_scene:
  - PREPARE

## Related Skills
- `strict-response-quality`: owns concise user-facing response structure.
- `deep-analysis-workflow`: owns repro and root-cause analysis when the failure mode is unclear or recurring.
- `plan-doc-workflow`: owns docs/plan synchronization and plan-state tracking when a planning conversation is active.
- `agent-critical-review`: can serve as an optional QA gate for medium/high-risk plans or outputs.

## Purpose
- This skill is a thin execution-control and reporting layer for implementation work.
- It strengthens evidence, validation, review, and blocked reporting without duplicating runtime approval policy.
- It is most useful for medium/high-risk changes, not every trivial edit.

## Hard Controls vs Soft Rules
- Hard controls belong to system/runtime policy: approval policy, sandbox mode, network access, protected paths, and destructive-action permissions.
- Soft rules belong to this skill: mode selection, evidence quality, validation split, review expectations, and blocked reporting.
- Never invent approval phrase whitelists when runtime policy already governs mutation.

## When To Apply
- Bug fixes, refactors, feature work, and behavior-changing docs/config updates.
- Especially useful for destructive changes, auth/security, infra, schema/data changes, external side effects, or cross-module edits.
- Skip for information-only requests, pure brainstorming, or trivial wording-only edits unless the user explicitly asks for strict execution discipline.

## Trigger Shortcuts
- `strict-evidence`
- `strict-reporting`
- `execution-strict`
- `evidence-workflow`
- `실행통제`

## Trigger Guard (Do Not Trigger)
- Information-only Q&A with no requested implementation.
- High-level brainstorming with no decision to execute.
- Pure rewrite/polish tasks with no behavior change.
- Small harmless edits where the extra workflow would add more cost than risk reduction.

## Activation Rules
- Activate directly when the skill is explicitly requested.
- Activate for medium/high-risk implementation tasks where stronger evidence and validation discipline are warranted.
- Do not auto-activate from vague keywords alone such as `탐색해` or `제대로`.
- If the task is low-risk, prefer `lite` mode or stay inactive unless explicitly requested.

## Rule Priority
1. Higher-level system/project/runtime safety policy
2. `deep-analysis-workflow` analysis procedure when active
3. This skill's mode, evidence, validation, and review contracts
4. `strict-response-quality` user-facing response schema when active

## Cross-Skill Resolution
- `deep-analysis-workflow` decides repro and root cause.
- `plan-doc-workflow` decides plan artifact location, synchronization, and plan-state sections when planning is active.
- This skill decides execution rigor, evidence requirements, and completion gates.
- `agent-critical-review` may run as an optional QA gate after planning or implementation when the user requests review.
- `strict-response-quality` decides how the final answer is presented to the user.
- If all three are active, use this order: DAW analysis -> evidence-driven execution -> SRQ final presentation.

## Default Flow
1. Select mode from actual risk and scope.
2. Gather only the evidence needed to justify the change.
3. Check runtime approval/sandbox requirements before mutating.
4. Implement with scope discipline.
5. Run split validation.
6. Perform a review pass when the selected mode requires it.
7. Report only the required fields with explicit `Unverified` markers where needed.

## Mode Selection
### Lite
- Use for local low-risk edits, usually within 1-3 files, with no destructive action, no external side effect, and low regression surface.
- Required fields: `mode`, `scope`, `changed_files`, `risks`, `evidence`, `validation_agent`, `validation_user`.
- Review pass is optional unless regression risk remains unclear.

### Standard
- Use for normal implementation work with moderate coupling or meaningful regression risk.
- Required fields: `mode`, `scope`, `changed_files`, `risks`, `evidence`, `validation_agent`, `validation_user`, `review_pass`.
- Use when behavior changes span multiple modules or require non-trivial verification.

### Strict
- Use for destructive changes, schema/data migration, auth/security, infra, external side effects, multi-package refactors, or when the user explicitly asks for highest rigor.
- Required fields: `mode`, `scope`, `changed_files`, `risks`, `evidence`, `validation_agent`, `validation_user`, `review_pass`, `remaining_uncertainty`.
- Prefer read-only parallel exploration/review/test-design agents when subagents are available; final writes stay with the main agent.

## Collaboration Rules
- Parallel exploration, risk review, and test-design work may be delegated when tooling supports subagents.
- Read-only sidecar agents are preferred for `strict` mode; the main agent owns final file edits, integration, and the closing report.
- Subagents must not revert or overwrite another agent's work.
- If subagents are unavailable, keep the same separation conceptually rather than faking collaboration.

## Planning Contract
- Plan depth must match the selected mode.
- Include changed files or modules, core change intent, key risks, and validation strategy for non-trivial work.
- If `plan-doc-workflow` is active, do not override its file location or plan-state sections; add only the evidence and validation depth required by the selected mode.
- Use a Mermaid diagram only when runtime interaction, control flow, or concurrency is materially relevant, or when the user explicitly asks for one.
- Do not force `sequenceDiagram` for every plan.

## Evidence Contract
- For exploration, cite the decisive file paths and line numbers.
- For changes, cite the decisive diff, snippet, or command output that supports the claim.
- Prefer a few high-signal proofs over exhaustive transcripts.
- Mark missing or incomplete proof as `Unverified`.

## Validation Contract
- Always split validation into two tracks:
  - `validation_agent`: checks the agent actually executed
  - `validation_user`: runtime/manual checks still needed from the user, or `N/A` with reason
- Never treat assumptions as a passed validation result.
- If GUI, credentials, or environment limits block a check, mark that item `Unverified`.

## Implementation Completion Gate
- For implementation, bug fix, refactor, UI implementation, or test repair requests, completion requires at least one non-documentation implementation artifact:
  - source code diff
  - test diff
  - runtime config or build diff directly required for behavior
  - generated executable scaffold or entry point
- Markdown-only, plan-only, spec-only, report-only, memory-only, or planning-manifest-only diffs do not satisfy implementation completion unless the user explicitly requested documentation/spec work only.
- Active plans are task input and optional status trackers; they are not implementation output.
- If target source files, test locations, or validation commands cannot be identified, continue targeted discovery first.
- If no non-documentation implementation diff is possible after targeted discovery, report `blocked` or analysis-only with the exact blocker and next action.

## Review Contract
- `standard` and `strict` mode require a self-review or review pass before completion whenever feasible.
- Review should focus on regression risk, behavior drift, missing tests, data-loss/security exposure, and scope creep.
- If a review pass was not feasible, mark it `Unverified` and explain why.

## Approval and Permission Rules
- Runtime approval policy and sandbox policy are the source of truth for whether a mutating action can run.
- Before approval, read/search, repro definition, static checks, dry runs, and non-mutating observations are allowed unless runtime policy says otherwise.
- Do not hardcode approval phrases as the policy.
- For destructive or high-side-effect actions, surface the risk and ask once if user intent is still ambiguous.

## Resource and Risk Boundary
- Reads: targeted code, docs, logs, diffs, and validation contracts tied to the active change.
- Writes: only the requested scope; READ-only analysis does not imply WRITE permission.
- Tool/process calls: require a clear purpose, non-destructive check, and validation relevance.
- Network access: require data boundary awareness and explicit need.
- Credential access: default deny.
- Generated artifacts: only requested implementation/report artifacts and validation outputs.
- Destructive actions: require explicit user intent and runtime approval policy.
- Required checkpoints: before WRITE, DELETE, CALL_PROCESS, NETWORK, CREDENTIALS, GIT_PUSH, or broad report generation.

## Recovery and Context Expansion
- If repo structure is unclear, read repo source outline first.
- If test command is unclear, read repo validation contract.
- If architecture boundary is unclear, read architecture rules or nearby module docs.
- If user goal is unclear, state the assumption rather than loading unrelated context.
- If verification fails, read the failing output and changed hunk before expanding wider.
- If execution rigor is not the right concern, return to scheduling and use a primary or output skill instead.
- Never recover by loading all memory, all repo docs, or all skills at once.

## Reporting Fields
- Treat these as required fields, not a rigid template.
- Use concise prose or bullets as appropriate, but ensure the selected mode's fields are present.
- Core fields:
  - `mode`
  - `scope`
  - `changed_files`
  - `risks`
  - `evidence`
  - `validation_agent`
  - `validation_user`
- Additional required fields:
  - `review_pass` for `standard` and `strict`
  - `remaining_uncertainty` for `strict`
- Optional when applicable:
  - `blocked_reason`
  - `next_action`

## Completion Criteria
- Do not report completion unless the selected mode's required fields are present.
- For implementation-class requests, do not report completion unless the Implementation Completion Gate is satisfied or the result is explicitly reported as `blocked`/analysis-only.
- A passed test alone is insufficient.
- If required proof or validation is missing, keep the gap explicit as `Unverified`, or report `blocked` when the next step is external.

## Blocked Report Contract
- When blocked, report only:
  - `exact_blocked_point`
  - `attempted_steps` (max 3)
  - `blocked_reason`
  - `next_action`
- Keep the next action singular and concrete.

## Repeated Failure Control
- If the same symptom repeats twice:
  1. Stop branching the solution space.
  2. Reduce scope and simplify the logic path.
  3. Change one suspected cause at a time.
  4. Record what was disproven before trying the next cause.

## Prohibited
- Fabricated facts, logs, outputs, system state, or completion claims
- Test-passing-only fake fixes
- Completion claims without evidence
- Scope drift beyond the active request
- User-facing `metrics:` line injection unless the user explicitly asks for metrics
- Fake collaboration claims when no delegated review/exploration actually occurred

## Known Limits
- This modifier cannot create missing evidence; it only enforces evidence handling.
- Validation commands can be blocked by permissions or tooling and must remain `Unverified` when not run.
- It does not override the primary skill scope or artifact contract.
- Generated-code semantics still require tests, runtime checks, or review evidence.
