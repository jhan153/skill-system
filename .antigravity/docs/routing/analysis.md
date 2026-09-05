# Analysis Routing

> Generated from canonical skill-local Routing Cards. Read only the matching section.

## `analysis-algorithm`

- role: primary
- family: analysis
- intent_signature: algorithm/approach recommendation or candidate comparison under constraints
- use_when: credible solution families compete and workload, correctness, latency, memory, dependency, deployment, or implementation constraints change the winner.
- do_not_use_when:
  - failure mechanism/cause is the requested output: `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane; otherwise current task owner for diagnosis-only
  - an already-implemented accepted production contract needs one bounded defect repair: `workflow-bug-fix`
  - chosen method needs code: `workflow-implementation`
  - measured production bottleneck: `analysis-performance`
  - paper hypothesis, loss, ablation, or training plan: `research-hypothesis-planning`
  - selected interface/boundary contract: `analysis-boundary-design`
  - business identities, states, or invariants: `analysis-domain-modeling`
- expected_inputs: decision, current baseline, hard constraints, preferences, workload, success condition
- expected_outputs: recommendation or unverified gap, decisive trade-off, mechanism, evidence scope, falsifier, handoff
- context_targets:
  - must_read: current decision, success condition, constraints, and baseline when one exists
  - read_if_needed: narrow integration/measurement evidence; `references/problem-class-map.md` only for genuinely broad candidate discovery
  - do_not_load_by_default: full repo, memory bank, broad reports, unrelated candidate catalogs
- risk_profile: focused read-only comparison; no implementation writes; credentials denied
- entry_scene:
  - PREPARE

## `analysis-architecture-deepening`

- role: primary
- family: analysis
- intent_signature: ranked architecture-improvement or deep-module opportunity scan
- use_when: rank several improvements in a workflow, module cluster, or explicit broad scope before selecting one.
- do_not_use_when:
  - one boundary/interface is selected: `analysis-boundary-design`
  - several interacting boundaries need a normative target/transition design:
    `workflow-architecture-design`
  - architecture map, HLD/LLD modeling, or Mermaid flow/structure/state diagrams: `analysis-codebase-map`
  - recurring bug root cause: `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane; otherwise current task owner for diagnosis-only, or `workflow-bug-fix` only for a semantically admitted bounded repair under an already-implemented accepted contract
  - domain concepts/invariants: `analysis-domain-modeling`
  - measured bottleneck: `analysis-performance`
  - direct production change: route by the selected candidate's change contract—`workflow-refactor-safely` for behavior-preserving live restructuring, `workflow-source-maintenance` for proven-obsolete deletion, or `workflow-implementation` for behavior changes
- expected_inputs: user-named scope or bounded recent-change history, pain/change signals, implementation appetite
- expected_outputs: sampling basis, coverage, evidenced friction, ranked candidates, an evidenced next candidate or exact discriminator, handoff, and unverified gaps
- context_targets:
  - must_read: goal, compact scope outline, and production path/owner evidence for shortlisted candidates
  - read_if_needed: discriminating callers, contracts, failures, diffs, metrics, or formal invariants
  - do_not_load_by_default: every file, generated reports, full memory, unrelated docs
- risk_profile: focused read-only discovery; no implementation writes; credentials denied
- entry_scene:
  - PREPARE

## `analysis-boundary-design`

- role: primary
- family: analysis
- intent_signature:
  - one module/interface/seam/adapter/dependency/testability decision
- use_when:
  - one structural decision blocks a feature, fix, or refactor and current code evidence must select the boundary.
- do_not_use_when:
  - the request is a multi-view target/transition architecture (`workflow-architecture-design`),
    architecture map, ranked opportunity scan, domain model, bug RCA, direct implementation, or an
    obvious local edit with no boundary choice.
