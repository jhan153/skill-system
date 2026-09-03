# Static Code Review Contract

This contract governs pre-test, source-based review of one bound implementation change. It selects
review depth from changed semantics and consequence, accounts for every material changed effect,
and distinguishes current defects from non-blocking advice and later-owned unresolved work.

It does not own repair, runtime validation, production test design, test-oracle adequacy,
Plan/Handoff topology, merge readiness, or product acceptance. When the reviewed artifact is
itself a test implementation, its existing Test Design conformance contract remains applicable.

## Change Contract

Before choosing paths, risk axes, or Mermaid views, bind:

- the exact implementation identity and bounded review slice;
- the stated problem or intent and expected observable change;
- the assigned positive production output and accepted implementation/method contract, when one
  exists;
- every materially changed contract, state owner, effect owner, dependency, or external effect;
- preserved invariants and failure guarantees;
- claimed material risks and explicit exclusions;
- compatibility, rollout, and rollback concerns only when the change implicates them; and
- supplied normative baselines and Known Bug exclusions.

Give every material changed effect a stable local ID plus source refs. A material changed effect is
behavior, state, ownership, dependency, persistence, trust, resource, or failure semantics whose
change can alter an observable result or the safety of a production path. File count and diff size
do not determine materiality.

When no Core item supplies a snapshot, resolve and record an unambiguous repository diff or
worktree identity when available. Do not invent missing intent or a normative baseline. When
intended behavior cannot be established, continue intrinsic source review where possible and mark
the conformance scope `intrinsic_only`. When the implementation identity or required source cannot
be established, produce no review result.

## Design Preflight

Before line-level inspection, determine whether:

- the implementation addresses the bound intent;
- the snapshot actually contains a reviewable implementation of the assigned primary production
  output rather than only plans, scaffolding, or an unchanged baseline; absence makes the supplied
  implementation result incomplete and never turns the baseline into a Bug Fix target;
- changes with different reasons are separated or explicitly bounded;
- policy, state, and effects remain with their canonical owners;
- dependency direction and trust boundaries remain valid or are explicitly authorized;
- an abstraction or generalization is required by a current contract rather than speculative
  reuse; and
- the existing simpler boundary can satisfy the same accepted contract.

A current-scope ownership, boundary, or responsibility violation is a blocking finding, not
authority to design a replacement architecture. When a fundamental defect makes subordinate code
likely to be replaced, record that defect first and stop reviewing details whose truth depends on
the rejected structure. Continue reviewing independent security, irreversible-data,
trust-boundary, and resource-lifetime risks.

## Risk Activation

Activate only axes whose semantic signal is present. Record why each selected axis applies. Never
run every axis as a universal checklist or select depth from file count or diff size.

| Axis | Activate when the change affects |
| --- | --- |
| `contract_invariant` | observable behavior, public contract, guard, required omission, or invariant |
| `state_flow_reachability` | state, branch, callback, registration, dispatch, propagation, or terminal path |
| `failure_recovery` | error, cancel, timeout, retry, partial effect, rollback, or compensation |
| `ownership_dependency` | policy/state/effect owner, interface, module dependency, or effect boundary |
| `resource_lifetime_concurrency` | shared mutable state, async/thread work, lock, cleanup, handle, or resource lifetime |
| `data_integrity_compatibility` | persistence, schema, serialization, versioning, migration, or shared-data contract |
| `trust_boundary_security` | untrusted input, identity, permission, capability, secret, or privileged/external effect |
| `performance_resource` | hot path, bounded workload, fan-out, allocation, I/O, or an implementation-level cost claim |
| `observability_diagnostics` | the ability to distinguish, diagnose, or recover from a failure or operational state |

A production implementation review shall not assess test-oracle completeness, missing test cases,
coverage percentage, or runtime-result adequacy. Existing tests may be read only when they are
needed as direct caller or accepted contract evidence; they do not create a production test-review
lane.

For concurrency, a source-permitted interleaving that violates lifetime, synchronization,
ordering, visibility, or cleanup is a static finding. Its production frequency or
scheduler-dependent occurrence remains runtime-only. Source-proven cost amplification may support
a static finding only against an explicit bound or accepted implementation constraint; measured
latency, throughput, or resource behavior remains runtime-only.

When `resource_lifetime_concurrency` is active, distinguish asynchronous operation lifetime, CPU
task scheduling, and shared-memory coordination instead of treating every queue or callback as one
model. Trace the authoritative state owner, actual wait carrier, publication/visibility edge,
cancellation/shutdown cleanup, last-consumer reclamation, and any source-permitted task migration
or affinity dependency. Locks, atomics, dependency edges, and race-free ranges do not by themselves
prove whole-invariant correctness, forward progress, numerical determinism, or performance.

