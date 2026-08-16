---
name: knowledge-base-record
description: Create one new accepted domain, design, algorithm, architecture, decision, or recurring code-review record in an existing declared project Knowledge Base, including a durable decision admitted from an approved plan. Use only for a genuinely new identity; use knowledge-base-update for an existing identity, and never record tentative plans, TODOs, chronology, generic advice, or unanchored material.
---

# Knowledge Base Record

## Routing Card
- role: knowledge_operation
- intent_signature: create one new durable project Knowledge record by category, including one approved-plan decision
- use_when: the user explicitly requests recording or syncing one accepted project-specific fact, rule, boundary, or decision that does not already have a Knowledge identity
- do_not_use_when: the item is unresolved, generic, temporary, one-off, belongs to Memory, lacks authoritative anchors, or updates an existing record
- expected_inputs: category, accepted statement or approved plan slice, aliases/search terms, scope, canonical/evidence/work-item refs, consumers, overlap candidates, and declared store
- expected_outputs: one category-valid record, one index row, typed relations or observations when applicable, and direct readback
- context_targets:
  must_read:
    - exact or manifest-declared Knowledge root/index
    - matching records and `.codex/docs/knowledge_record_contract.md`
    - direct canonical/evidence anchors for the selected category
  read_if_needed:
    - `references/knowledge-category-profiles.md` for the selected category's admission and body fields
    - one representative consumer, counterexample, benchmark, or design source when the category profile requires it
  do_not_load_by_default:
    - full store or repository, unrelated categories, Memory, LLM Wiki, transcripts, review history, or benchmark history
- risk_profile:
  reads: matching records and exact category anchors
  writes: one new Knowledge record and its index row
  tools: targeted local read, edit, and readback
  sensitive_resources: private sources are admitted only as bounded summaries or stable scoped pointers
- entry_scene: PREPARE

## Category And Identity Gate
Select exactly one category: `domain`, `design`, `algorithm`, `architecture`, `code-review`, or `decision`. Read only that category's profile. Category selection changes the required body and anchors, not the shared record envelope or mutation workflow.

Create a record only when the statement is accepted, project-specific, durable, and a genuinely new identity. Search matching titles, aliases, scope, canonical anchors, relation targets, and provenance roots before writing. Classify the candidate as same identity, dependent recurrence, amendment, replacement, specialization/generalization, partial overlap, conflict, or new identity.

- Route same identity, recurrence, amendment, reverification, relinking, deprecation, or supersession to `knowledge-base-update`.
- Keep partial overlap as distinct identities with an explicit typed scope relation.
- Preserve conflicts; never merge or create a second identity from wording similarity.
- Reject speculative proposals, generic advice, transient status, one-off preference/review feedback, and source existence without claim support.

## Workflow
1. Bind `knowledge_root` and `knowledge_index` from the exact approved path or nearest `project-context.yaml`, and reuse both bound values for every record/index path. Missing or mismatched declarations are `unavailable`; never guess or scan for another store.
2. Confirm acceptance, durability, category, scope, and the profile-specific evidence contract. For plan input, admit only accepted/current durable statements and exclude TODOs, estimates, chronology, rejected proposals, and speculative future state. Inspect the exact anchors and only the representative consumers or counterexamples needed to disconfirm the candidate.
3. Search and classify overlap before assigning an ID. Route every existing identity to `knowledge-base-update` without writing a duplicate.
4. For a new identity, create one full current envelope with the selected `category`, aliases/search anchors, scope, canonical refs, consumers, typed relations/observations when supported, and one `created` semantic revision.
5. Add one navigable index row and read back the record, index, anchors, relations/history, provenance, consumers, and any supersession or conflict links.

## Output And Validation
Report `category`, record ID, identity classification, accepted source/provenance root, record/index paths, anchor and relation readback, affected consumers, and unresolved conflicts. Do not emit the full store or claim that structural consistency proves the recorded knowledge true.

Completion requires one new identity, all profile-required fields and anchors, the shared envelope, a matching index row, and target-only readback. Existing identities, missing anchors, unresolved acceptance, or unavailable stores remain no-write.
