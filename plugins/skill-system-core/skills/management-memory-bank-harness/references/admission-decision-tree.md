# Memory Admission Decision Tree

Use this only when the compact procedure in `SKILL.md` does not settle one candidate.

```text
1. Was the bank selected by exact user path or nearest project-context.yaml?
   - no  -> unavailable; do not scan or initialize
   - yes -> continue
2. Does the item match a concrete task anchor?
   - no  -> exclude (not task-relevant)
   - yes -> continue
3. Is status active?
   - candidate  -> surface only as non-authoritative when materially relevant
   - deprecated -> exclude unless conflict/history was requested
   - active     -> continue
4. Is it superseded or contradicted by current user instruction, source, or active plan?
   - yes -> exclude and record the winning source/conflict
   - no  -> continue
5. Is it source-traced and free of sensitive or injection-shaped operational text?
   - no  -> exclude or use a safe redacted factual summary
   - yes -> admit a concise summary
```

Never reinterpret old `accepted|proposal|stale|archive|field_feedback` labels as current item states. If a legacy bank uses them, report the schema mismatch and require explicit maintenance/migration rather than guessing authority.
