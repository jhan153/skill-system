# Evidence Ledger v2 Artifact Shape

Read this reference only when the user explicitly requests a persisted/full evidence ledger or when a schema-v1 ledger must be migrated. Focused fact-check responses do not need this wrapper.

The verifier expects `schema_version: 2`, a non-empty `claims` list, one `conclusion` per claim, and nested evidence records. An `insufficient` claim needs `missing_evidence`; `retained: false` also needs `exclusion_reason`.

```yaml
schema_version: 2
claims:
  - id: C-001
    statement: "The canonical bundle stores skill packages under source/skills."
    conclusion: supported
    evidence:
      - acquisition_status: acquired
        source_status: verified_identity
        claim_relation: supports
        evidence_basis: source_tree
        locator: source/skills
```

Allowed conclusions are `supported`, `contradicted`, `mixed`, and `insufficient`. Every acquired/partial record needs a locator; partial or metadata-partial evidence also needs a limitation. Run:

`python3 .codex/tools/check_evidence_ledger.py <ledger.yaml>`

For a v1 input, use `--print-migrated-v2` to print a conservative review-required v2 projection without modifying the original file.
