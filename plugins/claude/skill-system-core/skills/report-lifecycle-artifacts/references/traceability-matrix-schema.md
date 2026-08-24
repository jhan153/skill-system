# Lifecycle Traceability Matrix Schema

```yaml
traceability:
  - relation_id: TRACE-001
    source:
      id:
      kind:
      ref:
      owner:
    condition:
    targets:
      - id:
        kind:
        ref:
    evidence_refs: []
    status:
    gaps: []
```

Use source-native IDs and kinds. Add no fixed lifecycle column when the selected package has no
matching artifact. A relation is a locator, not proof that its condition passed.
