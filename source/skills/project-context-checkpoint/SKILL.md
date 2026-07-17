---
name: project-context-checkpoint
description: At an explicit project commit request or explicit closeout/record request, classify newly finalized durable context into an existing project Memory Bank or Knowledge Base declared by project-context.yaml. Use only for the current task's clear changes; never run from Stop hooks, initialize stores, write home/global context, collect raw chat, or duplicate one fact in both stores.
---

# Project Context Checkpoint

## Routing Card
- role: context_operation
- intent_signature: project commit/closeout durable context checkpoint
- use_when:
  - the user requests a commit and the nearest manifest declares an existing Memory or Knowledge store; or
  - the user explicitly requests closeout, context recording, or Memory/Knowledge checkpointing
- do_not_use_when:
  - ordinary session stop or status reporting
  - no store is declared/existing
  - the task produced no clear durable context
  - common/home Memory, another project, or raw conversation capture is requested implicitly
- expected_inputs: current request, relevant diff/artifacts, accepted decisions, manifest, and existing target indexes/current snapshots
- expected_outputs: no-op or minimal delegated Memory/Knowledge mutations plus exact changed-file/staging report
- context_targets:
  must_read: current task outcome, relevant diff/accepted decision slice, nearest `project-context.yaml`, and matching target current/index entries
  read_if_needed: direct plan/source/design refs needed to establish durability or avoid duplicates
  do_not_load_by_default: full chat, full plan history, full stores, events/archive, unrelated repo history, home/common context
- risk_profile:
  reads: current-task evidence and declared stores only
  writes: existing declared project-local stores only
  tools: targeted local read/edit/readback; normal commit tooling remains with the commit owner
  sensitive_resources: raw private text and credentials denied
- entry_scene: PREPARE

## Authorization Boundary
A commit request authorizes this checkpoint only for clear durable context finalized by the same commit and existing project-local stores. It does not authorize store initialization, unrelated cleanup, home/global writes, LLM Wiki mutation, or another approval prompt for each clear item. An explicit closeout/record request provides the same bounded authorization without authorizing a Git commit.

Respect manifest persistence:

- `storage: repository`: include the owned context file in the proposed commit scope and report it.
- `storage: local`: update only when the checkpoint is authorized, but do not force-add an ignored/local file.

## Classification

| Durable content | Destination | Owner |
| --- | --- | --- |
| recurring interaction/execution mistake | Memory candidate | `memory-bank-correction-capture` |
| cross-session project goal, working rule, or successful practice | Memory active item | `memory-bank-update` |
| domain/design/algorithm/architecture knowledge or recurring repository review rule | Knowledge category record/update | matching `knowledge-*-record` or `knowledge-base-update` |
| accepted durable plan/decision change | Knowledge decision or affected category | `knowledge-plan-sync` |
| task status, raw log/chat, one-off comment, speculative idea, generic advice | no write | none |

If one statement could fit both stores, choose its primary future use: agent interaction/working behavior goes to Memory; product/project truth and artifact-linked rules go to Knowledge. Never duplicate it for convenience.

## Workflow
1. Resolve the nearest manifest and verify each declared target exists. Missing targets are no-write; do not initialize or search elsewhere.
2. Read the current task diff/artifacts and only accepted decision slices. Derive candidate statements without copying raw chat.
3. Classify each candidate as Memory, Knowledge, or transient. Exclude ambiguous, speculative, already-recorded, sensitive, and one-off material.
4. Delegate each admitted item to the narrow owner and apply its normal mutation/readback contract. Keep one checkpoint owner and one changed-file inventory.
5. Confirm no item was duplicated, no unrelated store content changed, and `storage` staging behavior was respected.
6. Return the exact context files changed or `no durable context to record`, then let the normal commit/closeout owner continue.

## Output
Return trigger, manifest, admitted/excluded candidates with concise reasons, destination/record IDs, changed files, repository/local staging status, readback, and unresolved ambiguity. Omit raw source text and empty categories.
