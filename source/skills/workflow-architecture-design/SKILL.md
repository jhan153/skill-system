---
name: workflow-architecture-design
description: Design target or transition software architecture from accepted behavior and quality scenarios before implementation when a change spans multiple module/API, data-owner, protocol/event, runtime/thread/failure, deployment, or trust boundaries, including new services, databases, or subsystem-wide programming-paradigm composition. Not for current maps, one boundary, candidate scans, accepted-design implementation, or parallelism inside an existing scheduler.
---

# Workflow Architecture Design

## Routing Card
- role: primary
- family: analysis
- intent_signature:
  - multi-boundary software architecture design
  - target or transition architecture
  - quality-scenario-to-architecture contract
- use_when:
  - accepted behavior or quality requirements require a coherent target across several module,
    data/state, runtime/failure, integration, deployment/operations, or security/trust boundaries.
  - a new service, database/data owner, protocol, plugin ABI, process/deployment boundary, shared
    state model, or cross-module asynchronous/thread model changes several architecture views or
    owners and needs design before implementation.
- do_not_use_when:
  - the request is a descriptive HLD/LLD map (`analysis-codebase-map`), one seam/interface decision
    (`analysis-boundary-design`), ranked improvement scan (`analysis-architecture-deepening`),
    domain meaning (`analysis-domain-modeling`), measured bottleneck diagnosis
    (`analysis-performance`), production implementation, or static review.
  - the existing accepted architecture already decides the requested implementation slice and no
    material owner, public contract, dependency, state, runtime, deployment, or trust boundary moves.
  - the change adds an adapter inside an accepted Port contract or parallelizes work inside an
    existing Scheduler/resource owner without moving cross-module ownership, thread semantics, or
    another architecture view; use `workflow-implementation` or diagnose a measured bottleneck with
    `analysis-performance`.
- expected_inputs:
  - architecture question and target scope
  - accepted functional drivers, quality scenarios or the facts needed to form them, constraints,
    non-goals, and decision authority
  - current owners, canonical sources, and a representative actual path for brownfield work
  - artifact/write boundary and acceptance status when available
- expected_outputs:
  - one coherent `architecture_design`, candidate comparison, scoped pattern applications,
    boundary/ownership contracts, current-target-transition design, architecture delta and required
    approvals, fitness contract, implementation handoffs, and explicit unresolved decisions
- context_targets:
  must_read:
    - architecture request, target scope, accepted requirements/constraints, and decision authority
    - `references/architecture_design_contract.md`
    - `references/boundary_decision_contract.md`
    - current owner and one representative plus material-edge path for brownfield work
  read_if_needed:
    - accepted domain model, current HLD/LLD map, build/module graph, public APIs, schemas, state/data
      owners, runtime/failure path, deployment/operations contract, and security/trust rules that can
      change the decision
    - `references/programming_paradigm_contract.md` when the user selects a subsystem/module
      paradigm, supplies paradigm research, or a candidate materially changes state/effect
      ownership, shared data representation, compile/runtime extension, or execution architecture
    - after that base contract, only the selected files under
      `references/programming-paradigms/`; load a second thin profile only for another material axis
      or pairwise conflict
    - `references/database_persistence_transparency_contract.md` when database ownership, schema,
      consistency, transaction, migration, or data-access boundaries are material
  do_not_load_by_default:
    - full repository, broad architecture or pattern catalogs, all historical ADRs, full memory or
      Knowledge stores, unrelated design docs, generated reports, raw production data, or credentials
    - `workflow-implementation`'s detailed paradigm method profiles, code examples, or regression
      cases; Architecture consumes only the shared decision contract
- risk_profile:
  reads: accepted requirements and only the source, runtime, and contract evidence needed by the material views
  writes: explicit architecture artifact only; never production code, build/runtime config, schemas, tests, ADR/Knowledge records, or Plan/Handoff
  tools: focused search, safe current-path observation, and bounded diagram rendering only when it materially clarifies the design
  sensitive_resources: credentials and production data denied; external systems and persistent state remain read-only unless separately authorized
- entry_scene: PREPARE

### Resource Closure

```json
[
  {
    "source": "shared/docs/architecture_design_contract.md",
    "target": "references/architecture_design_contract.md",
    "projection": "verbatim",
    "load": "must_read",
    "condition": "selected skill's mandatory read contract applies"
  },
  {
    "source": "shared/docs/boundary_decision_contract.md",
    "target": "references/boundary_decision_contract.md",
    "projection": "verbatim",
    "load": "must_read",
    "condition": "selected skill's mandatory read contract applies"
  },
  {
    "source": "shared/docs/database_persistence_transparency_contract.md",
    "target": "references/database_persistence_transparency_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming-paradigms",
    "target": "references/programming-paradigms",
    "projection": "tree",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  },
  {
    "source": "shared/docs/programming_paradigm_contract.md",
    "target": "references/programming_paradigm_contract.md",
    "projection": "verbatim",
    "load": "read_if_needed",
    "condition": "selected skill's matching read_if_needed condition applies"
  }
]
```

## Ownership Boundary

Apply `references/architecture_design_contract.md`. This workflow owns a normative multi-view
architecture design and the coherence of its included `boundary_decision` records. It does not call
`analysis-boundary-design` once per boundary. Route there instead when one structural boundary is
the whole requested outcome.

Current-state mapping, domain meaning, measured performance diagnosis, implementation, static
review, test design/implementation, ADR or Knowledge persistence, and Plan/Handoff topology remain
with their named owners. A completed architecture design is input to those owners, never permission
to start them.

