# Analysis Codebase Map Reference

Load this file only when selecting views or rendering Mermaid.

## Altitude Precedence
- Honor an explicit `hld` or `lld` request before applying a scope heuristic.
- Without an explicit altitude, whole-repo/product scope defaults to `hld`; a named module/path/flow defaults to `lld`.
- A named-slice HLD stays inside that slice. An explicit LLD binds the detailed flow before selecting participants.
- Generic codebase-analysis/report wording keeps this same precedence and never revives the retired integrated report.

## View Catalog
- `hld`:
  - context: actors and external systems
  - container: deployable apps, workers, stores
  - sequence: one representative runtime story from entry to effect
  - state: only durable or user-visible state that the story depends on
  - deployment: only when compose/k8s/IaC/workflow evidence exists
- `lld`:
  - component: owners inside the bound slice
  - interface: contracts the slice exposes or consumes
  - sequence: the named flow, including cancel/failure if it changes control
  - state: transitions, stores, and who writes them

Every map includes a sequence. Skip a view rather than inventing participants.

## Evidence
- Names, folders, and import counts are leads.
- A sequence message needs a caller, a receiver, and a source or runtime ref.
- State needs a store, writer, and the transition that matters.
- Static topology does not prove runtime order. Missing runtime stays `Unverified`.
- Expand only when a new participant, store, or edge would change the diagram.
- Keep inventory and source inspection read-only. Do not create collector, findings, gate, or report artifacts.

## Mermaid Rules
- Prefer `sequenceDiagram`, `flowchart`, and `stateDiagram-v2`.
- Node labels are domain names, not `*.py` paths or function signatures.
- Edge labels are short actions. No `call`/`return`/`xN` tokens. No parentheses in flowchart edge labels.
- Keep one concern per diagram. Split when a chart needs a legend to stay readable.
- Each diagram lists `refs`. Heuristic or call-graph-only edges set `unverified: true`.

## Do Not
- Do not emit the old 10-chapter report, backlog tables, or quality-gate JSON.
- Do not draw HLD and LLD by default.
- Do not use file/import inventory as proof the map is complete.
- Do not turn the map into a ranked improvement list or a boundary verdict.
