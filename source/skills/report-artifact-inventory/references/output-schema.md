# Report Artifact Inventory — Output Schema

Use the smallest shape that answers the request. Omit empty sections.

## Compact final-response shape
```markdown
artifact inventory
- changed_files: src/foo.ts, src/foo.test.ts
- generated_artifacts: build/foo.js
- validation_evidence: `npm test foo` agent-verified (3/3)
- user_verification_needed: visual check of /foo route
- stale_followups: remove temp flag `FOO_DEBUG`
- excluded_items: unrelated lint warnings (out of scope)
```

## Handoff note shape
```yaml
artifact_inventory:
  task_id:
  changed_files: []
  generated_artifacts: []
  validation_evidence: []        # each item carries a label
  user_verification_needed: []
  stale_followups: []
  excluded_items: []
  handoff_note:
```

## Blocked / empty inventory shape
```markdown
artifact inventory
- status: blocked
- reason: no change set or artifact list available for this task
- next: provide the diff, changed file list, or the artifacts to inventory
```
- If there are genuinely no artifacts yet, say so explicitly rather than inventing entries.
- Validation evidence must carry a label: `agent-verified`, `user-verification-needed`, `unverified`, or `blocked`.
- Redact secrets/tokens in any quoted path or evidence; cite location only.
