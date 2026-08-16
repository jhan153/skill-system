# Plan Decision Map Schema

Use an exact user-provided path when supplied. Otherwise place local artifacts under `docs/decision-map/<topic>/`, with `index.md` as the canonical overview and item files under `items/`. Use an external tracker only when the user separately authorizes that service, project, and mutation.

## Canonical Index

```markdown
---
kind: decision_map
decision_owner: <person, role, or accepted rule>
storage: local_markdown | <authorized tracker>
status: framing | active | decision_complete | closed
---

# <Decision-map title>

## Target Outcome

<Observable condition that ends decision mapping.>

## Stable Constraints

- <Constraint that every item must preserve>

## Resolved Decisions

- [<Decision name>](<item link>) — <one-line result>

## Ready Set

- [<Open item name>](<item link>)

## Unshaped Unknowns

- <Material uncertainty that still lacks a precise question>

## Exclusions

- <Excluded work> — <boundary reason>
```

`Ready Set` is a derived view. Refresh it from item headers whenever an item, prerequisite, or claim changes; item state remains authoritative.

## Decision Item

```markdown
---
kind: decision_item
item_id: DM-001
item_type: evidence | choice | prototype | enabler
interaction: agent_runnable | user_guided
state: open | claimed | resolved | excluded
decision_owner: <person, role, or accepted rule>
claim_owner: null
requires: []
evidence_refs: []
---

# <Decision item name>

## Decision Need

<One question or prerequisite and why the target outcome depends on it.>

## Acceptance For This Item

<What observation or owner answer is sufficient to close this item.>

## Resolution

<Result, rationale, decisive evidence, counterevidence, and remaining uncertainty.>
```

## Derived Readiness

An item belongs in the ready set only when:

- `state` is `open`;
- `claim_owner` is `null`; and
- every id in `requires` has state `resolved`.

An excluded prerequisite does not silently unblock its dependents. Reassess each dependent item and either replace the prerequisite, narrow the item, or exclude it with a reason.

## Consistency Rules

- Detailed evidence and rationale live on one item only; the index links a short result.
- A newly discovered question receives a new stable id. Never repurpose a resolved item.
- An unshaped unknown becomes an item only after its question and completion evidence can be stated.
- An exclusion is not a resolved decision and does not count toward completion.
- Assets stay beside or behind the owning item and are linked rather than copied into the index.
- Before changing claims or prerequisites, read current item headers and preserve concurrent updates.
