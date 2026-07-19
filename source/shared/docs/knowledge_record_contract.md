# Knowledge Base Record Contract

Knowledge Base is a directly readable project store of current project knowledge, semantic history, and typed links to the artifacts and decisions that explain it. It is not an intermediate claim graph, an LLM Wiki projection, or an opaque ranking system.

## Location Variables And Default Layout

Every Knowledge operation binds `knowledge_root` and `knowledge_index` from `project_context_manifest.md` before it reads or writes. An exact user-approved path wins; otherwise consume the nearest manifest declaration. The resolved root may be anywhere the runtime can access. Never scan for alternatives, derive a path from repository conventions, or keep using a literal default after binding the variables.

```text
${knowledge_root}/
  domain/
  design/
  algorithm/
  architecture/
  code-review/
  decisions/

${knowledge_index}  # compact catalog; normally ${knowledge_root}/index.md
```

For a brand-new store with no supplied path, an initializer may propose `docs/knowledge-base/` and `${knowledge_root}/index.md` as defaults, but they become operative only after approval and manifest registration. A new initializer records both bound values explicitly; the index fallback remains a compatibility rule for existing manifests that omit `knowledge_base.index`. `knowledge_index` may be configured separately; if it resolves outside `knowledge_root`, that exact second target requires the same explicit visibility and write approval as any other external target. Consumers never migrate or scan for alternatives implicitly. Relations, observations, and revision events stay with their canonical Markdown record; do not create separate claim, edge, score, or Runtime Projection stores.

## Common Record Envelope

Keep the current usable snapshot first. Existing 9.3 records with the original required fields remain readable; every new or materially touched record should add the applicable 9.4 navigation and history fields below.

```yaml
id: KB-DOMAIN-001
category: domain | design | algorithm | architecture | code-review | decision
title: Short stable title
status: active | superseded | deprecated
verification: verified | unverified
summary: One directly usable current statement
aliases: []
search_terms: []
applies_to: []
evidence_refs: []
canonical_refs: []
verified_by: []
consumers: []
relations: []
observations: []
revisions: []
supersedes: []
superseded_by: []
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
```

- `aliases`: accepted names, former names, abbreviations, or user vocabulary that should retrieve the record. Do not add speculative synonyms.
- `search_terms`: a small set of discriminating concepts, ticket language, error signatures, or component names not already obvious from the title and anchors.
- `applies_to`: repo-relative files/symbols, product surfaces, components, workflows, or bounded domain scopes.
- `evidence_refs`: observations or source excerpts supporting the record; evidence is not automatically canonical.
- `canonical_refs`: actual code, design file/node, design-system component/token, specification, or accepted decision that owns the current rule.
- `verified_by`: existing command, runtime observation, independent review, or named user decision that checked the record.
- `consumers`: files, components, skills, or workflows expected to use the knowledge.
- `supersedes` and `superseded_by`: reciprocal lifecycle links for identity replacement. Superseded records remain addressable.

Use repo-relative paths and stable symbols, component/node IDs, WorkItem IDs, ticket URLs/IDs, decision IDs, and Git refs when available. Do not store credentials, raw chat, private identities, or copied large source bodies.

## Typed Relations: Spatial And Causal Navigation

Use an embedded relation only when it answers a future navigation question. Each relation has one explicit meaning and a stable target:

```yaml
relations:
  - type: motivated_by | raised_by | resolved_by | resulted_in | implemented_by | depends_on | generalizes | specializes | overlaps_with | conflicts_with | amends | revisits | recurrence_of
    target: KB-DECISION-004 | work-item:WI-20260718-001 | ticket:142 | plan:docs/plan/example.md | source/path#symbol
    basis_refs: []
```

Read every edge as `<current record> --type--> <target>`.

- `motivated_by`, `raised_by`, `resolved_by`, and `resulted_in` preserve why a decision or rule exists and what followed from it.
- `implemented_by` and `depends_on` connect knowledge to the project surfaces that realize or constrain it.
- `generalizes`, `specializes`, and `overlaps_with` preserve scope relationships without merging distinct identities.
- `conflicts_with` preserves a contradiction. It never counts as support.
- `amends` changes part of another still-addressable decision without replacing its identity; `revisits` records a later reconsideration.
- `recurrence_of` links a narrower Knowledge pattern to the durable pattern it repeats. Work-item recurrence remains an observation event with a stable `source_ref`.

Do not use a vague `related_to` edge when a typed relationship is unknown; keep it unresolved instead. A relation is a navigation fact, not proof that either endpoint is true. Give every relation at least one stable `basis_refs` entry explaining why the edge exists. Reverse traversal is derived by targeted search, so do not duplicate every directional edge merely to manufacture symmetry.

## Observation Events And Recurrence

Record a bounded event when a durable record is independently supported, recurs in work, applies in a new scope, or encounters a counterexample. Keep the current statement unchanged unless the event actually changes its meaning.

```yaml
observations:
  - observation_id: KB-OBS-20260718-001
    kind: support | recurrence | application | counterexample
    verification: verified | unverified
    source_ref: ticket:142
    provenance_root: field-feedback:31
    observed_at: YYYY-MM-DD
    scope: []
    note: One short source-traced distinction
```

