# Comment And Docstring Synchronization

Use only in `comment_sync` mode. Executable code must remain unchanged.

## Classification

- `sync_to_code`: update stale or misleading text from current signatures, control flow, invariants, and contracts.
- `prune_noise`: remove text that only restates adjacent code or refers to removed behavior without preservable rationale.
- `preserve_high_context`: keep or clarify design rationale, rejected alternatives, invariants, external contracts, past-bug guards, or concurrency/cache/security/performance constraints.
- `resolve_or_keep_marker`: remove a demonstrably resolved TODO/FIXME or keep it with a reason.
- `public_contract_docstring`: treat CLI/OpenAPI/schema/help/generated-doc content as user-facing metadata and report its impact.
- `unclear`: leave unchanged or request the missing evidence.

## Workflow And Gate

1. Inventory the scoped comments/docstrings/markers and read the code they describe; never trust the existing comment as behavior evidence.
2. Apply a small text-only batch. If executable code or structure must change, stop and hand off.
3. Prefer doc-build, docstring linter, doctest, or typecheck when text is tool-consumed; otherwise use focused diff review.
4. Confirm no executable token changed and no high-context rationale was lost.

A comment revealing a real defect routes to `workflow-bug-fix`. Feature/comment work stays with `workflow-implementation`; refactor/comment work stays with `workflow-refactor-safely`. General README/wiki documentation is outside this mode.
