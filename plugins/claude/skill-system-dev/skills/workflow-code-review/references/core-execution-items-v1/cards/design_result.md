---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "design_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-ui-design"],
  "required_consumers": ["design-frontend", "workflow-code-review"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `design_result` | `<producer>` / `<node_id-or-none>` | snapshot/target: `<design_snapshot>` / `<target_surfaces>`; requirements: `<requirements_refs>`; frames/states: `<viewports_and_states>`; visual decisions: `<visual_decisions>`; token/component intent: `<token_and_component_intent>`; implementation handoff: `<implementation_handoff>`; unresolved: `<unresolved_decisions-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
