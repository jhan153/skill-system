# Testing Strategy Contract

This contract defines the shared meaning and judgment rules for selecting software tests and
interpreting their evidence. It does not prescribe a universal test suite.

## Outcome

Choose the smallest test or direct observation that can expose one material failure on its
representative actual path, then limit every result claim to the condition and horizon directly
observed.

Use this model:

`testing strategy = failure risk × representative path × observable signal × execution horizon × proof ceiling`

A method name, coverage percentage, green command, or large test inventory is never the goal.
Testing exists to produce decision-relevant evidence about a material condition.

## Core Invariants

1. **Bind the failure before the method.** Name the user, system, data, performance, security,
   accessibility, release, or maintenance failure that matters before selecting a test type.
2. **Use the representative actual path.** Prefer the production entry, state/data flow, effect,
   and output that can exhibit the failure. A helper, mock, or surrogate path cannot replace it.
3. **Observe a material signal.** Name the visible output, state invariant, error, latency,
   resource measure, trace, dump, or side effect that distinguishes success from failure.
4. **Match the execution horizon.** A point check, one scenario, repeated sequence, accumulated
   state run, and direct human evaluation answer different questions. Do not substitute one for
   another.
5. **Establish testability prerequisites.** Control only the inputs, clocks, seeds, environments,
   baselines, and instrumentation necessary to make the selected signal comparable or
   diagnosable.
6. **Preserve diagnostic evidence.** A failing result should retain the smallest artifact needed
   to reproduce or narrow it, such as input, state, coordinates, screenshot diff, trace, profile,
   log, dump, build identity, or selected-source readback.
7. **Respect the proof ceiling.** A pass or failure remains local to the exercised condition,
   path, environment, state, and horizon.
8. **Combine automation and exploration by role.** Automate stable recurring checks; use human or
   bounded exploratory work for unknown paths, qualitative judgment, and unmodeled interactions.
   Neither lane proves the other.
9. **Compare evidence cost with failure cost.** Add or retain a test only when its discriminating
   value and recurrence justify implementation, runtime, triage, fixture, and maintenance cost.

## Selection Model

1. State the positive condition and one material negative, edge, or disconfirming case.
2. Bind each condition to its authority: user requirement, canonical specification/data,
   established production behavior, external contract, or explicit user judgment.
3. Trace the representative caller/input-to-effect/output path and identify where the failure can
   first be observed without replacing the real boundary.
4. Choose one evidence surface that most directly discriminates the condition. Add another lane
   only when it answers a materially different question.
5. Record the environment and horizon needed for comparability, including relevant input size,
   viewport, seed, clock, load, repetition count, duration, or state history.

## Failure-To-Method Selection

| Material failure | Representative signal | Suitable evidence surface | Necessary testability condition | Useful diagnostic artifact |
| --- | --- | --- | --- | --- |
| deterministic calculation or transformation error | output differs from authoritative expected value | focused unit or data-driven test | stable inputs and explicit invariant | failing case and expected/actual values |
| integration or protocol mismatch | representative request, event, state transition, or side effect fails | integration test or actual boundary readback | canonical source and real contract boundary | request/response, state transition, selected-source readback |
| user workflow failure | user-observable scenario cannot complete or produces the wrong result | UI-driven or end-to-end observation | representative route, state, and environment | action sequence, visible output, error, trace |
| rendered visual regression | pixels, hierarchy, framing, clipping, or overflow differs at a named state | screenshot comparison or rendered visual inspection | pinned state, viewport, assets, fonts, and intentional dynamic regions | baseline/current image and scoped diff |
| unexpected navigation or state-space trap | execution reaches an invalid or inescapable state | bounded exploratory, model-based, property, fuzz, or seeded randomized run | reproducible input/seed and state capture | seed, path, coordinates, minimized failing input |
| latency, throughput, CPU, memory, query, rendering, startup, or bundle regression | comparable metric crosses a threshold or baseline | representative performance measurement or profile | same workload, environment, correctness conditions, and metric | profile, trace, query plan, heatmap, before/after measurement |
| accumulated state, leak, fragmentation, or endurance failure | invariant drifts or the process fails after repetition/time | sequence, soak, stress, or long-running observation | relevant duration/repetition, stable workload, instrumentation | invariant history, dump, trace, build and elapsed identity |
| release, migration, or selected-version risk | canonical state or representative integration differs from required contract | structural readback plus actual-path smoke/integration evidence | authoritative target and selected runtime state | manifest/lockfile/schema diff and actual selected-path readback |
| accessibility interaction or semantic failure | rendered role, name, focus, keyboard, measurement, or reflow condition fails | scoped DOM/tree, interaction, screenshot, or measurement evidence | rendered target and named criterion/state | direct tree/DOM result, interaction trace, measurement, screenshot |
| qualitative acceptance uncertainty | usefulness, feel, acceptance, or business choice requires subjective judgment | direct human evaluation | clear judgment unit and acceptance criteria | recorded decision and remaining uncertainty |

