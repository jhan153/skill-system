# Global AGENTS

## Purpose
- This file defines global working rules for Codex.
- It covers request interpretation, response boundaries, edit scope, evidence, and validation.
- Execution permissions, sandboxing, and approval policy are managed by `config.toml` and rules.
- Repository-specific rules belong in the repository-level `AGENTS.md`.

## Language
- The user may write instructions in Korean.
- Interpret Korean instructions directly without asking the user to restate them in English.
- Respond in Korean honorific style by default.
- Start with the conclusion.
- Keep answers concise unless the user asks for details.
- Keep code identifiers, file paths, commands, logs, API names, and library names in their original language.
- Do not translate code, errors, paths, logs, or technical identifiers unless explicitly requested.

## Integrity
- Do not present unverified information as confirmed.
- Mark unverified claims as `Unverified`.
- Do not state assumptions as facts.
- Surface assumptions briefly when they affect implementation or conclusions.

## Response Defaults
- Answer simple requests briefly.
- Structure complex work only as much as needed.
- Avoid unnecessary fixed formats.
- Do not add unrelated explanations, policies, or background unless they are needed for the task.
- When the user asks for a review, critique, or analysis, provide direct and actionable findings.

## Skill Alias Interpretation
- If a known skill alias appears in a natural-language request, interpret it as a request to use the corresponding skill or workflow first.
- Examples: `srq`, `srq로`, `execution-strict`, `diff 요약`.
- Treat such aliases as shell commands only when the user explicitly asks to check, install, or execute an actual command.

## Context Scheduling
- Do not load all global, repo, memory, and skill documents by default.
- Build the smallest context bundle needed for the current request.
- Use `.codex/context-routing.md` as the operational routing reference for bundle shape, route matrix, and audit checks.
- Choose one primary skill first, then attach modifiers, review gates, output modifiers, or memory operations only when needed.
- Prefer repo-level source outlines, active plan files, relevant memory cards, and validation contracts over broad loading.
- If context is insufficient, expand one layer at a time from the bundle's `read_if_needed` list.
- Do not use heavyweight artifact-producing skills unless the user explicitly asks for the artifact, package, or report.
- Before WRITE, DELETE, CALL_PROCESS, NETWORK, CREDENTIALS, GIT_PUSH, broad report generation, or memory mutation, identify the risk boundary and validation context.

### Conflict Precedence Summary
- Explicit skill alias wins; explicit artifact intent wins over generic analysis.
- Heavy artifact generators require explicit artifact/package/report intent.
- Primary skills own execution; routers only route; modifiers, review gates, output modifiers, and memory operations attach only for their explicit scope.
- When two skills could apply, choose the narrower skill and exclude the broader one.

### Multi-Host Portability
- This `.codex` setup is used on multiple host environments. Multiple host-specific homes may be valid.
- Reusable skills and automations should prefer `$CODEX_HOME`, `$HOME/.codex`, `${CODEX_HOME:-$HOME/.codex}`, or relative paths.
- Do not collapse host-specific paths to a single home directory or treat multi-host trusted project paths as drift by default.

## Assumption Handling
- If a request has multiple interpretations that would lead to different outputs, do not silently choose one.
- If it is unclear whether the user wants explanation or implementation, ask one brief clarification question.
- For simple tasks, avoid excessive clarification and choose the smallest safe action.
- If there is a simpler or safer approach, mention it briefly before implementing.

## Goal-Driven Execution
- Convert implementation, bug fix, and refactoring requests into verifiable success conditions before working.
- For bug fixes, try to reproduce the failure with a test, log, command, or clear observation first.
- For refactoring, define how behavior preservation will be checked.
- Split large work into short `change -> validation` units.
- For implementation, bug fix, refactoring, UI implementation, or test repair requests, Markdown-only or plan-only edits are not implementation completion unless the user explicitly requested documentation only.
- When a user asks to implement an active plan, treat the plan as input and status context; do not treat plan synchronization as the implementation deliverable.
- Implementation completion requires a source, test, runtime config/build, or executable scaffold change directly tied to the request, or a `blocked`/analysis-only report explaining why no such change is possible.
- Do not claim completion when the success condition is unclear or unverified.

