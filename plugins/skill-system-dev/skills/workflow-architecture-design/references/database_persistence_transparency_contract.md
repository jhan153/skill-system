# Database Persistence Transparency Contract

Shared judgment and evidence guidance for database-backed persistent state. Use it when a database
schema, mapping, access path, transaction, or lifecycle is materially affected.

## Principle

A database abstraction may hide storage mechanics from ordinary callers, but it must not hide the
database model or material operational effects from the boundary that owns them. That owner must
be able to predict and inspect what data is read or written, under which consistency and lifecycle
rules, and where cost or failure can amplify.

Transparency means owner-level inspectability, not leaking SQL or storage details through every
domain API. Domain and persistence models may differ when an explicit mapping boundary preserves
their respective invariants.

## Scope

Use this contract for relational, document, key-value, or other database systems when the current
work materially affects one or more of:

- schema, keys, constraints, indexes, partitions, or stored data shape;
- ORM/ODM mapping, loading, tracking, cascades, generated joins, or graph persistence;
- queries, commands, fan-out, read/write amplification, locking, or transaction scope;
- migrations, backfills, compatibility, rollback, retention, deletion, or recovery; or
- the module, adapter, repository, or service that owns database access.

Do not activate it merely for transient in-process state or a cache, queue, event log, object
store, search index, or external write that is not the database boundary under decision. Those
systems retain their own source-of-truth and lifecycle contracts. A simple database change may
use only the applicable fields below.

## Decision Record

Use only fields material to the current work. Mark unsupported material claims `unverified`
instead of filling them from framework defaults or naming conventions.

```yaml
database_persistence_transparency:
  target:
  database_kind:
  boundary_owner:
  source_of_truth:
  database_model:
  caller_contract:
  read_effects:
  write_effects:
  consistency_and_transaction:
  lifecycle:
  cost_visibility:
  automation_boundary:
  validation:
```

- Identity and ownership: `target`, `database_kind`, `boundary_owner`, `source_of_truth`, and the
  minimum domain-facing `caller_contract`.
- Model and effects: `database_model`, `read_effects`, and `write_effects`.
- Semantics and lifecycle: `consistency_and_transaction` and `lifecycle`.
- Visibility and evidence: `cost_visibility`, accepted `automation_boundary`, and `validation`.

## Design Rules

1. Design the database model from its own invariants and access paths. For a relational database,
   include keys, constraints, cardinality, normalization/denormalization, indexes, joins, and
   transaction needs; an in-memory object shape alone is not schema authority.
2. Establish `source_of_truth`, persisted identity and invariants, and required consistency or
   lifecycle meaning from accepted domain authority. A current schema, ORM/ODM mapping, or
   framework default is evidence, not authority for those semantic decisions.
3. Keep one owner for database policy and one authoritative stored model. Repositories, adapters,
   and mappings may translate representations but must not create a second source of truth or hide
   fallback, retry, transaction, or migration policy.
4. Treat table-to-entity one-to-one mapping as a simple option, not a universal rule. Owned/value
   types, generated join tables, JSON/document columns, lazy/eager loading, change tracking, and
   graph saves are allowed when their generated schema, access effects, write effects, and
   transaction behavior are predictable and inspected for the representative path.
5. Use explicit mapping or queries when the abstraction cannot make a hot, complex, or correctness-
   critical path predictable. This is a local boundary decision, not a mandate to replace ORM/ODM
   safety, parameter binding, type handling, or migrations with handwritten database code.
6. Keep domain callers free of incidental storage mechanics. Expose consistency, latency, failure,
   or lifecycle facts only when callers must coordinate with them; keep query and schema knowledge
   at the database boundary owner.
7. Do not claim a performance problem or improvement from mapping shape alone. Bind such a claim to
   a representative workload and query plan, trace, count, or comparable measurement.

## Evidence Rules

- Review generated migrations or schema changes when the database model changes.
- Read back representative generated SQL/commands, query count, or affected write set when an
  abstraction materially determines them.
- Verify transaction and consistency behavior on the actual selected path when atomicity,
  ordering, retry, or concurrency is material.
- Pair migration/backfill work with its compatibility, rollback, and readback condition. A schema
  diff alone does not prove existing data or callers migrated successfully.
- Use query plans or measurements only for material performance claims; do not manufacture a
  benchmark for ordinary predictable CRUD.
- Static review can establish visible ownership and declared effects, but runtime-only query plans,
  cardinality, locking, and latency remain deferred until matching observation exists.

## Task Cases

- **Positive:** an ORM mapping adds an automatic join table or JSON/document column. Keep the
  automation when the generated migration, representative commands, affected write set, and
  transaction behavior are predictable and inspected.
- **Negative:** a change touches only transient in-process state and no database boundary. This
  contract does not apply; do not require database fields, migrations, or query evidence.
- **Edge:** a complex or hot query is correct but its generated access path is not predictable.
  Keep the caller contract, make that one persistence path explicit, and validate it under the
  representative workload; do not replace unrelated ORM/ODM usage by default.
