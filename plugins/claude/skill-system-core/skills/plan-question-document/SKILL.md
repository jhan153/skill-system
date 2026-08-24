---
name: plan-question-document
description: Create an explicitly requested Markdown question document for one answer owner who holds missing facts or decisions. Fit the artifact to the recipient and downstream decision, verify question coverage, and keep delivery external to this skill; do not use for live requirements discovery, broad surveys, or automatic sending.
disable-model-invocation: true
---

# Question Document

## Routing Card
- role: primary
- intent_signature: explicit local question document for one answer owner
- use_when:
  - the user explicitly requests a questionnaire or meeting-fill document for one person who owns a material knowledge gap.
- do_not_use_when:
  - the current user can resolve the questions through live discovery.
  - the requested work is audience-scale survey design, requirements distillation, interview facilitation without an artifact, or external delivery.
- expected_inputs: recipient role, knowledge ownership, decisions or facts needed back, downstream use, tone/language, effort or deadline constraints, optional output path, and optional Execution Handoff package/plan id
- expected_outputs: one recipient-ready Markdown file, a coverage readback, unresolved setup assumptions, and an explicit no-delivery statement; when package-bound, `inputs/question-documents/<topic>.md`
- context_targets:
  must_read:
    - current request and supplied recipient/outcome context
    - `references/execution_handoff_input_contract.md` before resolving a package-local path
    - [Question-document template](references/question-document.md) before authoring
  read_if_needed:
    - only supplied notes needed to give the recipient sufficient orientation
  do_not_load_by_default:
    - full repository, unrelated requirements, contact systems, private profiles, or unstated recipient data
- risk_profile:
  reads: current request and explicitly supplied supporting notes
  writes: one local Markdown artifact; prefer the associated package's `inputs/question-documents/` path when bound
  external_state: no sending, sharing, uploading, calendar creation, or messaging
  sensitive_resources: never request credentials, secrets, or personal/production data not required by the named decision
- entry_scene: PREPARE

## Separate Setup From Answer Ownership

The current user owns the document setup: who will answer, why their answer is needed, what decision follows, and any delivery constraints. The named answer owner owns the missing subject matter. Ask the current user only for unresolved setup that materially changes the artifact; write subject-matter questions for the recipient rather than asking the current user to guess those answers.

## Workflow

1. **Bind the recipient.** Record one recipient or role, what authority or knowledge they hold, and the relationship needed to choose vocabulary and context. If several independent owners are required, split the artifacts or return that ownership conflict instead of producing one ambiguous questionnaire.
2. **Bind the downstream decision.** Turn the user's desired outcome into a finite `needed_back` list. Each entry must be a fact, choice, approval condition, exception, or source pointer that a later owner can actually use.
3. **Set response constraints.** Use a concise professional default. Ask only when language, anonymity, deadline, expected effort, or required answer format materially changes what should be written.
4. **Design answerable prompts.** Assign one `needed_back` entry to one primary question, choose a suitable response shape, and add follow-ups only for branches that matter. Put authorization, blockers, and irreversible decisions before preferences.
5. **Write one artifact.** Use an exact requested path first. Otherwise, when an Execution Handoff package is bound, create `<package-root>/inputs/question-documents/<topic>.md`; without a package, create `question-document-<topic>.md` in the authorized workspace. Set `awaiting_response` at authoring. `answered` requires an actual returned response attributed to the answer owner. If file creation is unavailable, return the complete Markdown inline and identify that no file was written.
6. **Read back the contract.** Confirm every required answer is covered, every question serves a named downstream need, compound prompts are split, uncertainty can be stated, and sensitive or externally actionable requests have not slipped in.

## Authoring Rules

- Write to the recipient, not to the agent running the workflow.
- Give enough context to answer without copying the entire project history.
- Place the response field immediately after its question and make the expected answer shape visible.
- Allow partial, uncertain, unavailable, and delegated answers; silence must not be the only way to express uncertainty.
- Add rationale only where it changes how the recipient should answer.
- End with one opportunity to identify a missing constraint, owner, or source.
- Never fabricate an answer or treat completion of the document as receipt or approval.

## Output

Return `plan_id`, `recipient`, `needed_back`, `artifact_path | inline_fallback`, document status, `coverage_status`, `setup_assumptions`, and `external_delivery: not_performed`.