- expected_inputs:
  - one decision/pressure, target owner, common and edge callers, dependency/behavior evidence, constraints, and non-goals
  - optional accepted `architecture_design` reference that explicitly contains or constrains this
    one atomic boundary
- expected_outputs:
  - optional architecture reference/conformance, current owner, candidate moves including
    keep-local, exactly one boundary decision, and implementation/validation or architecture handoff
- context_targets:
  must_read:
    - design question, `references/boundary_decision_contract.md`, target owner/surface, common and material-edge callers, and one behavior path
  read_if_needed:
    - tests, contracts, side effects, canonical source, or readback that distinguishes candidates
    - `references/architecture_design_contract.md` when an accepted architecture design explicitly
      contains or constrains the assigned atomic boundary
    - `references/programming_paradigm_contract.md` when that accepted design contains a
      target-relevant `kind: programming_paradigm | adjacent_implementation_model` application or
      the one boundary question materially selects a paradigm/model
    - after that base contract, only the selected files under
      `references/programming-paradigms/`; load a second profile only for another material axis or
      conflict that can change this atomic decision
    - `references/database_persistence_transparency_contract.md` when the selected boundary concerns database ownership, domain/persistence separation, or an ORM/ODM/data-access seam
  do_not_load_by_default:
    - full repo/memory, broad reports, unrelated domain docs, raw production data, or credentials
- risk_profile:
  reads: target, callers, tests, dependency and actual-path signals
  writes: none; implementation owns changes
  tools: focused search and safe observations
  sensitive_resources: deny credentials
- entry_scene:
  - PREPARE

## `analysis-codebase-map`

- role: primary
- family: analysis
- intent_signature: architecture map, HLD/LLD modeling, sequence/state/structure diagrams
- use_when:
  - the user wants to understand how a repo or named slice is structured and how it runs.
  - the expected output is Mermaid maps of flow, structure, or state—not a findings backlog or one design verdict.
  - generic codebase-analysis or codebase-report wording has no explicit findings, backlog, or quality-gate contract; satisfy it with this compact map.
- do_not_use_when:
  - one module/seam/adapter decision is needed; use `analysis-boundary-design`.
  - the user wants ranked improvement candidates; use `analysis-architecture-deepening`.
  - the user wants a normative target/transition architecture across several interacting
    boundaries; use `workflow-architecture-design`.
  - the cause of a failure is unknown; use `workflow-runtime-debugging` for an explicitly requested execution-ready debugging scope or material debugger/dump/dynamic/graphics evidence lane, keep simple source/log-only diagnosis with the current task owner, or use `workflow-bug-fix` only for a semantically admitted bounded repair of an already-implemented accepted contract. First implementation or explicit production replacement uses `workflow-implementation`.
  - implemented code or a diff needs findings and a review disposition, with or without a design baseline; use `workflow-code-review`.
  - the request is domain language, performance RCA, direct implementation, or an explicit findings/quality-gate artifact.
- expected_inputs: repo root or named slice, the question to understand, any explicit HLD/LLD choice, and any required runtime/state focus
- expected_outputs: altitude (`hld` or `lld`), Mermaid diagrams with captions and source refs, and explicit `Unverified` gaps
- context_targets:
  must_read:
    - the map request, repo or named-slice outline, and one representative entrypoint-to-output path
  read_if_needed:
    - callers, manifests, state stores, and a disconfirming path that would change a diagram
    - `reference.md` for view selection and Mermaid render rules
  do_not_load_by_default:
    - full repo, bulk inventory dumps, prior reports, memory, or unrelated docs
- risk_profile:
  reads: targeted source, callers, manifests, and observed runtime only when needed
  writes: none by default; one map Markdown only when a file is explicitly requested
  tools: focused search and safe observation
  sensitive_resources: credentials and secret files default deny
- entry_scene: PREPARE

## `analysis-domain-modeling`

- role: primary
- family: analysis
- intent_signature:
  - domain modeling, ubiquitous language, identity/value/state boundary, invariant, business rule, or naming decision
