# Instruction Budget

Use this when a runtime instruction, spec packet, or plan bundle has grown too large.

## Budget Classes
- `runtime_terms`: minimal rules needed every turn.
- `skill_registry_metadata`: compact discoverability and route facts.
- `active_goal_brief`: current goal, non-goals, active plan ids.
- `active_plan_brief`: current tasks, risks, validation, next action.
- `reference_material`: details loaded only when needed.
- `memory_proposals`: durable facts or lessons awaiting memory workflow approval.
- `archived_raw_source`: preserved history, not default context.

## Split Rules
- Put stable operational rules in runtime terms.
- Put detailed procedures in skill or reference files.
- Put durable user preferences and decisions into memory proposals.
- Put raw history and closed plans into archive.
- Keep active plan briefs short enough to read before implementation.
- Do not include raw archives in the default context packet.

## Compact Packet Shape
```yaml
active_context_packet:
  runtime_terms_delta: []
  active_goal_brief: []
  active_plan_brief: []
  read_if_needed: []
  excluded_by_default: []
  memory_proposal_candidates: []
```
