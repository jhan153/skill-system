# Research Stage Contract

This contract defines shared ownership and transition rules for scientific evidence, hypothesis,
experiment, analysis, manuscript, and peer-review artifacts. It also separates direct specialist
work from the explicit `workflow-research` node envelope. It is not a lifecycle runner, required
pipeline, or permission to start another stage.

## Stage Ownership

| Requested artifact | Owner | Required input | Output ceiling |
|---|---|---|---|
| paper evidence | `search-paper-evidence` | explicit paper/citation question | traceable paper evidence or acquisition gap |
| cross-lane evidence set | `search-deep-evidence` | one claim requiring independent evidence lanes | evidence set and limits, not final synthesis |
| literature synthesis | `research-literature-synthesis` | identified paper/evidence set and scope | themes, contradictions, limitations, and coverage gaps |
| literature-derived hypotheses | `research-literature-ideation` | identified evidence set or synthesis | candidates; active selection only when requested |
| claim-first research decision | `research-hypothesis-planning` | premise, mechanism, scope, and evidence status | one falsifiable claim and cheapest discriminator |
| experiment protocol | `research-experiment-blueprint` | one selected hypothesis | identifiable protocol, not code or results |
| experiment wiring scaffold | `research-experiment-scaffold` | approved blueprint or equivalent complete contract | runnable wiring and synthetic smoke, not real method/data/results |
| statistical result or analysis plan | `research-statistical-analysis` | real data/statistics or explicit plan request | reproducible inference from adequate data, otherwise plan only |
| manuscript prose | `research-manuscript-writing` | named evidence/method/result artifacts | calibrated prose, not missing evidence or invented results |
| scholarly review | `research-peer-review` | exact manuscript/proposal/plan slice | anchored findings, not venue authority or automatic acceptance |

## Direct Work And Node Management

- An ordinary one-stage user request routes directly to the matching specialist above. Do not add
  `workflow-research` merely because the task uses Research vocabulary.
- In an accepted Plan/Handoff DAG, one `RES-*` node routes to `workflow-research` plus exactly one
  preselected `research-*` stage skill. The Workflow owns the node execution envelope; the selected
  specialist owns scientific method and artifact meaning.
- `workflow-research` is not a stage classifier. The accepted Plan or explicit user request must
  name the stage. Missing or conflicting stage identity is unresolved and produces no result card.
- One manager invocation executes one stage only. It never groups a literature-to-manuscript chain,
  starts an evidence search, or creates another node.
- Search acquisition remains a separately assigned evidence node. General method, data pipeline,
  training, or product implementation remains a separately assigned implementation node.

## Transition Rules

- For direct work, select one specialist from the requested artifact. For graph work, preserve the
  Plan-selected `workflow-research` plus one-stage binding. Research vocabulary, an upstream
  artifact, or a completed stage never invokes the next stage automatically.
- Run several stages only when the user explicitly requests the multi-stage outcome or an accepted
  Plan/Handoff DAG already contains those nodes and dependencies.
- When required upstream input is missing, return the exact missing artifact and its current owner.
  Do not create it, search for substitutes, or start another skill unless that work is separately
  authorized. Independent accepted Plan nodes may continue.
- A downstream owner consumes the upstream artifact as evidence, not as permission to change its
  claims, fabricate missing fields, or declare scientific success.
- Write an artifact only on explicit artifact intent, using the user path or current repository
  convention. This contract defines no fixed `papers/`, `experiments/`, `analysis/`, or `review/`
  location.
- Keep planned methods, executed methods, observed results, statistical interpretation, and
  manuscript claims distinguishable throughout the handoff.

## Execution Handoff Integration

- `plan-execution-handoff` may compile only explicitly selected Research stages as ordinary typed
  DAG nodes. It binds each `RES-*` node to `workflow-research` and exactly one selected stage skill.
- In graph mode, `workflow-research` returns Core `research_result`; the Coordinator records it and
  applies only an existing Plan edge. Stage specialists never emit the card or edit Handoff.
- A Research result contains the selected stage skill, input refs, compact outcome, output ceiling,
  artifact/evidence anchors, unresolved inputs, and user checks. It does not select a successor.
- A missing stage or material prerequisite returns lifecycle `not_produced`; it does not create a
  partial result, run an adjacent stage, or close the graph early.
- `research-experiment-scaffold` is a write node only for approved experiment wiring. Real method,
  baseline, metric, data pipeline, training, or product implementation belongs to a separate
  `workflow-implementation` node when explicitly requested.
- `research-statistical-analysis` cannot emit inferential results without adequate identified data.
  A plan-only output must remain visibly distinct from a result artifact.
- `research-peer-review` affects graph admission or completion only when the accepted Plan names
  that review as a required gate. Otherwise its findings do not block unrelated nodes or select the
  next stage.
