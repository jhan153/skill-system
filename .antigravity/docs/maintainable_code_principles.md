# Maintainable Code Principles

Maintainable code shall enable a maintainer to recover intent quickly, constrain a change to its
owning surface, predict material impact, and verify the result. All four criteria are required:

`maintainability = intent recovery × change locality × impact predictability × verifiability`

## Core Principles

| Principle | Requirement | Warning sign |
|---|---|---|
| 1. Keep intent close | A reader must be able to recover what the code does and why from nearby code. Names and execution order should reveal purpose before implementation detail. | Understanding requires tracing multiple files, documents, or Git history. |
| 2. Keep each reason to change in one place | Each policy, rule, or side effect must have a clear owner. | One requirement forces edits across unrelated files. |
| 3. Maintain one abstraction level within a unit | Function length shall not determine responsibility. Each unit shall preserve one conceptual responsibility and narrative level. | Calculation, file I/O, UI formatting, and logging cross within one flow. |
| 4. Control invariants and side effects at boundaries | Validate inputs at the entry, keep external I/O and transactions at boundaries, and keep domain rules inside. Make invalid states unrepresentable when possible. | Null checks, retries, and exception handling are scattered across functions. |
| 5. Solve the same problem the same way | Naming, error handling, return shapes, and layer transitions must be repeatable. Consistency should make the next code shape predictable. | The same meaning is represented by different names and patterns in different places. |
| 6. Make the result of a change provable | Tests, deterministic validation, observable logs, or readback must show whether the change is safe. Readable code is not maintainable when its safety cannot be checked. | The code can be modified, but there is no way to tell what broke. |

## Single-Responsibility Interpretation

Function size shall not define single responsibility.

- Each function shall have one purpose.
- Steps that explain the purpose shall remain at the same abstraction level.
- Detailed calculation, external I/O, and presentation formatting shall not mix in one flow.
- Decomposition shall not force the reader to navigate across several files to recover one purpose.

Continuity of intent shall take precedence over function count.

## Five Review Questions

1. Can the purpose of this code be explained within one screen?
2. When one rule changes, are the required edit locations clear?
3. Are the normal flow and the failure and side-effect boundaries visible?
4. Are invalid states rejected before they enter the internal flow?
5. Can the changed behavior be independently verified?

## Agent-Based Projects

Agent-oriented code shall expose intent, ownership, boundaries, and the verification method within
bounded context. Humans and agents shall recover the same intent. Code that obscures these elements
fails this maintainability contract even when its current behavior works.
