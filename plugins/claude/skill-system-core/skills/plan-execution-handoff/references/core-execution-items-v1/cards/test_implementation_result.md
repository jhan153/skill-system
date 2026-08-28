---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "test_implementation_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-test-implementation"],
  "required_consumers": ["workflow-code-review"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `test_implementation_result` | `<producer>` / `<node_id-or-none>` | scope/design/inline: `<implementation_scope>` / `<test_design_result_ref-or-none>` / `<inline_contract_refs-or-none>`; target/test assets: `<target_snapshot>` / `<test_asset_snapshot>`; changed: `<changed_test_artifacts-or-none>`; conditions: `<condition_results>`; execution/falsifier: `<execution_summary>` / `<falsifier_result>`; conformance/ceiling: `<design_conformance>` / `<proof_ceiling>`; exclusions: `<known_bug_exclusions-or-none>`; review slice: `<review_slice>`; unresolved: `<unresolved_design_testability_or_environment_gaps-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
