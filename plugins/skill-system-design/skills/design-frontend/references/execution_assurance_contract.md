# Execution Assurance Contract

This contract adds optional risk-proportional assurance to one active primary owner whose work
changes behavior or durable state, or produces material validation evidence. It is not a skill,
executable node, verifier, report, or second implementation owner. Baseline evidence
integrity, result labels, and the rule that a check proves only its matching condition remain global
requirements; do not load this contract merely to restate them.

## Activation Boundary

Apply this contract only when:

- a material completion claim would otherwise rest mainly on maker-authored implementation and
  checks;
- destructive, auth/security, schema/data, infrastructure, external-write, or broad-refactor risk
  requires stronger assurance; or
- the user or an accepted contract explicitly requires standard or strict execution assurance.

Do not apply it when no applicable primary owner is active, the work is low-risk or explanation-only,
ordinary validation is sufficient, or an equivalent specialist gate already provides the same
independent review or readback. A validation-only or report request keeps its own primary owner.

## Assurance Modes

If neither mode is triggered, add no assurance mode or extra work.

| Mode | Select when | Added assurance |
| --- | --- | --- |
| `standard` | A material completion claim otherwise rests mainly on maker-authored implementation and checks, or moderate risk makes one independent challenge valuable. | Pin one fixed point and run the single `Contract/Spec` or `Repository/Constraints` pass most likely to falsify the claim. |
| `strict` | Destructive, auth/security, schema/data migration, infrastructure, external-write, broad-refactor, or explicitly highest-rigor work is in scope. | Keep `Contract/Spec` and `Repository/Constraints` as separate independent passes and include rollback/readback evidence where relevant. |

Reviewer availability does not create work. If a material independent pass is unavailable, record
the limitation and lower the task result label. It changes a node or Plan state only when the
accepted contract already names that assurance as an exit gate.

## Review Axes

- `Contract/Spec`: missing or partial requirements, wrong behavior, scope drift, and mismatch
  against the accepted source.
- `Repository/Constraints`: repository instructions, architecture and ownership boundaries,
  compatibility, accepted local patterns, and material defects introduced by the fixed snapshot.

Give an independent reviewer the fixed snapshot and only its governing axis. Do not seed the
expected verdict, maker conclusion, or another review. Review judgment never replaces direct
condition evidence or turns maker-authored checks into an independent product oracle.

## Ownership And Attachment

- The primary workflow retains scope, writes, validation ownership, finding resolution, and final
  synthesis.
- In a DAG, record `assurance: standard | strict` on the owning node or graph contract. Assurance is
  not a node and creates no edge or successor.
- Attach a mode only when the owning primary contract explicitly declares its local
  `references/execution_assurance_contract.md` or an accepted external contract supplies an
  equivalent gate. Otherwise keep assurance unresolved instead of assuming cross-plugin access.
- If the Plan requires a separate review node, the Coordinator schedules the declared review owner
  and consumes its normal result. Assurance neither produces nor consumes Core execution cards.
- Assurance cannot edit Plan/Handoff, grant permission, choose a successor, finalize a Known Bug, or
  turn unavailable evidence into `blocked` unless an accepted exit gate is genuinely unmet.
- Reuse an equivalent specialist review or readback; never duplicate it only to satisfy a mode.

## Procedure

1. Confirm the active primary owner, material conditions, accepted exit gates, and fixed point.
2. Select `standard`, `strict`, or no assurance from consequence, reversibility, coupling, and
   evidence independence, not file count or duration.
3. Run only the additional independent pass or rollback/readback observation selected by that mode.
4. Return the assurance evidence and exact scope through the primary owner's normal result. Preserve
   contradictions and unavailable inputs without changing the owner's task state.

## Result Fields

Return only applicable fields through the primary owner: `assurance_mode`, `risk_basis`,
`fixed_point`, `independent_review`, `rollback_or_readback`, `unavailable_inputs`, and
`remaining_uncertainty`. These fields never imply that assurance owned the implementation.