- use_when:
  - a development decision depends on clarifying concepts, terminology, lifecycle, invalid states, or domain-policy ownership.
- do_not_use_when:
  - clear-term implementation (`workflow-implementation`), module/seam architecture (`analysis-boundary-design`), broad analysis, current failure RCA, persistent glossary/ADR/docs writing (documentation owner), memory/accepted-knowledge mutation, or product ideation.
- expected_inputs:
  - decision area, material use case, current terms, relevant production owner/callers/schema/API, and explicit write scope if any
- expected_outputs:
  - evidence-backed vocabulary, concept/state/invariant decision, rejected alternatives, smallest owner-mapped handoff, and unresolved rules
- context_targets:
  must_read:
    - request, actual domain owner, representative caller or transition path, and existing terms
  read_if_needed:
    - persisted/API schemas, errors, tests/fixtures, and explicitly referenced policy/docs
    - `references/boundary_decision_contract.md` when concept, invariant, lifecycle, or policy ownership requires grouping or separation
  do_not_load_by_default:
    - full repo/memory, unrelated product docs, production data, or generated reports
- risk_profile:
  reads: scoped production source, callers, schemas, tests, docs, and examples
  writes: none by default; code/docs only when explicitly requested
  tools: focused search and the smallest readback or counterexample that discriminates a rule
  sensitive_resources: deny credentials and production data
- entry_scene:
  - PREPARE

## `analysis-llm-wiki-context`

- role: support
- family: analysis
- intent_signature: explicit named LLM Wiki exploration and task context construction
- use_when: the user invokes this skill, supplies an exact Wiki path, or explicitly selects a named `llm_wikis` entry
- do_not_use_when: no Wiki is selected, several candidates remain, project Knowledge Base is the intended source, Wiki mutation/composition is requested, or ordinary repo evidence is sufficient
- expected_inputs: current task/owner, exact Wiki path or name, manifest declaration when used, and task anchors
- expected_outputs: compact role-organized context with source page refs returned to the current task owner
- context_targets:
  must_read: current task, selected Wiki declaration/path, and that Wiki's own guide/entrypoint
  read_if_needed: native index/search/graph/backlinks and only pages selected from them
  do_not_load_by_default: full Wiki, other named Wikis, Memory, Knowledge, raw transcripts, Book-specific assumptions
- risk_profile:
  reads: one explicitly selected Wiki
  writes: none
  tools: Wiki-native read/search/navigation only
  sensitive_resources: private Wiki access stays within the selected path/session
- entry_scene: PREPARE

## `analysis-performance`

- role: primary
- family: analysis
- intent_signature:
  - performance/latency/throughput/CPU/memory/query/render/startup/bundle analysis; 성능 분석; 병목
- use_when:
  - a current software symptom needs measurement-backed bottleneck diagnosis before an optimization is selected.
- do_not_use_when:
  - correctness diagnosis/fix, an already-selected implementation, a still-open algorithm choice, repo-wide reporting, or scientific experiment design is primary.
- expected_inputs:
  - user-relevant metric and symptom, representative workload/path, target environment/threshold, existing measurements, and material correctness constraints
- expected_outputs:
  - scoped target and baseline, actual hot path, discriminated bottleneck, evidence authority/scope, smallest next change or handoff, and unresolved conditions
- context_targets:
  must_read:
    - request, metric/workload/environment, affected actual path, and available baseline/profile/trace
  read_if_needed:
    - targeted code/query/config, benchmark method, recent regression diff, data-size assumptions, or observability contract
    - `references/systems-bottleneck-map.md` only when CPU microarchitecture, memory hierarchy,
      scheduler/synchronization, and I/O/queue hypotheses compete on the same representative path
  do_not_load_by_default:
    - full repo/memory, unrelated logs/reports, raw production data, or credentials
