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
  - the request is only to reopen a broader architecture or framework the user already accepted; preserve that boundary, but apply this modifier to implementation choices inside it when requested.
  - reducing scope would remove safety, data integrity, accessibility, compliance, migration safeguards, or a stated requirement.
- expected_inputs:
  - primary workflow, required behavior/safeguards, relevant local patterns, and planned/current diff
- expected_outputs:
  - minimum change/reuse choice, skipped complexity and revisit trigger, decisive behavior check, and pressure-gated cuts
- context_targets:
  must_read:
    - implementation request, directly relevant source, and local patterns
  read_if_needed:
    - relevant manifest/helper, validation contract, actual output path, and current diff
  do_not_load_by_default:
    - full repo, broad architecture docs, unrelated skills, plans, or memory
- risk_profile:
  reads: targeted source, manifest, tests, and diff
  writes: none directly; the primary workflow owns implementation
  tools: focused search, diff, and behavior validation
  sensitive_resources: credentials default deny
- entry_scene:
  - PREPARE

## Decision Contract
- Constrain solution shape; the primary workflow still owns implementation, correctness, and validation.
- Optimize for the smallest coherent change that satisfies current requirements, not the fewest lines at any cost.
- Preserve canonical-source ownership, fail-closed behavior, security, data integrity, accessibility, operability, and explicit scope.
- Tests, mocks, interfaces, wrappers, and generated artifacts do not substitute for the requested production path.
- Apply this modifier only where a real complexity choice exists.

## Minimum Ladder
Stop at the first rung that fully satisfies the current requirement:

1. Remove or defer speculative behavior.
2. Use standard-library or native-platform behavior.
3. Reuse an installed dependency or local helper.
4. Change the narrowest production owner and observe the affected path.
5. Add a package, file, config surface, or abstraction only when earlier rungs cannot meet a current requirement.

When two rungs are equally small, prefer the one that fits established local patterns and handles required edge cases better.

## Execution
1. Before writing, identify `minimum_behavior`, its production owner, selected rung, and non-negotiable safeguards.
2. Justify each new package, file/layer, interface/adapter/wrapper, config option, or generic facility with a current requirement, existing repeated need, or present boundary. Future reuse is not justification. Keep source selection, policy, and fallback in their real owner.
3. Let the primary workflow implement the smallest production change. Tests may preserve a known contract after it is understood; they do not discover or replace the requested path.
4. Run one decisive check or readback on the affected real path. Lower-scope checks prove only their boundary; conflicting production evidence keeps the condition open.
5. Re-evaluate minimality only when the diff adds a dependency, abstraction, config, file, boilerplate, or disproportionate churn.

## Review Pass
Emit one line only for a meaningful cut:

`<path>:<line>: <tag>: <what to cut>. <replacement>.`

Use `delete`, `stdlib`, `native`, `reuse`, `yagni`, or `shrink`. Optionally end with `net: -<N> lines possible`. If there is no material cut, say `No material minimality cut.` This is not a correctness or release verdict.

## Output And Limits
- Expose only `change_shape`, `reused`, `skipped_complexity`, `revisit_trigger`, `focused_check`, and optional findings. Do not expand a small diff into a long report.
- Use a `minimal:` comment only for an intentional shortcut with a named ceiling and revision trigger.
- Ask one question only when competing interpretations change the deliverable; otherwise state the smallest safe assumption.
- Fix failed validation at its cause. Never add a bypass, silent fallback, weaker check, or mock-only path to keep the diff small.
- Apply minimality inside a user-confirmed broader design. This modifier is not a correctness, security, performance, or accessibility review.

## Validation
- The chosen rung satisfies explicit behavior and safeguards; every added complexity surface has current-use justification.
- Non-trivial behavior has real-path evidence or an explicit unverified gap. Review findings appear only for pressure signals.
- Record skipped complexity and a concrete revisit trigger without duplicating the primary workflow report.