Choose the row from the failure and signal, not from repository fashion or available tooling. A
single task may need more than one row only when its material conditions are genuinely distinct.

## Evidence And Proof Ceilings

| Evidence | Directly supports | Does not support by itself |
| --- | --- | --- |
| unit or data-driven test | encoded examples or properties for the tested unit | integration, user workflow, performance, or product quality |
| mock, fake, stub, fixture, or agent-authored harness | the encoded surrogate boundary and authored cases | independent semantic truth or the real external/production boundary |
| build, typecheck, lint, or static scan | its structural or rule contract | runtime behavior, user-visible result, or complete correctness |
| integration test | exercised component/boundary interaction | unexercised integrations, UI behavior, or long-running stability |
| UI or end-to-end scenario | the named scenario in the observed state and environment | unvisited paths, complete state-space coverage, or unrelated quality attributes |
| screenshot comparison | visible pixels and framing at the named viewport/state | interaction, semantics, accessibility, responsive completeness, or business correctness |
| profile or performance measurement | the named metric under the recorded workload/environment | different environments, workloads, correctness, or user population |
| soak or stress result | observed behavior during the named duration, repetition, state, and load | longer horizons, different histories, or failure absence in general |
| manual or exploratory observation | the states and judgments actually exercised by the named observer | systematic coverage, repeatability, or automation readiness |
| coverage metric | execution of the counted code/branch/requirement mapping | assertion quality, semantic correctness, representative usage, or product readiness |
| canonical input and actual-path readback | selected source and observed output for the traced path | unrelated consumers, environments, or unobserved side effects |

When evidence conflicts, prefer the source and observation closest to the material condition while
preserving the contradiction. Never weaken a condition, widen a mock, skip a check, replace the
canonical source, or add a lower-quality fallback to manufacture a pass.

## Automation, Exploration, And Determinism

- Automate when the condition is stable, recurring, mechanically observable, and worth its
  maintenance and triage cost.
- Use deterministic control when exact comparison is the oracle. Pin only the relevant seed,
  clock, frame/update progression, viewport, data, assets, environment, or load.
- Do not remove meaningful production variability merely to make a test green. If variability is
  part of the risk, test or observe its distribution, bounds, invariants, and failure artifacts.
- Use bounded exploration when the important path is not fully enumerable or known. Preserve the
  seed, state history, or observer notes needed to reproduce a finding.
- Qualitative product acceptance requires direct human judgment. Automated and agent evidence may
  prepare that judgment but cannot replace it.

## Discriminating Examples

- **Positive:** For a pure tax calculation with an authoritative table, use focused data-driven
  cases for ordinary, boundary, and invalid inputs. Do not add an end-to-end browser run unless a
  separate UI/integration condition exists.
- **Positive:** For a memory increase after repeated session entry/exit, bind the expected memory
  invariant, run the representative sequence for the relevant horizon, and preserve the dump or
  allocation trace. A one-shot unit pass is not competing evidence.
- **Edge:** For a visual diff with intended animation or random particles, pin or mask only the
  non-semantic variability needed for comparison. If the variability itself matters, inspect its
  bounds instead of forcing identical pixels.
- **Negative:** Do not treat 100% coverage, a green mock suite, or one successful end-to-end path
  as proof of software quality. Report only the encoded or observed scope.
- **Negative:** Do not add unit tests merely because a broader user-path failure exists. Select the
  unit level only when it can discriminate the evidenced cause or protect a stable invariant.
