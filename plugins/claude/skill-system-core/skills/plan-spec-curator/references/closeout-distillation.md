# Closeout Distillation

Use this when a plan is completed, abandoned, superseded, or archived.

## Closeout Packet
```yaml
plan_id:
final_state:
outcome:
durable_decision_candidates: []
lesson_candidates: []
failure_pattern_candidates: []
artifact_pointers: []
follow_up_items: []
archive_target:
future_load_policy:
verification_status:
```

## Distillation Rules
- Keep durable decisions short and reusable.
- Mark uncertain lessons as `Unverified`.
- Preserve artifact pointers instead of copying raw plan text.
- Separate memory proposals from actual memory mutation.
- Put follow-up ideas in a backlog or next active plan, not in default context.
- Do not preserve failed or abandoned plan text as active instruction.

## Memory Proposal Criteria
A candidate is memory-worthy only when it is:
- durable beyond the current task
- reusable across future tasks
- grounded in explicit user decision or verified evidence
- not a raw transcript, raw tool output, or speculative note
