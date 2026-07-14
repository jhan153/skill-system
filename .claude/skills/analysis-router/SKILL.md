---
name: analysis-router
description: "Route deep technical analysis to bug diagnosis, algorithm selection, one codebase design decision, architecture-deepening candidate discovery, domain modeling, performance analysis, or a two-stage hybrid. Use when the analysis owner is ambiguous; requested brevity or conclusion-first formatting does not make an otherwise-deep task light. Skip direct implementation, genuinely light Q&A, and repo-wide report artifacts."
---

# Analysis Router

## Routing Card
- role: router
- intent_signature:
  - deep technical analysis lane or analysis-family entry selection
- use_when:
  - choose a specialist for deep diagnosis or recommendation before work starts.
  - order two analysis stages when the second decision depends on the first result.
- do_not_use_when:
  - the user explicitly invokes a fitting specialist, requests direct implementation, or the underlying task is genuinely light Q&A with no competing interpretation, cause, design, or evidence-dependent decision.
  - the user explicitly requests a repo-wide integrated report artifact; route to `analysis-codebase`.
- expected_inputs:
  - user request and any supplied symptom, constraint, metric, or decision target
- expected_outputs:
  - `mode`, `owner`, `reason`, minimal `context_slice`, and an optional `next_gate`
- context_targets:
  must_read:
    - user request
    - only the selected specialist card
  read_if_needed:
    - user-supplied failure signal, constraints, or metric needed to break a tie
  do_not_load_by_default:
    - adjacent specialist cards
    - repo files, full source outlines, memory, prior reports, or codebase-intel artifacts
- risk_profile:
  reads:
    - user request only
  writes:
    - none
  tools:
    - none
  sensitive_resources:
    - network and credentials default deny
- entry_scene:
  - PREPARE

## Decision Table

| Dominant question | Mode and owner |
| --- | --- |
| Why is behavior broken, incorrect, or recurring? | `bug` -> `analysis-bug` |
| Which algorithm, model, retrieval strategy, or local approach fits the constraints? | `algorithm` -> `analysis-algorithm` |
| What boundary/interface/seam/adapter decision should one target adopt? | `codebase_design` -> `analysis-codebase-design` |
| Which structural improvement or deep-module candidate should come next? | `architecture_deepening` -> `analysis-architecture-deepening` |
| What concepts, identities, states, invariants, rules, or names form the domain? | `domain_modeling` -> `analysis-domain-modeling` |
| What measured latency, throughput, CPU, memory, query, rendering, startup, bundle, or complexity bottleneck dominates? | `performance` -> `analysis-performance` |
| Must a current failure be explained before a different approach can be chosen? | `hybrid` -> at most two specialists, serially |
| None of the above | `out-of-scope` -> return to the task scheduler |

## Precedence and Mixed Requests
1. Honor an explicit fitting specialist invocation without loading alternatives.
2. Apply the heavy-artifact gate first: choose `analysis-codebase` only when both repo-wide scope and integrated report/artifact intent are explicit. “Architecture,” “review,” or “analyze” alone is insufficient.
3. Choose by the user's primary question, not by every noun in the prompt:
   - incorrect behavior -> `bug`; an SLO or resource target with correct behavior -> `performance`.
   - business meaning/invariants -> `domain_modeling`; code ownership/dependency surface -> `codebase_design`.
   - one selected boundary -> `codebase_design`; ranked opportunity scan -> `architecture_deepening`.
4. Use `hybrid` only when stage two cannot be framed until stage one resolves evidence. Run stage one, emit its decision evidence, then load one second specialist. Do not fan out parallel analyses.
5. When implementation is requested, let the implementation workflow own writes. Attach one narrow analysis owner only if a root cause or design choice remains unresolved.
6. Treat formal response formatting separately from repo-wide analysis; report wording alone does not activate `analysis-codebase`.

## Context Budget and Stop Rule
- Make the route from the request alone whenever possible; routing itself must not inspect the repository.
- Load one specialist card after selection. For `hybrid`, delay loading the second card until its input gate is known.
- Prefer the narrower owner. If two routes remain plausible, state one scope assumption and choose; ask only when the choice changes the deliverable, write boundary, or validation path.
- Stop routing as soon as `mode`, `owner`, `context_slice`, and optional `next_gate` are fixed. Do not restate every rejected mode.
- Never recover ambiguity by loading all skills, docs, memory, or reports.

## Output Contract
- If the route is user-visible, state the selected mode and owner in the first sentence.
- Keep rationale to the decisive signal and any material assumption.
- Hand the answer to the selected specialist; do not expose router internals unless requested.
- Mark missing downstream evidence `Unverified` rather than expanding context during routing.