## Mermaid And Coverage

Every produced review retains at least one source-linked Mermaid model covering the highest-risk
material changed effect. Add complementary views until every activated material axis is visible.
`model-comparison.md` exclusively owns view type, altitude, labeling, source-linking, and rendering
mechanics.

A representative path and one material disconfirming path are minimum observations, not a coverage
ceiling. Expand the path set for each materially distinct high-consequence effect or when one path
cannot expose a separate owner, trust boundary, irreversible effect, concurrency/lifetime risk, or
failure guarantee.

Before disposition, assign every material changed effect to all applicable activated axes and at
least one of:

- a reviewed source path and Mermaid element;
- a blocking finding;
- an authorized Known Bug exclusion;
- a typed deferred item; or
- an explicit material-unassessed entry with its consequence and later owner.

No material changed effect may remain unaccounted for in a produced result.

## Result Classification

A `finding` is a falsifiable current-scope implementation defect or required implementation
omission. It changes disposition to `repair_required`. Finding priorities are P0, P1, and P2 only.
Each finding states tight code refs, current impact, and the `required_condition` repaired code must
satisfy. A `suggested_solution` is optional and non-normative.

`repair_required` is a static disposition for the reviewed snapshot, not a Bug Fix classification
or successor authorization. The Coordinator compares the required condition with the Plan's
positive output and accepted implementation/method contract. A bounded defect repair that preserves
an already-implemented accepted contract may enter BF; first implementation, explicit
production-mechanism replacement, and unresolved method selection do not. The reviewer records the
finding and proof ceiling without selecting that owner or Plan edge.

An `advisory` is an evidenced improvement whose absence does not establish a current defect or
required omission. It does not change disposition, create a repair obligation, create a deferred
item, or authorize future Plan work. Evidenced future-drift concerns belong here; P3 is not a
finding priority.

Create a `deferred_item` only when all of the following hold:

1. it can materially change a later decision or outcome;
2. it is not a current-scope implementation repair;
3. it has a named later owner or observation point; and
4. dropping it would lose a material risk or authority gap.

Nice-to-have cleanup, generic questions, speculative reuse, and style preference are omitted or
recorded as advisories, never promoted automatically to durable deferred work.

## Coverage And Static Proof Ceiling

A produced result reports:

- covered material-effect IDs;
- activated risk axes;
- material items not assessed;
- whether conformance scope was `intrinsic_only` or `baseline_compared`; and
- the static proof ceiling.

Disposition precedence is `repair_required` over `complete_with_deferred_items` over `pass`.
`repair_required` requires at least one blocking finding.
`complete_with_deferred_items` requires no blocking finding and at least one deferred item. `pass`
requires no blocking finding, no deferred item, and no material-unassessed entry. Advisories may
accompany any disposition.

`pass` means only that the bound static slice is complete and every material changed effect is
accounted for without a repair-required defect or later-owned material gap. It does not establish
runtime behavior, test sufficiency, merge readiness, full requirement completion, or product
acceptance.

## Task Cases

- **Positive:** a one-line authorization-default change activates `contract_invariant` and
  `trust_boundary_security`, produces an actor-to-privileged-effect Mermaid path, and becomes a
  P0/P1 finding when ownership enforcement is absent.
- **Positive advisory:** all material effects are covered and no current defect exists, while an
  evidenced future-drift concern remains. Return `pass` with an advisory and no repair/deferred
  obligation.
- **Negative:** a production diff has no tests or has a weak existing oracle. Do not create a
  missing-test, coverage, or oracle finding; review only source-based implementation risk.
- **Negative routing:** a local rename or formatting-only change does not obstruct material
  state/flow/ownership tracing. Do not activate this Workflow merely to produce a review result.
- **Edge coverage:** a multi-file change alters retry defaults and authorization registration
  outside the representative path. Both effects must be assigned before `pass` is possible.
- **Edge design:** an ownership violation invalidates subordinate structure. Record the blocking
  design-preflight finding, stop dependent naming/style inspection, and continue only independent
  security, data-loss, or lifetime review.
- **Edge concurrency:** a source-permitted interleaving allows use-after-free or cleanup/order
  violation. Record a static finding; defer only occurrence or frequency.
- **Edge baseline:** no accepted design baseline exists. Use `conformance_scope: intrinsic_only`;
  baseline absence alone is neither a finding nor a deferred item.
- **Edge work kind:** an `implementation_result` snapshot is criticized against an accepted
  algorithm replacement, but the replacement has not been implemented at all. Record the invalid
  or incomplete implementation claim honestly; do not label
  the required production implementation as a Bug Fix or treat an optional reviewer solution as
  replacement authority. Plan/Coordinator semantic admission owns the next route.
