# Architecture Design Contract

This contract defines the shared meaning of a normative software architecture design when several
module, data, runtime, integration, deployment, or trust boundaries must work together. It is not
an architecture catalog, a required repository layout, a router, or a workflow owner.

## Design Principle

Architecture is a scoped set of constraints chosen to satisfy named behavior and quality scenarios.
A pattern name, directory shape, interface, or diagram is not an architecture decision by itself.
Preserve the current architecture when it can satisfy the scenarios without moving ownership or
adding conceptual machinery. Change it only when an accepted requirement, invariant, external
volatility, operating constraint, or actual-path failure establishes the pressure.

Architecture conservation does not protect accidental coupling or a boundary already contradicted
by its canonical owner, invariant, or representative path. Greenfield work may use accepted
requirements and quality scenarios as evidence; brownfield work also traces the current owner and
one representative and material-edge path.

## Architecture Design Record

Use only fields material to the current design. Mark material claims `established`, `inferred`,
`proposed`, or `unverified`. `accepted` is a decision status, not an evidence label.
`decision_status` applies to the whole record. Keep it `proposed` while any material decision lacks
authority; every `implementation_slice` in that record then remains a proposal, not implementation
authority. If a genuinely independent accepted scope must proceed, create a separate design record
for that narrower target instead of mixing accepted and proposed fields in one artifact.

```yaml
architecture_design:
  target:
  decision_status: proposed | accepted
  decision_authority:
  drivers: []
  quality_scenarios: []
  current_state_refs: []
  applicable_views: []
  candidate_comparison: []
  pattern_applications: []
  boundary_decisions: []
  canonical_authorities: []
  architecture_delta:
    change_class: local_internal | boundary_contract | system_topology
    changed_contracts: []
    required_approvals: []
  transition:
  fitness_contract: []
  risks_and_tradeoffs: []
  sensitivity_points: []
  exceptions: []
  implementation_slices: []
  unresolved: []
```

- `drivers`: accepted functional behavior, quality pressure, constraints, and explicit non-goals.
- `quality_scenarios`: stimulus, environment, expected response, measurable response or
  discriminator, and the owner of the requirement. Generic quality words are not scenarios. For a
  real-time or parallel scenario, name the representative workload and target environment plus
  only the claimed deadline/tail, throughput, end-to-end latency, memory, or in-flight bound; mean
  utilization is not a response measure.
- `applicable_views`: only the views that change the decision—logical/module/dependency,
  data/state/consistency, runtime/concurrency/failure, integration/protocol, deployment/operations,
  or security/trust. UI visual design stays with its Design owner.
- `candidate_comparison`: the smallest coherent baseline and material alternatives, including
  rejected reasons, cross-view interactions, sensitivity points, reversibility, and costs. It is
  decision rationale inside this record, not another architecture source of truth.
- `boundary_decisions`: the applicable records from `boundary_decision_contract.md`. The design
  owns their coherence as a set; a request whose only open outcome is one boundary belongs to
  `analysis-boundary-design`.
- `canonical_authorities`: the source of truth for each material fact or rule. Generated summaries
  and diagrams remain projections, not parallel authorities.
- `transition`: current-to-target sequencing, compatibility, migration, rollback, and removal of
  temporary exceptions when those concerns exist.
- `fitness_contract`: condition-scoped structural, semantic, or operational evidence that could
  expose a wrong design. It specifies evidence ownership; it does not authorize implementation of
  checks or execution of another workflow.
- `implementation_slices`: bounded handoffs whose dependencies and ownership follow the accepted
  design. They are not a generated backlog or permission to start implementation.

Use this minimum shape for each material quality scenario:

```yaml
quality_scenario:
  id:
  stimulus:
  environment:
  expected_response:
  measure_or_discriminator:
  requirement_owner:
```

## Pattern Application Contract

Load or describe only patterns implicated by the current decision. Do not place a general pattern
catalog in default context.

```yaml
pattern_application:
  kind: architecture_pattern | programming_paradigm | adjacent_implementation_model
  pattern:
  governed_axis:
  applies_to:
  owner:
  authority_ref:
  intent:
  triggers: []
  non_triggers: []
  claimed_properties: []
  minimum_closure: []
  maximum_scope:
  interactions: []
  architecture_impact:
  forbidden_drift: []
  costs: []
  evidence: []
  escalate_when: []
  revisit_or_retire_when: []
```

- `minimum_closure` is the smallest end-to-end realization needed to obtain the claimed property.
  A nominal interface, layer, queue, service, or repository that leaves the original dependency,
  ownership, failure, or consistency semantics in place is incomplete.
- `maximum_scope` says where the pattern stops. Never expand a useful pattern to unrelated internal
  objects, calls, modules, or data merely for symmetry, test convenience, or speculative reuse.
- `interactions` records combined costs or constraints when patterns govern different views, such
  as a service boundary changing transaction, event-ordering, deployment, and observability needs.
  For a cross-boundary pipeline, it also records snapshot/version publication, maximum in-flight
  work, last-consumer reclamation, backpressure, and end-to-end latency ownership.
- `evidence` must match the claimed property. Mocks and static shape prove only their own boundary.
- `owner` and `revisit_or_retire_when` prevent a locally useful pattern from becoming an ownerless,
  permanent default after its driver or external constraint disappears.
- A `kind: programming_paradigm | adjacent_implementation_model` entry follows
  `programming_paradigm_contract.md`. Its governed axis, claimed properties, architecture impact,
  decision owner, and selected thin-profile proof ceiling keep a paradigm/model decision distinct
  from repository-wide style and later code realization. Its structured `evidence` specializes the
  generic field; do not duplicate the same evidence or refs in parallel fields.

