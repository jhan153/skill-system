---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "test_design_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-test-design"],
  "required_consumers": ["workflow-test-implementation", "workflow-code-review"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `test_design_result` | `<producer>` / `<node_id-or-none>` | design/scope: `<test_design_snapshot>` / `<test_design_scope>`; target/path: `<target_snapshot>` / `<actual_path>`; basis/conditions: `<test_basis_refs>` / `<condition_ids>`; profile/oracles: `<test_profile>` / `<oracle_contracts>`; environment/horizon: `<environment_and_horizon>`; diagnostics/falsifier: `<diagnostic_and_falsifier_contract>`; handoff: `<implementation_handoff>`; ceiling: `<proof_ceiling>`; human decisions: `<human_decision_refs-or-none>`; unresolved: `<unresolved_decisions_or_testability_gaps-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
