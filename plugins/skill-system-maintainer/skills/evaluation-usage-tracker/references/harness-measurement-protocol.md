# Harness Measurement Protocol (design reference)

Decide whether a harness gate (e.g. the observed-evidence Stop gate) actually
helps **before** defaulting it on. A mandatory gate can add context noise and
re-instruction churn that cancels or outweighs its benefit — the "harness
paradox". Measure that first; do not assume "gate on" equals "quality up".

This is implemented. Holdout assignment and event tagging run in the hook
adapters (opt-in via `SKILL_SYSTEM_HARNESS_MEASUREMENT=1` with the strict gate
enabled); `.codex/tools/analyze_harness_measurement.py` aggregates the tagged
`turn_finalize` events read-only. Automated outcome collection beyond gate
firing / finalize status (reverts, re-instructions) still needs a host-specific
transcript/git collector and is a follow-up.

## Principles
- **Out-of-band only.** Labels and metrics are recorded after a session ends
  (via the existing hook event ledger and transcript review), never injected
  into model context. Measurement must not change the behavior it measures.
- **Holdout, model-blind.** Split sessions deterministically into gate-ON
  (treatment) and gate-OFF (baseline) by hashing a stable session id. The arm
  assignment is never surfaced to the model.
- **Post-session outcomes.** Collect outcome signals after the fact: reverted
  edits, user re-instructions, rework frequency, wall time, tool calls, failed
  verifications, and post-session defect discovery.
- **Sunset.** If a fixed number of sessions accumulates with no comparable
  on/off signal, recommend removing the instrumentation rather than keeping a
  gate whose benefit was never demonstrated.

## Outcome ledger (out-of-band, metadata only)
```yaml
- session_id_hash:            # stable hash; raw id never stored
  holdout_arm: on | off
  gate_fired: true | false
  task_mode: quick | normal | deep
  reverts:                    # count
  reinstructions:             # count
  failed_verifications:       # count
  wall_time_s:
  tool_calls:
  post_session_defect: true | false
```

## On/off comparison (implemented)
- Per arm: `sessions`, `finalizes`, `would_fire_rate`, `block_rate`, `finalize_fail_rate`.
- Key signal: `harness_paradox_fail_delta = finalize_fail_rate(on) - finalize_fail_rate(off)`.
  Negative = the gate reduces failures; ~0 = no effect; positive = the gate may be adding friction.
- `mean_reverts` / `mean_reinstructions` need the outcome collector (follow-up).
- Keep collecting until both arms have data; sunset at the horizon without a signal.

## Run it
- Enable (both runtimes): `SKILL_SYSTEM_AGENT_OUTPUT_GATE=strict SKILL_SYSTEM_HARNESS_MEASUREMENT=1`.
- Adapters tag each `turn_finalize` event with `holdout_arm` (deterministic 80/20 by session id), `would_fire`, and `did_block`; the off arm records `would_fire` but never blocks (gate-off baseline).
- Aggregate: `python3 .codex/tools/analyze_harness_measurement.py [--ledger PATH]`.

## Boundaries
- `eval/observed-runs/*` are **replay fixtures** for behavior evals, not a
  holdout outcome source. Do not repurpose them as measured outcomes.
- This measurement produces field evidence, not accepted knowledge: it never
  auto-promotes to the Wiki Bank or changes skill maturity on its own.
- Reuse the existing hash-chained hook event ledger as the event source; do not
  add a second always-on recorder.
