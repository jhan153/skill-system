# Context-Based Qualitative Quality Evaluation

Use this reference when criteria need collaborative elicitation, the user delegates criterion proposals, or an abstract supplied term needs an observable yardstick. User-supplied and user-accepted criteria remain authoritative.

## Definition

Qualitative evaluation interprets evidence against explicit, context-bound criteria to judge fitness, risk, tradeoffs, and improvement needs. It is not an opinion-only review and it is not a metric report.

```text
measurement or observation
-> contextual interpretation
-> criterion judgment
-> decision consequence
-> recommendation
```

A count, score, test result, or benchmark may be evidence. It has no quality meaning until the target's responsibility, expected use, constraints, and yardstick explain why the value matters.

## Evaluation Contract

Bind only fields that can change the criteria or judgment:

| Field | Question |
| --- | --- |
| target | What exact artifact, system, structure, module, path, or result is evaluated? |
| decision | What choice will the evaluation support? |
| stakeholder | Whose quality needs matter? |
| use context | Where and under what conditions is the target used? |
| lifecycle | Is this a proposal, implementation, operating system, or replacement candidate? |
| responsibility | What must the target do or preserve? |
| expected change | What likely change should the target absorb? |
| material failure | What outcome would defeat or seriously degrade its purpose? |
| constraints | What performance, platform, compatibility, safety, or delivery limits apply? |
| exclusions | What is explicitly outside this evaluation? |
| depth | What evidence strength is proportional to the decision? |

Do not invent missing goals or context. For a brief, state a narrow assumption when it cannot change the criteria. Ask when competing contexts would select different criteria or reverse the result.

## Criterion Authority And Origin

Admit criteria through one of these origins:

| Origin | Meaning |
| --- | --- |
| `supplied` | The user provided the criterion or yardstick directly. |
| `elicited` | The criterion was formed from the user's answers and confirmed by those answers. |
| `accepted_proposal` | The skill proposed a criterion and the user explicitly accepted or edited it. |
| `delegated` | The user explicitly asked the skill to select the fitting criteria. |
| `assumed` | A narrow non-material detail was assumed and cannot change selection or judgment. |

An unaccepted proposal is not authoritative. Artifact evidence may reveal an obligation or constraint, but it cannot silently override a user-owned quality priority or decision yardstick.

## Elicit Criteria From The User

Use elicitation when the user asks to define the criteria together or when missing preferences would materially change the evaluation. Do not interview merely because every contract field is not filled.

1. Separate discoverable target facts from user-owned choices. Inspect the target for responsibilities and existing contracts; ask the user about decision intent, stakeholder priorities, acceptable tradeoffs, and yardsticks.
2. Ask one round of up to three mutually independent, decision-changing questions. If one answer determines the next question, ask only that one.
3. Prefer concrete scenario wording over abstract attribute names. When useful, offer 2–4 mutually exclusive choices with a recommendation and tradeoff, while allowing the user to state a different criterion.
4. Record only criterion deltas; do not replay the full evaluation contract after every answer.
5. Stop before evidence collection and report generation when the user explicitly asked to set criteria first.

Common question families, used only when material:

- What decision should this evaluation support?
- Whose perspective or use context should dominate?
- Which outcome must be protected even at the cost of another quality?
- Which expected change or failure matters most?
- What would count as acceptable, conditional, or unacceptable?
- Is there a baseline or alternative that must be compared under the same criteria?
- What evidence depth or excluded scope should bound the judgment?

For an abstract supplied criterion such as “maintainability” or “natural interaction,” translate it into an observable scenario and yardstick. Ask for confirmation only when different translations could reverse the evaluation.

## Propose Criteria When Delegated

When the user asks the skill to recommend or choose criteria, return the smallest proposal set needed for the decision. For each proposal, state:

```text
criterion
why it matters to the user's decision
scenario or evaluation question
observable indicator and evidence needed
suggested yardstick
material tradeoff or exclusion
```

The user may accept, edit, reject, or delegate the final selection. If delegation is explicit and the target evidence is sufficient, proceed with the selected set labeled `delegated`; otherwise stop for the one decision-changing answer.

## Criterion Proposal Model

When proposal authority is delegated, derive candidates through this chain:

```text
Decision goal
-> target profile and responsibilities
-> expected change/failure/use scenario
-> quality obligation
-> criterion
-> indicator
-> evidence
-> yardstick
-> judgment
-> recommendation
```

