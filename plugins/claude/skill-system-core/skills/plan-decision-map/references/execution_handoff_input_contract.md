# Execution Handoff Input Contract

Contract ID: `execution-handoff-inputs-v1`

This contract centralizes where persisted Planning artifacts live and when
`plan-execution-handoff` may treat them as execution input. It does not require persistence for an
ordinary one-shot answer and never creates a second execution state beside `plan.md` and
`handoff.md`.

## Package Root

Resolve the associated package root in this order:

1. exact package directory supplied by the user;
2. existing `plan.md` or `handoff.md` parent directory for the selected `plan_id`;
3. for explicitly durable pre-execution planning, `docs/plans/<plan_id>/` using the same identity
   rules as `plan-execution-handoff`.

The first persisted Planning artifact may create the package root and its own `inputs/` path. It
must not create placeholder `plan.md`, `handoff.md`, `reference.md`, or unrelated input files.
When no package root and no persistence intent exist, return the skill's normal inline result and
do not guess a path.

## Canonical Layout

```text
<package-root>/
├── plan.md
├── handoff.md
├── reference.md                         # optional, non-authoritative technical material
└── inputs/
    ├── decision-map/
    │   ├── index.md
    │   └── items/
    │       └── <decision-item>.md
    ├── behavior-decisions.md
    ├── requirements-discovery.yaml
    ├── requirements-contract.yaml
    └── question-documents/
        └── <topic>.md
```

Create only artifacts actually produced for the package. Empty directories and placeholder input
files are forbidden.

## Common Input Meaning

Every persisted input declares or exposes:

- artifact kind and associated `plan_id`;
- current status and the owner allowed to change that status;
- source/evidence references supporting material decisions;
- unresolved, assumed, deferred, or unanswered items;
- intended downstream consumer.

The artifact's type-specific template owns its fields. Do not wrap every document in a duplicate
generic payload merely to satisfy this contract.

## Type Bindings And Authority

| Producer | Path | Consumable status | Execution authority |
|---|---|---|---|
| `plan-decision-map` | `inputs/decision-map/index.md` plus `items/` | resolved item or `decision_complete` map | Only resolved decisions with source/evidence refs constrain the Plan. Open, claimed, excluded, and unshaped items remain visible but are not implementation instructions. |
| `plan-behavior-discovery` | `inputs/behavior-decisions.md` | `decision_ready` artifact with `decided` rows | A decided observable product behavior may constrain a node. Assumed, delegated, and open rows remain non-authoritative. |
| `plan-requirements-discovery` | `inputs/requirements-discovery.yaml` | `ready_for_distillation` | Discovery evidence and decisions are input to distillation; the record is not an accepted requirements contract. |
| `plan-requirements-brief` | `inputs/requirements-contract.yaml` | `accepted` | Accepted scope, non-goals, and observable criteria may govern Plan compilation. `proposed` remains review input only. |
| `plan-question-document` | `inputs/question-documents/<topic>.md` | `answered` | Only returned answers with owner/source attribution may feed Discovery or the Requirements Contract. `awaiting_response` is a request, not evidence. |

## Plan Consumption

`plan.md` records every consumed artifact in one `Input Artifacts` table with kind, path, status,
authority/owner, and consumed scope or IDs. The table points to source artifacts; it does not copy
their full content.

- `plan-execution-handoff` may read unresolved inputs to identify blockers, exclusions, or a
  required question, but only consumable statuses establish execution conditions.
- A missing or non-consumable input remains explicit. Do not silently promote it, fabricate an
  answer, or replace it with agent preference.
- Input artifacts never select a successor node or mutate `handoff.md`.

## Freeze And Revision

Inputs may evolve while the execution pair is still `proposed`. When execution is approved, the
Plan pins the consumed paths, statuses, and source/evidence anchors.

- Do not silently rewrite a pinned input during execution.
- A correction that preserves the same outcome, owner/boundary, DAG, and completion oracle uses an
  explicit Plan revision before Task State synchronization.
- A material change to any of those axes creates a sibling package with a new `plan_id` through
  Scope Admission.
- Human Test results, new worklists, and new design briefs always enter the new package's `inputs/`
  tree; they never reopen the closed Waterfall package.

## Inline Boundary

An inline Planning result is valid when no durable package or cross-session handoff is requested.
If that result later becomes Execution Handoff input, persist it once in the bound path above and
record its source conversation/artifact reference. Do not maintain competing inline and file
copies as separate authorities.
