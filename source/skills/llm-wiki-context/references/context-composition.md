# LLM Wiki Context Composition

Use this reference only after reading the selected Wiki's own guide.

## Native Navigation First

Identify which mechanisms the Wiki itself treats as authoritative:

- root guide, map, catalog, or entrypoint;
- page metadata and lifecycle/status fields;
- curated indexes, topic paths, graph edges, backlinks, tags, or search commands;
- canonical source links and supersession conventions.

Do not invent a generic crawler or translate the Wiki into claim/edge schemas. If the guide defines a query or reading order, follow it.

## Task Decomposition

```yaml
task_query:
  objective:
  entities: []
  operation:
  invariants: []
  decisions: []
  artifact_anchors: []
```

Use these fields to select pages. A page enters context only when it changes execution, interpretation, constraints, source selection, or validation for the current task.

## Composition Roles

```yaml
wiki_context:
  vocabulary: []
  current_architecture_or_state: []
  invariants: []
  accepted_decisions: []
  rejected_or_superseded: []
  artifact_anchors: []
  consumers: []
  validation_expectations: []
  conflicts_or_unresolved: []
  source_pages: []
```

Summarize by these roles rather than producing page-by-page abstracts. Keep page IDs/paths and source links so the task owner can expand one item if needed.

## Stop Rule

Stop when every material task field has either sufficient context or an explicit gap and another page is unlikely to change the next decision. Do not load an entire namespace merely because it is linked, and do not merge another Wiki without an explicit selection.
