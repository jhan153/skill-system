---
name: analysis-codebase
description: "Generate one repo-wide integrated codebase report from static, runtime, security, and Git evidence, with architecture views, an actionable findings backlog, and explicit Unverified gaps. Use only when the user explicitly requests a codebase-wide report/artifact; do not use for point diagnosis, one design decision, candidate discovery, or ordinary review."
---

# Analysis Codebase

## Routing Card
- role: heavy_artifact_generator
- intent_signature:
  - explicit repo-wide integrated codebase report artifact
- use_when:
  - both repo-wide scope and an integrated report/artifact are explicit.
  - the requested artifact needs architecture, metrics, security, runtime, or Git evidence lanes.
- do_not_use_when:
  - the user wants a bug RCA, one module decision, ranked architecture candidates, short review, or direct implementation.
  - “architecture,” “analysis,” or “code review report” appears without explicit codebase-wide artifact intent.
- expected_inputs:
  - repo root, report scope, requested evidence lanes, commit range when relevant, and output directory
- expected_outputs:
  - one integrated Markdown report, architecture models, `findings.json`, and `quality-gate-result.json`
- context_targets:
  must_read:
    - explicit report request, repo policy, output/write scope, and compact tracked-source outline
  read_if_needed:
    - summarized collection artifacts and only the references mapped to the current stage
    - source paths selected by the evidence-sampling plan
  do_not_load_by_default:
    - raw full inventories, every source file, all reports/references, full memory, or point-analysis workflows
- risk_profile:
  reads:
    - READ_CODEBASE high
  writes:
    - WRITE_LOCAL_FS high, limited to the requested report directory
  tools:
    - CALL_PROCESS high for deterministic collectors and report generation
  sensitive_resources:
    - network normally no; credentials and secret files default deny
- entry_scene:
  - PREPARE

## Success Contract
- Produce one integrated report; do not split summary and detail into separate Markdown reports.
- Build report views from `evidence -> architecture model -> report` rather than from prose intuition.
- Tie every material finding to concrete `evidence_refs`, an evidence grade, impact, action, and validation path.
- Mark missing, blocked, or inference-only evidence `Unverified`.
- Report honest coverage and exclusions; repo-wide scope does not imply that every file was read by the model.

## Evidence Workflow
1. Record the repo root, tracked boundary, output directory, requested lanes, commit range, exclusions, and any authority boundary before collection.
2. Run the deterministic collector over that scope. Keep raw inventories and logs in artifacts; load compact summaries and selected rows.
3. Cover every material product/service/language/runtime group at inventory level, then sample an entrypoint-to-output path, internal and external boundaries, critical-behavior tests, multi-signal hotspots, and one low-signal control path where relevant.
4. Deepen a shortlisted claim through its caller, source, dependency/config, and relevant behavioral evidence. Expand only when evidence conflicts, a counterexample weakens the claim, a required view lacks support, or the sample can change the top backlog or gate.
5. Build architecture models from the collected evidence, generate the single report, and inspect the artifacts and gate rather than trusting process exit.

Maintain a compact coverage ledger of groups/strata, enumerated candidates versus inspected paths, selection reason, evidence refs/confidence, and excluded or blocked gaps. Absence from a sample or search is not proof of absence.

Stop when every material group and required view is evidenced or explicitly `Unverified`, findings meet the gate, one deliberate expansion of the weakest/highest-risk stratum no longer changes priority, and all required artifacts parse. If a new sample changes priority, deepen only that stratum; at a budget or permission boundary, report the remaining gap without claiming exhaustive coverage.

## Finding Gate
- Reference exact artifacts, commands, paths/lines, traces, tests, or Git ranges. Separate `observed`, `inferred`, and `recommended` statements.
- Promote a candidate only with an evidence grade and falsifiable validation path. Deduplicate symptoms with one root policy, owner, or dependency cause.
- Static topology, churn, complexity, coupling, imports, and tool silence select candidates; they do not prove runtime, deployment, security, or user impact. A static hotspot remains `verification-needed`, at most grade `B` and `medium` severity.
- A scanner may retain upstream severity for conservative triage, but remains grade `B`/`verification-needed` until applicability, reachability, or deployed exposure is confirmed.
- Every backlog item names the change, affected surface, expected impact, validation, and material rollback/containment.

## Semantic Comparison Selector
For a port, migration, legacy/new pair, or two implementations of one capability, read `references/semantic-comparison.md` before comparison. Pair the same capability, input/trigger, and oracle. Only paired behavioral result artifacts can establish `different` or `equivalent`; static, one-sided, or source-only evidence stays `Unverified` with the cheapest deciding check. Technology or internal-structure vocabulary is not a semantic delta.

## Artifact Ownership
After inventory and before model/report generation, read `reference.md`; it owns artifact layout, report section order, architecture/diagram rules, visualization requirements, and backlog columns. Then load only the resource needed at that decision point:
- `references/policy-default.json`: tool input and policy override
- `references/quality-gates.md`: gate interpretation or repair
- `references/schemas.md`: JSON generation or repair
- `references/review-checklists.md`: an explicitly requested manual lane
- `docs/document.md`: command or CI preparation

Prefer tool help, summarized artifacts, and targeted failure output over loading every reference or script.

## Completion and Handoff
- Check required architecture models, `findings.json`, `quality-gate-result.json`, and the single Markdown report; inspect gate reasons, top findings, ledger gaps, provenance/fallback, and entrypoint/scenario linkage.
- Collector/reporter exit zero proves artifact generation only, not coverage, evidence quality, an actionable report, or user success.
- Permission/tool failure remains `Unverified` in `notes/unverified.tsv`; rerun only that failed lane with identical inputs after approval. Do not fetch external data, inspect secrets, or write outside the approved report directory without separate authority.
- Until a compilation-aware C/C++ symbol/class/call index is collected, record that structural lane as `Not evidenced` and fail the quality gate; include/build hints are insufficient.
- Route a point bug to `analysis-bug`, one structural decision to `analysis-codebase-design`, a ranked opportunity scan to `analysis-architecture-deepening`, and code changes to an implementation workflow.
