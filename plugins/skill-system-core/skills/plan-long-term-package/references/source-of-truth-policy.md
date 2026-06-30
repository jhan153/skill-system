# Source Of Truth Policy

## Goal
Prevent multi-document planning packages from drifting into contradictory truth.

## Authority Map

| Concern | Canonical Document |
| --- | --- |
| Scope / Priority / Parity target | capability map |
| UI state names / transitions / error states | UI state contract |
| Module boundaries / extracted capabilities | integration contract |
| Release thresholds / datasets / pass-fail | release gate |
| Archetype-specific contract concern | matching `docs/spec/<slug>-<contract>.md` |
| Current execution status / approval / TODO | canonical dated plan |
| Navigation only | package README |

## Derived Documents
- README is derived
- phase/group docs are derived
- handoff index is procedural, not canonical for scope unless the package archetype is `documentation-handoff-package`
- group docs may propose contract changes, but they do not own canonical truth

## Drift Smells
- State names differ across docs
- README says a task is done while canonical dated plan says todo
- P0 capability exists only as a TODO
- Release gate has prose but no numbers
- A phase doc redefines an interface already owned by integration contract
- A group doc claims canonical ownership
- README contains authoritative checklist or status
- modifier-required docs are missing from `docs/spec/`
- package metadata declares one archetype while validation uses another

## Correction Rule
If two docs conflict:
1. choose the canonical document by the authority map
2. update the derived document
3. note the correction in the dated plan progress log
