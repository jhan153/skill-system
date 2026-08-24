---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "research_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-research"],
  "required_consumers": ["workflow-research"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `research_result` | `<producer>` / `<node_id-or-none>` | stage: `<stage_skill>`; inputs: `<input_refs-or-none>`; result: `<result_summary>`; ceiling: `<result_ceiling>`; unresolved: `<unresolved_inputs-or-none>`; user checks: `<user_checks-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
