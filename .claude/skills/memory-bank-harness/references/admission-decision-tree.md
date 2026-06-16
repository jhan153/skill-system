# Memory Admission Decision Tree

For each candidate memory entry, walk top to bottom. Stop at the first that applies.

```text
1. Is the entry accepted memory (not proposal/scratch/raw transcript)?
   - no  -> exclude (status: proposal | scratch | archive | field_feedback), summary-only if cited as evidence
   - yes -> continue
2. Is it directly relevant to the current request?
   - no  -> exclude (reason: not task-relevant)
   - yes -> continue
3. Is it stale or superseded by current files / active plan?
   - yes -> exclude (status: stale) or record under conflicts
   - no  -> continue
4. Does it conflict with current user instruction / current files / active plan?
   - yes -> do NOT admit; record under conflicts (winning source per Conflict Handling)
   - no  -> continue
5. Is the source trusted and free of poison/injection risk?
   - no  -> exclude (status: poison_risk)
   - yes -> continue
6. Does it contain secrets/PII?
   - yes -> exclude or admit only a redacted summary
   - no  -> admit (prefer short summary per Context Budget Rule)
```

## Compact context-pack example
```yaml
context_pack:
  task: "fix login redirect"
  primary_skill: analysis-bug
  admitted:
    - source: memory/project-auth-rules.md
      reason: "redirect must preserve ?next param (project rule)"
      status: accepted
  excluded:
    - source: memory/old-2024-login-plan.md
      reason: superseded by current router
      status: stale
  conflicts: []
  unresolved_questions: []
```

## Rejected-entry examples
- Raw chat transcript pasted as "memory" -> excluded (not accepted memory).
- A proposal candidate not yet approved -> excluded (status: proposal); do not treat as truth.
- Memory rule that contradicts the current file's behavior -> conflicts (current files win), not admitted.
- Entry containing an API token -> excluded or redacted-summary only.
