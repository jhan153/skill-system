---
name: management-memory-bank-init
description: Initialize a project-scoped Memory Bank and register only its location in project-context.yaml. Use only for an explicit init or reinit request; never discover, overwrite, or merge an existing bank as fallback.
disable-model-invocation: true
---

# Management Memory Bank Init

## Routing Card
- role: memory_operation
- intent_signature: initialize project Memory Bank, 메모리뱅크 초기화
- use_when: the user explicitly requests fresh initialization or reinitialization
- do_not_use_when: read, update, correction capture, checkpoint, or maintenance is primary
- expected_inputs: verified project root/identity, exact target or manifest state, and explicit init/reinit intent
- expected_outputs: four baseline files, first event, manifest section update, and readback result
- context_targets:
  must_read: exact project/target state, `reference.md`, `.claude/docs/memory_mutation_contract.md`, and existing `project-context.yaml` when present
  read_if_needed: repository persistence convention
  do_not_load_by_default: other banks, transcripts, full project history, common/home Memory
- risk_profile:
  reads: exact target and manifest only
  writes: one project-local bank and only the manifest's `memory_bank` section
  tools: local file operations and readback
  sensitive_resources: credentials and raw private history denied
- entry_scene: PREPARE

## Initialization Contract
Target precedence is: exact user path, declared `memory_bank.root`, then the default path from `reference.md` only because initialization itself was explicitly requested. Ordinary resolution never creates this default.

If a bank already exists, ordinary init stops. Reinit requires explicit intent and a repository-approved preservation or migration path; never overwrite active history. When writing `project-context.yaml`, preserve all unknown and unrelated sections and update only `memory_bank`.

## Workflow
1. Resolve project identity and target; inspect the exact bank and manifest state.
2. Stage `current.md`, `archive.md`, `events.jsonl`, and `meta.json` under one operation ID.
3. Append the first `entity=project`, `action=create` event and create the compact baseline snapshot.
4. Add or update only the manifest `memory_bank` section.
5. Commit the bank as one unit and read back all four files, shared event ID, snapshot version, project identity, and manifest path.

Any partial creation, parse failure, identity mismatch, or manifest clobber remains failed/blocked.

## Output
Report exact created/preserved paths, project/event IDs, four-file and manifest readback, and any portability uncertainty. Initialization creates storage; it does not populate inferred project rules or session history.
