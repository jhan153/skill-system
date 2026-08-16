---
name: analysis-codebase-map
description: Model a repository or named slice as evidence-linked Mermaid architecture maps. Honor an explicit HLD/LLD request; otherwise use HLD for whole-repo/product scope and LLD for a named module, path, or flow. Generic codebase-analysis report wording resolves to this map, not the retired findings report. Do not use for one-boundary decisions, ranked improvement scans, bug RCA, or explicit findings/quality-gate requests.
---

# Analysis Codebase Map

## Routing Card
- role: primary
- intent_signature: architecture map, HLD/LLD modeling, sequence/state/structure diagrams
- use_when:
  - the user wants to understand how a repo or named slice is structured and how it runs.
  - the expected output is Mermaid maps of flow, structure, or state—not a findings backlog or one design verdict.
  - generic codebase-analysis or codebase-report wording has no explicit findings, backlog, or quality-gate contract; satisfy it with this compact map.
- do_not_use_when:
  - one module/seam/adapter decision is needed; use `analysis-boundary-design`.
  - the user wants ranked improvement candidates; use `analysis-architecture-deepening`.
  - the cause of a failure is unknown; use `analysis-bug`.
  - the request is domain language, performance RCA, direct implementation, or an explicit findings/quality-gate artifact.
- expected_inputs: repo root or named slice, the question to understand, any explicit HLD/LLD choice, and any required runtime/state focus
- expected_outputs: altitude (`hld` or `lld`), Mermaid diagrams with captions and source refs, and explicit `Unverified` gaps
- context_targets:
  must_read:
    - the map request, repo or named-slice outline, and one representative entrypoint-to-output path
  read_if_needed:
    - callers, manifests, state stores, and a disconfirming path that would change a diagram
    - `reference.md` for view selection and Mermaid render rules
  do_not_load_by_default:
    - full repo, bulk inventory dumps, prior reports, memory, or unrelated docs
- risk_profile:
  reads: targeted source, callers, manifests, and observed runtime only when needed
  writes: none by default; one map Markdown only when a file is explicitly requested
  tools: focused search and safe observation
  sensitive_resources: credentials and secret files default deny
- entry_scene: PREPARE

## Altitude
- An explicit user-requested `hld` or `lld` wins. Keep a named HLD inside that slice; do not widen it to the whole repository.
- Otherwise, whole repository, product surface, or no named slice → `hld`. Model context, containers, representative sequences, and only the state or deployment that evidence supports.
- Otherwise, a named module, path, workflow, or runtime flow → `lld`. Model components, interfaces, detailed sequences, and state transitions on that slice.
- Do not emit both altitudes unless the user asked for both or the HLD map cannot be understood without one LLD inset.
- A map is not a completeness claim. Unseen groups stay `Unverified`.
- Generic codebase-analysis or report wording changes neither the altitude precedence nor the map-only output shape.

## Workflow
1. Bind the inspection boundary and choose `hld` or `lld`: explicit altitude first, then the scope default. A user-named slice wins over repository history.
2. Inspect only enough entrypoints, owners, and stores to pick the views. Keep searches and outlines read-only; do not generate collection artifacts.
3. Trace one representative path and one material-edge or failure path that could change the diagram.
4. Select views from `reference.md`. Every map includes at least one sequence diagram. Add structure and state views when those axes exist in the bound slice.
5. Draw Mermaid from evidenced participants and messages. Label nodes with domain names, not file paths. Mark inferred edges `Unverified`.
6. Stop when the requested altitude is readable, each diagram has refs or an explicit gap, and a further file would not change the map.

## Output Contract
Return only:
- `altitude` and `bound_slice`
- Mermaid diagrams (`sequence`, plus `structure`/`state` when applicable)
- a one-line reading of each diagram
- `source_refs` per diagram
- `unverified_gaps`

Generic codebase-analysis/report wording still returns this map contract. Do not recreate the retired 10-chapter report, `findings.json`, `quality-gate-result.json`, or an improvement backlog. Route a selected boundary to `analysis-boundary-design` and a selected change to an implementation workflow.
