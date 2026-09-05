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

| Evidence ID | Claim ID | Acquisition | Source status | Relation | Basis | Locator | Directness / independence / recency | Limitation |
|---|---|---|---|---|---|---|---|---|
| `E-001` | `C-001` | `acquired \| partial \| inaccessible \| not_acquired` | `<identity=...; version=...; correction=...; retraction=...; only applicable facets>` | `supports \| contradicts \| mixed \| mentions \| not_assessed` | `<exact observed basis>` | `<URL, file/line, artifact, section, or receipt>` | `<compact assessment>` | `<limit or none>` |

The Source status cell carries independent facets, not a choice of one overall label. Identity is
`verified_identity`, `metadata_partial`, `unverified`, or `unknown`; version may record
`duplicate_version`, correction `corrected`, and retraction `retracted` when evidenced. Relevant
unestablished facets are `unknown`; omit only facets inapplicable to the source kind. Keep exact
locators for each asserted fact in Locator or the compact assessment. A negative check records its
source/date/scope, not universal absence of correction or retraction.

For example, a DOI-confirmed duplicate with a correction and retraction notice can retain
`identity=verified_identity; version=duplicate_version; correction=corrected; retraction=retracted`
together. This is a notation example, not a claim about an actual paper. No fact may be filled merely
to match it. Existing `Source identity` headings and scalar status cells remain readable: preserve
their declared fact and mark other relevant facets unknown when consuming them. A scalar
`corrected` alone does not establish identity or no retraction; reading never rewrites old records.

Keep contradictory, partial, dependent, and unavailable evidence visible. A conclusion is an
evidence disposition, not a machine-verified truth label. Do not add schema versions, migration
state, a validation script, or a parallel evidence database.
