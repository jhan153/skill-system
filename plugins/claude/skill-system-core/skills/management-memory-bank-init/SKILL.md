---
name: management-memory-bank-init
description: Initialize the single-file project Memory Bank defined by the shared Memory contract and register its location in project-context.yaml. Use only for an explicit fresh init request or approved bootstrap action. Never discover a fallback bank, overwrite/reinitialize existing Memory, populate inferred records, or recreate the legacy four-file event ledger.
disable-model-invocation: true
---

# Management Memory Bank Init

## Routing Card
- role: memory_operation
- intent_signature: explicit project Memory Bank initialization
- use_when: the user explicitly requests a fresh init or approves one exact bootstrap action
- do_not_use_when: reading, updating, checkpointing, maintenance, or automatic project setup is primary
- expected_inputs: verified project identity, exact/approved empty target, manifest state, storage intent, and init authorization
- expected_outputs: one empty canonical `memory.md`, manifest section update, and direct readback
- context_targets:
  must_read:
    - exact target and manifest state
    - `references/project_context_manifest.md`
    - `references/memory_mutation_contract.md`
  read_if_needed: repository persistence convention and explicit legacy-migration decision
  do_not_load_by_default: other stores, raw history, transcripts, full repository, or home Memory
- risk_profile:
  reads: exact target and manifest only
  writes: one approved `memory.md` and only the manifest `memory_bank` section
  tools: local file operations and readback
  sensitive_resources: credentials denied; external paths require exact resolved-path approval
- entry_scene: PREPARE

## Workflow

1. Bind `memory_root` from the exact approved directory or existing manifest declaration. Only an
   explicit init with neither may propose `docs/memory-bank/`; obtain approval before writing.
2. Bind `memory_file := memory_root/memory.md` and show the resolved target before external/home
   writes. Stop when current or legacy Memory exists. Explicit legacy migration belongs to
   `management-memory-bank-maintenance`; replacement requires a separately approved preservation
   decision and a new empty target.
3. Create the shared contract's `memory-bank-v1` header with project identity and no records.
4. Update only `memory_bank.root` and `memory_bank.storage` in `project-context.yaml`, preserving
   all other sections and the approved path representation.
5. Read back the file header, empty record state, project identity, manifest section, and unchanged
   sibling sections. Initialization creates storage, not Memory content.

## Output

Report created/preserved paths, project identity, storage intent, manifest readback, and any
migration uncertainty. Partial creation never counts as success.
