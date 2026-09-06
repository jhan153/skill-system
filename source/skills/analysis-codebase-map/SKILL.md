---
name: analysis-codebase-map
description: Map the current repository or named slice with source-linked HLD/LLD Mermaid diagrams; generic codebase-analysis reports route here. Not for target/transition architecture, single-boundary decisions, ranked improvement scans, bug RCA, explicit findings/quality gates, or implementation code review.
---

# Analysis Codebase Map

## Routing Card
- role: primary
- family: analysis
- intent_signature: architecture map, HLD/LLD modeling, sequence/state/structure diagrams
- use_when:
  - the user wants to understand how a repo or named slice is structured and how it runs.
  - the expected output is Mermaid maps of flow, structure, or state—not a findings backlog or one design verdict.
  - generic codebase-analysis or codebase-report wording has no explicit findings, backlog, or quality-gate contract; satisfy it with this compact map.
- do_not_use_when:
  - one module/seam/adapter decision is needed; use `analysis-boundary-design`.
  - the user wants ranked improvement candidates; use `analysis-architecture-deepening`.
  - the user wants a normative target/transition architecture across several interacting
    boundaries; use `workflow-architecture-design`.
  - the cause of a failure is unknown; use `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane, keep simple source/log-only diagnosis with the current task owner, or use `workflow-bug-fix` only for a semantically admitted bounded repair of an already-implemented accepted contract. First implementation or explicit production replacement uses `workflow-implementation`.
  - implemented code or a diff needs findings and a review disposition, with or without a design baseline; use `workflow-code-review`.
  - the request is domain language, performance RCA, direct implementation, or an explicit findings/quality-gate artifact.
- expected_inputs: repo root or named slice, the question to understand, any explicit HLD/LLD choice, and any required runtime/state focus
- expected_outputs: altitude (`hld` or `lld`), Mermaid diagrams with captions and source refs, and explicit `Unverified` gaps
- context_targets:
  must_read:
    - the map request, repo or named-slice outline, and a representative entrypoint-to-output path when runtime flow is in scope; for a structure/schema-only slice, the relevant definitions and relationships instead
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

### Resource Closure

```json
[]
```

## Altitude
- An explicit user-requested `hld` or `lld` wins. Keep a named HLD inside that slice; do not widen it to the whole repository.
- Otherwise, whole repository, product surface, or no named slice → `hld`. Model context, containers, any evidenced runtime sequences, and only the state or deployment that evidence supports.
- Otherwise, a named module, path, workflow, or runtime flow → `lld`. Model the slice's components and interfaces, plus detailed sequences and state transitions only when applicable and evidenced.
- Do not emit both altitudes unless the user asked for both or the HLD map cannot be understood without one LLD inset.
- A map is not a completeness claim. Unseen groups stay `Unverified`.

## Workflow
1. Bind the inspection boundary and choose `hld` or `lld`: explicit altitude first, then the scope default. A user-named slice wins over repository history.
2. Inspect only enough entrypoints, owners, and stores to pick the views. Keep searches and outlines read-only; do not generate collection artifacts.
3. Trace one representative path and one material-edge or failure path when runtime flow is in scope.
   For a structure/schema-only slice, trace the relevant definitions, relationships, and a material
   structural counterexample instead.
4. Select views from `reference.md`. Include a sequence when an evidenced runtime interaction is
   needed to answer the request. A structure/schema-only slice may omit sequence and say why;
   never invent participants or messages to fill the view. If a requested runtime path lacks
   evidence, retain that gap as `Unverified` rather than treating a structural map as its answer.
   Add structure and state views when those axes exist in the bound slice.
5. Draw Mermaid from evidenced participants and messages. Label nodes with domain names, not file paths. Mark inferred edges `Unverified`.
6. Stop when the requested altitude is readable, each diagram has refs or an explicit gap, and a further file would not change the map.

## Output Contract
Return only:
- `altitude` and `bound_slice`
- Mermaid diagrams for the evidenced structure/schema/state and any required runtime sequence
- a one-line reading of each diagram
- `source_refs` per diagram
- `unverified_gaps`
