---
name: workflow-bug-fix
description: Fix a concrete test, build, runtime, regression, or user-visible failure by changing its production cause and verifying the original condition on the actual path. When the same failure fingerprint survives an intervention, hand the stuck slice to workflow-recovery.
---

# Workflow Bug Fix

## Routing Card
- role: primary
- intent_signature:
  - bug/failing-test/build/runtime/regression fix; broken behavior repair
- use_when:
  - the user requests a code fix for an observed or reproducible failure and expects verification afterward.
- do_not_use_when:
  - diagnosis-only (`analysis-bug`), repeated same-signature recovery (`workflow-recovery`), ordinary feature work, or validation-only work.
- expected_inputs:
  - observed symptom/original signal, material expected condition, available oracle or canonical source, and reproduction context
- expected_outputs:
  - reproduced condition or explicit gap, one evidenced cause, production change, actual-path verification/readback, scoped status, and remaining uncertainty
- context_targets:
  must_read:
    - original failure, material expected condition, implicated production owner/path, and repository instructions
  read_if_needed:
    - canonical input/source, caller/state flow, boundary readback, existing tests, config/manifests, and validation contract
    - `workflow-recovery` after the same material fingerprint survives an intervention
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated history, raw production data, or credentials
- risk_profile:
  reads: failure output, production source/callers/state, tests/config, and validation/readback evidence
  writes: one causal code scope at a time
  tools: reproduction, focused diagnostics, actual-path readback, and narrow validation
  sensitive_resources: deny credentials; external or destructive reproduction needs explicit boundary review
- entry_scene:
  - PREPARE

## Completion And Evidence
- Bind each material condition to its authority and evidence. A user/canonical contract or production observation can define expected behavior; an agent-authored test can preserve that expectation but is not an independent oracle.
- Fix and read back the actual production path. Structural checks, command exit, mocks, interfaces, and test passes prove only what they directly cover; they cannot establish a broader semantic result.
- A required `fail`, `needs_review`, blocked, or unverified condition stays unresolved until evidence from that same condition resolves it. Do not report complete or agent-verified from a narrower pass.
- Source selection, migration, media/data transformation, adapters, and external boundaries require canonical-input identification plus actual selected/output readback. Missing or mismatched canonical input fails closed; never substitute legacy data silently.

## Workflow
1. Lock the observed and expected result, current reproducibility, material conditions, and oracle origin. If reproduction is unavailable, mark that gap and inspect only evidence that can discriminate a cause.
2. Trace the actual entry, production owner, state/data flow, canonical source when relevant, and one representative boundary/readback. Use the existing failure signal as the feedback loop; do not create a speculative test before the contract is known.
3. Select one cause supported by the path and one smallest coherent production fix. Keep source/policy/fallback decisions at their domain owner and translation at adapters; keep cause and effect adjacent unless an existing boundary requires otherwise. If a boundary decision is needed, `workflow-bug-fix` remains the primary repair owner and `analysis-boundary-design` supports that decision before the edit.
4. Apply the production change before optional test scaffolding. Never weaken assertions, skip checks, widen mocks, add bypasses, or replace a required failure with a plausible fallback.
5. Rerun the original signal and read back the actual affected path/output. Record condition-level pass/fail/needs review/unverified and evidence scope.
6. Add or update regression coverage only when the expected contract is established and the check would remember the observed bug; it does not replace production readback.
7. If the same failure signature repeats after this causal change, stop changing guesses and hand off to `workflow-recovery`.

## Output Contract
Return only needed sections: material failure/condition, oracle and reproduction, production cause/owner, changed artifacts, actual-path verification/readback, regression coverage scope, unresolved conditions, and next step. Do not use a task-level label to hide condition evidence.

## Cross-Skill Boundaries
- `analysis-bug` owns diagnosis-only RCA and broad root-cause selection.
- `workflow-recovery` owns repeated same-signature failure after attempted fixes.
- `workflow-implementation` owns ordinary feature work and refactoring without a current failure.
- `workflow-validation` owns validation-only planning or revised check selection when installed or explicitly requested.
- `analysis-boundary-design` supplies deep module, seam, and boundary decisions when needed; it does not replace `workflow-bug-fix` as owner of the concrete repair.
