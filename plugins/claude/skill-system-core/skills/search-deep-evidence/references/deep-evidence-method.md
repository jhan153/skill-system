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
- `source_status`: verified_identity, metadata_partial, duplicate_version, corrected, retracted, or unverified
- `claim_relation`: supports, contradicts, mixed, mentions, or not_assessed
- `evidence_basis`: exact source/code/runtime/visual basis
- `locator`: direct URL, file/line, artifact ID, or receipt
- directness, authority, independence, recency, and limitations

Source identity is not claim verification. Dependent sources are not independent votes.

## Adversarial verification
- Search for the strongest plausible contradiction and alternative explanation.
- Compare evidence predictions and provenance, not agent/source counts.
- Preserve `mixed` or `insufficient` conclusions when evidence conflicts or is unavailable.
- Never delete a contradicted claim to force a preferred conclusion.

## Handoff
Return a resolved claim–evidence matrix and name the owning synthesis/review skill. A valid resolution may be `supported`, `contradicted`, `mixed`, or `insufficient` with explicit missing evidence.
