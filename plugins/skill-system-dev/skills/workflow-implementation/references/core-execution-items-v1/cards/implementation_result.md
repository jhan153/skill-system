---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "implementation_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["design-frontend", "workflow-implementation"],
  "required_consumers": ["workflow-code-review", "workflow-test-design"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `implementation_result` | `<producer>` / `<node_id-or-none>` | snapshot: `<commit-diff-or-worktree-identity>`; design: `<design_result-item-id-or-none>`; changed: `<changed_artifacts-or-none>`; implemented: `<implemented_conditions-or-none>`; review slice: `<bounded-files-or-flow>`; unresolved: `<unresolved_conditions-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
