---
doc_type: source_of_truth_policy
canonical: true
status: draft
last_validated: Unverified
source_of_truth_for:
  - source-of-truth-policy
derived_from: []
---

# {{SLUG}} Source Of Truth Policy

## Authority Map
| Concern | Canonical Document | Derived Documents |
| --- | --- | --- |
| Scope / Priority / Parity target | capability map | README, phase/group docs |
| UI state names / transitions / error states | UI state contract | README, phase/group docs |
| Module boundaries / extracted capabilities | integration contract | README, phase/group docs |
| Release thresholds / datasets / pass-fail | release gate | README, phase/group docs |
| Archetype-specific contract concern | matching `docs/spec/<slug>-<contract>.md` | README, phase/group docs |
| Current execution status / approval / TODO | canonical dated plan | README, handoff index |
| Navigation only | package README | none |

## Derived Documents
| Document | Role | Must Not Own |
| --- | --- | --- |
| package README | navigation and rollup | scope, status, approval, release verdict |
| phase/group docs | execution decomposition | canonical scope, state ids, gate thresholds, interface ownership |
| handoff index | read order and procedural notes | scope, status, release verdict |

## Drift Smells
| Smell | Why It Matters | Correction |
| --- | --- | --- |
| State names differ across docs | implementation cannot identify one state machine | update UI state contract, then derived docs |
| README says done while canonical dated plan says todo | handoff status becomes unreliable | update README from dated plan |
| P0 capability exists only as TODO | release scope can silently shrink | add contract link or descoping decision |
| Release gate has prose but no numbers | QA cannot pass/fail the work | add numeric thresholds and evidence |
| Group doc claims canonical ownership | source-of-truth hierarchy is broken | move contract to `docs/spec/` |

## Correction Rule
1. Identify the canonical document for the concern.
2. Update the canonical document first.
3. Update derived documents to match.
4. Record the correction in the canonical dated plan.

## Validation Rule
- Validator must fail when derived docs redefine canonical state, status, scope, gate, or interface contracts.
