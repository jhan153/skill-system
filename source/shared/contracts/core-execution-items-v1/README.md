# Core Execution Cards

These Markdown files are the canonical, Handoff-ready cards for
`core-execution-items-v1`. A Workflow uses only the card files named in its `## Core Cards`
section. Runtime and plugin generation project those files into the same skill-local
`references/core-execution-items-v1/cards/` path.

Each card owns its compact record shape and current producer/consumer/recorder binding. Do not
copy a card into a skill-owned template or create an alternate wrapper. Change or remove the Core
card and every affected `## Core Cards` binding in the same product-design change.

Each card body is one row for the existing Handoff ledger section named by its metadata:
`Execution Items`, `Deferred Items`, or `Known Bugs`. The producing Workflow returns the compact
row values; the Coordinator writes that row into `handoff.md`. Replace every angle-bracket
placeholder, escape a literal `|` as `\|`, and use `none` for an allowed empty value. Keep full
source analysis, diagrams, logs, transcripts, and diffs in their owning artifacts.
