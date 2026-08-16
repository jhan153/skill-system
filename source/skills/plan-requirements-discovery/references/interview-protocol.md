# Requirements Interview Protocol

Use this reference when missing requirements form more than a single clarification.

## Build The Question Set

1. List each decision that can change scope, acceptance, failure behavior, ownership, data handling, or launch conditions.
2. For each decision, list the prior decisions and fact checks required before its question and options are valid.
3. Resolve safe repository, contract, configuration, or external facts through the narrowest admitted source. The user is not a substitute for discoverable evidence.
4. Derive the ready-question set from decisions whose prerequisites are settled.
5. Order the ready set by blocking effect, reversibility, cost of a wrong assumption, and downstream fan-out.

## Round Construction

- Ask no more than three ready questions in one round.
- Questions in the same round must remain valid regardless of how the others are answered.
- Number multi-question rounds and keep one decision per number.
- State the consequence of the decision in one sentence.
- Offer exclusive options only when they clarify the choice; put the recommendation first and state its tradeoff.
- Use a single-question round for dependency-bearing, irreversible, high-stakes, explicitly paced, or host-limited decisions.

After the user responds, record only changed ledger entries, invalidate questions whose premises changed, and derive the next ready set. Never repeat a settled decision merely to preserve an old script.

## Default Decision Order

1. Target outcome and observable success.
2. Actor or accountable owner.
3. Scope, exclusions, and deferrals.
4. Domain rules and vocabulary.
5. Failure, cancellation, and edge behavior.
6. Data, permissions, privacy, and external systems.
7. Runtime, validation, and launch constraints.

## Stop Conditions

Stop when all applicable decisions are recorded, remaining uncertainty has an explicit owner and impact, the user stops, or the next artifact owner is clear. A completed interview is input to `plan-requirements-brief`; it is not itself an accepted contract or implementation approval.
