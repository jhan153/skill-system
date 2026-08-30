---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "code_review_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-code-review"],
  "required_consumers": ["design-frontend", "workflow-bug-fix", "workflow-implementation"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `code_review_result` | `<producer>` / `<node_id-or-none>` | input/design/test-design: `<implementation_result-or-test_implementation_result-or-bug_fix_result-item-id>` / `<design_result-item-id-or-none>` / `<test_design_result-item-id-or-none>`; round/snapshot: `<review_round>` / `<implementation_snapshot>`; coverage/ceiling: `<covered-effects-axes-unassessed-conformance>` / `<static-proof-ceiling>`; disposition: `<pass-or-repair_required-or-complete_with_deferred_items>`; findings/advisories/deferred: `<findings-or-none>` / `<advisories-or-none>` / `<deferred_item_refs-or-none>`; exclusions: `<known_bug_exclusions-or-none>` | `<required-mermaid-review-artifact-ref>` / `<evidence_refs-or-none>` |
