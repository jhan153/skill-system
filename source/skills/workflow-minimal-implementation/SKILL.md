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
  - focused check for non-trivial logic
  - deletion-focused findings only when the diff shows pressure signals
- context_targets:
  must_read:
    - current implementation request
    - directly relevant source and local patterns
  read_if_needed:
    - dependency manifest when package choice is in scope
    - touched tests or validation contract for non-trivial logic
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
- Preserve trust-boundary validation, security, data-loss prevention, accessibility, operability, and explicit user scope.
- Apply the pressure only where a real complexity choice exists; otherwise stay silent.

## Minimum Ladder
Stop at the first rung that fully satisfies the current requirement:

1. Remove or defer behavior that is speculative rather than requested.
2. Use standard-library or native-platform behavior.
3. Reuse an installed dependency or an existing local helper.
4. Make the narrowest local implementation and focused test change.
5. Add a dependency, file, configuration surface, or abstraction only when the earlier rungs cannot satisfy a current requirement.

When two rungs are equally small, prefer the one that fits established local patterns and handles required edge cases better.

## Complexity Gate
Require a current-use justification for each new:

- package or framework;
- file or generated layer;
- interface, factory, adapter, registry, or wrapper;
- configuration option or extension point;
- generic infrastructure replacing one concrete use.

A possible future use is not a justification. Existing repeated use, a present boundary, or an explicit requirement is. If no justification exists, cut the addition or fold it into the narrow local change.

## Attach Points
- Before the primary workflow writes: identify `minimum_behavior`, the selected ladder rung, and any non-negotiable safeguard.
- During implementation: re-evaluate only when a pressure signal appears; do not narrate routine small choices.
- After implementation: run the review pass only if the diff added a dependency, abstraction, config surface, extra file, broad boilerplate, or substantially more churn than the behavior suggests.
- For non-trivial logic, require one focused runnable check in the repository's existing style. If it cannot run, leave the gap explicit rather than weakening the solution.

## Review Pass
Emit one line only for a meaningful cut:

`<path>:<line>: <tag>: <what to cut>. <replacement>.`

Tags:

- `delete`: unused or speculative behavior.
- `stdlib`: custom code covered by the standard library.
- `native`: custom/dependency code covered by the platform.
- `reuse`: duplicate of an existing helper or installed dependency.
- `yagni`: layer or option without a current second use or boundary.
- `shrink`: same behavior with less code and no safety/clarity loss.

If useful, end with `net: -<N> lines possible`; otherwise omit the estimate. If there is nothing material to cut, say `No material minimality cut.` This is not a correctness or release verdict.

## Output Contract
Expose only decisions that matter to the user or primary workflow:

- `change_shape`
- `reused`
- `skipped_complexity`
- `revisit_trigger`
- `focused_check`
- optional review findings

Do not produce a long minimalism report for a small diff. Use a `minimal:` code comment only when an intentional shortcut has a known ceiling; name both the ceiling and the condition that should trigger revision.

## Recovery and Limits
- If minimum behavior is ambiguous, choose the smallest safe interpretation and state the assumption, or ask one question when the deliverable would materially differ.
- If the minimal version fails validation, fix the cause; do not add bypasses or weaken checks to preserve diff size.
- If the user confirms the broader design, stop challenging its scope and apply minimality only inside that design.
- This modifier cannot enforce dependency or file budgets and is not a correctness, security, performance, or accessibility review.

## Validation
- Every added dependency, abstraction, config surface, and extra file has a current-use justification.
- The chosen rung satisfies all explicit behavior and safeguards.
- Non-trivial logic has a focused check or an explicit unverified gap.
- The review ran only when a pressure signal existed.
- The output records skipped complexity and a concrete revisit trigger without duplicating the primary workflow report.
