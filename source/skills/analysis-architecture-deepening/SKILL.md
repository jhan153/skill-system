---
name: analysis-architecture-deepening
description: Rank evidence-backed improvements across deep modules, seams, adapters, wrappers, policy ownership, and interfaces. Use for scoped “what next?” scans; not selected-boundary design, implementation, or repo-wide reports.
---

# Analysis Architecture Deepening

## Routing Card
- role: primary
- intent_signature: ranked architecture-improvement or deep-module opportunity scan
- use_when: rank several improvements in a workflow, module cluster, or explicit broad scope before selecting one.
- do_not_use_when:
  - one boundary/interface is selected: `analysis-codebase-design`
  - repo-wide integrated report or generated model: `analysis-codebase`
  - recurring bug root cause: `analysis-bug`
  - domain concepts/invariants: `analysis-domain-modeling`
  - measured bottleneck: `analysis-performance`
  - direct production change: route by the selected candidate's change contract—`workflow-refactor-safely` for behavior-preserving live restructuring, `workflow-source-maintenance` for proven-obsolete deletion, or `workflow-implementation` for behavior changes
- expected_inputs: bounded scope, pain/change signals, implementation appetite
- expected_outputs: coverage, evidenced friction, ranked candidates, next candidate, handoff, unverified gaps
- context_targets:
  - must_read: goal, compact scope outline, and production path/owner evidence for shortlisted candidates
  - read_if_needed: discriminating callers, contracts, failures, diffs, metrics, or formal invariants
  - do_not_load_by_default: every file, generated reports, full memory, unrelated docs
- risk_profile: focused read-only discovery; no implementation writes; credentials denied
- entry_scene:
  - PREPARE

## Candidate Standard
A ranked candidate needs observed change/failure pressure plus evidence from its production owner and a representative path.
Request every missing prerequisite; path evidence never substitutes for change/failure evidence.

Rank moves that remove caller knowledge/change surface, return policy, isolate proven volatility, or remove a proven policy-free layer. Size, fan-out, wrapper count, naming, churn, and test inconvenience create hypotheses only. Exception: complete caller inventory plus a formal invariant can rank an exactly structural candidate without change/failure or path evidence; it proves no runtime behavior.

## Two-Pass Workflow

### 1. Discover cheaply
1. Bound the scan by workflow, module cluster, product/service group, or explicit broad scope.
2. Inventory modules, entrypoints, dependencies, usages, tests, churn, and complexity mechanically; keep raw data out of context. Sample one path per material group plus a low-signal control.
3. Seek duplicated caller policy, ownership drift, delegation, boundaries, and observed change/failure pressure.
4. Record inventory findings as hypotheses, never recommendations.

### 2. Confirm narrowly
1. Shortlist 3–5 hypotheses by leverage and evidence availability.
2. Trace callers, production owner, side effects, and boundary contract. Seek a counterexample; deduplicate symptoms sharing one ownership cause.
3. Rank only established improvements. Without actual-path evidence, label `Unverified hypothesis`, make no top recommendation, and request one discriminating observation.

## Evidence And Ownership
- Semantic authority: user decisions, canonical sources, external contracts, formal invariants, or observed behavior. Agent-authored tests preserve established contracts; they neither define nor independently prove them.
- Adapters translate; canonical-source, domain, failure, and fallback policy stay with the production owner. Source selection, migration, media/data transformation, external-boundary, and adapter changes require actual-path readback.
- Record the narrowest decisive scope: inventory for classification/exclusion, structural for exact structure, path for owner/caller/wrapper duties, runtime for execution, and semantic for authoritative readback. Mocks prove only their boundary.
- Preserve wrappers enforcing security, lifecycle, protocol/retry ordering, or anti-corruption rules. Collapse only when representative callers and the real path prove pure delegation.
- A proven removal/deepening opportunity is itself a ranked candidate; identify that option rather than returning no candidate.
- Exclude generated/vendor/migration churn without matching pressure in canonical owners and production callers.

## Coverage, Ranking, And Stop
Track material groups, enumerated/inspected counts, selection reason, evidence scope, confidence, exclusions, and gaps. Coverage means representative evidence, not every file.

Rank ordinally by leverage, knowledge/change removed, observed pressure, counterevidence, validation/reversibility, and cost/blast radius. Avoid fake precision.

Stop when groups are inventoried or excluded, 3–5 candidates have discriminating evidence (or an explicit deficit), a counter-sample preserves the leader, and it has a design question and validation path.

## Output Contract
Return only:
- `scanned_scope` and `coverage_ledger`
- `friction_signals` with evidence scope and references
- `candidates` with stable IDs, `ranking`, and counterevidence
- `recommended_next_candidate` as a ranked candidate ID (never `none` when ranking an opportunity), plus the decisive tradeoff
- `handoff` to `analysis-codebase-design` when one boundary still needs design, `workflow-refactor-safely` for selected behavior-preserving live restructuring, `workflow-source-maintenance` for selected proven-obsolete deletion, or `workflow-implementation` for selected behavior changes
- `unverified_gaps`

Do not implement, generate a repo-wide report, or expand the shortlist into an exhaustive backlog.