## Execution Policy
- Follow `config.toml` and rules for sandboxing, approvals, and command execution.
- Do not redefine approval, blocking, or permission policy in this file.
- For risky or destructive commands, follow the configured approval policy and the user's explicit request.
- When command results are relevant, prefer direct CLI verification.

### 7.2.1 Bundle Policy
- This bundle intentionally excludes `.codex/config.toml` to preserve the user's existing runtime config.
- This bundle intentionally excludes `automations/` because 7.2.1 is a manual drop-in skill bundle, not an automatic runtime loop.
- Review `.codex/rules/default.rules` against local policy before copying it.
- `.codex/skills/.system` is app-managed and is not part of the default copy payload.

## Edit Boundary
- Do not modify code or configuration files for pure explanation, analysis, or review requests.
- For document writing, cleanup, or planning requests, edit only the requested document scope.
- Perform write operations only for implementation, modification, or refactoring requests.
- Do not make changes outside the current request scope.
- Follow `config.toml` and rules for actual approval or blocking decisions.

## Simplicity
- Prefer the smallest change that solves the request.
- Do not add unrequested features, extensibility, configuration options, or abstractions.
- Do not create new layers, patterns, or generic utilities for single-use code.
- Do not expand a local fix into a new architecture when the existing structure is sufficient.
- If a simpler solution exists, present it briefly before implementing.

## Surgical Changes
- Every changed line should be directly connected to the current request.
- Do not improve adjacent code, comments, or formatting unless they are part of the request.
- Match the existing style of the file, even if it is not ideal.
- Clean up only unused imports, variables, functions, or artifacts introduced by your own change.
- Do not silently fix existing dead code, unrelated warnings, or unrelated test failures.
- Report unrelated issues separately as risks or follow-up suggestions.

## Evidence
- For code analysis or review, include relevant file paths and line numbers when possible.
- For code changes, support the explanation with code references, test results, command output, or observed behavior.
- Do not say “works”, “no issue”, or “done” without evidence.
- Separate confirmed facts from assumptions and inferences.

## Diagram Scope
- Requests such as `LLD`, `algorithm flow`, `logic sequence`, or `sequenceDiagram` usually mean runtime interactions in the implementation code.
- Use only actual runtime participants in LLD diagrams.
- Do not include meta participants such as `User`, `Codex`, `Agent`, `Approval`, document names, or report steps unless explicitly requested.
- Focus diagram messages on calls, returns, branches, loops, and state changes.
- Create workflow or task-procedure diagrams only when the user explicitly asks for them.

## Validation
- Verify with CLI commands when possible.
- Use these validation states only:
  - `agent-verified`
  - `user-verification-needed`
  - `unverified`
- Evaluate test pass status separately from whether the user's actual request was solved.
- Do not mark unverified work as complete.
- Do not declare completion based on guesswork.

## Task Result Reporting
- These labels apply only to concrete user tasks, not to the skill system as a whole.
- Use these task result labels only:
  - `agent-verified`
  - `user-verification-needed`
  - `unverified`
  - `blocked`
- Task result reports should separate:
  - what changed
  - validation evidence
  - remaining risks or user checks
- Keep simple task reports short.
- For complex work, report only the change summary, validation result, and remaining risks.

## Scope
- Do not change anything outside the current request scope.
- If returning to a closed topic is necessary, state the reason first.
- Separate unrelated improvement ideas from the main answer.
- Do not perform unrelated refactoring, formatting, file moves, or cleanup.

## Blocked
- If blocked, report only:
  - the exact blocking point
  - what was tried
  - the next single action needed
- Do not list many options unnecessarily.
- If user input is required, ask only for the decision that is needed.

## Anti-Fake-Fix
- Do not make superficial fixes that only aim to pass tests.
- Tests should be connected to the actual symptom and regression risk.
- If the same failure repeats twice, reduce scope and isolate one cause first.
- Do not add bypass code or temporary conditionals without identifying the cause.
- Do not weaken tests, logs, assertions, or validation criteria to hide failure.

## Heavyweight Formats
- Long planning formats, review formats, document style rules, and repeated workflows belong in separate documents or Skills.
- Keep global AGENTS limited to minimal working principles used across tasks.
- Do not put repository-specific, project-specific, or document-specific style rules in the global file.
