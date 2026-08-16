---
name: analysis-bug
description: Diagnose an unclear, recurring, or high-risk failure by discriminating credible causes on the actual path; use workflow-bug-fix when repair is the primary outcome.
---

# Analysis Bug

## Routing Card
- role: primary
- intent_signature:
  - root-cause analysis; deep debugging; recurring/unclear failure; 원인 분석
- use_when:
  - the user asks why a failure occurs, requests RCA, or a repair owner needs one uncertain cause resolved before editing.
- do_not_use_when:
  - direct repair (`workflow-bug-fix`), repeated same-signature recovery, known-cause implementation, algorithm/performance/design selection, or broad repository reporting is primary.
- expected_inputs:
  - observed and expected behavior, triggering condition, oracle/canonical source when relevant, repro status, and available evidence
- expected_outputs:
  - repro status, decisive and disconfirming evidence, one root cause or leading hypothesis, repair direction, verification target, and remaining gaps
- context_targets:
  must_read:
    - original symptom, material expected condition, and repro or explicit `Unverified` gap
  read_if_needed:
    - actual call/state/data/source-selection path, logs, tests, timing, environment, and output readback
  do_not_load_by_default:
    - full repo/memory, unrelated history/reports, raw production data, or credentials
- risk_profile:
  reads: targeted source, tests, logs/config, runtime state, and repro/readback evidence
  writes: none for diagnosis; implementation authority stays with its primary workflow
  tools: focused reproduction, tracing, measurement, and non-destructive probes
  sensitive_resources: deny credentials; redact external-service and production evidence
- entry_scene:
  - PREPARE

## Causal Diagnosis Loop
1. Lock the material condition: observed result, trigger, expected result and its authority, reproducibility, and any unresolved status.
2. Trace the smallest actual path across entry, production owner, state/data flow, source selection, timing, environment, and one representative readback.
3. If a direct reproduction already isolates the cause, select it. Otherwise keep two or three credible hypotheses, state their differing predictions, and run the cheapest safe observation that separates them.
4. Record confirming and disconfirming evidence with its scope. A diagnostic probe can test a prediction; an agent-authored test does not create the user or canonical contract.
5. Name one root cause only when the observation distinguishes it from credible alternatives. Otherwise report a leading hypothesis as `Unverified` and name the next discriminator.
6. Define the repair direction, owning implementation workflow, and check/readback for the original signal.

Static inspection can establish possible paths and contract mismatches; it cannot confirm runtime ordering, environment state, frequency, generated behavior, or selected output without corresponding observation. Mocks prove only their boundary.

## Evidence And Depth Rules
- For an obvious local failure with a direct repro, report the decisive cause; do not fabricate three hypotheses or a fix matrix.
- For ambiguous, intermittent, concurrent, security-sensitive, or high-impact failures, retain predictions and refutations until one cause is discriminated.
- Source selection, migrations, media/data transforms, adapters, and external boundaries need canonical-source identification and actual selected/output readback. A wrong selection can confirm the cause while the outcome remains open until post-repair same-path readback. Missing or mismatched required input fails closed; never treat silent legacy fallback as causal resolution.
- A nearby pass cannot override the original condition's `fail`, `needs_review`, `unverified`, or `blocked` state. Do not weaken assertions, skip checks, add bypasses, or widen mocks to remove the signal.

## Fix Boundary
- Diagnosis-only stops after the causal finding or scoped hypothesis, repair direction, and verification target; it does not write code.
- For RCA plus implementation, `workflow-bug-fix` remains the primary write owner and this skill supplies the causal decision. A direct fix routes there immediately; a repeated post-fix signature routes to `workflow-recovery`.
- Correct-behavior bottleneck analysis routes to `analysis-performance`, a boundary-only decision to `analysis-boundary-design`, and no-failure feature work to `workflow-implementation`.
- Compare repairs only when materially different choices remain after the cause is known; structural redesign belongs to its design owner.

## Output Contract
Lead with the root cause and decisive evidence, or explicitly say `Unverified leading hypothesis`. Add only applicable repro status, refuted alternatives, evidence scope, repair owner/direction, original-signal verification target, unresolved runtime/user conditions, and next discriminator. Do not turn a narrow RCA into a formal report.
