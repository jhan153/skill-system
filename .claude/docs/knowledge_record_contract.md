# Knowledge Base Record Contract

Knowledge Base is a directly readable project store, not an intermediate claim graph or LLM Wiki projection.

## Default Layout

```text
docs/knowledge-base/
  index.md
  domain/
  design/
  algorithm/
  architecture/
  code-review/
  decisions/
```

Projects may declare another root and index in `project-context.yaml`. Consumers never migrate or scan for alternatives implicitly.

## Common Record Envelope

```yaml
id: KB-DOMAIN-001
category: domain | design | algorithm | architecture | code-review | decision
title: Short stable title
status: active | superseded | deprecated
verification: verified | unverified
summary: One directly usable statement
applies_to: []
evidence_refs: []
canonical_refs: []
verified_by: []
consumers: []
supersedes: []
updated_at: YYYY-MM-DD
```

- `applies_to`: repo-relative files/symbols, product surfaces, components, workflows, or bounded domain scopes.
- `evidence_refs`: observations or source excerpts supporting the record; evidence is not automatically canonical.
- `canonical_refs`: actual code, design file/node, design-system component/token, specification, or accepted decision that owns the rule.
- `verified_by`: existing command, runtime observation, review, or named user decision that checked the record.
- `consumers`: files, components, skills, or workflows expected to use the knowledge.
- `supersedes`: stable record IDs replaced by this record. Superseded records remain addressable.

Use repo-relative paths and stable symbols/component/node IDs when available. Do not store credentials, raw chat, private identifiers, or copied large source bodies.

## Category Body

After the envelope, each record contains only the sections its category needs:

- domain: vocabulary, invariant, allowed/forbidden state, operational consequence;
- design: product intent, token/component rule, states/variants, implementation anchors, accessibility constraints;
- algorithm: problem/constraints, selected method, invariants/complexity, rejected alternatives, implementation/verifier anchors;
- architecture: boundary/ownership, dependency direction, lifecycle/data flow, invariants, migration consequences;
- code-review: recurring repository-specific review rule, detection cues, correct pattern, exceptions, examples by pointer;
- decision: context, accepted decision, consequences, rejected/superseded alternatives, effective scope.

Do not turn one-off review comments, tentative plan language, generic industry advice, or model-generated patterns into durable records.

## Index Contract

`index.md` is a compact catalog, not a duplicate store. Each active entry includes ID, category, title/summary, main `applies_to` anchors, record path, and status. Readers start at the index, select matching records, and stop at minimum sufficient context.

## Mutation Contract

- Exact user path wins; otherwise use the nearest manifest declaration.
- Writes require the matching explicit category/update/maintenance/plan-sync workflow or an approved project checkpoint.
- Create one stable ID, update the existing record in place, or supersede with explicit cross-links. Never silently fork the same rule.
- Update the record and its index row in the same operation and read both back.
- Do not compute maturity, confidence, usage, popularity, or satisfaction scores.
- Knowledge mutation never writes Memory Bank or an LLM Wiki automatically.
