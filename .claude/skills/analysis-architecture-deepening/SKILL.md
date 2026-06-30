---
name: analysis-architecture-deepening
description: Finds targeted architecture deepening opportunities in a codebase. Use when the user asks to improve architecture, find deep-module candidates, reduce shallow modules, identify better seams/adapters, or choose high-leverage structural improvements without generating a full repo-wide report artifact.
---

# Analysis Architecture Deepening

## Routing Card
- role: primary
- intent_signature:
  - architecture deepening
  - improve architecture
  - deep module opportunities
  - shallow module cleanup
  - seam opportunities
  - architecture improvement
  - 아키텍처 개선
  - 딥모듈 후보
- use_when:
  - the user asks for architecture improvement candidates or deep-module opportunities.
  - the task needs a targeted scan across modules but not a heavy repo-wide report artifact.
  - the goal is to choose what structural improvement to implement next.
- do_not_use_when:
  - the user asks for a full codebase analysis report artifact; use `analysis-codebase`.
  - the user already selected one module/interface decision; use `analysis-codebase-design`.
  - the user asks for direct implementation; use `workflow-implementation` after a candidate is selected.
  - the task is first-pass bug diagnosis or repeated failure recovery.
- expected_inputs:
  - repo area, architecture concern, or target workflow
  - optional pain signal such as churn, test pain, duplicated policy, or dependency instability
  - constraints on scope and implementation appetite
- expected_outputs:
  - scanned scope, architecture friction signals, ranked deepening candidates, recommended next candidate, and implementation handoff
- context_targets:
  must_read:
    - current architecture improvement request
    - scoped source tree or module list
    - representative call sites/tests for candidate areas
  read_if_needed:
    - recent diffs or churn evidence
    - architecture docs, ADRs, or module README files
    - validation contract for candidate implementation
  do_not_load_by_default:
    - full repo unless scope is explicitly repo-wide
    - full memory bank
    - generated report artifacts
    - unrelated research or design assets
- risk_profile:
  reads:
    - targeted source, tests, dependency surfaces, docs, and optional git/churn evidence
  writes:
    - none by default; WRITE_CODEBASE only after handing off to an implementation owner
  tools:
    - focused search, file listing, static inspection, and optional targeted tests for evidence
  sensitive_resources:
    - credentials default deny; architecture analysis should not inspect secrets
- entry_scene:
  - PREPARE

## Purpose
- Find high-leverage structural improvements without turning every request into a heavy report.
- Convert vague architecture improvement requests into a short ranked backlog.
- Prefer changes that deepen modules, reduce caller knowledge, improve testability, or isolate unstable dependencies.

## Candidate Signals
Look for current evidence, not speculative futures:
- callers repeatedly know the same policy, ordering, data shape, or error handling.
- a module exposes many small operations but hides little complexity.
- tests require broad setup because there is no stable seam.
- external APIs, storage, network, or runtime services leak into domain logic.
- changes frequently touch many files for one concept.
- adapters or wrappers only delegate and can be collapsed.
- module names do not match the concepts that own the policy.

## Workflow
1. Scope the scan: repo area, workflow, module set, or pain signal.
2. Sample enough files, call sites, tests, and docs to locate real friction.
3. Identify 3-5 candidate deepening moves.
4. For each candidate, state:
   - current friction
   - proposed deeper boundary
   - caller knowledge removed
   - validation or test seam gained
   - implementation size and rollback cost
5. Rank candidates by leverage, confidence, and implementation cost.
6. Recommend one next candidate and hand off to `analysis-codebase-design` or `workflow-implementation`.

## Candidate Types
- deepen module: keep interface small while moving policy and complexity inside.
- extract seam: make hard-to-test behavior observable or substitutable.
- isolate adapter: contain external dependency, protocol, storage, or runtime leakage.
- collapse shallow wrapper: remove layers that repeat implementation without hiding decisions.
- move policy: place rules with the concept that owns them.
- narrow interface: remove caller choices that should be internal decisions.

## Output Contract
Return only the sections needed:
- `scanned_scope`
- `friction_signals`
- `candidates`
- `ranking`
- `recommended_next_candidate`
- `handoff`
- `unverified_gaps`

## Cross-Skill Boundaries
- `analysis-codebase-design` owns the detailed design decision for one selected candidate.
- `workflow-implementation` owns code changes after the user selects a candidate.
- `workflow-minimal-implementation` should challenge candidates that add speculative abstractions.
- `analysis-codebase` owns full repo-wide evidence reports and generated artifacts.
- `analysis-bug` and `workflow-bug-fix` own concrete failure diagnosis and repair.

## Invocation Examples
Positive:
- "이 코드베이스에서 deep module 후보를 찾아줘."
- "아키텍처 개선할 만한 지점 3개만 뽑아줘."
- "테스트가 어려운 구조를 seam 중심으로 개선 후보화해줘."

Negative:
- "이 선택된 모듈 interface를 설계해줘." -> `analysis-codebase-design`
- "전체 코드베이스 분석 리포트 생성해줘." -> `analysis-codebase`
- "이 후보를 바로 구현해줘." -> `workflow-implementation`
