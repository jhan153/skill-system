---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "bug_fix_result",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-bug-fix"],
  "required_consumers": ["workflow-code-review"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `bug_fix_result` | `<producer>` / `<node_id-or-none>` | round/review: `<A1-or-A2>` / `<code_review_result-item-id>`; fingerprint: `<failure_fingerprint>`; hypothesis: `<one-causal-claim>`; snapshot: `<changed_snapshot-or-none>`; signal: `<observation-or-unavailable-reason>`; status/disposition: `<attempt_status>` / `<change_disposition>`; postcondition: `<postcondition>`; candidate: `<known_bug_candidate-item-id-or-none>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
