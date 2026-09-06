---
name: workflow-research
description: Execute one explicitly selected Research stage as a bounded task or Plan/Handoff DAG node by applying exactly one named Research specialist, enforcing its input and scientific output ceiling, and returning a Core research_result. Use for explicit Research node management or an assigned RES-* node. Do not use for ordinary direct single-stage research, choosing a stage from a vague goal, automatic multi-stage pipelines, DAG authoring, successor selection, or general implementation.
---

# Workflow Research

## Routing Card
- role: execution_primary
- family: research
- intent_signature: explicit Research node execution, RES-* node management, bounded scientific stage envelope
- use_when:
  - an accepted Plan/Handoff assigns one Research node and one exact Research stage skill
  - the user explicitly requests a managed one-node Research execution with a fixed stage and result boundary
- do_not_use_when:
  - an ordinary direct request already matches one Research specialist
  - the Research stage is undecided, several stages must be designed, or a new DAG is needed
  - the request is evidence search, general implementation, graph coordination, polling, or lifecycle monitoring
- expected_inputs: node/scope identity, one canonical Research stage skill, upstream input references, artifact/write boundary, evidence ceiling, and user checks
- expected_outputs: one stage-bounded result, artifact/evidence anchors, unresolved inputs, user checks, and Core `research_result` when crossing a graph or owner boundary
- context_targets:
  must_read:
    - assigned node contract and exact selected Research stage skill
    - available required upstream artifacts and the declared status of missing ones
    - `references/research_stage_contract.md` for authoritative stage ownership, direct-vs-graph execution, and output ceilings
  read_if_needed:
    - `references/execution_item_contract.md` when the result crosses a Coordinator, Plan/Handoff, or plugin boundary
  do_not_load_by_default:
    - unselected Research skills, full paper corpus, unrelated experiments, implementation tree, manuscript, or another worker transcript
- risk_profile:
  reads: only the assigned node, selected stage inputs, and evidence needed by that stage
  writes: only the explicitly requested stage artifact within its accepted boundary
  tools: only those authorized by the selected Research stage; no automatic network, install, training, or external write
  sensitive_resources: credentials, private data, authenticated sources, and external publication require explicit authority
- entry_scene: PREPARE

## Core Cards

- produces: `references/core-execution-items-v1/cards/research_result.md`
- consumes: `references/core-execution-items-v1/cards/research_result.md`

## Stage Admission

Accept exactly one `research-*` specialist from the Research rows of the authoritative Stage
Ownership table in `references/research_stage_contract.md`. Do not reinterpret Search evidence
owners as managed Research stages.

If the stage is missing, ambiguous, unavailable in the host, or conflicts with the node output,
return `not_produced` with the unresolved selection through the current lifecycle channel.

## Workflow

1. Bind the node/scope identity, exact stage skill, accepted inputs, output artifact, write boundary,
   evidence ceiling, user checks, and non-goals. In graph mode, preserve `plan_ref` and `node_id`.
2. Load only the selected stage instructions and the input slices they require. Treat prior
   `research_result` cards as locators to their artifacts/evidence.
3. Check the selected stage's required input. If a material prerequisite is absent or mismatched,
   return `not_produced` with the exact missing input/current owner.
4. Execute the selected stage inside its scientific, data, tool, and write boundary. Preserve
   planned/executed/observed/interpreted distinctions and every stage-specific no-fabrication rule.
5. Read back the produced artifact or inline result against the assigned scope and the selected
   stage's output ceiling. Scientific uncertainty may be a valid completed output when that stage
   allows it; keep unresolved evidence, inconclusive results, and human judgment visible.
6. When crossing a graph or owner boundary, emit one Core `research_result`. Otherwise return the
   same compact fields directly.
7. In worker lifecycle mode, send only the result item ID, selected stage, compact outcome,
   artifact/evidence anchors, unresolved inputs/user checks, and required one-time timing fields.

## Output Contract

Return only applicable fields:

- `stage_skill`
- `input_refs`
- `result_summary`
- `result_ceiling`
- `artifact_refs`
- `evidence_refs`
- `unresolved_inputs`
- `user_checks`
- Core `research_result` when graph-mode or cross-owner identity is supplied
