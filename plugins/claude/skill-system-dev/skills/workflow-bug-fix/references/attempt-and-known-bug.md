# Bug-Fix Attempt And Known Bug Contract

Read this reference when a prior attempt exists, a Plan DAG assigns `BF1`/`BF2`, or standalone repair may need a second locally reviewed round.

## Problem Identity And Modes

Use one `bug_scope` plus one `failure_fingerprint`. The fingerprint includes the command or user path, failing phase/test/symbol, and first stable causal error, assertion, exit class, or observed mismatch. Ignore timestamps, temporary paths, random IDs, ordering noise, and wrapper frames.

A repair intervention is one code, configuration, test, or harness change intended to alter that problem. A diagnostic observation or unchanged rerun is not another intervention. Preserve history across retriggers, agents, and compaction.

- **DAG mode:** `node_id`, `round`, and `source_review_item_ref` are supplied from Plan/Coordinator. The assigned `BF1` or `BF2` performs exactly one intervention and returns.
- **Standalone mode:** those Plan fields are absent. The workflow may own at most two locally reviewed interventions; the second is optional and evidence-gated.

## DAG Result Shape Authority

Cross-owner output must validate as `execution_item.kind: bug_fix_result` under the Core schema
referenced by `references/execution_item_contract.md`. This file does not redefine its envelope or
payload. `source_findings` must name concrete findings in `source_review_item_ref`; the Core
validator checks that reference. Each source finding's `required_condition` is the repair contract;
an optional `suggested_solution` is non-normative and never authorizes a broader rewrite.
`changed_snapshot` and `review_anchor` identify what a later review can inspect and are never
review verdicts.

## Attempt Observation

Expose exactly one `attempt_status` after the assigned intervention.

| status | meaning |
| --- | --- |
| `resolved` | the original material signal passes at its required scope with no contradiction observed by the bounded check |
| `narrowed` | evidence eliminates a credible cause while the original condition remains unresolved |
| `moved` | the stable causal signature changes |
| `unchanged` | the same fingerprint remains and the intervention adds no material information |
| `unreproducible` | the decisive signal cannot currently be observed |

A lower-scope pass alone is not `resolved` or `narrowed`. These statuses are observations, not Code Review dispositions or DAG permissions.

## DAG Authorization And Return

- `BF1/A1` returns after one intervention. It cannot begin `A2`.
- `BF2/A2` is valid only when the assigned input names the existing Plan node and includes concrete `CR1 repair_required` findings.
- Internal confirmation is limited to diff churn, one original-signal observation, actual-path readback, and attempt classification. `workflow-code-review` owns full static review and disposition.
- When a meaningful change remains, return `changed_snapshot_ready_for_review` with both anchors.
- When no meaningful change remains or the signal is unreproducible, return `no_change_unresolved` with null anchors as applicable. The consumer must not fabricate an empty Code Review or retry.
- After `A2`, return a non-final candidate when attempt evidence may later support Known Bug registration. `BF2` cannot know the later `CR2` disposition and therefore cannot finalize that record.

## Known Bug Candidate

When candidate evidence exists, emit a separate canonical
`execution_item.kind: known_bug_candidate` and place its item ID in
`bug_fix_result.payload.known_bug_candidate_ref`. Candidate attempt refs must point to the ordered
Core `bug_fix_result` cards for the same fingerprint and scope. Candidate status is unresolved and
therefore never `resolved`; the Core schema and validator own the exact fields.

The candidate contains no final Handoff status. Apply the Core-owned
`references/execution_item_contract.md` for review-result composition, final Known Bug ownership,
deferred carry, and Plan successor rules. `workflow-bug-fix` supplies repair evidence only; `A2`
is the maximum, not a required round.

## Standalone Finalization

Without Plan/Coordinator fields, the workflow may run its own bounded review between at most two interventions. After the optional second review remains unresolved, it may return a final standalone Known Bug result containing attempt history, `condition_status: excluded_known_bug`, and reopening condition. It still creates no third intervention or new validation campaign.
