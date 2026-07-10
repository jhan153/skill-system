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

## Scope Gate
Before collection:
1. Record repo root, tracked-file boundary, output directory, requested evidence lanes, commit range, and exclusions.
2. Identify material product/service/language/runtime groups from manifests and the source outline.
3. Record safe defaults instead of asking when they do not change the deliverable or risk boundary.
4. Stop or request authority if collection would access credentials, external systems, destructive commands, or writes outside the report directory.

## Progressive Evidence Plan

### Stage A: Inventory Without Context Flooding
- Run the deterministic collector over the approved tracked scope.
- Keep raw file lists, tool logs, and complete metric tables in artifacts; load only compact summaries and selected rows.
- Use `top-n` outputs as a candidate pool, not as a mandate to read every candidate.
- Separate generated/vendor/resource files before deriving churn, ownership, or architecture conclusions.

### Stage B: Stratified Sampling
Cover each material codebase group at inventory level, then sample relevant strata:
- an entrypoint and representative end-to-end workflow
- internal module/dependency boundaries
- external I/O, auth/security, storage, queue, or runtime boundaries
- tests that encode critical behavior
- hotspots where multiple signals intersect, such as churn + complexity + centrality
- one low-signal control path to challenge hotspot-only bias

Start with one representative path per relevant stratum/group. Expand only when:
- another usage shape differs materially.
- evidence conflicts or a counterexample weakens a claim.
- a required architecture/report view remains unsupported.
- the new sample could change a high-priority finding or quality gate.

### Stage C: Deepen Shortlisted Claims
- Inspect complete claim paths—source, caller, dependency/config, and relevant test—rather than isolated snippets.
- Use runtime, trace, security, and Git evidence only within the approved/requested lanes.
- Deduplicate symptoms that share one root policy, ownership, or dependency cause.
- Promote a candidate to a finding only after recording evidence quality and a falsifiable validation step.

## Coverage Ledger
Maintain a compact ledger with:
- codebase group and evidence stratum
- candidates enumerated vs paths inspected
- sample-selection reason
- evidence artifact/path and confidence
- excluded, unsampled, failed, or permission-blocked gaps

Use the ledger to qualify claims such as “no issue found.” Absence from a sample or grep result is not proof of absence.

## Evidence and Finding Rules
- Reference exact artifact IDs, commands, paths/lines, traces, tests, or Git ranges; avoid unsupported summaries.
- Separate `observed` facts, `inferred` explanations, and `recommended` changes.
- Triangulate high-impact findings across independent signal types when feasible. If only one source exists, state that limitation in the evidence grade.
- Do not infer runtime behavior solely from static calls, deployment behavior from file names, or security from tool silence.
- Treat churn, complexity, coupling, imports, file extensions, frameworks, and topology as candidate-selection evidence only. Those static hotspot candidates remain `verification-needed`, cannot receive grade `A`, and cannot exceed `medium` severity until behavioral impact is observed.
- A security scanner may retain its upstream severity for conservative triage, but a single static scan remains grade `B`/`verification-needed` until rule applicability, reachability, or deployed-version exposure is confirmed.
- Write one root-cause finding instead of repeating the same symptom across chapters.
- Make each backlog item name the change, affected surface, expected impact, validation, and rollback/containment where material.

## Semantic Comparison Gate
Activate this gate only for a port, migration, legacy/new pair, or two implementations of the same capability. Read `references/semantic-comparison.md` before writing any parity or end-to-end difference section.

- Pair one capability and the same input/trigger before comparing implementations.
- Call a difference material only when a caller/user can observe a delta in output, state/persistence, error/recovery, external side effect, ordering/timing, precision/tolerance, or permission behavior.
- Treat language, framework/toolkit, runtime/platform stack, library/dependency, build system, type, symbol, file layout, architecture shape, and internal control flow as implementation vocabulary. They may appear in architecture context but never as a parity gap or finding by themselves.
- Require paired behavioral result artifacts from both sides for `different` or `equivalent`; test source locations are not execution evidence. Static inference, one-sided evidence, or a missing oracle is `Unverified` plus the cheapest paired characterization test.
- Never write a bare “다르다” row. State the common capability/input, baseline observable, candidate observable, exact semantic delta/status, paired evidence, and validation.
- Compare one critical flow per pair first; expand only when a material or `Unverified` result could change the backlog or gate.

## Saturation and Stop Rules
Stop evidence expansion when all are true:
- every material codebase group has inventory coverage or an explicit exclusion.
- every required stratum/view is represented or marked `Unverified` with a reason.
- material findings meet the evidence contract.
- one deliberate expansion of the weakest or highest-risk stratum no longer changes the top backlog or gate result.
- architecture models, report, findings, and quality-gate artifacts have been generated and checked.

