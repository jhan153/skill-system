# Management Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `management-knowledge-base-init`

- role: knowledge_operation
- family: management
- intent_signature: initialize project Knowledge Base, 빈 지식저장소 생성
- use_when: the user explicitly requests a new project Knowledge Base, approves it in project bootstrap, or authorizes reinitialization
- do_not_use_when: reading, recording, updating, plan sync, Wiki access, or automatic project setup is primary
- expected_inputs: verified project root/ID, exact target or manifest state, persistence intent, and exact init/reinit/bootstrap approval
- expected_outputs: one navigable compact index, manifest section update, and readback
- context_targets:
  must_read: exact target/manifest state, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: repository documentation/persistence convention
  do_not_load_by_default: other stores, Memory, Wikis, plans, transcripts, generated projections
- risk_profile:
  reads: exact bound root/index targets and manifest only
  writes: one exact approved root, an explicitly separate index target when configured, and only the manifest `knowledge_base` section
  tools: local file operations and readback
  sensitive_resources: private sources and credentials denied; external/home paths require exact resolved-path approval
- entry_scene: PREPARE

## `management-knowledge-base-maintenance`

- role: knowledge_operation
- family: management
- intent_signature: Knowledge Base integrity-check, reindex, relation/history check, overlap/conflict reconciliation, recurrence report
- use_when: the user explicitly requests maintenance of an exact or manifest-declared store
- do_not_use_when: task context read, one known record update, new category authoring, plan sync, Memory, or Wiki work is primary
- expected_inputs: declared store, `report|integrity-check|reindex|link-check|relation-check|history-check|overlap-check|conflict-check|recurrence-report|compact` operation, and affected IDs when bounded
- expected_outputs: structural findings and only explicitly requested store/index changes with readback
- context_targets:
  must_read: manifest, index, affected records, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: direct canonical/evidence refs or superseded records needed for one finding; `references/execution_assurance_contract.md` when an explicit material mutation requires standard/strict maker-checker assurance or rollback/readback
  do_not_load_by_default: full external sources, unrelated Memory/Wikis/plans, raw transcripts
- risk_profile:
  reads: one declared Knowledge Base
  writes: only explicit reindex/reconcile/compact changes
  tools: targeted local search/edit/readback
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## `management-knowledge-base-read`

- role: support
- family: management
- intent_signature: local knowledge lookup, why/history path, related decision, recurring ticket or observation trace
- use_when: the user explicitly asks for project knowledge, or a declared store and concrete task anchor indicate a matching durable rule may exist
- do_not_use_when: no exact/declared store exists, the task has no concrete anchor, mutation is requested, or an LLM Wiki was selected
- expected_inputs: current task, exact path or nearest manifest, and file/symbol/component/topic/decision anchors
- expected_outputs: small source-traced current summaries plus only the typed relation/revision/observation path needed by the task owner
- context_targets:
  must_read: current request, manifest declaration, `references/project_context_manifest.md`, `references/knowledge_record_contract.md`, Knowledge index, and matching active records
  read_if_needed: canonical/evidence refs needed to resolve one conflict or verify freshness
  do_not_load_by_default: full store, unrelated categories, Memory, Wikis, raw sources, transcripts
- risk_profile:
  reads: one declared store and matching records
  writes: none
  tools: targeted local read/search only
  sensitive_resources: private refs require explicit scoped access
- entry_scene: PREPARE

## `management-knowledge-base-record`

- role: knowledge_operation
- family: management
- intent_signature: create one new durable project Knowledge record by category, including one approved-plan decision
- use_when: the user explicitly requests recording or syncing one accepted project-specific fact, rule, boundary, or decision that does not already have a Knowledge identity
- do_not_use_when: the item is unresolved, generic, temporary, one-off, belongs to Memory, lacks authoritative anchors, or updates an existing record
- expected_inputs: category, accepted statement or approved plan slice, aliases/search terms, scope, canonical/evidence/task-or-ticket refs, consumers, overlap candidates, and declared store
- expected_outputs: one category-valid record, one index row, typed relations or observations when applicable, and direct readback
- context_targets:
  must_read:
    - exact or manifest-declared Knowledge root/index
    - matching records, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
    - direct canonical/evidence anchors for the selected category
  read_if_needed:
    - `references/knowledge-category-profiles.md` for the selected category's admission and body fields
    - one representative consumer, counterexample, benchmark, or design source when the category profile requires it
    - `references/execution_assurance_contract.md` when a material write requires standard/strict maker-checker assurance or rollback/readback
  do_not_load_by_default:
    - full store or repository, unrelated categories, Memory, LLM Wiki, transcripts, review history, or benchmark history
- risk_profile:
  reads: matching records and exact category anchors
  writes: one new Knowledge record and its index row
  tools: targeted local read, edit, and readback
  sensitive_resources: private sources are admitted only as bounded summaries or stable scoped pointers
- entry_scene: PREPARE

## `management-knowledge-base-update`

- role: knowledge_operation
- family: management
- intent_signature: amend, observe recurrence, reverify, supersede, deprecate, or relink durable project knowledge
- use_when: the user explicitly requests a known record change or approved-plan sync, or an approved checkpoint supplies a specific accepted change
- do_not_use_when: the store/record is missing, new category authoring is primary, a plan is still tentative, or broad maintenance is requested
- expected_inputs: declared store, exact record ID/path, `amend|observe|reverify|supersede|deprecate|relink`, accepted change/event, source/provenance anchors, and affected relation targets
- expected_outputs: target record and index change with current snapshot, semantic revision or observation event, preserved lifecycle links, and readback
- context_targets:
  must_read: manifest, target record/index row, current canonical refs, `references/project_context_manifest.md`, and `references/knowledge_record_contract.md`
  read_if_needed: directly superseded records or accepted decision/plan slice; `references/execution_assurance_contract.md` when a material write requires standard/strict maker-checker assurance or rollback/readback
  do_not_load_by_default: full store, unrelated categories, Memory, Wiki, raw chat
