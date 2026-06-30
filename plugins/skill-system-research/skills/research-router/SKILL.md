---
name: research-router
description: Routes evidence-grounded scientific research requests to the correct narrow Research Cluster skill without searching, writing files, generating code, or producing research artifacts.
---

# Research Router

## Routing Card
- role: router
- intent_signature:
  - research workflow routing
  - scientific workflow
  - research cluster
  - literature to experiment routing
  - 논문 연구 라우팅
  - 연구 단계 선택
- use_when:
  - the user asks for a scientific workflow but the exact research stage must be selected.
  - a request spans paper search, literature synthesis, ideation, planning, blueprint, scaffold, statistics, writing, or peer review.
- do_not_use_when:
  - ordinary development, bug fixing, refactoring, or implementation tasks.
  - a single narrow research skill is explicitly named.
  - requests to write files, search the web, scaffold code, analyze results, or write manuscripts directly.
- expected_inputs:
  - research request
  - stage hints
  - artifact intent
  - provided evidence or artifact paths
- expected_outputs:
  - selected research cluster skill
  - next skill sequence
  - minimal context bundle
  - excluded skills
- context_targets:
  must_read:
    - current user request
    - available artifact hints
  read_if_needed:
    - .codex/research-routing.md
    - provided artifact names only
  do_not_load_by_default:
    - full repo
    - full memory bank
    - .codex/skills/.system
    - paper search results unless routed to evidence search
- risk_profile:
  reads:
    - current request
    - available artifact hints
    - `.codex/research-routing.md` pointer when needed
  writes:
    - none
  tools:
    - none
  network:
    - none
  credentials:
    - none
  generated_artifacts:
    - none
  destructive_actions:
    - none
- entry_scene:
  - PREPARE

## Purpose
Routes evidence-grounded scientific research requests to the correct narrow Research Cluster skill without searching, writing files, generating code, or producing research artifacts.

## When To Apply
- the user asks for a scientific workflow but the exact research stage must be selected.
- a request spans paper search, literature synthesis, ideation, planning, blueprint, scaffold, statistics, writing, or peer review.

## When Not To Apply
- ordinary development, bug fixing, refactoring, or implementation tasks.
- a single narrow research skill is explicitly named.
- requests to write files, search the web, scaffold code, analyze results, or write manuscripts directly.

## Workflow
1. PREPARE - identify whether this is research or development mode.
2. CLASSIFY - choose exactly one owning research stage or a short sequence when the user requests a multi-stage workflow.
3. EXCLUDE - mark unrelated heavy generators and implementation skills as excluded.
4. RETURN - route to the selected skill; do not perform the work locally.

## Resource and Risk Boundary
Summary:
- Reads only the current request, artifact hints, and research-routing pointers.
- Writes nothing.
- Uses no tools and no network.
- Does not generate artifacts, mutate memory, perform research claims, or touch `.system`.
- Required checkpoints: research vs development mode, selected narrow skill, excluded heavy skills.

## Recovery and Context Expansion
- If the request belongs to development/implementation, return to scheduling instead of forcing research routing.
- If required inputs are missing, ask one focused question or produce a non-writing plan with missing evidence marked.
- Expand from must-read to read-if-needed one layer at a time.
- Do not load the full repo, full memory bank, `.system`, or unrelated research cluster skills by default.
- Do not invent citations, datasets, metrics, results, or file artifacts to fill gaps.

## Output Contract
1. Mode decision
2. Selected primary research skill
3. Optional next skills
4. Must-read context
5. Default exclusions
6. Risk gates to check before action

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
- Router decisions depend on explicit user intent and artifact names.
- It does not verify evidence or perform research work.
- Ambiguous multi-stage requests may need one clarification before routing.
