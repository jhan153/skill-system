---
name: plan-decision-map
description: Maintain an explicitly requested decision map for work whose target outcome is known but whose decision path will span multiple sessions. Use for durable uncertainty management before ordinary requirements or implementation planning; do not use for a settled feature, an implementation backlog, or direct execution.
---

# Decision Map

## Routing Card
- role: primary
- intent_signature: explicit durable map of unresolved decisions for a multi-session outcome
- use_when:
  - the user explicitly invokes `plan-decision-map` or requests a persistent decision map.
  - the target outcome is stable enough to name, while material prerequisites and choices are still unknown.
- do_not_use_when:
  - one discovery round, requirements brief, tactical plan, or implementation task can cover the work.
  - the requested artifact is a build backlog, phase package from settled decisions, status report, or execution queue.
- expected_inputs: target outcome, decision owner, scope boundary, known constraints, authorized workspace, and optional existing map
- expected_outputs: one canonical decision index, bounded decision items, prerequisite links, current ready set, unshaped unknowns, exclusions, and one next-owner recommendation when decision work closes
- context_targets:
  must_read:
    - current request or named decision index
    - repository instructions and the authorized artifact boundary
    - [Decision-map schema](references/decision-map-schema.md) before creating or changing artifacts
  read_if_needed:
    - the selected item, its prerequisites, linked resolutions, and evidence that can change its answer
    - existing requirements or domain contracts that constrain the target outcome
  do_not_load_by_default:
    - all item bodies, full repository history, unrelated plans, or every prior session
- risk_profile:
  reads: begin with the index and admit detail only for the selected item
  writes: local Markdown inside the authorized workspace; a named external tracker still requires separate mutation authority
  tools: narrow evidence, prototype, or coordination tools only when their own routing and authority contracts are met
  sensitive_resources: credentials and production data denied; never store secrets in planning artifacts
- entry_scene: PREPARE

## Ownership Boundary

This skill owns unresolved-decision structure, not delivery work. Its artifacts explain what must be learned or decided before normal requirements, architecture design, or implementation planning can take over.

A decision item is not a disguised implementation task. It may request evidence, a user choice, a throwaway discriminator, or a prerequisite action, but it closes only the uncertainty named in that item. Starting production work always remains with the normal execution owner and requires current authorization.

The map stays outside the persisted implementation planning state. A complete map means the material decisions are recorded; it does not prove feasibility, implementation readiness, or delivered behavior.

## Artifact Model

Keep one canonical index plus one file or native tracker record per decision item. The index carries only navigation and current aggregate state. The item owns its detailed evidence and resolution.

Use these local concepts:

- **Target outcome:** the decision-complete condition and its owner.
- **Decision item:** one question or prerequisite that can reach a traceable result in a bounded session.
- **Prerequisites:** item ids whose resolutions are required before this item can be answered responsibly.
- **Ready set:** open, unclaimed items whose prerequisites are resolved.
- **Unshaped unknown:** material uncertainty that cannot yet be written as a precise item.
- **Exclusion:** work outside the target outcome, including an explicit reason.

Classify each item by the owner it needs:

- `evidence`: acquire a fact through the narrowest evidence owner.
- `choice`: obtain a decision from the named human or policy owner.
- `prototype`: produce one cheap observable discriminator through `workflow-prototype`.
- `enabler`: complete a prerequisite action that makes a later decision answerable.

Mark interaction as `agent_runnable` or `user_guided`. Availability of tools or delegates never changes a user-guided decision into an agent-owned answer.

## Persistence Threshold

Before writing a map, test whether persistence earns its cost:

1. Can the target outcome be stated without inventing it?
2. Will unresolved decisions or evidence dependencies survive beyond the current session?
3. Would a single requirements artifact or ordinary plan lose material dependency information?

If any answer is no, keep the task with the smaller existing owner. Do not create uncertainty to justify a durable map.

## Initialize

1. Fix the target outcome, decision owner, in-scope boundary, and completion condition.
2. Survey the decision space breadth-first. Record precise current questions as items and leave later, premise-dependent uncertainty unshaped.
3. Create item identities before adding prerequisite links so relationships never point at unstable names.
4. Derive the ready set from item state; do not infer readiness from document order.
5. Start agent-runnable evidence work only when the current host and user authority permit it. Creating the map does not authorize delegation, remote issues, branches, or messages.
6. Stop after the initial index and current ready set are readable. Initialization does not begin delivery of the target outcome.

## Advance One Decision

1. Re-read the index and candidate item headers because another session may have changed ownership or prerequisites.
2. Use the item named by the user; otherwise choose the first item in the derived ready set.
3. Claim only that item, then read its prerequisites and the minimum evidence needed by its type.
4. Resolve one user-guided item per turn. Independent evidence items may finish concurrently only when they were separately authorized.
5. Store the detailed result and evidence pointers on the item. Add one linked summary line to the index.
6. Re-evaluate dependent items, promote newly expressible unknowns into fresh items, and record any newly exposed exclusions.
7. Stop at the decision boundary. Do not continue into implementation because the answer now looks actionable.

For local Markdown, a claim is cooperative coordination rather than a lock. Re-read immediately before writing, preserve other claims, and reselect if another owner already claimed the item.

## Close And Hand Off

Decision mapping is complete when no in-scope unshaped unknown remains and every decision item is resolved or explicitly excluded. The index must also state the resulting outcome well enough that the next owner does not need an unrecorded decision.

Recommend one next owner without invoking it automatically:

- `plan-requirements-brief` for a requirements contract;
- `plan-long-term-package` for a multi-document strategic package;
- `plan-short-term-docs` for one persisted tactical plan;
- `analysis-boundary-design` for one selected technical boundary; or
- the intent-matched execution owner only when the result already defines a bounded authorized change.

Return the index path, target outcome, created or resolved item names, ready set, unshaped unknowns, exclusions, coordination conflicts, completion status, and recommended next owner.
