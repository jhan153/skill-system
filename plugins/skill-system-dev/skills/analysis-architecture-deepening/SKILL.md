---
name: analysis-architecture-deepening
description: Rank evidence-backed improvements across deep modules, seams, adapters, wrappers, policy ownership, and interfaces. Use for scoped “what next?” scans; not selected-boundary design, normative multi-view target architecture, implementation, or repo-wide reports.
---

# Analysis Architecture Deepening

## Routing Card
- role: primary
- family: analysis
- intent_signature: ranked architecture-improvement or deep-module opportunity scan
- use_when: rank several improvements in a workflow, module cluster, or explicit broad scope before selecting one.
- do_not_use_when:
  - one boundary/interface is selected: `analysis-boundary-design`
  - several interacting boundaries need a normative target/transition design:
    `workflow-architecture-design`
  - architecture map, HLD/LLD modeling, or Mermaid flow/structure/state diagrams: `analysis-codebase-map`
  - recurring bug root cause: `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane; otherwise current task owner for diagnosis-only, or `workflow-bug-fix` only for a semantically admitted bounded repair under an already-implemented accepted contract
  - domain concepts/invariants: `analysis-domain-modeling`
  - measured bottleneck: `analysis-performance`
  - direct production change: route by the selected candidate's change contract—`workflow-refactor-safely` for behavior-preserving live restructuring, `workflow-source-maintenance` for proven-obsolete deletion, or `workflow-implementation` for behavior changes
- expected_inputs: user-named scope or bounded recent-change history, pain/change signals, implementation appetite
- expected_outputs: sampling basis, coverage, evidenced friction, ranked candidates, an evidenced next candidate, scoped no-improvement conclusion, or exact evidence discriminator, handoff, and unverified gaps
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
1. Resolve the inspection boundary before collecting candidates. A user-named workflow, module, subsystem, or pain point is authoritative and cannot be displaced by repository history.
2. With no named boundary, use recent change only to allocate inspection effort. Start with roughly 20 material non-merge commits, count recurrence at canonical owners and their production callers, and remove generated/vendor output, formatting-only edits, lockfiles, mechanical migrations, and mass renames from that sample.
3. Promote a frequently touched path to deeper inspection, never directly to the candidate ranking. If the bounded history has no useful concentration, fall back to representative material groups. A less-changed path still enters the sample when the current failure, stated pressure, or user scope points to it.
4. Inventory modules, entrypoints, dependencies, usages, tests, churn, and complexity mechanically; keep raw data out of context. Sample one path per material group plus a low-signal control.
5. Seek duplicated caller policy, ownership drift, delegation, boundaries, and observed change/failure pressure.
6. Record inventory findings as hypotheses, never recommendations.

### 2. Confirm narrowly
1. Shortlist up to five hypotheses by leverage and evidence availability. Keep only hypotheses
   actually supported by the scoped discovery, including a shortlist of one or two.
2. Trace callers, production owner, side effects, and boundary contract. Seek a counterexample; deduplicate symptoms sharing one ownership cause.
3. Rank only established improvements. Without actual-path evidence, label `Unverified hypothesis`, make no top recommendation, and request one discriminating observation.

## Evidence
- Adapters translate; canonical-source, domain, failure, and fallback policy stay with the production owner. Source selection, migration, media/data transformation, external-boundary, and adapter changes require actual-path readback.
- Record the narrowest decisive scope: inventory for classification/exclusion, structural for exact structure, path for owner/caller/wrapper duties, runtime for execution, and semantic for authoritative readback.
- Preserve wrappers enforcing security, lifecycle, protocol/retry ordering, or anti-corruption rules. Collapse only when representative callers and the real path prove pure delegation.
- A proven removal/deepening opportunity is itself a ranked candidate; identify that option rather than returning no candidate.

## Coverage, Ranking, And Stop
Track the scope decision, recent-history window when used, change-weighted priority paths, material groups, enumerated/inspected counts, selection reason, evidence scope, confidence, exclusions, and gaps. Coverage means representative evidence, not every file.

Rank ordinally by leverage, knowledge/change removed, observed pressure, counterevidence, validation/reversibility, and cost/blast radius. Avoid fake precision.

Stop when groups are inventoried or excluded and either:
- one or more established candidates have discriminating evidence, a counter-sample preserves the leader,
  and the leader has a design question and validation path; or
- the available evidence sufficiently covers the requested scope but establishes no improvement;
  return `none` with that bounded coverage and exclusions, without inventing an evidence deficit; or
- a material evidence deficit remains explicit and one smallest discriminator is named, with no leader or
  recommendation claimed.

A fully covered small scope may therefore return one or two established candidates. Do not widen
the inspection scope, invent candidates, or withhold an evidenced leader merely to fill a quota;
zero established candidates yields no recommendation, with a discriminator only when an actual
material evidence gap remains.

## Output Contract
Return only:
- `scanned_scope` and `coverage_ledger`
- `sampling_basis` as `user_named | recent_change_weighted | representative_widened`, including excluded mechanical churn when history was used
- `friction_signals` with evidence scope and references
- `candidates` with stable IDs, `ranking`, and counterevidence
- `recommended_next_candidate` as an established ranked candidate ID plus the decisive tradeoff;
  when no candidate is established, return `none` with the bounded no-improvement conclusion or
  the exact discriminator for a remaining material evidence gap
- `handoff` to `analysis-boundary-design` when one boundary still needs design,
  `workflow-architecture-design` when an established candidate requires a coherent normative design
  across several architecture views, `workflow-refactor-safely` for selected behavior-preserving
  live restructuring, `workflow-source-maintenance` for selected proven-obsolete deletion, or
  `workflow-implementation` for selected behavior changes whose architecture is already accepted
- `unverified_gaps`
