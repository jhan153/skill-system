---
name: workflow-minimal-implementation
description: Conditional minimal-implementation policy for coding and refactoring work. Use when a task needs YAGNI discipline, standard-library/native-platform preference, dependency restraint, smallest correct diffs, or a post-change over-engineering check for added abstractions, files, packages, or boilerplate.
---

# Workflow Minimal Implementation

## Routing Card
- role: execution_modifier
- intent_signature:
  - `workflow-minimal-implementation`, `minimal-implementation`, `minimum implementation`, `minimal solution`, `simplest correct solution`, `YAGNI`, `do less`, `avoid over-engineering`, `최소 구현`, `최소구현`, `과잉 구현`, `과잉설계`
- use_when:
  - implementation or refactoring work has a credible risk of unnecessary abstractions, new dependencies, boilerplate, generic infrastructure, or broad file churn.
  - the user explicitly asks for the smallest correct implementation, YAGNI, dependency restraint, or over-engineering resistance.
  - a planned or actual diff adds a package, framework, adapter layer, factory, interface, config surface, or multiple files for a narrow behavior change.
- do_not_use_when:
  - the request is pure Q&A, research, planning, documentation, code explanation, or review with no implementation pressure.
  - the user explicitly asks for a complete architecture, extensible framework, teaching walkthrough, or exhaustive implementation and accepts the added scope.
  - minimality would remove input validation, security, data-loss prevention, accessibility, compliance behavior, migration safety, or an explicit user requirement.
- expected_inputs:
  - selected primary implementation workflow
  - requested behavior and explicit non-negotiables
  - relevant existing files, dependencies, and local patterns
  - current or planned diff when doing the review pass
- expected_outputs:
  - selected minimum viable change shape
  - skipped complexity and the trigger that would justify adding it later
  - one focused validation check for non-trivial logic
  - optional over-engineering findings for the final diff
- context_targets:
  must_read:
    - current implementation or refactor request
    - relevant source files and existing local patterns
    - package/dependency manifest only when dependency choice is in scope
  read_if_needed:
    - validation contract or existing tests for the touched behavior
    - current diff after implementation when review pressure signals are present
    - adjacent helper APIs only when choosing between reuse and new code
  do_not_load_by_default:
    - full repo
    - broad architecture docs
    - unrelated skill library
    - old plans or memory unless explicitly in scope
- risk_profile:
  reads:
    - targeted source, manifests, tests, and diff evidence only
  writes:
    - WRITE_CODEBASE only through the selected primary implementation workflow
  tools:
    - focused search, diff, and validation commands tied to the touched behavior
  sensitive_resources:
    - credentials default deny; do not inspect secrets to justify minimality
- entry_scene:
  - PREPARE

## Purpose
Apply just enough YAGNI pressure to implementation work. This skill is a soft execution policy, not a hard gate: it changes how Codex chooses a solution, but it does not block tool calls, dependency installs, or large diffs by itself.

Keep it conditional. Do not turn every task into a minimalism exercise.

## When To Apply
- Use before writing code when the request can be solved by reusing existing code, stdlib, platform behavior, or a narrow local change.
- Use during implementation when the proposed solution starts adding new layers, packages, config, generic wrappers, or speculative extension points.
- Use after implementation when a diff grew beyond the requested behavior and needs a deletion-focused check.

## When Not To Apply
- Do not use for pure analysis, documentation, planning, or research output.
- Do not use to override explicit user scope after they confirm the larger design.
- Do not simplify away trust-boundary validation, security controls, data-loss prevention, accessibility basics, migration safeguards, observability needed to operate the change, or hardware calibration knobs.

## Workflow
1. Restate the minimum requested behavior in one sentence.
2. Walk the ladder and stop at the first rung that satisfies the request:
   - skip the feature if it is speculative and not actually required.
   - use standard library behavior when available.
   - use native platform behavior when available.
   - reuse an already-installed dependency or existing local helper.
   - implement the narrowest local change.
3. Reject speculative structure unless the current task proves it is needed:
   - no interface with one implementation.
   - no factory for one product.
   - no config for a value nobody changes.
   - no wrapper that only delegates.
   - no new package for behavior already covered by stdlib, platform, or installed code.
4. Implement through the selected primary workflow with the smallest coherent diff.
5. For non-trivial logic, leave one focused runnable check. Use the repo's existing test style when obvious; otherwise use the smallest command or assert-style check that fails if the logic breaks.
6. If the diff added dependencies, abstractions, files, or broad boilerplate, run the review pass below before finalizing.

## Review Pass
Use this only after there is a planned or actual diff.

Report one line per finding:

`<path>:<line>: <tag>: <what to cut>. <replacement>.`

Tags:
- `delete`: dead code, unused flexibility, speculative feature, or future-only branch.
- `stdlib`: custom code that the standard library already provides.
- `native`: dependency or custom code that the platform already provides.
- `reuse`: new code that should use an existing local helper or installed dependency.
- `yagni`: abstraction, config, interface, factory, adapter, or layer with no current second use.
- `shrink`: same behavior in fewer lines with no loss of safety or clarity.

End the review pass with `net: -<N> lines possible` when a useful estimate is available. If there is nothing meaningful to cut, say `Lean enough. Ship.`

## Output Contract
- Keep implementation notes short: what was changed, what was skipped, and when to add the skipped complexity.
- Mark any intentional shortcut with a `minimal:` comment only when it has a known ceiling. The comment must name the ceiling and the trigger to revisit it.
- Do not present minimality as verified correctness. Verification still comes from tests, runtime checks, or explicit evidence.

## Resource and Risk Boundary
- Reads stay local to the requested behavior, dependency surface, and diff.
- Writes stay inside the selected primary workflow's code/test/config scope.
- Tool calls are limited to search, diff, and focused validation.
- Hard enforcement belongs outside this skill: CI checks, dependency policies, pre-commit rules, AST linters, file-count budgets, and review gates.

## Recovery and Context Expansion
- If the minimum behavior is unclear, ask one focused clarification or choose the smallest safe interpretation and state it.
- If two options are equally small, choose the one that handles edge cases better.
- If a minimal version fails validation, fix the cause; do not add bypasses or weaken tests to preserve a smaller diff.
- If the user reaffirms the broader architecture, stop challenging the scope and implement it cleanly.

## Known Limits
- This skill cannot technically prevent package installation, broad edits, tool calls, or commits.
- It can under-build if the user requirement hides scale, compliance, or operational constraints.
- It should not be the only review for correctness, security, performance, or accessibility.

## Validation
- Confirm the frontmatter has only `name` and `description`.
- Confirm the Routing Card keeps the canonical field order.
- Confirm non-trivial logic has one focused runnable check or an explicit `Unverified` gap.
- Confirm any added dependency, abstraction, config, or extra file is justified by current requirements.
- Confirm no safety, validation, data-loss, accessibility, or explicit user requirement was removed for minimality.

## Anti-Patterns
- Using this skill as an always-on personality mode.
- Rejecting a confirmed user requirement because it is not minimal.
- Removing safety checks to reduce line count.
- Adding a custom mini-framework while claiming it is future-proof.
- Writing a long justification for a tiny diff when one skipped-complexity line is enough.
