# Ingestion Packet & Event Schema

## Closeout packet example (approved)
```yaml
closeout_packet:
  source_artifact: docs/plan/2026-06-15-skill-grouping-plan.md
  approval_evidence: "user: 'approve memory promotion for the family decisions'"
  durable_candidates:
    - "skill families are the user-facing grouping; family is the registry source of truth"
    - "routers declare no writes"
  transient_excluded:
    - entry: "interim Phase A entry was search-paper-evidence"
      reason: superseded by search-router in Phase B
  sensitivity_check: "no secrets/PII present"
  target_memory_path: memory/project/skill-system.md
  maintenance_handoff: "dedupe against existing family notes"
```

## Ingestion event example (append-only)
```yaml
ingestion_event:
  timestamp: 2026-06-15T12:00:00Z
  source_artifact: docs/plan/2026-06-15-skill-grouping-plan.md
  accepted_entries:
    - "family is the registry source of truth"
    - "routers declare no writes"
  excluded_entries:
    - "interim Phase A entry (superseded)"
  approval_pointer: "chat 2026-06-15 approval"
  validation_status: user-verification-needed
```

## Blocked output example
```markdown
ingestion: blocked
- reason: no explicit approval for persistent memory mutation
- have: a proposal-only closeout packet from plan-spec-curator
- next: obtain explicit user approval, or route consolidation to memory-bank-maintenance
```
- Never write memory in a blocked state. Approval + approved packet are mandatory preconditions.
