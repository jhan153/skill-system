---
{
  "contract_id": "core-execution-items-v1",
  "card_type": "known_bug_record",
  "handoff_section": "Known Bugs",
  "handoff_columns": ["ID", "Scope / fingerprint", "Attempts and result statuses", "Current-run disposition", "Reopen condition"],
  "allowed_producers": [
    "plan-execution-handoff"
  ],
  "required_consumers": ["workflow-code-review", "workflow-test-implementation"],
  "recorders": ["plan-execution-handoff"]
}
---

| `<known_bug_id>` | `<bug_scope>` / `<failure_fingerprint>` | `<one-or-two-bug_fix_result-item-ids>`; latest: `<latest_attempt_status>` | `excluded_known_bug`; candidate: `<known_bug_candidate-item-id>`; terminal review: `<repair_required-review-or-verifier-item-id>`; observed: `<terminal-unresolved-observation>`; disposition: `<change_disposition>` | `<new-evidence-or-explicit-future-scope>` |