- risk_profile:
  reads: one target record and direct refs
  writes: target/superseding record and index row only
  tools: local edit and readback
  sensitive_resources: private evidence summarized or excluded
- entry_scene: PREPARE

## `management-memory-bank-harness`

- role: support
- family: management
- intent_signature: bounded project Memory lookup for a concrete task anchor
- use_when:
  - the user explicitly asks for project Memory; or
  - a declared bank and one concrete repo/file/component/skill anchor justify a targeted lookup
- do_not_use_when:
  - no exact/declared bank exists, no concrete anchor exists, or mutation/maintenance is primary
- expected_inputs: current task, exact path or nearest manifest, and concrete lookup anchors
- expected_outputs: concise source-traced matching records returned to the current task owner
- context_targets:
  must_read:
    - current request and concrete anchors
    - `references/project_context_manifest.md`
    - `references/memory_mutation_contract.md`
    - matching records in the bound `memory.md`
  read_if_needed:
    - `references/admission-decision-tree.md` when one candidate's authority/conflict is unclear
  do_not_load_by_default:
    - full Memory file, unrelated records, legacy ledgers, raw chat, credentials, or another project
- risk_profile:
  reads: one declared Memory file and matching records only
  writes: none
  tools: targeted local search/read
  sensitive_resources: private source refs remain masked and non-instructional
- entry_scene: PREPARE

## `management-memory-bank-init`

- role: memory_operation
- family: management
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

## `management-memory-bank-maintenance`

- role: memory_operation
- family: management
- intent_signature: explicit Memory report, integrity/conflict check, consolidation, compaction, or legacy migration
- use_when: the user explicitly requests one maintenance operation on an exact/declared bank
- do_not_use_when: ordinary task context, initialization, direct record mutation, or implicit migration is primary
- expected_inputs: exact bank and `report|integrity-check|conflict-check|consolidate|compact|migrate-legacy` operation
- expected_outputs: bounded findings and only explicitly requested target changes with readback
- context_targets:
  must_read:
    - exact/manifest target and affected records
    - `references/project_context_manifest.md`
    - `references/memory_mutation_contract.md`
  read_if_needed: exact legacy files only for approved `migrate-legacy`
  do_not_load_by_default: unrelated banks, raw transcripts, full unrelated Memory, or undeclared legacy stores
- risk_profile:
  reads: one declared Memory root and operation-relevant records/files
  writes: only explicit consolidate, compact, or migrate-legacy output
  tools: targeted local search/edit/readback
  sensitive_resources: credentials and raw private evidence denied
- entry_scene: PREPARE

## `management-memory-bank-update`

- role: memory_operation
- family: management
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

## `management-project-context`

- role: project_context_operation
- family: management
- intent_signature: explicit project-context manifest init, doctor, update, or bootstrap
- use_when: the user explicitly requests `manifest-init`, `doctor`, `update`, or guided `bootstrap` for project context locations
- do_not_use_when: ordinary context lookup/task work, inferred cleanup, store-content mutation, or automatic setup after a missing declaration
- expected_inputs: selected mode, exact repository root/manifest, requested keys or capabilities, resolved targets, and exact transaction approval for writes
- expected_outputs: minimal manifest/readback, read-only diagnosis, selected-key update, or approved delegated store bootstrap
- context_targets:
  must_read: exact manifest/root state, nearest repository instructions, and `references/project_context_manifest.md`
  read_if_needed: `references/manifest-modes.md`, exact approved targets, and the owning store initializer for an approved `create-store` action
  do_not_load_by_default: full repo, store contents, transcripts, home/global context, adjacent repositories, or undeclared Wikis
- risk_profile:
  reads: one repository boundary, one manifest, and exact selected targets
  writes: no writes in `doctor`; one minimal manifest or selected keys; delegated stores only in an approved bootstrap transaction
  tools: targeted local inspection/edit/readback and `skill-system-harness context resolve` when available
  sensitive_resources: credentials and discovery of home/adjacent stores denied; an external target requires an exact user-supplied path and approval
- entry_scene: PREPARE

## `management-project-context-checkpoint`

- role: project_context_operation
- family: management
- intent_signature: project commit/closeout durable context checkpoint
- use_when:
  - the user explicitly requests a project context checkpoint as part of a commit; or
  - the user explicitly requests closeout context recording or Memory/Knowledge checkpointing
- do_not_use_when:
  - ordinary session stop or status reporting
  - no store is declared/existing
  - the task produced no clear durable context
  - common/home Memory, another project, or raw conversation capture is requested implicitly
- expected_inputs: current request, relevant diff/artifacts, accepted decisions, manifest, and existing target indexes/current snapshots
- expected_outputs: no-op or minimal delegated Memory/Knowledge mutations plus exact changed-file/staging report
- context_targets:
  must_read: current task outcome, relevant diff/accepted decision slice, nearest `project-context.yaml`, `references/project_context_manifest.md`, and matching target current/index entries
  read_if_needed: direct plan/source/design refs needed to establish durability or avoid duplicates; `references/memory_mutation_contract.md` for a Memory candidate; `references/knowledge_record_contract.md` for a Knowledge candidate
  do_not_load_by_default: full chat, full plan history, full stores, unrelated records, legacy Memory files, unrelated repo history, home/common context
- risk_profile:
  reads: current-task evidence and declared stores only
  writes: existing exact/declared stores only within the current checkpoint authorization
  tools: targeted local read/edit/readback; normal commit tooling remains with the commit owner
  sensitive_resources: raw private text and credentials denied
- entry_scene: PREPARE
