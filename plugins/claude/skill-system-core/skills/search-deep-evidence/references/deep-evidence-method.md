# Deep Evidence Method

Use this reference only when a claim genuinely needs more than one evidence lane. The skill gathers
and assesses evidence; a report or research-synthesis owner writes the final narrative.

## Claim decomposition
- Split only where subclaims require different evidence or can fail independently.
- Record the claim scope, freshness need, and what observation would support or contradict it.
- Do not force a fixed number of angles or agents.

## Lane selection
| evidence kind | lane / owner |
| --- | --- |
| papers / citations | `search-paper-evidence` |
| source code / contracts | targeted code inspection or the owning analysis skill |
| runtime | authorized runtime observation from the owning workflow |
| visual / accessibility | `design-visual-regression` / `design-a11y-audit` |
| accepted memory | `management-memory-bank-harness` |
| declared project knowledge | `management-knowledge-base-read` (read-only) |
| explicitly selected LLM Wiki | `analysis-llm-wiki-context` (read-only) |
| current public facts | authoritative web sources |

Lane selection grants no new write, network, runtime, credential, or mutation authority. Named
skill owners are optional routing hints: use them only when exposed in the current session. A
missing owner leaves that lane unavailable; it does not require a sibling plugin, alias, or
substitute evidence.

## Evidence record
Record these axes separately:

- `acquisition_status`: acquired, partial, inaccessible, or not_acquired
- `source_status`: identity assessment plus independent source-kind-relevant version, correction, and retraction observations
- `claim_relation`: supports, contradicts, mixed, mentions, or not_assessed
- `evidence_basis`: exact source/code/runtime/visual basis
- `locator`: direct URL, file/line, artifact ID, or receipt
- directness, authority, independence, recency, and limitations

Source identity is not claim verification. Dependent sources are not independent votes.

Preserve the incoming facets together: identity uses `verified_identity`, `metadata_partial`,
`unverified`, or `unknown`; `duplicate_version`, `corrected`, and `retracted` belong to separate
version/correction/retraction facets and can all coexist. Bind each asserted fact to its locator.
A relevant unestablished facet stays `unknown`; an inapplicable facet may be omitted. Absence of a
flag is not evidence of absence, and a negative check names its source/date/scope.

When consuming legacy scalar `source_status`, retain exactly that fact and leave other relevant
facets unknown. Thus `corrected` alone neither verifies identity nor rules out retraction. Do not
rewrite old evidence records just to adopt facets, choose one status to discard another, or require
an artifact for a focused inline answer.

## Adversarial verification
- Search for the strongest plausible contradiction and alternative explanation.
- Compare evidence predictions and provenance, not agent/source counts.
- Preserve `mixed` or `insufficient` conclusions when evidence conflicts or is unavailable.
- Never delete a contradicted claim to force a preferred conclusion.

## Handoff
Return a resolved claim–evidence matrix and name the owning synthesis/review skill. A valid resolution may be `supported`, `contradicted`, `mixed`, or `insufficient` with explicit missing evidence.
