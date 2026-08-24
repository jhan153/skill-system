# Persisted Evidence Set

Read this only when the user explicitly requests a persisted evidence artifact. Ordinary fact
checks and multi-claim responses remain inline.

Use Markdown so Codex, Claude, Grok, Antigravity, and a human reader can consume the same artifact
without a provider-specific runtime or validator.

## Scope

- Question or claim boundary:
- Freshness/date boundary:
- Included lanes:
- Unavailable lanes:

## Claims

| Claim ID | Statement | Conclusion | Missing evidence / limit |
|---|---|---|---|
| `C-001` | `<independently falsifiable statement>` | `supported \| contradicted \| mixed \| insufficient` | `<gap or none>` |

## Evidence

| Evidence ID | Claim ID | Acquisition | Source identity | Relation | Basis | Locator | Directness / independence / recency | Limitation |
|---|---|---|---|---|---|---|---|---|
| `E-001` | `C-001` | `acquired \| partial \| inaccessible \| not_acquired` | `verified_identity \| metadata_partial \| duplicate_version \| corrected \| retracted \| unverified` | `supports \| contradicts \| mixed \| mentions \| not_assessed` | `<exact observed basis>` | `<URL, file/line, artifact, section, or receipt>` | `<compact assessment>` | `<limit or none>` |

Keep contradictory, partial, dependent, and unavailable evidence visible. A conclusion is an
evidence disposition, not a machine-verified truth label. Do not add schema versions, migration
state, a validation script, or a parallel evidence database.
