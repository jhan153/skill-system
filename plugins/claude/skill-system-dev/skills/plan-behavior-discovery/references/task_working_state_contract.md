# Task Working State Contract

The current task owner keeps the smallest task-relevant working state needed to avoid losing a
constraint, acting on stale evidence, or repeating a settled decision. This is an epistemic aid,
not a new skill, execution contract, planning state, or persistence owner.

## Activation And Bypass

Use this contract only when at least one condition can materially change the outcome:

- unresolved interpretations would change the deliverable, boundary, or validation;
- a later decision depends on facts or choices from earlier turns that must remain distinguishable;
- a consequential or costly action depends on uncertain classification or evidence that can expire.

Informal wording, the number of messages, or task length alone is not an activation condition.
A clear one-shot task, such as correcting a named typo, stays direct: no working-state reference
load, question round, visible envelope, or state artifact. Preserve the current task owner when
this contract is used; it does not automatically start a discovery interview.

## Minimum State

Represent only entries that change an action, decision, or final claim. Plain prose or existing
artifact fields are sufficient; no fixed YAML envelope or complete checklist is required.

| Concern | Meaning to preserve when material |
|---|---|
| Objective and success | The requested outcome, scope, and observable completion condition. |
| Sourced facts | A bounded statement with its direct source or observation and the scope it establishes. |
| Hard constraints | An explicit authoritative requirement or established boundary; record who or what imposes it. |
| Soft preferences | A negotiable preference with its source; repetition or confidence does not make it mandatory. |
| Authority | The person, contract, or policy that may decide the field; evidence about behavior is not authorization. |
| Evidence status | Preserve observed, source-established, inferred, assumed, conflicting, or unavailable status separately from authority and task completion. |
| Freshness | Stable or dynamic; a dynamic entry names the change/event that requires refresh before use. |
| Dependent unknowns | The missing fact or choice, its owner, prerequisites, decision impact, and what it blocks. |

Use an ID only when another material entry actually depends on it. Add qualitative confidence only
when it changes the next question, action, or disclosure; explain its evidence basis rather than
inventing a numerical score. Class, authority, evidence status, confidence, and freshness are
separate axes. An accepted requirement can depend on an unverified implementation claim; a
confirmed fact cannot approve a proposed requirement or a source write.

## Freshness And Corrections

Before relying on a dynamic entry, check its declared refresh condition. A changed repository
revision, scope, availability, or source invalidates that entry until the narrowest permitted
observation refreshes it. Do not reread unrelated stable context on every turn.

On a correction, update the corrected entry and trace its actual dependents. Invalidate dependent
assumptions, unknown readiness, recommendations, validation choices, and response choices; then
recompute them from current evidence. Preserve unrelated sourced facts and already settled
decisions. A corrected provider scope may change the affected files without changing the privacy
constraint or repository identity. Never carry the previous answer forward with only a new label.

## Elicitation Mode

Resolve discoverable facts through the narrowest authorized source before asking the user.
Among unresolved decisions, consider only those whose prerequisites are ready; prefer the one
whose resolution changes the outcome most relative to user effort. This is a qualitative choice,
not a score or a new priority ledger.

| Mode | Admission and boundary |
|---|---|
| `inspect` | A permitted source can settle the fact; inspect that source and preserve its proof limit. |
| `ask_one` | One ready, material choice belongs to the user and cannot be resolved from existing authority. |
| `show_choices` | Concrete alternatives with grounded consequences help the answer owner decide; preserve the active skill's question limit and interaction format. |
| `assume_reversible` | Existing user delegation permits a low-impact reversible implementation default; state the assumption when it affects the result and retain its reversal condition. |
| `defer` | Required evidence or authority is unavailable; name the dependent action and continue independent authorized work. |

An unavailable fact or a still-human-owned choice cannot be replaced by `assume_reversible`.
Elapsed time, silence, a preferred option, or a confidence label is not an answer. Existing
authorization remains valid; do not ask the user to reconfirm an already decided boundary.
Requirements Discovery retains its bounded independent-question rounds; Behavior Discovery
retains exactly one question. This contract does not override either or require a question when
the task can proceed from settled intent.

## Response Surface

Choose the smallest surface that helps the current decision: a direct answer for settled work,
one focused question for a missing choice, short alternatives for a concrete tradeoff, or a compact
comparison when several exact relationships matter. A durable document is used only when already
requested or admitted by its owning workflow. Internal state need not be shown as a template.

Explicit user format, the selected skill's Output Contract, and machine-consumer fields outrank
this presentation choice. Preserve source attribution, uncertainty, exclusions, and verdict when
changing format. A polished response never upgrades assumed or stale evidence.

## Ownership And Retention

Working state stays within the active task by default. It does not authorize a file, hook record,
Memory Bank or Knowledge Base write, a new Plan/Handoff, or a second execution ledger. Runtime User
Work Contract identity, permissions, continuation, and enforcement keep their existing owner.

When an existing owner is already authorized to persist a discovery or requirements artifact,
project only the material entries needed by that artifact into its existing fields. Preserve
source, hard/soft meaning, evidence status, and any future refresh obligation. Keep unresolved
claims non-authoritative; do not rewrite an approved pinned input without its existing revision
procedure. Do not persist elicitation-mode history, confidence trends, or response-choice logs.

No raw prompt, transcript, tool-output dump, click/hover telemetry, personal profile, or inferred
long-term preference is collected. One task's preference does not silently become a global rule.
Static checks can establish this declared contract and package closure; actual interaction
usefulness requires observation at its own evidence boundary.
