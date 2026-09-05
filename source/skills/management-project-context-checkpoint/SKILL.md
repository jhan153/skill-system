---
name: management-project-context-checkpoint
description: At an explicitly requested project context checkpoint during commit or closeout, classify newly finalized durable context into an existing project Memory Bank or Knowledge Base declared by project-context.yaml. Use only for the current task's clear changes; an ordinary commit does not invoke this writer, and it never runs from Stop hooks, initializes stores, writes home/global context, collects raw chat, or duplicates one fact in both stores.
---

# Management Project Context Checkpoint

## Routing Card
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

### Resource Closure

```json
[
  {
    "source": "shared/docs/knowledge_record_contract.md",
    "target": "references/knowledge_record_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/memory_mutation_contract.md",
    "target": "references/memory_mutation_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/project_context_manifest.md",
    "target": "references/project_context_manifest.md",
    "projection": "verbatim",
    "load": "must_read",
    "condition": "selected skill's mandatory read contract applies"
  }
]
```

## Authorization Boundary
An ordinary commit request does not authorize or invoke this checkpoint. An explicit context-checkpoint request made alongside a commit authorizes only clear durable context finalized by that same commit and existing repository-contained project stores. It does not authorize store initialization, unrelated cleanup, external/home writes, LLM Wiki mutation, or another approval prompt for each clear item. An explicit closeout/record request provides the same bounded authorization without authorizing a Git commit; an external Knowledge store is writable only when that request names or approves its exact resolved `knowledge_root` and any `knowledge_index` outside that root.

Respect manifest persistence:

- `storage: repository`: include the owned context file in the proposed commit scope and report it.
- `storage: local`: update only when the checkpoint is authorized, but do not force-add an ignored/local file.

## Classification

| Durable content | Destination | Owner |
| --- | --- | --- |
| recurring interaction/execution mistake | Memory candidate | `management-memory-bank-update` in `candidate_mistake` mode |
| cross-session project goal, working rule, or successful practice | Memory active item | `management-memory-bank-update` in `durable_item` mode |
| new domain/design/algorithm/architecture knowledge or recurring repository review rule | new Knowledge category identity | `management-knowledge-base-record` after overlap classification |
| existing Knowledge rule observed again or semantically changed | Knowledge observation/revision/relation | `management-knowledge-base-update` with stable provenance and history |
| accepted durable plan/decision change | new or existing Knowledge identity | `management-knowledge-base-record` or `management-knowledge-base-update` after plan-admission and overlap classification |
| task status, raw log/chat, one-off comment, speculative idea, generic advice | no write | none |

If one statement could fit both stores, choose its primary future use: agent interaction/working behavior goes to Memory; product/project truth and artifact-linked rules go to Knowledge. Never duplicate it for convenience.

## Workflow
1. Resolve the nearest manifest and verify each declared target exists. Bind `memory_root`/`memory_file` or `knowledge_root`/`knowledge_index` once for the selected destination and reuse them through the delegated operation. Missing targets are no-write; do not initialize or search elsewhere.
2. Read the current task diff/artifacts and only accepted decision slices. Derive candidate statements without copying raw chat.
3. Classify each candidate as Memory, Knowledge, or transient. Exclude ambiguous, speculative, sensitive, and one-off material; treat an already-recorded fact as a possible source-traced observation or no-op rather than a duplicate record.
4. For Knowledge candidates, admit only accepted/current durable statements, exclude TODOs/estimates/chronology/speculation, then classify same identity, dependent recurrence, amendment, replacement, scope overlap, conflict, or new identity. Preserve stable plan/work/canonical refs and a provenance root; never infer causality from plan proximity or turn repeated wording into confidence.
5. Delegate each admitted item to the narrow owner and apply its normal mutation/readback contract. Keep one checkpoint owner and one changed-file inventory.
6. Confirm no identity or observation was duplicated, contradictions remain visible, no unrelated store content changed, and `storage` staging behavior was respected.
7. Return the exact context files changed or `no durable context to record`, then let the normal commit/closeout owner continue.

## Output
Return trigger, manifest, admitted/excluded candidates with concise reasons, destination/record IDs, changed files, repository/local staging status, readback, and unresolved ambiguity. Omit raw source text and empty categories.
