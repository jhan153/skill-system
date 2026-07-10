---
name: report-diff
description: Present verified changed lines in intent-grouped diff blocks with short Korean summaries. Use only when the user explicitly wants changed-lines-only, readable diff, or before/after presentation; this skill does not provide review or root-cause judgment.
---

# Report Diff

## Routing Card
- role: output_modifier
- intent_signature:
  - `diff 요약`, `readable-diff`, `바뀐부분만`, changed-lines-only, before/after comparison
- use_when:
  - the user explicitly wants readable changed-line presentation or grouped before/after comparison.
- do_not_use_when:
  - the user wants root-cause analysis, architecture explanation, ordinary review verdicts, or full raw patches.
- expected_inputs:
  - verified diff, changed file list, or before/after snapshots
- expected_outputs:
  - grouped changed-lines-only diff blocks with concise Korean summaries
- context_targets:
  must_read:
    - verified diff or snapshot baseline
  read_if_needed:
    - changed file list
    - up to two context lines when changed lines are unreadable
  do_not_load_by_default:
    - full repo
    - full memory bank
    - unrelated source files
- risk_profile:
  reads:
    - diff and narrow snapshots only
  writes:
    - none
  tools:
    - safe diff/status commands only
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - FINALIZE

## Operating Rules
- Apply only to explicit diff-presentation intent; this modifier never supplies review, diagnosis, or implementation judgment.
- Use real `git diff`, `diff`, or verified snapshots as the baseline. Never infer removed lines from current content.
- Group by change intent rather than raw file order. Keep one intent per unit and identify each file or symbol.
- Show only `+`/`-` lines by default. Add at most two unchanged context lines only when a signature, terse config, or long one-line change is otherwise unreadable.
- Preserve exact changed lines. Explain field-level meaning below a long line instead of reformatting it as if the reformatted text were the diff.

## Modes
- `VerifiedDiff`: a real diff or verified before/after pair exists; additions and removals may be shown.
- `ContextAssist`: the verified change needs at most two context lines or a symbol label.
- `UnverifiedSnapshot`: no baseline exists; mark the unit `Unverified`, show confirmed current lines only, and never invent removals.

If the user asked for a full raw or machine-readable patch, return that request to the normal diff/tool path instead of applying this readability format.

## Workflow
1. Establish the baseline and select a mode.
2. Exclude unchanged material and identify effective additions, removals, renames/moves, binaries, and generated/vendor churn.
3. Group remaining lines by logical intent; split unrelated edits in one file and combine same-intent edits across files.
4. Order units by behavior/API, schema/config, refactor/rename, tests, then docs/comments unless user priority differs.
5. Render each unit with its label, fenced `diff` block, and one short Korean explanation of effect or purpose.
6. End with at most three bullets only when a cross-unit summary adds value.

## Output Contract
Start with a one-line conclusion, then for each unit emit:

1. numbered intent title;
2. file path or symbol label;
3. one or more fenced `diff` blocks containing verified changed lines;
4. one short Korean summary directly after the unit.

When there is no effective change, say so and emit no fabricated diff block. If a review skill is also active, show its findings/verdict first unless the user explicitly asked for diff only.

## Special Cases
- Rename/move only: label `이름변경만` or `이동만`; do not imply behavior change.
- Whitespace only: label `공백/정렬만 변경`.
- Generated, lock, or vendored file: collapse to a file-level summary unless raw lines were requested.
- Binary file: report the file-level change; never fabricate line content.
- Mixed intent: split into separate units even when edits share a file.
- Missing baseline: use `UnverifiedSnapshot`; do not guess prior text.

## Recovery and Boundaries
- If a changed line is unclear, read only its symbol label or up to two context lines.
- If the user asks for verdict, root cause, or architecture meaning, hand back to the owning review/analysis skill; use this only for the optional diff layer.
- Read only the verified diff and minimal labels. Do not expand to the full repo or unrelated files.
- Write no files and perform no destructive, network, or credential operations.

## Validation
- Confirm every displayed addition/removal exists in the baseline evidence.
- Confirm `Unverified` units contain no invented removed lines.
- Confirm each unit has one intent, a source label, and a concise summary.
- Confirm moves, formatting, generated files, and binaries are not overstated as behavior changes.
- Confirm the response stays changed-lines-first rather than becoming a prose review or full-file dump.

## Known Limits
- Without a verified baseline, only current lines can be shown.
- Generated, lock, vendored, and binary changes may support only file-level summaries.
- This modifier cannot establish correctness or explain root cause.
