---
name: workflow-minimal-implementation
description: Conditional minimal-implementation policy for coding and refactoring work. Use when a task needs YAGNI discipline, standard-library/native-platform preference, dependency restraint, smallest correct diffs, or a post-change over-engineering check for added abstractions, files, packages, or boilerplate.
---

# Workflow Minimal Implementation

## Routing Card
- role: execution_modifier
- intent_signature:
  - `minimal-implementation`, `simplest correct solution`, `YAGNI`, `avoid over-engineering`, `최소 구현`, `과잉설계`
- use_when:
  - implementation or refactoring has credible pressure toward unnecessary dependencies, abstractions, config, boilerplate, or file churn.
  - the user explicitly asks for the smallest correct implementation, dependency restraint, or an over-engineering check.
- do_not_use_when:
  - the request is Q&A, research, planning, documentation, explanation, or review without implementation pressure.
  - the user explicitly chose a broader architecture or extensible framework and accepts its scope.
  - reducing scope would remove safety, data integrity, accessibility, compliance, migration safeguards, or a stated requirement.
- expected_inputs:
  - selected primary implementation workflow
  - required behavior and non-negotiables
  - relevant local patterns and planned/current diff
- expected_outputs:
  - minimum viable change shape and reuse choice
  - skipped complexity with a concrete revisit trigger
  - decisive check for the requested behavior
  - deletion-focused findings only when the diff shows pressure signals
- context_targets:
  must_read:
    - current implementation request
    - directly relevant source and local patterns
  read_if_needed:
    - dependency manifest when package choice is in scope
    - validation contract or actual output path for non-trivial behavior
    - current diff when review pressure signals appear
    - adjacent helper API when reuse is plausible
  do_not_load_by_default:
    - full repo, broad architecture docs, unrelated skills, old plans, or memory
- risk_profile:
  reads:
    - targeted source, manifest, tests, and diff only
  writes:
    - none directly; the primary workflow owns implementation
  tools:
    - focused search, diff, and validation tied to the chosen change
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Decision Contract
- Constrain solution shape; never replace the primary workflow or its correctness and validation duties.
- Optimize for the smallest coherent change that satisfies current requirements, not the fewest lines at any cost.
- Preserve canonical-source ownership, fail-closed behavior, security, data integrity, accessibility, operability, and explicit scope.
- Tests, mocks, interfaces, and wrappers do not substitute for the requested production path.
- Apply this modifier only where a real complexity choice exists.

## Minimum Ladder
Stop at the first rung that fully satisfies the current requirement:

1. Remove or defer behavior that is speculative rather than requested.
2. Use standard-library or native-platform behavior.
3. Reuse an installed dependency or an existing local helper.
4. Change the narrowest production owner and observe the affected path.
5. Add a dependency, file, configuration surface, or abstraction only when the earlier rungs cannot satisfy a current requirement.

When two rungs are equally small, prefer the one that fits established local patterns and handles required edge cases better.

## Complexity Gate
Require a current-use justification for every new package, file/layer, interface/adapter/wrapper, configuration option, or generic infrastructure. Future reuse is not justification; use an existing repeated need, present boundary, or explicit requirement. Keep source selection, policy, and fallback in their real owner rather than moving them into a convenience adapter.

## Attach Points
- Before writing, identify `minimum_behavior`, its production owner, the selected rung, and non-negotiable safeguards.
- Re-evaluate only when the diff adds a dependency, abstraction, config surface, file, boilerplate, or disproportionate churn.
- Use one decisive runnable check or readback for non-trivial behavior. A regression test is useful after the contract is known, but cannot alone prove a semantic condition or an unexercised production path.

## Review Pass
Emit one line only for a meaningful cut:

`<path>:<line>: <tag>: <what to cut>. <replacement>.`

Use `delete`, `stdlib`, `native`, `reuse`, `yagni`, or `shrink`. Optionally end with `net: -<N> lines possible`. If there is no material cut, say `No material minimality cut.` This is not a correctness or release verdict.

## Output Contract
Expose only decisions that matter to the user or primary workflow:

- `change_shape`
- `reused`
- `skipped_complexity`
- `revisit_trigger`
- `focused_check`
- optional review findings

Do not produce a long report for a small diff. Use a `minimal:` code comment only for an intentional shortcut with a named ceiling and revision trigger.

## Recovery and Limits
- Ask one question only when competing interpretations materially change the deliverable; otherwise state the smallest safe assumption.
- Fix the cause of failed validation. Do not add a bypass, silent fallback, weaker check, or mock-only path to preserve diff size.
- Apply minimality inside a user-confirmed broader design. This modifier is not a correctness, security, performance, or accessibility review.

## Validation
- Every added dependency, abstraction, config surface, and extra file has a current-use justification.
- The chosen rung satisfies all explicit behavior and safeguards.
- Non-trivial behavior has a decisive check/readback or an explicit unverified gap.
- The review ran only when a pressure signal existed.
- The output records skipped complexity and a concrete revisit trigger without duplicating the primary workflow report.
