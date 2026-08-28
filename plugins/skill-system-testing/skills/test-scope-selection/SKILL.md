---
name: test-scope-selection
description: Select the smallest real SUT boundary and multi-axis test profile that can expose a named material failure. Distinguish component, internal integration, system, external-system integration, and human acceptance without changing production architecture or treating mocks, APIs, automation, regression, or performance as test levels.
---

# Test Scope Selection

## Routing Card

- role: test_design_specialist
- intent_signature: test boundary, test level, SUT selection, unit versus integration versus system
- use_when: a named condition has materially competing SUT boundaries, observation boundaries, or test-level/profile classifications
- do_not_use_when: the boundary is already accepted, production module design is open, test scenarios/oracles are primary, or implementation is requested
- expected_inputs: material failure, accepted basis, current production path, candidate SUT boundaries, observable signal, and constraints
- expected_outputs: selected SUT/observation boundary, multi-axis test profile, preserved production boundary, and one falsifier
- context_targets:
  must_read:
    - named failure/condition, accepted basis, actual production path, and candidate observation points
    - `references/testing_strategy_contract.md`
  read_if_needed:
    - targeted callers, interface contracts, state/data flow, existing tests, and environment boundary
  do_not_load_by_default:
    - full repo, broad architecture maps, unrelated test inventory, or credentials
- risk_profile:
  reads: targeted owner/path/callers and existing test evidence
  writes: none
  tools: focused source/runtime inspection only
  sensitive_resources: production data and credentials denied without governing authority
- entry_scene: PREPARE

## Selection Model

Choose level from the largest real implementation boundary exercised, not speed, file count,
framework, API entry, automation, or use of test doubles.

| Boundary actually exercised | Level meaning |
|---|---|
| one accepted component/algorithm/module contract | component/unit |
| two or more real internal components and their data/control/state/time/error transfer | component integration |
| completed software system against system requirements | system |
| software plus independently deployed external system/device/service | system integration |
| declared stakeholder making an acceptance decision | acceptance/human judgment |

Record other axes separately: static/dynamic execution, functional or quality purpose, black-box,
white-box or experience-based technique, confirmation/regression relation, manual/automated or
exploratory mode, input/oracle strategy, environment fidelity, and horizon.

## Workflow

1. Bind the failure, authority, production entry-to-effect-to-output path, and earliest material
   signal that does not replace the real boundary.
2. Compare the smallest sufficient boundary with one broader and, when material, one narrower
   candidate. Account for diagnostic value, real dependency coverage, fixture/harness cost, and
   proof ceiling.
3. Preserve the production boundary. If testing requires a new module/seam or production
   ownership decision, return that gap to `analysis-boundary-design`; never create a mock-only seam.
4. Select one SUT and observation boundary. Describe test doubles only by the volatility/effect
   they replace and the evidence lost; a mock never defines the level or semantic authority.
5. Return the multi-axis profile and one falsifier that would show the boundary cannot expose the
   named failure.

## Output Contract

Return only applicable fields: condition/failure, authority, selected SUT, observation boundary,
largest real implementation boundary, multi-axis test profile, rejected candidates/costs,
test-double effect, representative path, falsifier, proof ceiling, and unresolved production
boundary gaps.
