---
name: report-diff
description: Presents only actual changed lines in grouped diff blocks with short Korean summaries for each change unit.
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

## Purpose
- Show only real changed lines.
- Group diffs by logical change unit, not by raw file order.
- Add one short summary right below each diff block.

## Related Skills
- `report-qualitative`: 사용자가 형식적 보고를 원할 때 바깥 요약 문장을 정리할 수 있지만, diff block 중심 본문 구조는 이 스킬이 유지합니다.
- `report-critical`: 리뷰 verdict나 finding을 먼저 도출하고, 이 스킬은 실제 변경 줄을 사람이 읽기 좋은 형태로 보여 주는 후행 표현 계층입니다.
- `analysis-codebase`: 통합 분석/설계 리포트가 본체이고, 이 스킬은 사용자가 실제 변경 줄을 보고 싶다고 했을 때만 보조적으로 사용합니다.

## When To Apply
- User explicitly wants readability-first diff presentation, changed-lines-only output, grouped patch blocks, or before/after comparison focused on real edits.
- User says prose review is hard to scan and asks to see actual changed lines grouped by change intent.

## When Not To Apply
- User wants root-cause analysis, debugging, code review findings, or architectural explanation without asking for diff-style output.
- User wants a full raw patch, full-file dump, or machine-parsable diff rather than readability-first presentation.
- No verified baseline is available and the user did not ask for a best-effort snapshot summary.

## Trigger Shortcuts
- `diff 요약`
- `diff-format`
- `readable-diff`
- `바뀐부분만`
- `변경단위`

## Activation Rule
- Activate when the user explicitly wants readable diff presentation or changed-line comparison.
- Treat trigger shortcuts as intent hints, not as the only valid activation phrase.
- If the request is ambiguous between general review and diff presentation, prefer normal review unless the user also asks to see the changes in diff form.

## Cross-Skill Resolution
- 이 스킬은 diff presentation만 소유하며, root-cause analysis, review verdict, architecture explanation을 대체하지 않습니다.
- 리뷰 스킬과 함께 쓰이면 기본적으로 finding/verdict를 먼저 제시하고 그 뒤에 diff units를 보여 줍니다. 사용자가 diff만 원하면 예외로 합니다.
- `report-qualitative`가 함께 활성화되면 conclusion/action framing만 따르고, numbered diff units와 changed-lines-only 계약은 유지합니다.
- baseline evidence가 다른 스킬이나 도구에서 오더라도 검증된 변경 줄만 표시하고, 기준선이 불완전하면 `Unverified`를 유지합니다.

## Output Modes
### A. VerifiedDiff
- Use when real `git diff`, `diff`, or verified before/after snapshots are available.
- Show changed lines only by default.

### B. ContextAssist
- Use when changed lines alone would be hard to understand, such as long one-line JSON, signature changes, or terse config edits.
- Allow up to 2 unchanged context lines or a file/symbol label.

### C. UnverifiedSnapshot
- Use when baseline is missing but the user still wants a best-effort readable snapshot.
- Mark the unit as `Unverified`.
- Show only confirmed current lines and never invent removed lines.

## Output Contract (Mandatory)
1. Start with one-line conclusion.
2. Split into numbered change units (`## 1. ...`, `## 2. ...`).
3. For each unit, include one or more fenced `diff` blocks.
4. Add a file path or symbol label before each diff block when a unit spans multiple files or symbols.
5. Put one short Korean summary line directly below each unit.
6. End with short overall summary of change intent (3 bullets max).

## Formatting Rules
- Use fenced code block language: `diff`.
- Use changed lines only by default.
- Do not include unchanged context lines unless the mode is `ContextAssist` and they are essential for understanding.
- Keep context to at most 2 unchanged lines.
- Keep one logical intent per block.
- If a line was only added, show only `+` lines.
- If a line was only removed, show only `-` lines.
- If old text is unknown, label it as `Unverified` instead of guessing.
- If a long single-line change is hard to parse, keep the verified changed line and explain the important field-level difference in the summary instead of reformatting the line.

## Grouping Rules
- Group by meaning first (e.g., wording hardening, process clarification, schedule framing).
- If a file has multiple unrelated edits, split into separate units.
- If multiple files implement one intent, group together in one unit.

## Ordering Policy
1. Behavior or API changes
2. Data schema or config changes
3. Refactor, move, or rename
4. Tests
5. Docs or comments

## Evidence Rules
- Prefer real command output (`diff`, `git diff`, or verified before/after snapshots).
- If no baseline is available, switch to `UnverifiedSnapshot`, state `Unverified`, and show only confirmed current content.
- Never fabricate removed lines.

## Resource and Risk Boundary
- Reads: verified diff, before/after snapshot, and minimal context needed to label units.
- Writes: none.
- Tool/process calls: safe read-only diff/status commands only.
- Network access: none.
- Credential access: default deny.
- Generated artifacts: none unless the user explicitly requests a diff report file.
- Destructive actions: out of scope.
- Required checkpoints: verify the baseline before showing removed lines.

## Recovery and Context Expansion
- If baseline is missing, switch to `UnverifiedSnapshot` instead of inventing removed lines.
- If changed lines are hard to understand, read at most two context lines or symbol labels.
- If the user actually wants review findings, return to scheduling and use review behavior first.
- If the user asks for root cause, return to scheduling and use `analysis-router`.
- Never recover by loading the full repo, full memory bank, or unrelated source files.

## Special Cases
- Rename or move only: label as `이름변경만` or `이동만`, and do not imply logic change.
- Whitespace only: label as `공백/정렬만 변경`.
- Generated, lock, or vendored files: collapse to a file-level summary unless the user explicitly asks for raw diff details.
- Binary files: do not fabricate line diffs; summarize the file-level change only.
- No effective behavior change: say so explicitly.
- Mixed intent in one file: split the file into separate change units by intent.

## Example Skeleton
````markdown
결론: 요청하신 형식으로 실제 변경 줄만 정리했습니다.

## 1. <변경 단위 제목>
### <file-or-symbol-label>
```diff
- <old line>
+ <new line>
```
요약: <왜 바꿨는지 한 줄>

## 2. <변경 단위 제목>
### <file-or-symbol-label>
```diff
+ <added line>
```
요약: <효과 한 줄>

### 정리
- <핵심 1>
- <핵심 2>
- <핵심 3>
````

## Regression Cases
- Pure add only
- Pure delete only
- Single-line wording change
- Long one-line JSON or config change
- Move only
- Rename only
- Whitespace only
- Multi-file single intent
- One file with mixed intents
- No baseline or `Unverified` input

## Guardrails
- Do not dump full-file patches when user asks readability-first diff.
- Do not replace diff blocks with prose-only explanations.
- Do not overstate refactor, move, or rename as behavior change.
- Keep default response concise.

## Known Limits
- Diff presentation is incomplete without a verified baseline or snapshot.
- Generated, lock, vendored, or binary changes may need file-level summaries only.
- This output modifier is not a review, diagnosis, or implementation workflow.
- Return to scheduling when the user asks for a verdict or root cause.
