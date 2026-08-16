# Browser-Openable Logic Prototype

Use this artifact when a decision depends on exercising rules, state changes, legal actions, or domain feedback and the decision owner should not need developer tooling.

## Delivery Contract

Produce exactly one `.html` file that opens from the filesystem in a current browser. Inline the markup, styling, scripts, fixtures, and labels. The artifact must not depend on package installation, compilation, a local server, a CDN, remote fonts, analytics, or network access.

The page answers one visible prototype question and identifies its proof ceiling. If the target environment prevents a browser-openable file, report the conflict; a CLI or source listing does not satisfy this delivery contract.

## Internal Shape

Separate two responsibilities inside the file:

- **Rule model:** deterministic functions, reducer, state machine, or small stateful module with explicit inputs, results, rejected operations, and invariants. It cannot read or modify the DOM.
- **Observation adapter:** event handlers and rendering that translate page controls into model inputs and model results into human-readable output. It cannot reimplement domain rules.

Use in-memory state and fixed representative fixtures. Stub databases, accounts, files, services, authentication, and persistence unless one is the explicit question and the stub itself is sufficient to discriminate the decision.

## Required Observation Surface

The page must make the decision observable without source inspection:

1. State the question, the choice it informs, and what the prototype cannot establish.
2. Show the current relevant state with domain labels, plus the last accepted or rejected operation and its reason.
3. Provide direct controls for every operation needed to explore the question.
4. Provide resettable scenario presets for a normal sequence, one material edge, and one invalid or counterexample sequence.
5. Keep an action/result trace that the decision owner can copy into feedback when useful.

Use semantic controls, visible focus, readable spacing, and restrained presentation. Visual design exists to make state and consequences legible; it is not a second design exploration.

## Verification And Evidence

Open the exact file directly. Exercise every preset and at least one unscripted sequence. Repeat one fixture to confirm deterministic output, and verify that rejected operations remain visible rather than disappearing or throwing an opaque error.

Record:

- prototype question and absolute artifact path;
- direct-open instruction;
- fixture, operations, resulting state, and invariant outcome;
- decisive observation and counterevidence;
- `selected | supported | contradicted | inconclusive`;
- proof ceiling and retention trigger.

A browser smoke check proves only that the local artifact and exercised controls work. A user-owned judgment remains `user-verification-needed` until the decision owner observes it. Keep the page runnable until that point, and never ship the observation adapter as production UI. A rule model may move forward only after production ownership, API, failure policy, and actual-path validation are selected.

## Rejection Conditions

- More than one output file or any required network/build/server step.
- Domain rules duplicated in click handlers or rendering code.
- Raw JSON as the only explanation of state.
- Real external mutation or persistence outside the explicit prototype question.
- General framework work, broad test infrastructure, or production hardening.
- A claim that loading the file proves usability, accessibility, integration behavior, or release readiness.
