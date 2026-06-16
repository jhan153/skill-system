# Context Admission Test

Run this before loading long instructions, old plans, raw archives, field feedback, or tool outputs.

## Required Checks
1. Is the item directly connected to the current goal or explicit user request?
2. Is the item needed for the current task?
3. Is the lifecycle state `active`, or did the user explicitly request this item?
4. Is the item not `abandoned`, `superseded`, or `archived`?
5. Can a shorter summary safely replace the raw source?

## Decision Labels
- `admit_raw`: load the raw item now.
- `admit_summary`: load only a compact summary.
- `explicit_request_only`: do not load unless the user names it.
- `reject_load`: do not load for this task.
- `unverified`: state or relevance is unclear.

## Default Bias
- Prefer `admit_summary` over `admit_raw`.
- Prefer `explicit_request_only` for old plans.
- Prefer `reject_load` for abandoned or superseded items.
- Do not load full memory bank, full chat history, or all plans to answer an admission question.

## Report Shape
```markdown
context admission
- item:
- decision:
- reason:
- replacement summary:
- verification_status:
```
