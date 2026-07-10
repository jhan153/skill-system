---
name: memory-bank-update
description: Add, change, or deprecate an explicitly persistent project goal or cross-session rule using append-only events and current/archive reflection. Do not use for one-turn preferences, correction-mistake capture, initialization, or maintenance.
---

# Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature:
  - persistent goal or rule mutation, 메모리 goal/rule 수정
- use_when:
  - the user explicitly wants a goal or rule to persist across sessions.
- do_not_use_when:
  - persistence is ambiguous, the bank is missing, or the operation is correction capture/maintenance.
- expected_inputs:
  - target goal/rule, mutation (`create`, `update`, `deprecate`), and explicit persistent intent
- expected_outputs:
  - append-only event, reflected current/archive state, affected IDs, and validation status
- context_targets:
  must_read:
    - relevant meta/event state and the target current item
    - `.codex/docs/memory_mutation_contract.md` before a write
  read_if_needed:
    - `reference.md` for canonical schema and matching archive history for conflict resolution
  do_not_load_by_default:
    - full memory bank, unrelated project memory, or correction history
- risk_profile:
  reads:
    - targeted memory item and ledger state
  writes:
    - goal/rule event plus current/archive/meta reflection
  tools:
    - safe file and schema validation
  sensitive_resources:
    - credentials default deny; summarize private evidence
- entry_scene:
  - PREPARE

## Mutation Gate
Write only when the target is a `goal` or `rule`, the bank exists, and the user clearly intends persistence. A temporary instruction such as “이번 작업에서만” must not become memory.

Deletes become `status=deprecated`; never remove accepted history. Ambiguous targets require user verification before mutation.

## Workflow
1. Resolve the target item and latest snapshot version.
2. Confirm the operation belongs here rather than init, correction capture, or maintenance.
3. Build the canonical event and expected current/archive/meta result under one stable operation ID.
4. Apply the shared staging/replay contract and validate cross-file consistency before reporting success.

## Validation
- The event, current state, and archive entry agree on IDs and final state.
- A deprecation preserves history.
- Only the targeted goal/rule changed.
- Persistent intent is recorded without copying raw conversation text.

## Output
Report affected item/event IDs, final status, validation evidence, and unresolved conflict or user check. Do not emit the full bank.

## Behavior Cases
- Positive: “앞으로 모든 세션에서 release 전 smoke test를 필수 rule로 기억해줘.”
- Negative: “이번 턴에서는 smoke test를 생략해.” → temporary instruction, no memory write.
- Edge: the user names a rule ambiguously and two items match → `user-verification-needed`, no write.

## Known Limits
- Explicit persistence can still overfit a single event; the user owns the policy decision.
- Consistency validation does not establish that the new rule is objectively correct.
