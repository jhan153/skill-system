# Deep Evidence Method

This reference details the `search-deep-evidence` sweep. The skill owns evidence
gathering and verification only; final synthesis is handed to a report or
research-synthesis skill.

## 1. Angle decomposition
- Split the topic/claim into 3-6 angles that fail differently (definition, mechanism, counter-evidence, recency, scale/limits, adversarial/critique).
- Each angle must be independently searchable so one blind spot does not hide evidence.

## 2. Lane mapping (via search-router)
| evidence kind | lane / owner |
| --- | --- |
| papers / citations | `search-paper-evidence` |
| codebase | `analysis-codebase` / `analysis-bug` evidence phase |
| runtime | `workflow-rigor` evidence phase |
| visual | `design-visual-regression` / `design-a11y-audit` |
| memory | `memory-bank-harness` |
| project knowledge | `knowledge-context-harness` (read) |
| open web | web search when permitted |

## 3. Evidence ledger discipline
- Reuse `search-paper-evidence` rules: no citation without a source; never fabricate DOI, arXiv ID, venue, dataset, metric, or result.
- Record per entry: claim, source/identifier, evidence role (support | contradict | context), finding query.

## 4. Adversarial verification
- For each falsifiable claim, run N independent skeptics (default 3) that try to REFUTE using the cited source.
- Kill the claim when a majority refute (default 2 of 3). Keep verdict: `confirmed | refuted | partial` with the vote tally.
- Prefer outcome/source evidence over transcript assertion; diverse skeptic lenses beat identical ones.

## 5. Citation-status labels (shared with search-paper-evidence)
- `verified`: claim has a real, retrievable source and survived adversarial verification.
- `unverified`: source missing, unreachable, or verification inconclusive.
- `fabricated-risk`: citation/identifier could not be confirmed to exist; treat as non-evidence until checked.

## 6. Handoff
- Output the verified evidence set and name the owning skill for synthesis
  (`report-critical`, `report-qualitative`, or `research-literature-synthesis`).
- Mark missing evidence and `Unverified` inputs explicitly; never invent to fill gaps.
