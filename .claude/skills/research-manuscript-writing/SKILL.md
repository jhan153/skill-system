---
name: research-manuscript-writing
description: Writes or revises scientific manuscript sections from verified evidence and research artifacts without inventing citations, results, tables, or figures.
---

# Research Manuscript Writing

## Routing Card
- role: primary
- intent_signature:
  - manuscript
  - paper draft
  - IMRAD
  - related work section
  - method section
  - LaTeX
  - 논문 초안
  - 논문 작성
- use_when:
  - the user asks to write or revise scientific manuscript sections.
  - evidence ledger, literature review, blueprint, analysis report, or user manuscript should be converted into prose.
- do_not_use_when:
  - paper evidence search; use search-paper-evidence.
  - peer-review critique; use research-peer-review.
  - present planned experiments as completed results.
- expected_inputs:
  - evidence ledger
  - literature review
  - research plan
  - experiment blueprint
  - analysis report
  - user manuscript
- expected_outputs:
  - papers/draft/manuscript.md or main.tex when requested
  - section draft
  - citation gaps
  - unverified claims
- context_targets:
  must_read:
    - target section or manuscript goal
    - available evidence/artifacts
  read_if_needed:
    - refs.bib
    - analysis report
    - literature review
    - journal style notes
  do_not_load_by_default:
    - experiment scaffold
    - statistical analysis if data interpretation is not done
- risk_profile:
  reads:
    - evidence ledger
    - literature review
    - research plan
    - blueprint
    - analysis report
    - manuscript draft
  writes:
    - manuscript or draft artifacts only when requested
  tools:
    - none by default
  network:
    - none by default
  credentials:
    - none
  generated_artifacts:
    - `papers/draft/*` only if requested
  destructive_actions:
    - none
  forbidden_by_default:
    - fabricated citations
    - fabricated results
- entry_scene:
  - PREPARE

## Purpose
Writes or revises scientific manuscript sections from verified evidence and research artifacts without inventing citations, results, tables, or figures.

## When To Apply
- the user asks to write or revise scientific manuscript sections.
- evidence ledger, literature review, blueprint, analysis report, or user manuscript should be converted into prose.

## When Not To Apply
- paper evidence search; use search-paper-evidence.
- peer-review critique; use research-peer-review.
- present planned experiments as completed results.

## Workflow
1. PREPARE - identify target section and available evidence.
2. GROUND - map claims to citations or mark placeholders.
3. DRAFT - write coherent paragraphs unless outline is requested.
4. SEPARATE - keep methods, results, and interpretation distinct.
5. VERIFY - avoid invented citations/results/tables/figures.
6. FINALIZE - provide draft text or artifact path when requested.

## Resource and Risk Boundary
Summary:
- Reads evidence ledgers, literature reviews, research plans, blueprints, analysis reports, and manuscript drafts.
- Writes manuscript or draft artifacts only when explicitly requested.
- Uses no tools or network by default.
- Does not invent citations, results, tables, figures, venues, or completed experiments.
- Required checkpoints: citation status, evidence grounding, results availability, and artifact intent.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Draft scope
2. Evidence used
3. Manuscript prose
4. Citation placeholders/gaps
5. Unverified claims
6. Next revision targets

## Citation Status Contract
Use `citation_status` values: `verified`, `user_provided`, `placeholder`, `missing`, `unverified`. Mark draft claims with `[verified citation: ...]`, `[user-provided citation: ...]`, `[citation needed]`, or `[unverified claim]`. Final prose must not present unverified citation claims as established fact.

## Validation
- Confirm `.codex/skills/.system` was not touched.
- Confirm user intent matches this skill, not ordinary development.
- Confirm required evidence or artifact inputs are present or explicitly marked missing.
- Confirm no secrets, credentials, hardcoded single-host paths, fabricated citations, or fabricated results are introduced.
- Confirm artifact writes happen only when explicitly requested.

## Anti-Patterns
- Installing or invoking monolithic `codex-research-lifecycle`.
- Treating search keywords as conclusions.
- Collapsing evidence search, ideation, blueprint, scaffold, analysis, writing, and review into one step.
- Creating custom transcribe/speech skills from research source material.
- Weakening development/implementation routing because a request mentions model, metric, loss, experiment, or training.

## Known Limits
- Writing quality depends on available evidence and results.
- It cannot invent completed experiments or verified citations.
- Venue-specific formatting may need separate style guidance.
