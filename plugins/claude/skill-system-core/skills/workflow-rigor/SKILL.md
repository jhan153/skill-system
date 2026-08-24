---
name: workflow-rigor
description: Attach optional risk-proportional execution assurance to an active behavior-changing workflow when independent checker separation, rollback/readback, or explicit strict evidence is material. This is the Workflow family's non-node execution modifier; it never owns mutation, Plan transitions, or ordinary low-risk evidence handling.
disable-model-invocation: true
---

# Workflow Rigor

## Routing Card

- family: workflow
- role: execution_modifier
- intent_signature: strict evidence, independent checker, rollback/readback assurance, execution rigor, 실행 통제
- use_when:
  - an active behavior-changing workflow has a material maker/checker separation problem;
  - destructive, auth/security, schema/data, infrastructure, external-write, or broad-refactor risk requires stronger assurance; or
  - the user or an accepted contract explicitly requests strict execution evidence.
- do_not_use_when:
  - no primary execution owner is active;
  - the work is low-risk, explanation-only, formatting-only, or already covered by an equivalent specialist gate; or
  - the request is merely to run ordinary validation or produce a report.
- expected_inputs: active workflow or DAG node, fixed implementation snapshot, material conditions and risks, available evidence, and accepted exit gates
- expected_outputs: assurance mode and basis, fixed point, independent review evidence when required, rollback/readback evidence when required, and remaining uncertainty
- context_targets:
  must_read: active request/contract, primary owner scope, fixed implementation snapshot, and the evidence directly tied to the selected assurance mode
  read_if_needed: one governing Contract/Spec slice, one Repository/Constraints slice, or the exact rollback/readback surface
  do_not_load_by_default: full repository, full Plan/Handoff, unrelated reports, worker transcripts, or previous reviewer reasoning
- risk_profile:
  reads: fixed snapshot, governing sources, and targeted evidence
  writes: none; the primary workflow owns mutation
  tools: targeted readback and independent read-only review only
  sensitive_resources: runtime policy owns permission and side-effect boundaries
- entry_scene: PREPARE

## Identity

`workflow-rigor` belongs to the Workflow family because it changes how active execution is
assured. It is not an executable work node. Attach it to one primary workflow or declared DAG
node; never schedule it as a successor, give it production ownership, or let it select the next
node.

The global harness already owns baseline evidence integrity, result labels, and the rule that a
check proves only its matching condition. Do not invoke this skill to restate that baseline. Its
only distinct job is optional assurance above the baseline.

## Assurance Modes

If neither mode is triggered, do not attach this skill.

| Mode | Select when | Added assurance |
|---|---|---|
| `standard` | A material completion claim otherwise rests mainly on maker-authored implementation and checks, or moderate risk makes one independent challenge valuable. | Pin one fixed point and run the single `Contract/Spec` or `Repository/Constraints` pass most likely to falsify the claim. |
| `strict` | Destructive, auth/security, schema/data migration, infrastructure, external-write, broad-refactor, or explicitly highest-rigor work is in scope. | Keep `Contract/Spec` and `Repository/Constraints` as separate independent passes and include rollback/readback evidence where relevant. |

Reviewer availability does not create work. If an independent pass is material but unavailable,
record that limitation and lower the task result label. It changes a node or plan state only when
the accepted contract already names that assurance as an exit gate.

## Review Axes

- `Contract/Spec`: missing or partial requirements, wrong behavior, scope drift, and mismatch
  against the accepted source.
- `Repository/Constraints`: repository instructions, architecture and ownership boundaries,
  compatibility, accepted local patterns, and material defects introduced by the fixed snapshot.

Give an independent reviewer the fixed snapshot and only its governing axis. Do not seed the
expected verdict, maker conclusion, or another review. Review judgment never replaces direct
condition evidence or turns maker-authored checks into an independent product oracle.

## Attachment Contract

- The primary workflow retains scope, writes, validation ownership, finding resolution, and final
  synthesis.
- In a DAG, record `assurance: standard | strict` on the owning node or graph contract. Rigor itself
  is not a node and creates no edge.
- If the Plan requires a separate review node, the Coordinator schedules the declared review
  workflow and consumes its normal result. `workflow-rigor` neither produces nor consumes Core
  execution cards.
- Rigor cannot edit Plan/Handoff, grant permission, choose a successor, finalize a Known Bug, or
  turn unavailable evidence into `blocked` unless the accepted exit gate is genuinely unmet.
- Reuse an equivalent specialist review or readback; never duplicate it only to satisfy a mode.

## Workflow

1. Confirm the active primary owner, material conditions, accepted exit gates, and fixed point.
2. Select `standard`, `strict`, or no attachment from consequence, reversibility, coupling, and
   evidence independence—not file count or duration.
3. Run only the additional independent pass or rollback/readback observation selected by that
   mode.
4. Return the assurance evidence and its exact scope to the primary owner. Preserve contradictions
   and unavailable inputs without changing the owner's task state.

## Output Contract

Return only applicable fields: `assurance_mode`, `risk_basis`, `fixed_point`,
`independent_review`, `rollback_or_readback`, `unavailable_inputs`, and
`remaining_uncertainty`. Do not return changed files as if this modifier owned the implementation.
