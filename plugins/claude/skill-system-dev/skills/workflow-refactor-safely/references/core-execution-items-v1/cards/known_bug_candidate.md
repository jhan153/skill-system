---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "known_bug_candidate",
  "handoff_section": "Execution Items",
  "handoff_columns": ["Item ID", "Kind", "Producer / node", "Compact outcome", "Artifact / evidence refs"],
  "allowed_producers": ["workflow-bug-fix"],
  "required_consumers": [],
  "recorders": ["plan-execution-handoff"]
}
---

| `<item_id>` | `known_bug_candidate` | `<producer>` / `<node_id-or-none>` | scope/fingerprint: `<bug_scope>` / `<failure_fingerprint>`; expected/observed: `<condition-and-authority>` / `<latest-unresolved-observation>`; attempts: `<one-or-two-bug_fix_result-item-ids>`; latest status: `<latest_attempt_status>`; disposition: `<change_disposition>`; reopen: `<new-evidence-or-explicit-future-scope>` | `<artifact_refs-or-none>` / `<evidence_refs-or-none>` |
