---
name: artifact-librarian
description: Helps summarize important task artifacts and verification notes without maintaining a persistent 7.0 artifact registry.
---

# Artifact Librarian

## Routing Card
- role: support
- intent_signature:
  - artifact summary
  - verification note
  - stale artifact note
  - follow-up artifact
  - output inventory
- use_when:
  - the user asks to summarize produced files, verification evidence, or stale follow-up candidates.
  - a handoff needs a small artifact inventory.
- do_not_use_when:
  - the task only needs source edits and a brief final answer.
  - a persistent registry, event log, deployment tracker, or evidence-finality queue would be required.
- expected_inputs:
  - changed file paths
  - checks run
  - relevant user-facing artifacts
- expected_outputs:
  - concise artifact inventory in the current response or an explicitly requested handoff note
  - no persistent artifact registry
  - no event log
- context_targets:
  must_read:
    - current task diff or provided artifact list
  read_if_needed:
    - active plan document
  do_not_load_by_default:
    - live `$HOME/.codex`
    - unrelated artifacts
    - historical workflow harness files
- risk_profile:
  reads:
    - task-local artifacts only
  writes:
    - none unless the user explicitly requested a document update
  tools:
    - local validation commands when relevant
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Verification Labels
- `agent-verified`
- `user-verification-needed`
- `unverified`
- `blocked`
