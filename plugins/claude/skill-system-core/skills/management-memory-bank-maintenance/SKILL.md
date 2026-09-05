---
name: management-memory-bank-maintenance
description: Inspect, integrity-check, conflict-check, consolidate, compact, or explicitly migrate one existing declared project Memory Bank under the shared single-file contract. Read-only operations never repair, and write operations preserve stable IDs, source refs, status, and semantic revisions. Never score records, infer authority, or silently migrate the legacy four-file layout.
disable-model-invocation: true
---

# Management Memory Bank Maintenance

## Routing Card
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

## Operations

- `report`: summarize document identity, record states, navigation anchors, and unresolved issues;
  read-only.
- `integrity-check`: check the shared format, stable IDs, required fields, source refs, and duplicate
  revisions; read-only.
- `conflict-check`: identify duplicate identities, contradictory active rules, broken anchors, and
  candidate overlap; read-only.
- `consolidate`: merge only directly equivalent identities under one stable record and revision.
- `compact`: shorten duplicated prose/revisions while preserving current meaning and source trail.
- `migrate-legacy`: create one new `memory.md` from an explicitly selected former four-file bank,
  preserve uncertainty, read back the new file, and leave legacy files untouched.

## Workflow

1. Bind the exact/nearest declared target and requested operation. Missing paths are unavailable,
   never replaced by a default.
2. Read only affected records or exact legacy inputs. Separate structural format, identity,
   authority, current truth, and source verification.
3. Stop after findings for read-only operations.
4. For writes, apply one bounded shared-contract mutation or approved migration and read back the
   target plus unchanged unrelated content. Ambiguous mappings remain no-write.

## Output

Lead with operation, affected IDs/files, decisive findings, mutation/readback when applicable, and
one unresolved decision only when required. Structural consistency never proves a Memory claim true.
