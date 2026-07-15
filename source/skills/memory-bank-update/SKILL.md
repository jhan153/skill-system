---
name: memory-bank-update
description: Add, change, or deprecate an explicitly persistent project goal or cross-session rule using append-only events and current/archive reflection. Do not use for one-turn preferences, correction-mistake capture, initialization, or maintenance.
---

# Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature: persistent goal or rule mutation, 메모리 goal/rule 수정
- use_when: the user explicitly wants an identifiable project goal or rule to persist across sessions
- do_not_use_when: persistence/target is ambiguous, the bank is absent, or init/correction/maintenance is primary
- expected_inputs: exact goal/rule, `create|update|deprecate`, existing bank state, and explicit persistent intent
- expected_outputs: append-only event/current/archive/meta reflection, affected IDs, and readback status
- context_targets: read targeted meta/event/current state and matching archive only; before writing load `.codex/docs/memory_mutation_contract.md` and `reference.md`
- risk_profile: mutate only the targeted goal/rule under a stable operation; credentials denied and private evidence summarized
- entry_scene: PREPARE

## Mutation Gate
Write only when the named canonical bank exists, the target is one identifiable `goal` or `rule`, and the user clearly intends persistence. Temporary instructions and inferred preferences never become memory. Ambiguous/missing targets or source mismatch require user verification or block; never initialize or select a stale bank as fallback. Deprecation sets `status=deprecated` and preserves accepted history.

## Workflow
1. Resolve the target item and latest snapshot version.
2. Confirm the operation belongs here rather than init, correction capture, or maintenance.
3. Build the canonical event and expected current/archive/meta result under one stable operation ID.
4. Apply the shared staging/replay contract, then read back event/current/archive/meta agreement, snapshot advancement, history preservation, and that only the target changed. Partial reflection remains failed/blocked.

## Output
Report gate decision, affected item/event IDs, final status, cross-file readback, and unresolved conflict/user check without emitting the full bank or raw conversation. Explicit persistence is the user's policy decision; consistency validation does not establish that the rule is objectively correct.
