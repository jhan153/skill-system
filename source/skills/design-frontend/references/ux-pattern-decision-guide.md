# UX Pattern Decision Guide

Use this guide only when implementation must choose a material interaction pattern or control that is not already fixed by the target artifact, approved component catalog, or supplied product requirement. It improves implementation judgment; it does not authorize product strategy, user research findings, copy, or KPI invention.

## Decision inputs

Record the evidence available for:

- primary user task and critical success path;
- frequency and user expertise;
- choice cardinality, label length, and whether choices are mutually exclusive;
- reversibility, error cost, destructive impact, and permission boundary;
- latency, offline behavior, partial failure, and recovery needs;
- platform, viewport, input method, keyboard/touch expectations, and density;
- loading, empty, error, disabled, validation, success, and interrupted states;
- approved catalog candidates and nearby product-family precedents.

Mark missing inputs `unverified`. Do not fill them with plausible product assumptions.

## Control discriminators

Use these as questions, not universal styling rules:

| need | prefer when | reject or reconsider when |
| --- | --- | --- |
| button | the user initiates an action | the element only navigates, selects persistent state, or hides an immediate setting change |
| link/navigation item | destination change is the intent | the action mutates data without a destination |
| checkbox | independent options or explicit multi-select | choices are mutually exclusive |
| radio group | a small set of mutually exclusive choices should stay visible | the option set is long, dynamic, or space-constrained |
| segmented control | a few short peer modes switch the current view immediately | labels are long, choices are numerous, or selection submits a high-risk decision |
| select/combobox | many or dynamic choices need compact presentation; use search only when findability requires it | the few choices benefit from direct comparison |
| switch | a binary setting takes effect immediately and its current state is clear | the change requires form submission, is destructive, or needs substantial explanation |
| dialog/sheet | a scoped task must interrupt or confirm the current context | routine browsing, long multi-step work, or reference content needs persistent context |
| inline disclosure | optional details or local controls can expand without losing context | the content blocks the primary flow or needs its own navigation state |
| table/list/card | choose from comparison density, scan path, available actions, and responsive constraints | visual fashion is the only rationale |

Prefer an approved catalog component that satisfies the semantic role and required states. Do not custom-build a visually novel control to bypass a catalog match.

## Risk and recovery

- For reversible actions, prefer clear feedback and undo when the product policy supports it.
- For destructive, irreversible, costly, or permission-changing actions, expose consequences and use the project-approved confirmation pattern; do not add redundant confirmations to low-risk routine actions.
- Define pending, success, error, retry, cancel, duplicate-submit, and partial-success behavior when latency or mutation makes them possible.
- Preserve entered data across recoverable failures when project behavior permits.
- Connect mutations to an existing API/action/callback or an accepted repo fixture. Do not synthesize a successful default handler, delay, local persistence, or swallowed failure to demonstrate the flow.
- When the real handler or runnable fixture is absent, keep the integration boundary explicit and the critical path `unverified`; a rendered success message is not execution evidence.
- Keep primary action availability, validation timing, focus movement, and keyboard/touch behavior explicit.

## Decision record

```yaml
ux_pattern_decision:
  primary_user_task:
  evidence: []
  constraints:
    frequency_and_expertise:
    choice_complexity:
    reversibility_and_error_cost:
    latency_and_failure:
    platform_and_input:
  catalog_candidates: []
  selected_pattern:
  selected_component:
  rejected_alternatives:
    - option:
      reason:
  required_states: []
  recovery_behavior: []
  critical_path_steps: []
  conflicts: []
  unverified: []
```

Validate that the selection cites supplied requirements, repo evidence, or a marked inference; covers the material failure/recovery states; preserves accessible semantics; and does not invent business policy. If the missing context could reverse the decision, ask for that decision or keep the implementation `user-verification-needed`.
