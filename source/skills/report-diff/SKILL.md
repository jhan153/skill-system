---
name: report-diff
description: Present verified changed lines in intent-grouped diff blocks with concise Korean summaries. Use only for explicit changed-lines, readable-diff, or before/after requests; do not use for review or diagnosis.
---

# Report Diff

## Routing Card
- role: output_modifier
- intent_signature: `diff 요약`, `readable-diff`, `바뀐부분만`, changed-lines-only, before/after
- use_when: the user explicitly requests readable changed lines or grouped before/after presentation
- do_not_use_when:
  - Root cause belongs to `analysis-bug`; blocker-first QA/release verdicts belong to `report-critical`.
  - Implementation belongs to `workflow-implementation`; changed-file/validation-command inventories belong to `coordination-handoff`.
  - Full raw or machine-readable patches stay on the normal diff/tool path.
- expected_inputs: verified diff or verified snapshots; current snapshot only for explicitly unverified presentation
- expected_outputs: intent-grouped changed-line blocks, source labels, concise Korean summaries, and calibrated evidence notes
- context_targets:
  must_read:
    - supplied diff/baseline and requested presentation scope
  read_if_needed:
    - changed-file list, symbol label, or at most two context lines
  do_not_load_by_default:
    - full repository, memory, unrelated source, generated mirrors, or unrelated logs
- risk_profile:
  reads: verified diff and narrow snapshots
  writes: none
  tools: safe diff/status commands only
  sensitive_resources: deny credentials
- entry_scene: FINALIZE

## Baseline And Modes

Use real `git diff`, `diff`, or an authoritative before/after pair. Never infer prior or removed text from current content.

- `VerifiedDiff`: additions and removals are verified.
- `ContextAssist`: a verified unit needs a symbol or at most two unchanged lines.
- `UnverifiedSnapshot`: no baseline exists; label it `Unverified`, show current lines separately—not as verified additions—show no removals, and mark any effect `not_established`.

If verified changes are required from an unverified snapshot, request the missing baseline. A readable-diff request is itself structural: exact verified lines can satisfy it without runtime evidence.

## Evidence And Meaning

Keep three layers distinct in every summary:

1. `change_fact`: exact added, removed, renamed, moved, generated, binary, or formatting evidence;
2. `intent`: user/source-stated intent, or explicitly labeled inference;
3. `observed_effect`: only a condition directly established by an authoritative oracle plus scope-matched actual-path/readback evidence.

A diff alone proves textual change, not correctness, fix completion, release readiness, or user success. When an authoritative oracle and actual-path/readback directly match, the modifier may state that exact `observed_effect` with semantic scope. This is an evidence-linked fact, not a correctness/release verdict or claim on unobserved scope.

Agent-authored tests may preserve an established oracle but cannot invent independent semantic authority. State that mocks prove only their boundary and name the missing real path. A generated-target diff does not prove canonical behavior; identify canonical-source drift and request canonical inspection/regeneration. Preserve conflicting `fail`, `needs_review`, unverified, or blocked status despite narrower passes.

Label rename/move-only and whitespace-only changes without implying behavior change. Collapse generated, lock, vendored, and binary changes to file-level facts unless raw lines were requested.

## Workflow

1. Select the baseline/mode and exclude unchanged material.
2. Identify effective changes and evidence scope; split mixed intent and combine same-intent edits across files.
3. Order behavior/API, schema/config, refactor/rename, tests, then docs/comments unless user priority differs.
4. Preserve exact `+`/`-` lines. Add minimal context only when necessary; explain long-line fields below the block instead of rewriting the diff.
5. Render each unit with intent title, path/symbol, fenced `diff` block, one Korean summary, and any required evidence limitation.

## Output And Validation

Start with one conclusion. Emit only needed units and at most three cross-unit bullets. If review is separately active, put its verdict first unless the user requested diff only.

Before returning, confirm that every displayed addition/removal exists in the baseline, unverified snapshots invent none, each unit has one intent/source label, special cases are not overstated, and the response remains changed-lines-first. When there is no effective change, say so and emit no fabricated block.
