# Delivery Slice Contract

Use this contract only when an approved change needs more than one executable batch. It is a batching heuristic, not a router, plan requirement, development methodology, or completion proof.

## Delivery Shape Selection

First decide whether decomposition is needed. If one coherent change and check fit the execution boundary, classify it as `single_batch` only when a report needs the term, then stop without loading, recording, or applying the rest of this contract. Otherwise select one multi-batch `delivery_shape` before decomposition:

| shape | use when | consequence |
| --- | --- | --- |
| `single_batch` | one coherent change and its matching check fit the current execution boundary | Optional classification only; do not persist slice metadata or apply the rest of this contract. |
| `vertical_slice` | feature behavior needs several batches and each can expose a bounded consumer-visible or operational outcome | Use the thin observable path rules below. |
| `migration_sequence` | compatibility or mechanical breadth requires old and new forms to coexist while callers move | Use `expand -> migrate -> contract`. |
| `evidence_unit` | research, documentation, infrastructure, data work, or source maintenance has no honest feature path | Use the smallest independently reviewable unit with a matching observation. |

Shape follows the actual dependency and observation path, not the work's label. A data change that needs coexistence is a `migration_sequence`; a bounded operational data task may be an `evidence_unit`. This contract does not mandate TDD, one ticket per slice, or any UI/API/database/test layer that the outcome does not cross.

## Default: Thin Observable Path

Prefer the smallest coherent slice that makes one externally observable behavior work through every relevant layer of its real path. A good slice:

- has one user/public/consumer-visible outcome or one directly observable operational effect;
- includes only the schema/config, policy owner, implementation, caller/adapter, and verification surfaces that outcome actually crosses;
- can be demonstrated or decisively checked independently;
- fits one bounded implementation context and leaves the repository in a valid state;
- names blockers and does not claim independence when another slice must land first.

Do not interpret “vertical” as touching every architectural layer. Omit irrelevant layers, and do not create a UI, API, database, mock, fixture, or test framework merely to make a slice look end-to-end.

## Migration Sequence

Use `expand -> migrate -> contract` when one mechanical or compatibility change has a blast radius that cannot stay valid as a thin feature slice:

1. `expand`: introduce the new form beside the old without breaking existing consumers;
2. `migrate`: move callers in bounded batches, each with its own observable compatibility check;
3. `contract`: remove the old form only after direct search/readback shows no required consumer remains.

When individual migration batches cannot remain valid alone, keep them behind an explicitly named integration boundary and reserve the green claim for the final integration check. Do not call a knowingly broken intermediate state complete.

## Evidence Unit

Research, documentation, infrastructure, data migration, and broad source maintenance may not have a user-facing vertical path. Use the smallest independently reviewable and evidence-bearing unit appropriate to that work instead of manufacturing a feature slice. Preserve the same rules: bounded outcome, explicit dependencies, valid intermediate state, and a matching check.

## Evidence Boundary

A completed slice proves only its own outcome. It does not imply phase or plan completion, and an authored test or structural check does not replace direct evidence for the behavior the slice claims.

Direct implementation may report that its scoped production change is present while lowering the task result to `unverified` or `user-verification-needed` for a missing observation. It must not call a delivery unit evidenced or complete. A copied Plan/Handoff marks a node complete only when every material node condition has matching evidence. Review availability changes that state only when the accepted plan makes review an exit gate.
