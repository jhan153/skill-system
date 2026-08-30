---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "debugging_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-runtime-debugging"],
  "required_consumers": ["workflow-runtime-debugging", "workflow-bug-fix"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `debugging_result` | `<producer>` / `<node_id-or-none>` | mode/target: `<scope-or-operate>` / `<target-and-trigger>`; scope: `<debugging_scope>`; identity: `<identity_and_artifact_status>`; observations/perturbations: `<direct_observations-or-none>` / `<perturbations-or-none>`; causal: `<causal_status>` / `<cause_summary>`; next: `<next_discriminator>`; session: `<session_handoff>`; ceiling: `<proof_ceiling>`; repair/performance: `<repair_handoff-or-none>` / `<performance_handoff-or-none>`; unresolved: `<unresolved_conditions-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