- risk_profile:
  reads: targeted path, comparable measurements, profiles/traces, configs, and correctness evidence
  writes: none; implementation belongs to its workflow after bottleneck selection
  tools: focused profiling and comparable measurement of the relevant path
  sensitive_resources: production data/traces require their governing access and redaction boundary
- entry_scene:
  - PREPARE

## `workflow-architecture-design`

- role: primary
- family: analysis
- intent_signature:
  - multi-boundary software architecture design
  - target or transition architecture
  - quality-scenario-to-architecture contract
- use_when:
  - accepted behavior or quality requirements require a coherent target across several module,
    data/state, runtime/failure, integration, deployment/operations, or security/trust boundaries.
  - a new service, database/data owner, protocol, plugin ABI, process/deployment boundary, shared
    state model, or cross-module asynchronous/thread model changes several architecture views or
    owners and needs design before implementation.
- do_not_use_when:
  - the request is a descriptive HLD/LLD map (`analysis-codebase-map`), one seam/interface decision
    (`analysis-boundary-design`), ranked improvement scan (`analysis-architecture-deepening`),
    domain meaning (`analysis-domain-modeling`), measured bottleneck diagnosis
    (`analysis-performance`), production implementation, or static review.
  - the existing accepted architecture already decides the requested implementation slice and no
    material owner, public contract, dependency, state, runtime, deployment, or trust boundary moves.
  - the change adds an adapter inside an accepted Port contract or parallelizes work inside an
    existing Scheduler/resource owner without moving cross-module ownership, thread semantics, or
    another architecture view; use `workflow-implementation` or diagnose a measured bottleneck with
    `analysis-performance`.
- expected_inputs:
  - architecture question and target scope
  - accepted functional drivers, quality scenarios or the facts needed to form them, constraints,
    non-goals, and decision authority
  - current owners, canonical sources, and a representative actual path for brownfield work
  - artifact/write boundary and acceptance status when available
- expected_outputs:
  - one coherent `architecture_design`, candidate comparison, scoped pattern applications,
    boundary/ownership contracts, current-target-transition design, architecture delta and required
    approvals, fitness contract, implementation handoffs, and explicit unresolved decisions
- context_targets:
  must_read:
    - architecture request, target scope, accepted requirements/constraints, and decision authority
    - `references/architecture_design_contract.md`
    - `references/boundary_decision_contract.md`
    - current owner and one representative plus material-edge path for brownfield work
  read_if_needed:
    - accepted domain model, current HLD/LLD map, build/module graph, public APIs, schemas, state/data
      owners, runtime/failure path, deployment/operations contract, and security/trust rules that can
      change the decision
    - `references/programming_paradigm_contract.md` when the user selects a subsystem/module
      paradigm, supplies paradigm research, or a candidate materially changes state/effect
      ownership, shared data representation, compile/runtime extension, or execution architecture
    - after that base contract, only the selected files under
      `references/programming-paradigms/`; load a second thin profile only for another material axis
      or pairwise conflict
    - `references/database_persistence_transparency_contract.md` when database ownership, schema,
      consistency, transaction, migration, or data-access boundaries are material
  do_not_load_by_default:
    - full repository, broad architecture or pattern catalogs, all historical ADRs, full memory or
      Knowledge stores, unrelated design docs, generated reports, raw production data, or credentials
    - `workflow-implementation`'s detailed paradigm method profiles, code examples, or regression
      cases; Architecture consumes only the shared decision contract
- risk_profile:
  reads: accepted requirements and only the source, runtime, and contract evidence needed by the material views
  writes: explicit architecture artifact only; never production code, build/runtime config, schemas, tests, ADR/Knowledge records, or Plan/Handoff
  tools: focused search, safe current-path observation, and bounded diagram rendering only when it materially clarifies the design
  sensitive_resources: credentials and production data denied; external systems and persistent state remain read-only unless separately authorized
- entry_scene: PREPARE

