---
name: test-replay-corpus
description: Design capture, recording, replay, and versioned reality-corpus contracts that preserve production-valid inputs, state history, provenance, schema/build identity, sanitization, minimization, and diagnostic reproduction. Replay is stimulation evidence only and never becomes correctness without a separate oracle.
---

# Test Replay Corpus

## Routing Card

- role: test_design_specialist
- intent_signature: replay test, recording test, captured fixtures, reality corpus, deterministic reproduction
- use_when: a named failure or regression needs production-path capture/replay or a versioned representative corpus
- do_not_use_when: synthetic data is sufficient and authoritative, exact oracle selection is primary, raw production capture is unauthorized, or implementation alone is requested
- expected_inputs: failure/condition, production capture point, loader/validator path, state history, privacy boundary, oracle ref, schema/build identity, and recurrence
- expected_outputs: capture/replay/corpus contract, provenance schema, sanitization/minimization rules, representativeness limits, and proof ceiling
- context_targets:
  must_read:
    - named condition, actual capture-to-replay path, data authority/privacy, oracle ref, and `references/testing_strategy_contract.md`
  read_if_needed:
    - production schemas/loaders/validators, representative failures, build/version metadata, storage limits, or existing fixture conventions
  do_not_load_by_default:
    - raw production datasets, credentials, full telemetry history, or unrelated corpus files
- risk_profile:
  reads: authorized schema/path metadata and minimum representative samples
  writes: none; `workflow-test-implementation` owns requested capture/replay/corpus assets
  tools: safe metadata/readback inspection only
  sensitive_resources: default deny raw private data; require minimization, sanitization, retention, and access ownership
- entry_scene: PREPARE

## Workflow

1. Bind the failure, real capture boundary, replay entry, production loader/validator/canonicalizer,
   required state history, oracle, and diagnostic objective.
2. Specify case identity and provenance: source category, schema version, producer/capture version,
   build/config, seed/clock, environment, sanitization/minimization history, known properties,
   expected success/failure scope, and related defect/decision refs.
3. Keep reality, generated-valid, invalid, reference, and regression cases distinct. Production
   validation proves schema/invariant admission, not field representativeness.
4. Define deterministic controls only where exact replay requires them. Preserve meaningful
   variability as data, bounds, distributions, or state history instead of masking it to Green.
5. Define capture consent/access, redaction, retention, portability, schema migration, corruption,
   and unavailable-case behavior. Never persist secrets or developer-machine paths.
6. Return the bounded implementation handoff and proof ceiling: replay shows repeatable
   stimulation/observation for the recorded case; correctness requires its separate oracle.

## Output Contract

Return condition, capture point, replay path, production validation path, case taxonomy,
provenance/identity schema, state/seed/environment controls, sanitization/minimization/retention,
oracle ref, diagnostics, representativeness limits, implementation handoff, proof ceiling, and
unresolved access/testability gaps.
