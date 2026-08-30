# Causal Diagnosis Method

Read this reference only when the concrete repair's cause is unclear, recurring, intermittent, high-risk, or not separated from credible alternatives. An obvious local failure with a direct reproduction does not need a hypothesis ceremony.

This method runs inside the existing `workflow-bug-fix` node. It creates no second owner, changes no graph state, and consumes no repair round until an intervention intended to alter the failure is made. When a supplied `debugging_result` or live/postmortem/dynamic/graphics artifact is material, also apply `references/runtime_debugging_contract.md` and only its matching selected file under `references/runtime-debugging/`; preserve debugging scope, identity checks, direct observations, session handoff, perturbations, causal status, and proof ceiling instead of reducing it to a symbolized stack.

## Bounded Diagnosis

1. Lock the material condition: observed result, trigger, expected result and its authority, reproducibility, and unresolved evidence gaps.
2. Trace the smallest actual path across entry, production owner, state/data flow, source selection, timing, environment, and one representative readback. For crash/runtime artifacts, establish exact target, binary/module, load-address, build, symbol/unwind, dump/capture scope, and instrumentation identity before causal interpretation.
3. If direct reproduction or a verified runtime observation isolates the cause, select it. Otherwise retain only two or three credible causes, state their differing predicted observations, and run the cheapest safe observation that separates them. Treat optimized-out values, omitted dump state, ambiguous unwind frames, and unsupported capture state as unavailable rather than inferred facts.
4. Record confirming and disconfirming evidence with scope. A diagnostic probe can test a prediction; an agent-authored test does not create the user or canonical contract.
5. Name a root cause only when the observation distinguishes it from credible alternatives. Otherwise keep `Unverified leading hypothesis` and name the next discriminator.
6. Return the causal result to the same workflow owner with the direct repair direction and original-signal verification target.

Static inspection can establish possible paths and contract mismatches. It cannot confirm runtime ordering, selected environment state, frequency, generated behavior, or actual output without corresponding observation. Mocks prove only their boundary. A dump is a selected postmortem snapshot, a trace or replay is historical only for recorded state, and debugger attachment or instrumentation can alter timing, schedule, allocation, layout, or device work.

## Integrity Rules

- Do not fabricate three hypotheses or a repair matrix for an obvious direct repro.
- For ambiguous, concurrent, intermittent, security-sensitive, or high-impact failures, keep predictions and refutations visible until one cause is discriminated.
- Source selection, migration, media/data transformation, adapters, and external boundaries require canonical-source identification plus selected/output readback.
- A nearby or lower-scope pass cannot override the original condition. Never weaken assertions, skip checks, widen mocks, add bypasses, or treat a silent legacy fallback as causal resolution.

Return only the applicable `root_cause` or `Unverified leading hypothesis`, decisive and disconfirming evidence, evidence scope, repair direction, original-signal verification target, and remaining discriminator. The enclosing `workflow-bug-fix` owns the assigned intervention and attempt result; `workflow-code-review` owns static review disposition, and the Coordinator owns Handoff state and final Known Bug registration in DAG mode.
