# Harness Measurement Protocol (design reference)

Decide whether a harness gate (e.g. the observed-evidence Stop gate) actually
helps **before** defaulting it on. A mandatory gate can add context noise and
re-instruction churn that cancels or outweighs its benefit — the "harness
paradox". Measure that first; do not assume "gate on" equals "quality up".

This is a design reference only. It defines how a measurement would run; it does
not itself enable live instrumentation (deferred to a later 8.4.x point).

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

## On/off comparison (sketch)
- Per arm: session count, gate-fire rate, mean reverts, mean re-instructions.
- Key signal: `harness_paradox_delta = mean_reverts(on) - mean_reverts(off)`.
- Keep collecting while the delta is not yet comparable; sunset when the horizon
  is reached without a signal.

## Boundaries
- `eval/observed-runs/*` are **replay fixtures** for behavior evals, not a
  holdout outcome source. Do not repurpose them as measured outcomes.
- This measurement produces field evidence, not accepted knowledge: it never
  auto-promotes to the Wiki Bank or changes skill maturity on its own.
- Reuse the existing hash-chained hook event ledger as the event source; do not
  add a second always-on recorder.
