# Semantic Contract Comparison

Use this protocol only for a port, migration, legacy/new pair, or two implementations intended to provide the same capability. Do not activate it for ordinary multi-language repositories.

## Comparison Unit

Compare one tuple at a time:

`capability + same input/trigger -> decision/state -> external effect -> output/error`

Pair entrypoints and test fixtures before inspecting implementation details. Give each valid pair one `pair_key` that identifies the shared capability, input fixture, and oracle. If the two sides do not share those things, set `comparable: false`, record the reason, and stop.

## Material Dimensions

Admit only caller/user-observable dimensions:

- `output`: value, shape, ordering, rendering result, or response
- `state`: transition, persistence, invariant, or lifecycle result
- `error`: status, exception/result mapping, recovery, retry, or rollback
- `side_effect`: file, database, message, network, notification, or external mutation
- `ordering`: event/callback/commit ordering when externally meaningful
- `timing`: timeout, scheduling, latency budget, or debounce behavior
- `precision`: rounding, tolerance, units, numeric stability, or truncation
- `permission`: authentication, authorization, ownership, or visibility result

Treat `framework`, `language`, `toolkit`, `runtime`, `platform`, `library`, `dependency`, `build_system`, `architecture`, `type`, `symbol`, `file_layout`, and internal `control_flow` as implementation-only. Collapse them into an excluded count; do not list them as semantic gaps.

## Evidence Gate

Use these statuses:

- `different`: the same scenario has paired runtime, trace, executed test-result, contract-test-result, characterization-test-result, or captured manual-observation artifacts and an observable delta.
- `equivalent`: paired behavioral evidence observes the same result. Similar code or names are insufficient.
- `intentional`: paired behavioral evidence shows a documented, accepted delta; retain the delta but do not create a defect finding.
- `Unverified`: evidence is static, one-sided, stale, missing, or lacks a shared oracle. State the cheapest paired test that would decide it.
- `implementation-only`: the row describes only technology vocabulary; exclude it from the semantic table and backlog.
- `not-comparable`: the records do not implement the same capability or cannot share an input fixture and oracle; exclude them rather than inventing a delta.

Static source or a test source location may select a comparison candidate and help design a fixture. Neither establishes `different` or `equivalent`. Two behavioral-looking records without the same `pair_key` and result artifacts remain `Unverified`.

`manual_observation` counts as behavioral evidence only when each side has an `evidence_ref` to a captured observation note or transcript that states the shared fixture, observed result, and oracle. An uncited prose assertion remains `Unverified`; capture it under `artifacts/manual/` before using it as paired evidence.

Runtime/trace/test-result refs must resolve to existing result files under `artifacts/{dynamic,runtime,results,test-results,tests,traces}/`. Reject `artifacts/static/`, source-code suffixes, absolute paths, traversal (`..`), and missing files as behavioral evidence.

## Artifact Contract

Write optional comparison input to `artifacts/manual/contract-comparisons.json`:

```json
{
  "comparisons": [
    {
      "pair_key": "document-close|modified-document-cancel|window-and-dirty-state",
      "scenario": "close a modified document",
      "dimension": "state",
      "severity": "medium",
      "quality_attribute": "correctness",
      "baseline": {
        "value": "prompts and keeps the document open on cancel",
        "evidence_refs": ["artifacts/runtime/baseline-close.json"],
        "evidence_kind": "runtime"
      },
      "candidate": {
        "value": "closes without a prompt and discards changes",
        "evidence_refs": ["artifacts/runtime/candidate-close.json"],
        "evidence_kind": "runtime"
      },
      "verification": "replay the same modified-document fixture and assert window/state outcome",
      "related_files": ["desktop/document-close.cpp", "service/DocumentClose.cs"],
      "comparable": true
    }
  ]
}
```

For an accepted delta, add `intentional: true` and an `intentionality_ref` to the approving requirement or decision. Without that reference, the observed delta remains a finding candidate.

The reporter filters implementation-only, invalid-dimension, and not-comparable rows; folds confirmed equivalence into counts; displays material/Unverified rows; adds invalid or missing paired evidence to the Unverified ledger; and promotes confirmed non-intentional differences into `findings.json` and the backlog.

## Output Rule

Use this table only when at least one comparison record exists:

| Capability / Input / Pair Key | Dimension | Baseline Observable | Candidate Observable | Semantic Delta / Status | Paired Evidence Kind + Ref | Validation |
| --- | --- | --- | --- | --- | --- | --- |

Expose the `pair_key` plus each side's evidence kind and ref so a reviewer can audit pairing and asymmetry. Never write only `다르다`, `uses Qt`, `uses .NET`, `different type`, or `different control flow`. State the observable before/after delta and its user/system impact, or state `Unverified` with the deciding test.

Start with one critical flow per implementation pair. Expand only when a verified or unresolved delta can change priority, migration readiness, or release gating.
