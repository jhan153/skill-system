# Bug-Fix Attempt And Known Bug Contract

Read this reference when a prior attempt exists, a Plan DAG assigns `BF1`/`BF2`, or standalone repair needs a continuation or stop decision after local review.

## Problem Identity And Modes

Use one `bug_scope` plus one `failure_fingerprint` under one accepted repair-contract reference carried by the Core `scope_ref` or direct task contract. The fingerprint includes the command or user path, failing phase/test/symbol, and first stable causal error, assertion, exit class, or observed mismatch. Ignore timestamps, temporary paths, random IDs, ordering noise, and wrapper frames.

A repair intervention is one code, configuration, test, or harness change intended to alter that problem while preserving the accepted repair contract. A diagnostic observation, unchanged rerun, or pre-edit owner-kind correction is not another intervention. Preserve genuine same-contract history across retriggers, agents, and compaction; a newly accepted production-mechanism replacement is Implementation scope, not a reset or continuation of this attempt ledger.

- **DAG mode:** `node_id`, `round`, and `source_review_item_ref` are supplied from Plan/Coordinator after semantic admission. The assigned `BF1` or `BF2` performs exactly one contract-preserving intervention and returns within the accepted copied graph's finite budget. A worker never extends that budget or switches to standalone mode to bypass it.
- **Standalone mode:** those Plan fields are absent. Locally review each bounded intervention; continue only under the gate below and any user-supplied budget. Use task-local ordinal attempt identities, never DAG `A1`/`A2` cards.

## DAG Result Shape Authority

DAG-assigned output must validate as `execution_item.kind: bug_fix_result` under the Core schema
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

## Standalone Continuation Gate

Keep one compact row per intervention: ordinal identity, problem/fingerprint and accepted-contract
reference, causal prediction, changed snapshot/source refs, original-signal observation,
actual-path readback, attempt status, and the decisive continuation or stop evidence. Preserve all
intervention identities across retriggers, agents, and compaction; summarize old evidence without
discarding causal exclusions. Reuse task-local output/context and create no new history artifact
by default.

After each local review:

1. Stop intervening when the original material condition is resolved with matching actual-path
   evidence. A narrower passing check does not close it.
2. Continue only when new causal or disconfirming evidence rules out a credible cause, or an
   explained change in the original signal demonstrates material progress, and that evidence
   supports one distinct next intervention. Name its causal prediction and the available
   original-signal/readback observation that could refute it before editing. Keep the same accepted
   repair contract and scope; preserve any user-supplied budget or stop term.
3. `narrowed` or `moved` is not authorization by itself: a different error, changed log, or another
   edited location must establish a new causal constraint or explained progress. Do not revisit
   a rejected cause unless new direct evidence contradicts the reason it was rejected.
4. If the same failure repeats without new evidence, make no further repair edit. One bounded
   diagnostic may resolve a named missing discriminator on the existing path; if it provides no
   new causal constraint, stop and return the unresolved condition. Do not restart unchanged
   checks, rotate equivalent patches, or open a new validation campaign to keep the loop alive.
5. Stop further interventions when the required original signal/readback is unavailable, the
   user-supplied budget is exhausted, or the next intervention lacks a distinct supported
   prediction. State the missing observation, evidence, or decision needed to resume. A changed
   production mechanism requires its proper owner; it is not a reset of this repair history.

There is no universal standalone attempt-count cap. Each continuation needs fresh qualifying
evidence; exhausted or repetitive speculation never earns another round.

## DAG Authorization And Return

- `BF1/A1` requires concrete `CR0 repair_required` findings and returns after one intervention. It cannot begin `A2`.
- `BF2/A2` is valid only when the assigned input names the existing Plan node and includes concrete `CR1 repair_required` findings.
- Internal confirmation is limited to diff churn, one original-signal observation, actual-path readback, and attempt classification. `workflow-code-review` owns full static review and disposition.
- When a meaningful change remains, return `changed_snapshot_ready_for_review` with both anchors.
- When no meaningful change remains or the signal is unreproducible, return `no_change_unresolved` with null anchors as applicable. The consumer must not fabricate an empty Code Review or retry.
- After `A2`, return a non-final candidate when attempt evidence may later support Known Bug registration. `BF2` cannot know the later `CR2` disposition and therefore cannot finalize that record.

## Known Bug Candidate

When candidate evidence exists, emit a separate canonical
`execution_item.kind: known_bug_candidate` and place its item ID in
`bug_fix_result.payload.known_bug_candidate_ref`. Candidate attempt refs must point to the ordered
Core `bug_fix_result` cards for the same fingerprint, scope, and accepted repair contract. Candidate status is unresolved and
therefore never `resolved`; the Core schema and validator own the exact fields.

The candidate contains no final Handoff status. Apply the Core-owned
`references/execution_item_contract.md` for review-result composition, final Known Bug ownership,
deferred carry, and Plan successor rules. `workflow-bug-fix` supplies repair evidence only; `A2`
is the maximum, not a required round.

## Standalone Finalization

Return the task-local attempt rows, decisive current evidence, stop reason, and any unresolved
condition with its resume requirement. Do not emit Core `bug_fix_result`, `known_bug_candidate`, or
`known_bug_record` cards, map later ordinals onto `A1`/`A2`, or automatically register/exclude a
Known Bug. Task labels never hide an unresolved original condition.

## Discriminating Cases

- **Progressing standalone repair:** after two interventions, original-path evidence eliminates a
  previously credible cause and supports a distinct third intervention under the same accepted
  contract. Continue after stating its refutable prediction; the count alone is not a stop reason.
- **Repeated failure:** the same fingerprint returns and the proposed next edit repeats an
  unsupported premise. A bounded discriminator finds nothing new. Stop with the unresolved
  condition instead of another patch or rerun.
- **Changed signature without progress:** a new exception merely masks the original failure.
  `moved` does not qualify; restore a discriminating observation before another intervention.
- **DAG limit:** assigned `BF2/A2` discovers a promising additional cause. Return its evidence and
  candidate within the existing graph; do not perform a third edit or adopt standalone mode.
