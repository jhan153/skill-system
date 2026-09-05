# Verified Compare Mode

Use only for an explicit changed-lines, readable-diff, or before/after request. This mode presents change facts; it does not diagnose, review, or establish correctness.

## Baseline

- `VerifiedDiff`: use real `git diff`, `diff`, or an authoritative before/after pair.
- `ContextAssist`: add only a symbol or at most two unchanged lines around a verified unit.
- `UnverifiedSnapshot`: when no baseline exists, label current lines `Unverified`, show no removals, and mark effect `not_established`.

Never infer prior or removed text from current content. If verified changes are required and no baseline exists, request it.

## Evidence Layers

Keep `change_fact`, `intent`, and `observed_effect` separate. Exact additions/removals establish textual change only. State an observed effect only from an authoritative oracle plus scope-matched actual-path/readback evidence; never turn it into a correctness or release verdict. Label rename/move-only and whitespace-only changes accurately, and collapse generated, vendored, binary, and lock-file changes to file-level facts unless raw lines were requested.

## Workflow And Output

1. Select the baseline and exclude unchanged material.
2. Group verified changes by intent, splitting mixed intent and combining same-intent edits across files.
3. Order behavior/API, schema/config, refactor/rename, tests, then docs/comments unless the user asks otherwise.
4. Preserve exact `+`/`-` lines. Add minimal context only when necessary and never rewrite long changed lines.
5. Produce the comparison in content-primary Markdown under the active skill's delivery contract. Each unit contains an intent/source label, path/symbol, exact before/after block, concise summary, and any evidence limitation. Only when that contract selects HTML (`html`/`both` or required inspectable spatial evidence), project the same content through the local Report Canvas contract and renderer; changed-line comparisons use `compare` mode.

When there is no effective change against a verified baseline, return an explicit no-change summary in the selected delivery format. Selected HTML uses `status: info` and the same empty comparison; it does not manufacture changed units. An absent baseline remains `UnverifiedSnapshot`, not a no-change result. Honor explicit chat-only or raw-diff delivery without creating HTML.