## `workflow-runtime-debugging`

- role: execution_primary
- family: analysis
- intent_signature:
  - debugging scope, live debugger operation, crash/core/minidump analysis, symbol and unwind validation, watchpoint or record/replay diagnosis, graphics/device-loss debugging, runtime root cause; 디버깅 범위, 디버거, 덤프, 심볼, 런타임 원인 규명
- use_when:
  - one concrete runtime correctness failure needs an execution-ready debugging scope even when no debugger or artifact is currently available
  - one concrete runtime correctness failure has an existing stopped debugger, approved launch/attach path, crash artifact, dynamic diagnostic report, record/replay trace, graphics frame capture, or device-loss artifact
  - the requested outcome is debugging-scope selection, causal localization, artifact sufficiency, or the next discriminating runtime observation without source repair
- do_not_use_when:
  - ordinary source/log reasoning already answers the question without a runtime evidence lane
  - the user requests a source/test write: use `workflow-bug-fix` only for a semantically admitted bounded repair of an already-implemented accepted contract, or `workflow-implementation` for first implementation or explicit production-mechanism replacement
  - the target is progressing correctly and the dominant question is latency, throughput, utilization, frame time, resource cost, or another performance metric; use `analysis-performance`
  - test design, test-only implementation, static code review, or production diagnostic infrastructure is the requested deliverable
- expected_inputs:
  - original trigger and expected condition, target/process/build or artifact identity when known, available or missing session/artifacts, environment, prior observations, permitted debugger effects, and optional Plan/node identity
- expected_outputs:
  - one direct task-local or graph-mode Core `debugging_result` containing an execution-ready debugging scope and, in operate mode, identity/sufficiency checks, observations, perturbations, causal status, session handoff, proof ceiling, next discriminator, and optional repair/performance handoff
- context_targets:
  must_read:
    - concrete runtime trigger, expected condition/authority, available or missing session/artifact state, repository/runtime instructions, and `references/runtime_debugging_contract.md`
    - supplied Plan/node identity and predecessor `debugging_result` when graph mode is assigned
  read_if_needed:
    - implicated source, loaded modules, build manifest, symbol manifest/store, capture metadata, prior attempts, and only the callers/state owners needed to interpret observed machine or device state
    - `references/execution_item_view.md` in graph mode or when a result crosses another Workflow/plugin
    - `references/runtime-debugging/debugging-signal-and-causal-loop.md` when competing causes or signal quality determine the next observation
    - `references/runtime-debugging/live-debugger-operation.md` for an existing session, launch, attach, stop, breakpoint, watchpoint, stepping, or hang inspection
    - `references/runtime-debugging/crash-dump-symbols-and-unwind.md` for core/minidump/crash artifacts, address symbolization, optimized code, or unreliable stacks
    - `references/runtime-debugging/dynamic-temporal-and-concurrency-debugging.md` for corruption, races, deadlocks, time-dependent failure, sanitizer output, trace, or record/replay
    - `references/runtime-debugging/graphics-debugging.md` for API validation, frame/resource/shader state, CPU-GPU correlation, device loss, or GPU crash artifacts
  do_not_load_by_default:
    - full repository/history, unrelated tests/logs, every reference, raw production data, credentials, or untrusted debugger extensions
- risk_profile:
  reads: target/source identity, live process state, dumps, symbols, traces, captures, registers, memory, disassembly, and directly relevant code
  writes: no production or test source; only approved debugger/session control and explicitly authorized diagnostic artifact capture
  tools: debugger prompt and process control, stack/register/memory/disassembly inspection, breakpoint/watchpoint, symbol/dump tools, dynamic diagnostics, trace/replay, and graphics capture tools
  sensitive_resources: attach/launch/continue/step changes execution; dumps and captures may contain secrets; target-state mutation and untrusted auto-load code are denied without separate authority
- entry_scene:
  - PREPARE
