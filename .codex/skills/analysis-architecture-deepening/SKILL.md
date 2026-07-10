---
name: analysis-architecture-deepening
description: Find and rank evidence-backed deep-module, seam, adapter, shallow-wrapper, policy-move, and interface-narrowing opportunities. Use for a scoped architecture-improvement scan or “what should we improve next?” decision; do not use for one selected boundary, direct implementation, or a repo-wide report artifact.
---

# Analysis Architecture Deepening

## Routing Card
- role: primary
- intent_signature:
  - ranked architecture improvement or deep-module opportunity scan
- use_when:
  - discover and rank several structural improvements before selecting one.
  - inspect a workflow, module cluster, or explicitly broad codebase scope without generating a heavy report.
- do_not_use_when:
  - one module/interface decision is already selected (`analysis-codebase-design`).
  - the user requests direct implementation, bug RCA, or a repo-wide integrated report (`analysis-codebase`).
- expected_inputs:
  - target scope or workflow, current pain signals, and implementation appetite
- expected_outputs:
  - coverage ledger, evidenced friction, ranked candidates, one recommended next candidate, and handoff
- context_targets:
  must_read:
    - current improvement goal
    - compact source/module outline for the scoped area
    - representative path and test/dependency evidence for shortlisted candidates
  read_if_needed:
    - churn/complexity summaries, recent diffs, ADRs, manifests, or validation contracts that distinguish candidates
  do_not_load_by_default:
    - every source file, full memory, generated reports, or unrelated docs
- risk_profile:
  reads:
    - scoped source, usage/test surfaces, dependency signals, and optional git evidence
  writes:
    - none; hand selected work to an implementation owner
  tools:
    - focused inventory, search, and targeted checks only
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Candidate Standard
Prefer a move only when current evidence shows that it removes caller knowledge, localizes change, isolates volatility, creates a useful test seam, or returns policy to its owner. Treat churn, file size, fan-out, wrapper count, and naming as discovery signals—not proof.

## Two-Pass Workflow

### Pass 1: Broad, Cheap Discovery
1. Bound the scan by workflow, module cluster, product/service group, or explicit repo-wide scope.
2. Enumerate modules, entrypoints, dependencies, usages, tests, churn, and complexity mechanically; keep raw inventories out of context.
3. Sample workflows, hotspots, external boundaries, broad test setup, duplicated caller policy, delegation layers, and ownership mismatches.
4. Start with one path per relevant stratum/group; expand only for material variation or shortlist-changing evidence.
5. Form hypotheses, not recommendations, from inventory signals.

### Pass 2: Narrow, Deep Confirmation
1. Shortlist 3-5 distinct candidates by leverage and evidence quality.
2. Inspect one end-to-end path, caller, test, and boundary/dependency contract for each.
3. Seek one counterexample, then deduplicate symptoms sharing one policy/ownership cause.
4. Rank retained candidates and recommend one next design decision.

## Coverage Ledger
Track group/stratum, enumerated vs inspected counts, selection reason, evidence/confidence, exclusions, and unsampled/blocked gaps.

Coverage means representative architecture evidence, not reading every file. For an explicitly broad scan, cover each material codebase group at inventory level and deepen only groups selected by risk plus one low-signal control sample.

## Candidate Record
For each retained candidate, provide:
- observed friction and concrete evidence refs
- proposed deeper boundary or removal
- caller knowledge/policy removed
- testability/dependency benefit, counterevidence, and confidence
- size, blast radius, rollback, and validation

Consider deepening a module, extracting a seam, isolating an adapter, collapsing a shallow wrapper, moving policy, or narrowing an interface. Do not assume adding a module is the answer.

## Ranking
Rank ordinally by leverage, knowledge/change surface removed, confidence/counterevidence, validation/reversibility, and cost/blast radius. Avoid fake precision; explain close calls with the decisive tradeoff.

## False-Positive Checks
- Exclude generated/vendor/migration churn from ownership conclusions.
- Preserve thin wrappers that enforce security, lifecycle, protocol, or anti-corruption policy.
- Do not infer poor boundaries from caller count, environmental test pain, or similar names alone.

## Stop Conditions
Stop when:
- every material scope group has inventory coverage or an explicit exclusion.
- 3-5 candidates have path-level evidence, or fewer candidates survive with the deficit explained.
- one deliberate counter-sample does not change the top recommendation.
- the top candidate has a clear design question and validation path.

If unstable, expand only the weakest stratum. At a budget, permission, or runtime boundary, return the gap as `Unverified` instead of widening indefinitely.

## Output Contract
Return only:
- `scanned_scope` and `coverage_ledger`
- `friction_signals` with evidence refs
- `candidates` and `ranking`
- `recommended_next_candidate` with decisive tradeoff
- `handoff` to `analysis-codebase-design` or an implementation owner
- `unverified_gaps` when material

## Boundaries
- `analysis-codebase-design` decides the selected candidate's exact interface/boundary.
- `analysis-codebase` owns explicit repo-wide report artifacts and generated architecture models.
- `analysis-domain-modeling` owns domain concepts and invariants.
- `workflow-implementation` owns writes after selection.
- Do not turn this ranked backlog into an exhaustive architecture report.
