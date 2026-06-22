---
name: knowledge-base-maintenance
description: Validate, review, and maintain Wiki Bank source/claim/edge stores and knowledge feedback packets without direct hook mutation.
---

# Knowledge Base Maintenance

## Routing Card
- role: primary
- intent_signature:
  - Wiki Bank maintenance
  - knowledge proposal review
  - promote knowledge feedback
  - supersede knowledge claim
  - conflict or trust policy
- use_when:
  - the user explicitly asks to inspect, validate, review, promote, reject, supersede, or reconcile Knowledge Store entries.
  - a feedback packet needs human-reviewable proposal handling.
  - source, claim, edge, trust, conflict, freshness, or supersession metadata must be checked.
- do_not_use_when:
  - a task only needs read-only Context Pack compilation; use `knowledge-context-harness`.
  - the user asks for ordinary Memory Bank mutation; use the matching memory-bank skill.
  - hooks or agent runs emit a candidate packet but no explicit maintenance/review request exists.
- expected_inputs:
  - Knowledge Store path
  - source/claim/edge/context-pack/feedback files
  - explicit review or maintenance action
  - validation command
- expected_outputs:
  - validation result
  - proposed accepted/rejected/superseded changes
  - conflict, trust, freshness, and load-policy notes
  - no automatic promotion without explicit approval
- context_targets:
  must_read:
    - target Knowledge Store files
    - feedback packet or claim IDs under review
    - `.codex/schemas/knowledge/*.schema.json`
  read_if_needed:
    - generated Wiki Projection
    - Runtime Projection cards
    - raw source handles for disputed claims
  do_not_load_by_default:
    - all historical plans
    - raw chat transcripts
    - unrelated Memory Bank entries
    - credentials
- risk_profile:
  reads:
    - knowledge store and selected source handles
  writes:
    - knowledge store files only after explicit maintenance intent
  tools:
    - `.codex/tools/validate_knowledge_store.py`
    - `.codex/tools/build_context_pack.py --check`
  sensitive_resources:
    - external/private source locators require verification before promotion
- entry_scene:
  - PREPARE

## Policy
- Accepted knowledge is mutated only through explicit maintenance/review flow.
- Agent Run output and hooks may produce feedback candidates, not accepted knowledge.
- Source of Truth remains source evidence; Wiki and Runtime Projection are derived.
- Runtime Projection drift must be fixed by regenerating from accepted claims, not editing generated cards by hand.
- Supersession and conflict records must keep source provenance.

## Workflow
1. Identify the requested maintenance action: validate, review, promote, reject, supersede, reconcile, or regenerate.
2. Validate the current store with `validate_knowledge_store.py`.
3. If projections are in scope, validate them with `--require-projections` and `build_context_pack.py --check`.
4. For proposal review, inspect evidence refs and source freshness before changing accepted claims.
5. Apply only the explicitly approved Knowledge Store change.
6. Regenerate projection artifacts after accepted knowledge changes.
7. Report changed claims/edges/sources, validation evidence, and remaining review risks.

## Output Contract
```yaml
knowledge_maintenance:
  action:
  reviewed_items: []
  accepted_changes: []
  rejected_changes: []
  supersession_or_conflicts: []
  projection_regenerated: false
  validation:
    command:
    result:
```

## Compatibility Boundary
- Memory Bank skills keep ownership of explicit persistent memory operations.
- Knowledge Store may reference Memory Bank as a source lane, but this skill does not rewrite Memory Bank files.
- Kanboard and plan documents enter as source records or candidate metadata until separately promoted.

## Known Limits
- Current validator covers file-backed source/claim/edge/context-pack/feedback references and generated projection freshness.
- Trust scoring, dense retrieval, and full conflict-resolution automation are not implemented in this phase.