## Runtime And Concurrency View Closure

Activate this closure only when a material design uses the runtime/concurrency/failure view. Record
only the fields that can change the decision:

- execution domains and actual wait carriers, distinguishing caller suspension, blocking adapters,
  readiness/completion loops, CPU workers, pinned lanes, and external queues;
- canonical state owner, immutable or versioned snapshots, read/write access sets, and the sole
  publication/commit boundary for frame-, request-, or operation-visible results;
- execution and completion dependencies, representative total work and critical path, queue or
  in-flight bounds, overload/backpressure policy, and any forward-progress exception;
- cancellation, deadline, failure, shutdown, and last-consumer reclamation across every staged or
  suspended operation lifetime;
- the claimed latency/throughput tradeoff, including whether pipelining or batching increases
  end-to-end latency while improving throughput; and
- trace/task identity and timestamps sufficient to distinguish useful work, ready-queue delay,
  blocking wait, synchronization, and downstream completion.

Do not infer parallelism from `async`, performance from worker utilization, determinism from race
freedom, or low latency from pipeline throughput. Local lock, atomic, coroutine, fiber, queue, and
scheduler mechanics remain with Implementation unless they change a cross-owner contract.

## Rule, Source, And Enforcement

Every normative rule must name its scope, rationale or driver, owner, canonical authority,
enforcement or observation path, and exception/approval owner. Without those fields it remains
guidance, not an established architecture constraint.

- Documentation, skills, diagrams, and local agent rules communicate intent but do not prove or
  enforce the production boundary.
- Prefer the existing compiler/type system, module/build graph, schema, contract/integration path,
  trace, benchmark/budget, permission, or deployment control that directly owns the fact.
- Do not duplicate one fact across README, architecture prose, agent rules, code comments, and
  diagrams. Record decision rationale separately from executable or machine-owned truth.
- An exception needs an owner, affected scope, reason, review or expiry condition, and removal or
  convergence path. A permanent undocumented bypass is a second architecture.

## Architecture Delta And Approval

Classify risk by changed boundary, not code size.
At design level, record the highest material change class and list each changed contract with its
owner and approval state; do not hide a system-topology change inside a larger local diff.

- `local_internal`: private implementation changes with no public contract, dependency direction,
  state/data owner, runtime model, deployment unit, or trust boundary change. Keep this local to the
  implementation owner unless another accepted rule requires review.
- `boundary_contract`: a public API, module dependency, shared state/schema, asynchronous flow,
  thread/resource model, lifecycle, or failure contract changes. Name the affected owner and leave
  acceptance unresolved when authority was not delegated.
- `system_topology`: a process, service, database or data owner, external protocol, plugin ABI,
  deployment unit, security/trust boundary, or regulated-data path changes. Keep it `proposed`
  until the declared authority accepts it before implementation.

The classes communicate required review; they do not create universal organization roles or grant
the agent authority that the request did not supply.

## Fitness Evidence

Use only layers implicated by the design, and state the proof ceiling of each observation.

```yaml
fitness_condition:
  id:
  claim:
  layer: structural | semantic | operational
  evidence_status: planned | observed
  evidence_owner:
  evidence_path:
  evidence_refs: []
  representative_scenario:
  falsifier:
  proof_ceiling:
```

- `structural`: dependency direction, forbidden imports, cycles, build/module graph, public API
  types, schema shape, or deployment topology.
- `semantic`: domain/data ownership, invariants, error meaning, consistency, actual adapter or
  protocol contract, and representative valid input/output.
- `operational`: latency/resource budgets, ordering, concurrency, cancellation, retry/idempotency,
  recovery, failure isolation, security controls, deployment behavior, or observability.
  For a parallel or pipelined claim, use the smallest relevant combination of total work, critical
  path/span, queue/wait/idle time, tail/deadline, in-flight count, memory footprint, and end-to-end
  latency. Job count, DAG shape, and mean utilization alone cannot close the claim.

A structural check cannot close a semantic or operational claim. Every accepted architecture claim
that crosses a real production boundary must name one representative scenario and one material edge
or falsifier plus the evidence owner/path that will exercise them. Mark the condition `observed`
only when that path actually ran and has an evidence reference; architecture design normally leaves
future implementation/validation evidence `planned`.

## Consumer Responsibilities

- `workflow-architecture-design` authors one coherent multi-view `architecture_design`, including
  target and transition state, pattern scope, architecture delta, approvals, and fitness contract.
- `analysis-boundary-design` owns every standalone one-boundary request or explicitly assigned
  atomic structural decision. When an accepted design explicitly constrains that target, it may
  consume only the relevant drivers/scenarios, canonical authorities, pattern scope,
  dependency/transition rules, architecture-delta class/changed-contract scope and approval state,
  approvals, and fitness conditions; it returns the design reference plus exactly one conforming
  `boundary_decision` without rewriting or accepting the architecture. A delta expansion,
  coupled-view move, or accepted-constraint conflict returns to `workflow-architecture-design`.
- `analysis-codebase-map` owns descriptive current-state maps, not target architecture selection.
- `analysis-domain-modeling` owns business meaning, identity, lifecycle, and domain invariants.
- `workflow-implementation` consumes only an accepted design record for its bounded production
  slice; it neither accepts a proposed record nor silently redesigns a competing boundary.
- `workflow-code-review` may check a bound diff against an accepted design, but it owns findings,
  not architecture creation or runtime validation.
