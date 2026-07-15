---
name: knowledge-base-maintenance
description: Review and maintain accepted Wiki Bank claims against current source evidence; validate stores and projections without treating structural validity as semantic truth.
---

# Knowledge Base Maintenance

## Routing Card
- role: primary
- intent_signature:
  - Wiki Bank validation, proposal review, promotion, rejection, supersession, or conflict reconciliation
- use_when:
  - the user explicitly requests maintenance of Knowledge Store items or review of a feedback packet.
  - source, claim, edge, trust, freshness, conflict, or supersession metadata needs a decision.
- do_not_use_when:
  - read-only Context Pack compilation (`knowledge-context-harness`), Memory Bank mutation, or unrequested hook/agent-run candidate handling.
- expected_inputs:
  - store path, exact item/packet IDs, requested action, relevant source handles, and validation commands
- expected_outputs:
  - per-item evidence and decision, exact accepted/proposed changes, structural validation results, and unresolved risk
- context_targets:
  must_read:
    - target store items, packet/claim IDs, referenced source spans, and applicable knowledge schemas
  read_if_needed:
    - generated projections, Runtime cards, or current external/private source for the reviewed items
  do_not_load_by_default:
    - historical plans, raw transcripts, unrelated Memory Bank entries, credentials, or the whole store
- risk_profile:
  reads: selected store items and source handles
  writes: explicitly approved Knowledge Store items and regenerated projections only
  tools: `validate_knowledge_store.py`; `build_context_pack.py --check`
  sensitive_resources: external/private locators require scoped retrieval and provenance
- entry_scene:
  - PREPARE

## Authority And Admission
- Accepted knowledge changes only through an explicit maintenance request and item-level approval. Hook, Agent Run, loop, test, Kanboard, plan, or transcript output is a candidate/source lane, never automatic acceptance.
- For each material claim, connect the exact statement to current source IDs and spans, authority, freshness, verification state, and conflicts. Schema validity, reference consistency, and projection freshness prove only those contracts; they do not prove the statement true.
- Missing, stale, superseded, unreadable, or conflicting material evidence blocks acceptance until resolved or surfaced for an explicit user decision. A lower-scope pass cannot erase that state.
- Accepted claims are canonical for Wiki/Runtime projections, which are regenerated rather than hand-edited. Supersession/conflict records retain the old ID and source provenance.

## Workflow
1. Scope the requested action and exact source/claim/edge/packet IDs; do not widen a one-item decision into store cleanup.
2. Validate the pre-state with `validate_knowledge_store.py`; add `--require-projections` and `build_context_pack.py --check` only when projections are in scope.
3. Read each referenced source span and compare its current digest/freshness/authority with the proposed statement. Separate observed facts from interpretations, process lessons, temporary failures, and rejected shortcuts.
4. Decide each item as accept, reject, supersede, conflict, or needs user decision. Show the proposed diff and evidence before any accepted-store mutation.
5. Apply only approved items, preserving stable IDs and provenance. Regenerate derived projections from accepted claims.
6. Re-run store/projection validation and read back affected IDs. A pre-write pass is not post-write evidence, and a post-write structural pass is not semantic source proof.
7. Report per-item statement, source span, decision, mutation/readback, validation command/result, and remaining risk.

## Stop Policy
- `success`: the scoped validation/review is reported; an approved mutation also has affected-item readback and required projection regeneration.
- `approval`: an accepted item would change without explicit item-level authorization.
- `blocked`: required store/schema/source/command is missing, or IDs are unstable/duplicate/unmappable.
- `needs_review`: material evidence is stale, unverified, unreadable, or conflicting; preserve the proposal and request the exact decision/evidence needed.
- `unsafe`: candidate, generated projection, transcript, or private/external text would be silently accepted; or a generated card would be hand-edited.
- `fatal`: tool/schema/store inconsistency makes the scoped decision untrustworthy.

## Output Contract
For each reviewed item, return `id`, `statement/action`, `source evidence`, `decision`, `mutation/readback`, and `remaining risk`. For multi-item artifacts, also separate accepted, rejected, superseded/conflicted, and unresolved items; omit empty sections.

## Compatibility Boundary
- Memory Bank skills keep ownership of explicit persistent memory operations.
- Knowledge Store may reference Memory Bank as a source lane, but this skill does not rewrite Memory Bank files.
- Kanboard and plan documents enter as source records or candidate metadata until separately promoted.