After acceptance, a later request may route one explicitly atomic enforcement/boundary question to
`analysis-boundary-design` with `architecture_design_ref`. That skill may return exactly one
conforming `boundary_decision`; any coupled-view or accepted-constraint conflict returns here for
re-design and re-acceptance. This is a conditional handoff, not an automatic skill chain.

This version returns a direct, user-owned architecture artifact and has no Core execution-item
kind. Do not bind it as a Plan/Handoff DAG node or send its result through a Coordinator envelope;
typed graph integration requires a separately accepted Core contract change.

## Architecture Authority

- Classify the result `proposed` unless the user or an authoritative accepted artifact grants the
  decision authority needed by the recorded architecture delta. Never turn inferred team,
  deployment, data, regulatory, or risk-tolerance assumptions into accepted boundaries.
- Use architecture conservation as the baseline, while allowing an evidenced brownfield defect or
  canonical-owner conflict to reject the current structure. Compare the smallest viable baseline,
  not an artificially weak status quo.
- Select only patterns implicated by the scenarios. A named pattern supplies vocabulary, not proof
  or permission to apply it across the system.
- When `references/programming_paradigm_contract.md` is active, own only
  `architecture_material` applications whose `decision_owner` is `coupled_architecture`. Local
  choices stay with Implementation; one-boundary choices stay with Boundary Design. Record the
  accepted application in this design's `pattern_applications`, load only selected thin profiles,
  and never load detailed Implementation method profiles here.
- Keep one canonical owner for each policy, state/data set, public contract, failure rule, and
  architectural fact. Adapters translate; they do not acquire domain, source-selection, fallback,
  migration-truth, or failure-policy ownership.

## Workflow

1. Bind the design question, target and non-goals, greenfield or brownfield mode, accepted drivers,
   decision authority/status, artifact/write boundary, observable design benefit, and one negative
   or edge scenario. Leave a material missing business or ownership decision explicit.
2. Convert material qualities into scenarios with stimulus, environment, expected response,
   measurable response or discriminator, and requirement owner. Do not substitute a generic
   availability, performance, security, or maintainability checklist.
3. Inspect only the views that can change the decision. For brownfield work, trace current owners,
   canonical sources, one representative actual path, and one falsifying or material-edge path.
   Reuse a supplied current-state map as a locator only after checking its source refs.
4. Compare at most three coherent candidates, including preserving or minimally deepening the
   current design when viable. Evaluate ownership removed or added, scenario satisfaction,
   translation/coordination/testing/latency/failure/operating cost, reversibility, and cross-pattern
   interactions and sensitivity points where one assumption or tactic changes several qualities.
   Apply the programming-paradigm architecture-impact/decision-owner gate to every material choice,
   including agent-selected choices. Record each accepted `coupled_architecture` application on its
   own governed axis/owner/scope; leave `local_implementation` choices out and hand a standalone
   `atomic_boundary` decision to `analysis-boundary-design`. Reject a candidate that works only by
   omitting a required view.
5. Select the smallest coherent design supported by the evidence. Record every chosen pattern's
   owner, triggers, non-triggers, minimum closure, maximum scope, interactions, costs, evidence,
   escalation conditions, and review/retirement trigger. A paradigm/model entry uses
   `kind: programming_paradigm | adjacent_implementation_model`, its selected thin profile, and the
   shared specialization fields without copying the generic pattern record. Use
   `boundary_decision_contract.md` for the material boundaries without multiplying pass-through
   layers or parallel policy paths.
6. Define applicable module/API, data/state, runtime/failure, integration/protocol,
   deployment/operations, and security/trust contracts: owner, purpose, public crossing contract,
   allowed/forbidden knowledge and dependencies, consistency/lifecycle/failure semantics,
   invariants, and non-goals. Omit views that add no decision information.
7. For brownfield change, define current, target, and transition states, including sequencing,
   compatibility, migration, rollback, temporary exception owner/expiry, and convergence. Do not
   claim a target design is implementable when its transition preserves two authoritative paths.
8. Classify the architecture delta by changed boundaries and name each required approval. Keep the
   whole record `proposed` while any material decision lacks authority; its implementation slices
   are non-authoritative. If the user explicitly narrows work to a genuinely independent accepted
   scope, return a separate design record for that target rather than mixing statuses.
9. Map every accepted claim to the smallest structural, semantic, or operational fitness evidence,
   its owner/path, representative scenario, material falsifier, and proof ceiling. Mark it `planned`
   unless an existing path actually ran and the observed evidence is referenced. Specify the
   contract; do not create checks, tests, CI, hooks, or validation infrastructure unless separately
   requested.
10. Read the design back against every driver, pattern stop boundary, canonical owner, transition,
    and falsifier. Return bounded implementation slices and unresolved approvals without creating a
    backlog, invoking another skill, or choosing a Plan successor.

## Stop Rule

Stop when each material driver is either mapped to a selected constraint and condition-matched
fitness evidence or named unresolved; every applied pattern has a minimum closure and maximum
scope; ownership and source-of-truth crossings are explicit; the architecture delta and approvals
are visible; and a brownfield design has a non-duplicative transition/rollback path. More diagrams,
patterns, files, or scenarios are out of scope when they cannot change those decisions.

## Output Contract

Return one canonical `architecture_design` record from
`references/architecture_design_contract.md`, plus only `evidence_refs` and `artifact_refs` that
support or locate it. Keep drivers, candidate comparison, patterns, boundaries, transition, delta,
fitness conditions, implementation slices, and unresolved authority inside that one record rather
than repeating them as parallel top-level sections.

An architecture artifact establishes only the recorded design decision and evidence ceiling. It
does not prove production conformance, runtime fitness, migration safety, or human acceptance.
