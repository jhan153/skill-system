---
name: report-lifecycle-artifacts
description: Package and trace explicitly selected existing lifecycle artifacts across requirements, design, implementation, review, validation, security, release, and retrospective evidence. Produce a content-first Markdown index and traceability matrix by default, with optional matching lifecycle HTML on explicit html/both intent. Do not generate empty SDLC shells, replace canonical Plan/Handoff or Core Cards, execute lifecycle work, infer completion, or run automatically at closeout.
---

# Report Lifecycle Artifacts

## Routing Card
- role: report_primary
- family: report
- intent_signature: explicit lifecycle artifact package, SDLC traceability index, selected delivery evidence package
- use_when:
  - the user explicitly requests packaging or normalization of named lifecycle artifacts and their evidence links
- do_not_use_when:
  - implementation, planning, status tracking, validation execution, critique, task-local inventory, or automatic closeout is primary
  - source artifacts do not exist and the request is merely to create generic planned shells
- expected_inputs: selected source artifacts, package scope, result/evidence authority, destination, and delivery mode
- expected_outputs: Markdown lifecycle index, selected artifact links/normalizations, traceability matrix, preserved gaps/statuses, and optional matching HTML trace
- context_targets:
  must_read:
    - explicit package scope, selected source artifacts, and evidence supporting represented results
    - `references/report_delivery_contract.md`
  read_if_needed:
    - `references/artifact-tiering.md` only to bound an explicitly requested package
    - `references/traceability-matrix-schema.md` for a persisted matrix
    - applicable requirements, Plan/Handoff, Core execution-item cards, review, validation, security, release, or retrospective artifacts named by the request
    - `references/report_canvas_contract.md` only for selected HTML delivery
    - `references/report_visual_authoring.md` only when packaged spatial evidence must be inspected
  do_not_load_by_default:
    - full repository, plan inventory, memory store, unrelated logs, generic templates, or generated mirrors
- risk_profile:
  reads: explicitly selected artifacts and condition-matched evidence
  writes: requested Markdown index/matrix, bounded normalization of selected artifacts, and only the selected optional HTML projection
  tools: local readback and optional report rendering; no implementation, validation, release, or external publication
  sensitive_resources: credentials denied; redact secrets and audience-sensitive data
- entry_scene: PREPARE

## Delivery And Ownership

Apply `references/report_delivery_contract.md`. Markdown is the primary lifecycle index. HTML may
only project the same artifact graph and statuses. A missing renderer never blocks the package or
changes a represented lifecycle result.

This skill packages and links existing evidence. It never creates a Plan/Handoff, changes its
state, reinterprets Core Cards, selects a successor, runs a gate, or claims delivery from document
presence. It is not an automatic closeout step.

## Package Contract

Select only artifacts explicitly requested or already present in the selected scope. Common source
classes include requirements, decision/design records, Plan/Handoff, implementation and review
results, validation evidence, security/risk records, release decisions, and retrospectives. Their
owning contracts remain authoritative.

Modes:

- `traceability_index`: index and matrix over selected existing artifacts; default.
- `selected_package`: index plus explicitly requested normalization/copy of named artifacts.
- `full_lifecycle_pack`: only when the user explicitly names the complete package scope and source
  artifacts; missing stages remain gaps rather than generated shells.

Never create empty milestone, HLD/LLD, QA, security, release, or retrospective documents merely to
complete a list. A requested new report is authored only from identified source evidence and stays
within that report's actual authority.

## Status And Evidence

Separate package construction from represented lifecycle results. Use typed lifecycle status only
for the source condition it describes: `planned`, `not_executed`, `evidence_unavailable`,
`needs_review`, `user_verification_needed`, `blocked`, `fail`, or the authoritative completed state
supplied by the source contract.

For every material link, record the source condition/claim, evidence scope, oracle origin, exact
reference, freshness, and preserved status. Structural checks close only structural link/matrix
conditions. Mocks, generated files, hooks, schemas, and harnesses prove only their own boundary.
Never lower an unresolved result because the package or a narrower check succeeded.

## Workflow

1. Bind package purpose, audience, selected source artifacts, destination, exact represented
   conditions, status authority, redaction boundary, and delivery mode.
2. Read each selected artifact once and preserve its identity, owner, status, evidence anchors,
   unresolved items, and relation to other selected artifacts. Do not reconstruct missing stages.
3. Build only the needed traceability rows using stable source IDs when available. A link records a
   relation; it does not manufacture requirement coverage, validation, or completion.
4. Normalize or copy an artifact only when explicitly requested and without replacing its canonical
   owner. Otherwise link the authoritative source in place.
5. Produce the Markdown lifecycle index and optional persisted matrix. If HTML is selected, project
   the same graph as a lifecycle trace and render once without adding nodes or statuses.

## Output Contract

Return only applicable fields:

- `artifact_scope` and `source_artifacts`
- Markdown lifecycle index
- requested normalized artifacts, if any
- traceability matrix
- condition-scoped evidence/status and gaps
- user-owned follow-ups
- optional lifecycle HTML link

Return the Markdown link first. Canvas is an optional navigation view over the package, never the
package or proof. A follow-up is a recommendation, not Handoff mutation or workflow dispatch.
