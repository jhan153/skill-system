---
name: research-literature-ideation
description: Generates candidate research hypotheses from evidence and literature synthesis, labels claim sources, and selects exactly one active hypothesis for validation.
---

# Research Literature Ideation

## Routing Card
- role: primary
- intent_signature:
  - research gap
  - hypothesis from literature
  - gap analysis
  - candidate hypotheses
  - active hypothesis
  - 연구 아이디어 후보
  - gap에서 가설
- use_when:
  - the user asks to derive gaps, candidate hypotheses, or an active hypothesis from literature evidence.
  - an evidence ledger or literature review exists and needs ideation.
- do_not_use_when:
  - paper search; use search-paper-evidence.
  - literature review prose; use research-literature-synthesis.
  - claim-first planning from a raw user premise when no literature evidence is needed; use research-hypothesis-planning.
- expected_inputs:
  - evidence_ledger.json
  - literature_review.md
  - domain references
- expected_outputs:
  - gap map
  - candidate hypotheses
  - claim labels
  - selected active hypothesis
  - backlog
  - ideation_output.json when requested
- context_targets:
  must_read:
    - evidence ledger or literature review
    - research scope
  read_if_needed:
    - speech-enhancement-research reference for speech/audio research
    - provided papers
  do_not_load_by_default:
    - experiment scaffold
    - manuscript writing
    - statistical analysis
- risk_profile:
  reads:
    - evidence ledger
    - literature review
    - domain references
  writes:
    - `papers/ideation_output.json` only when requested
  tools:
    - none by default
  network:
    - none by default
  credentials:
    - none
  generated_artifacts:
    - ideation artifacts only if requested
  destructive_actions:
    - none
- entry_scene:
  - PREPARE

## Purpose
Generates candidate research hypotheses from evidence and literature synthesis, labels claim sources, and selects exactly one active hypothesis for validation.

## When To Apply
- the user asks to derive gaps, candidate hypotheses, or an active hypothesis from literature evidence.
- an evidence ledger or literature review exists and needs ideation.

## When Not To Apply
- paper search; use search-paper-evidence.
- literature review prose; use research-literature-synthesis.
- claim-first planning from a raw user premise when no literature evidence is needed; use research-hypothesis-planning.

## Workflow
1. PREPARE - verify evidence or synthesis exists; otherwise route to evidence search.
2. GAP MAP - identify open problems, contradictions, metric mismatches, dataset gaps, and failure modes.
3. CANDIDATES - generate 2-4 temporary hypotheses with [paper], [math], [experiment], [dataset], or [assumption] labels.
4. SELECT - choose exactly one active hypothesis for validation.
5. BACKLOG - move non-active hypotheses to backlog.
6. FINALIZE - output ideation summary or `papers/ideation_output.json` only when requested.

## Resource and Risk Boundary
Summary:
- Reads evidence ledgers, literature reviews, and targeted domain references.
- Writes `papers/ideation_output.json` only when explicitly requested.
- Uses no tools or network by default.
- Uses no credentials and performs no destructive actions.
- Required checkpoints: evidence basis, one active hypothesis, claim labels, and backlog separation.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Evidence basis
2. Gap map
3. Candidate hypotheses
4. Claim labels
5. Selected active hypothesis
6. Backlog
7. Assumptions and missing evidence

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
- Candidate hypotheses are scaffolds, not validated conclusions.
- Evidence gaps can make all hypotheses tentative.
- Intuition-only claims must remain `[assumption]`.
