---
name: test-evidence-review
description: Review a bounded test design, implementation, or result for false-green risk, circular or unauthorized oracles, surrogate paths, weak falsifiers, baseline/tolerance drift, missing diagnostics, and proof-ceiling inflation. Return evidence-linked findings only; do not implement, repair, rerun broadly, or declare product quality.
disable-model-invocation: true
---

# Test Evidence Review

## Routing Card

- role: testing_evidence_gate
- intent_signature: review tests, false green, test quality, oracle audit, mutation adequacy, test evidence review
- use_when: a named test design/implementation/result needs a bounded credibility review before its evidence is consumed
- do_not_use_when: test design or implementation is requested, a concrete failing test must be repaired, broad code review is primary, or no bounded artifact/condition exists
- expected_inputs: test design/contract, test assets/result, target snapshot/path, authority refs, diagnostics, falsifier, and claimed proof ceiling
- expected_outputs: prioritized evidence-linked findings, condition-level credibility/limits, and exact design/implementation/authority handoff
- context_targets:
  must_read:
    - bounded test contract/assets/result, claimed condition, authority, actual path, and `references/testing_strategy_contract.md`
  read_if_needed:
    - target production owner/path, expected-value computation, fixture/generator, baseline history, run artifacts, or semantic-mutant observation
    - `references/runtime_debugging_contract.md` when the evidence includes a debugger stop, crash/core/minidump, symbols, dynamic diagnostic, concurrency trace, graphics capture, or device-loss artifact
  do_not_load_by_default:
    - full repo/test suite/history, unrelated product conditions, raw production data, or credentials
- risk_profile:
  reads: bounded test and target path plus decisive artifacts
  writes: none
  tools: focused static inspection and one safe non-debugger falsifier/readback when already authorized; runtime-debugging evidence review uses existing artifacts/session metadata only
  sensitive_resources: deny credentials and minimize production data
- entry_scene: PREPARE

## Review Model

Select only applicable risks:

- authority: requirement/invariant/baseline owner exists and is not agent-invented;
- path: concrete SUT and representative production validation/composition path are exercised;
- oracle: expected result is independent enough and comparison/tolerance is not circular;
- scenario/data: positive and material negative/edge case plus valid provenance exist;
- environment/horizon: seed/clock/viewport/load/history match the claimed failure;
- discrimination: falsifier or semantic mutant demonstrates the test can fail for the targeted
  defect class;
- diagnostics: failure retains enough input/state/diff/trace/build identity to reproduce or narrow;
- runtime-debugging artifact: target/build/module/symbol/device/tool identity matches, capture scope
  and missing state are explicit, perturbation is preserved, and sensitive-data controls are present;
- proof ceiling: the reported claim stays within exercised condition/path/environment/state/horizon;
- maintenance: baseline, masks, retries, quarantine, and tolerance changes require named authority.

## Workflow

1. Pin test and target snapshots, claimed condition/proof ceiling, authority, actual path, and
   available artifacts. Separate direct facts, inferences, and unavailable runtime evidence.
2. Trace stimulus through the real SUT to the observed signal and expected-value path. Flag mocks,
   test-only semantic inputs, duplicate production logic, current-output goldens, or skipped
   validators that break the claimed evidence chain.
3. Inspect the strongest false-green case: default/empty/identity result, disabled work, reversed
   sign/order, widened tolerance, stale output, reduced horizon, or a domain-specific mutant. Do
   not create mutation infrastructure merely for the review.
4. Check whether a passing/failing result is scoped to its environment/horizon and whether absent
   evidence is honestly `unverified` rather than substituted by coverage, command exit, or mocks.
   For a runtime-debugging artifact, apply `references/runtime_debugging_contract.md`; reject
   filename-only or symbol-load-only identity, omitted-state assumptions, and root-cause claims that
   exceed the captured stop/dump/trace/replay/frame/device evidence. Do not issue continue/step,
   breakpoint/watchpoint, replay-query, shader-invocation, or other adaptive debugger commands; when
   another observation is required, return the exact Runtime Debugging handoff.
5. Return findings ordered by consequence. Name the current Test Design owner for semantic contract
   faults, Test Implementation owner for test-asset conformance, human authority for an open
   judgment, or a production-defect candidate for Coordinator/direct-owner classification. Test
   evidence alone never authorizes `workflow-bug-fix` or another production repair. Do not invoke
   any owner.

## Output Contract

Return target/test snapshots, reviewed conditions, authority/path/oracle findings, scenario and
environment findings, falsifier evidence, diagnostic/proof-ceiling findings, prioritized issues,
credible evidence scope, unavailable evidence, and exact handoff owner. Do not emit a global
quality score, release verdict, runtime root-cause verdict, successor, or repair action.