- `source_ref` identifies this occurrence. Do not append the same occurrence twice.
- `provenance_root` identifies the earliest known common origin. Copied documents, derived tickets, and tests generated from the same requirement share one root.
- `verification` says whether the observation's asserted support, recurrence, application, or counterexample relationship to the record was checked. Source identity, source existence, or an explicit report alone does not verify that relationship; keep it `unverified` until the behavioral or decision claim is directly checked.
- Use `unresolved:<source-ref>` when dependence is unknown. Unresolved roots do not count as independent support.
- A counterexample or conflict remains visible even when several supporting observations exist.
- Explicit user-reported field evidence may be summarized by a stable bounded pointer, but raw prompt/session/transcript text is never collected automatically.

Derive a recurrence profile on demand from the events; never persist one scalar score:

- total distinct observations;
- distinct verified provenance roots for `support` or `recurrence`;
- first and last observed dates;
- distinct scopes;
- unresolved roots and counterexamples.

These dimensions mean different things. Frequent observation is not truth, broad scope is not importance, reference count is not confidence, and repeated tickets do not prove a shared cause.

## Semantic Revision History

Keep the full current snapshot readable and append only the semantic delta that explains a material change:

```yaml
revisions:
  - revision_id: KB-REV-20260718-001
    changed_at: YYYY-MM-DD
    kind: created | adopted_snapshot | amended | relinked | reverified | superseded | deprecated
    summary: What meaning or linkage changed
    reason_refs: []
```

- Git or another VCS owns literal line deltas. Knowledge revisions store the semantic reason, effective change, and evidence pointers.
- `updated_at` matches the newest semantic revision or observation that changed the record.
- When adopting a 9.3 record, use `adopted_snapshot` and state that earlier semantic history was not reconstructed; never fabricate prior revisions.
- Update a stable identity in place. Create a new record only when the meaning or ownership identity changed materially, then set reciprocal `supersedes`/`superseded_by` links.

## Category Body

After the envelope, each record contains only the sections its category needs:

- domain: vocabulary, invariant, allowed/forbidden state, operational consequence;
- design: product intent, token/component rule, states/variants, implementation anchors, accessibility constraints;
- algorithm: problem/constraints, selected method, invariants/complexity, rejected alternatives, implementation/verifier anchors;
- architecture: boundary/ownership, dependency direction, lifecycle/data flow, invariants, migration consequences;
- code-review: recurring repository-specific review rule, detection cues, correct pattern, exceptions, examples by pointer;
- decision: context, accepted decision, consequences, rejected/superseded alternatives, effective scope.

Do not turn one-off review comments, tentative plan language, generic industry advice, or model-generated patterns into durable records.

## Index And Retrieval Contract

`index.md` is a compact catalog and navigation surface, not a duplicate store. A new index should use:

```text
ID | Category | Title / summary | Search anchors | Related | Path | Status
```

- `Search anchors` compacts accepted aliases, main `applies_to` anchors, and discriminating search terms from the accepted current snapshot. Terms found only in an unverified observation do not silently become current search anchors; keep them inside the record or mark them explicitly during an authorized reindex.
- `Related` lists only the few record/work targets needed to choose a next hop; it is not a popularity ranking.
- Existing 9.3 index columns remain valid until an explicitly requested reindex.

Readers start at the index, select a record, and expand one typed edge at a time. For a why/history question, prefer `motivated_by`, `raised_by`, `amends`, `revisits`, revisions, and supersession. For a scope question, prefer `applies_to`, `implemented_by`, `depends_on`, `generalizes`, and `specializes`. For repeated work, inspect observations, `provenance_root`, and `recurrence_of`. Track visited targets, stop on cycles, and stop as soon as the question is answered.

## Overlap Classification

Before creating or changing a record, classify the nearest existing match:

| incoming material | operation |
| --- | --- |
| same identity and unchanged meaning | append or merge one source-traced observation; do not create a record |
| same origin copied through several files/tickets | preserve the shared `provenance_root`; do not count independent support |
| stable identity with changed current meaning | update in place and append a semantic revision |
| materially replaced identity | create the replacement and set reciprocal supersession links |
| narrower, broader, or partially shared scope | keep distinct identities and add `specializes`, `generalizes`, or `overlaps_with` |
| contradiction or counterexample | preserve both sides with `conflicts_with` or a counterexample observation |
| no material overlap | create one new stable identity |

Similarity is a candidate-discovery signal, not merge authority. Do not auto-merge from lexical or embedding similarity. When an overlap classification can change a widely consumed rule, use an independent read-only semantic review when available and keep the mutation owner responsible for the decision.

## Mutation Contract

- Bind and reuse `knowledge_root` and `knowledge_index`; exact user path wins, otherwise use the nearest manifest declaration.
- Writes require the matching explicit category/update/maintenance/plan-sync workflow or an approved project checkpoint.
- Update the record and its index row in the same operation and read both back.
- Preserve unresolved relations, source dependence, and contradictory evidence; do not convert them into a clean consensus.
- Do not compute maturity, confidence, importance, usage, popularity, satisfaction, or composite frequency scores.
- Knowledge mutation never writes Memory Bank or an LLM Wiki automatically.