If a new sample changes the top backlog, deepen only that stratum until the ranking stabilizes or the agreed budget is reached. At a time, token, permission, or tool boundary, stop broadening and report the remaining ledger gaps; never claim exhaustive coverage.

## Architecture Model Contract
- Generate the required models for entrypoints, context, containers, components, interfaces, scenarios, deployment, crosscutting concerns, and decision candidates.
- Treat call graphs, class hierarchies, regex signals, manifests, and optional complexity tools as supporting evidence, not as the architecture source of truth.
- Connect scenarios to traces/root spans when available; otherwise anchor them to evidenced entrypoints and mark fallback provenance.
- Keep deployment and runtime views `Unverified` when their evidence is unavailable.
- Use domain subject names in diagrams and preserve provenance/fallback flags. Load `reference.md` for detailed model and rendering rules only after inventory.

## Report Contract
Keep this section order:
1. 실행 요약
2. 범위/가정/비목표
3. 코드베이스 개요
4. 상위 설계 (HLD)
5. 상세 설계 (LLD)
6. 정적 분석 결과
7. 동적 분석 결과
8. 수동 리뷰 결과
9. 우선순위 개선 백로그
10. 부록

Quality requirements:
- HLD: Context, Container, Deployment, Crosscutting, and Architecture Decision Candidate views.
- LLD: multiple representative runtime scenarios plus Component and Interface views; add class/function detail only for complex core components.
- Label heuristic architecture items as decision candidates with a verification method, not accepted decisions.
- When semantic comparison is in scope, use `artifacts/manual/contract-comparisons.json`; exclude implementation-only/invalid-dimension rows, surface static-only rows as `Unverified`, and promote confirmed non-intentional behavior deltas into findings/backlog.
- Require result refs to resolve under approved runtime/test-result/manual artifact lanes; confirmed high/critical semantic-contract findings participate in the quality gate.
- Static analysis: graph-first LOC, complexity, branch, density, and LOC-vs-complexity views; do not replace the quadrant with a table.
- Backlog columns: `파인딩`, `액션`, `Severity`, `Priority`, `구체적인 개선 내용`, `관련 파일`.
- Every diagram must expose provenance and fallback status.

## Execution and Validation
1. Read `docs/document.md` only when preparing commands; resolve `SKILL_ROOT` through `CODEX_HOME` or an explicit path.
2. Run `scripts/collect.sh` with the approved scope and `references/policy-default.json`.
3. Build/promote architecture models, then run `scripts/report.py` against the collected output.
4. Check that required model files, `findings.json`, `quality-gate-result.json`, and the single Markdown report exist and parse.
5. Inspect the gate reasons, top findings, coverage ledger, `Unverified` notes, diagram provenance, and entrypoint/scenario linkage.
   If semantic comparison is in scope, also inspect paired evidence, excluded implementation-only rows, and every `Unverified` comparison task.
6. Rerun only the failed stage with identical inputs after fixing or obtaining approval; do not repeat broad collection by default.

Keep collector/reporter success separate from report quality: a zero exit code does not prove coverage, evidence quality, or actionable findings.

## Progressive Resource Map
Load resources only at their decision point:
- `reference.md`: architecture/report rules after inventory, before model/report generation
- `references/policy-default.json`: pass to tools; inspect only for policy overrides
- `references/quality-gates.md`: interpret or repair gate failures
- `references/schemas.md`: generate, inspect, or repair JSON artifacts
- `references/review-checklists.md`: only for requested manual review lanes
- `references/semantic-comparison.md`: only for port/migration/legacy-new or equivalent capability comparison
- `docs/document.md`: command/CI setup

Do not load all references or script source by default; prefer tool help, summarized artifacts, and targeted failure output.

## Risk, Failure, and Handoff
- Write only report artifacts under the approved output directory; destructive actions are out of scope.
- Do not fetch external data or inspect secrets unless separately authorized and bounded.
- On permission/tool failure, record the exact lane and reason in `notes/unverified.tsv` and keep it out of PASS assumptions.
- Static models may miss runtime/generated semantics; C/C++ semantic depth remains limited without compilation metadata and suitable tools.
- Route a point bug to `analysis-bug`, one structural decision to `analysis-codebase-design`, and a ranked opportunity scan to `analysis-architecture-deepening`.
- Let implementation workflows own code changes. Load review/report formatting skills only when explicitly requested after artifact generation.