Quality-model terms such as maintainability, reliability, usability, security, performance, or compatibility are candidate vocabulary. They are not criteria by themselves.

Bad criterion:

```text
Is the module maintainable?
```

Decision-ready criterion:

```text
When a new frame-transport policy is added, can it be implemented and registered without changing mesh assembly or existing callers?
```

## Profile The Target

Inspect only dimensions relevant to the decision:

- responsibilities, inputs/outputs, preconditions, postconditions, and invariants
- state, lifecycle, ownership, and failure representation
- callers, dependencies, exposed policy, and change propagation
- expected changes and stable surfaces
- material failure, recovery, diagnosis, and operating cost
- existing tests, runtime observations, history, or comparison baselines

Target type changes the likely obligations. A closed numerical kernel may prioritize mathematical correspondence, degeneration handling, determinism, and data locality. A frequently extended processing layer may prioritize change locality, contract stability, policy ownership, and regression isolation. Large size or many dependencies alone do not decide either case.

## Quality Obligations

Select only obligations that matter to the decision:

| Obligation | Prompt |
| --- | --- |
| functional | What must be performed correctly? |
| preservation | What must remain valid before and after operation? |
| boundary | What knowledge, state, or policy must stay inside the owner? |
| change | Which likely change must remain local or compatible? |
| failure | What state and information must failure preserve? |
| operation | What performance, memory, concurrency, availability, or recovery behavior matters? |
| diagnosis | What must be observable to identify a material failure? |
| verification | What property must be repeatably observable or checked? |

Turn each admitted obligation into a falsifiable criterion, not a design-fashion proxy. An interface, small class, dependency injection, passing test, low coupling count, ECS, or functional style does not prove quality by presence.

## Scenario Families

Use the smallest scenarios that discriminate the decision:

- normal responsibility path
- boundary or degenerate input
- most likely expected change
- dependency or platform change
- partial failure and remaining state
- workload or scale increase
- concurrent execution, cancellation, or restart
- diagnosis of an incorrect result
- recovery to a valid state
- caller misuse
- representative new-maintainer change

A scenario should state the trigger, operating condition, affected target, expected response, and observable yardstick. Do not evaluate every family by default.

## Indicators, Evidence, And Yardsticks

For each criterion, distinguish:

- `indicator`: a signal that may reveal quality, such as changed callers, duplicated branches, failure frequency, user confusion, or output artifacts
- `measurement`: the observed value, such as seven changed files, four failures, or 82% coverage
- `evidence`: the source that supports the observation, such as code, diff, runtime output, interaction record, or supplied result
- `yardstick`: the context-specific condition that makes the observation acceptable, conditional, or unacceptable

Example:

```text
Measurement: one policy addition changed seven files.
Context: the policy is intended to be internal to one algorithm owner.
Interpretation: unrelated callers and assembly code know the policy.
Judgment: the change-locality criterion is not met.
```

Never infer a universal threshold for LOC, complexity, coverage, latency, defects, or participant counts. A supplied threshold is authoritative only for its stated scope.

## Findings

Use this finding unit:

```text
criterion
observation or measurement
evidence location
interpretation
impact on the decision
counterexample or boundary condition
judgment
recommendation
confidence and limitation
```

Separate the existence of a problem from its cause. A qualitative evaluation may establish that a behavior is confusing or a change spreads too widely while leaving the causal mechanism unresolved for its analysis owner.

## Counterexamples And Tradeoffs

Seek one condition that could reverse or narrow each material judgment. A large cohesive numerical kernel can be preferable to fragmented abstractions; a simple screen-space interaction can be preferable to a context-sensitive method in a narrow 2D workflow. Preserve these conditions instead of forcing a universally positive or negative verdict.

## Stop Rule

Stop when:

- the evaluation contract is sufficient for the requested decision;
- every admitted criterion has an authorized origin, and no unaccepted proposal is used for judgment;
- every selected criterion has an indicator, evidence basis, and yardstick or is `Not assessable`;
- the material findings cover the decision without duplicate symptoms;
- one result-changing counterexample or tradeoff has been checked;
- remaining gaps and the next action are explicit.

Do not expand into implementation, exhaustive audit, generic standards coverage, or new validation infrastructure merely to strengthen the report label.
