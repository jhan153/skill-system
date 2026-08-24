---
name: management-memory-bank-update
description: Create, update, activate, or deprecate one explicitly persistent goal, rule, proven practice, or recurring-mistake candidate in an existing declared single-file Memory Bank. Append one concise semantic revision to the target record and read it back. Never infer persistence, initialize a bank, write raw chat, activate from recurrence alone, or update multiple records.
disable-model-invocation: true
---

# Management Memory Bank Update

## Routing Card
- role: memory_operation
- intent_signature: explicit durable Memory record mutation
- use_when: the user explicitly requests persistence or an approved context checkpoint supplies one exact durable item
- do_not_use_when: the bank is unavailable, the item is temporary/inferred, or init/read/maintenance is primary
- expected_inputs: exact item, operation, persistence authority, declared bank, stable source refs, and affected scope
- expected_outputs: one target record mutation, one semantic revision, and target-only readback
- context_targets:
  must_read:
    - manifest declaration and target/nearest matching Memory records
    - `references/project_context_manifest.md`
    - `references/memory_mutation_contract.md`
  read_if_needed: one deprecated or candidate record needed for supersession/equivalence
  do_not_load_by_default: full bank, unrelated records, legacy ledgers, raw chat, or implementation history
- risk_profile:
  reads: one declared Memory file and target identity candidates
  writes: one target record plus its revision in `memory.md`
  tools: targeted local mutation and readback
  sensitive_resources: private evidence is reduced to a stable pointer or masked summary
- entry_scene: PREPARE

## Modes

- `durable_item`: one project goal, constraint, or proven reusable practice.
- `candidate_mistake`: one explicitly persistent cross-session failure pattern; new records remain
  `candidate` and `unverified`.

Allowed operations are `create`, `update`, `activate`, and `deprecate`. Multi-record consolidation
belongs to `management-memory-bank-maintenance`.
Activation requires explicit acceptance or directly verified project policy. Similar wording,
frequency, elapsed time, or a score never authorizes activation or consolidation.

## Workflow

1. Bind the declared `memory_file`, project identity, requested mode/operation, and current target
   snapshot. Missing/mismatched stores remain `unavailable`; do not initialize or migrate.
2. Confirm cross-session usefulness, explicit persistence authority, Memory ownership, stable source
   refs, and duplicate/conflict classification.
3. Apply the shared contract to one record. Preserve its stable ID, current statement, status,
   verification, applicability, exclusions, and source refs; append one concise revision.
4. Read back the target record/revision and confirm unrelated records are unchanged.

## Output

Report mode, operation, record ID, authority/source refs, resulting status/verification, readback,
and unresolved conflict. A semantic no-op is a valid no-write result.
