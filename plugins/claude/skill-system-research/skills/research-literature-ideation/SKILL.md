---
name: research-literature-ideation
description: Derive research-gap hypotheses from an evidence set or literature synthesis, preserving claim provenance and distinguishing observed gaps from speculative novelty. Use to generate/rank candidates and, when requested, select one active hypothesis for validation.
---

# Research Literature Ideation

## Routing Card
- role: primary
- family: research
- intent_signature: research gaps, candidate hypotheses from literature, active hypothesis, 문헌 기반 연구 아이디어
- use_when: an existing evidence set or synthesis can support gap-derived hypotheses or ranking
- do_not_use_when: papers need acquisition/synthesis, or a raw premise has no literature dependency
- expected_inputs: identified evidence artifact, scope, and ranking/selection constraints
- expected_outputs: provenance-linked gap classes, falsifiable candidates, ranking, optional active hypothesis, and evidence needs
- context_targets: read the named evidence set/synthesis and scope; expand only sources needed to resolve candidate provenance, not the full corpus, scaffold, manuscript, or unrelated results
- risk_profile: no search by default and write an ideation artifact only when requested; credentials denied
- entry_scene: PREPARE

## Stage Boundary
Read `references/research_stage_contract.md` only when upstream/downstream ownership, multi-stage
intent, or Plan/Handoff mapping matters. This skill owns candidate generation/ranking and selects
one active hypothesis only on explicit decision intent; it never starts hypothesis planning or an
experiment stage.

## Ideation Contract
1. Identify evidence-supported contradictions, boundary conditions, method/data/metric mismatches, failure modes, or missing comparisons.
2. Label each as an `observed gap` supported by reviewed evidence, a corpus `coverage gap`, or a `speculative opportunity` needing evidence.
3. Generate only candidates linking the gap to a mechanism, bounded observable prediction, and falsifier; tag every premise as `paper|dataset|experiment|math|assumption` with a source locator.
4. Rank by evidence basis, identifiability, expected information gain, feasibility, and risk—not popularity or novelty wording.
5. Selection is omitted unless the user requests a decision/next experiment. Then select one active hypothesis; otherwise return a shortlist and keep non-selected candidates with the evidence needed to reconsider them.

If the named evidence artifact is missing/mismatched or provenance cannot be resolved, return the acquisition/synthesis gap rather than substituting stale evidence. Absence from the supplied corpus never proves field novelty; a current novelty claim requires a fresh, appropriately scoped search.

## Output
Return proportional gap evidence, candidate mechanism/prediction/falsifier, ranking rationale, requested selection, and missing evidence. Do not emit a large catalog or imply that a generated hypothesis is verified.
