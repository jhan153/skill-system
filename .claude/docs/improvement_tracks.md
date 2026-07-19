# Improvement Tracks

This document records active improvement tracks for the next version cut. It is a field-quality backlog, not a package gate.

## Active Tracks

| track | target files | current action | next evidence |
| --- | --- | --- | --- |
| Design implementation issues | `.codex/docs/design_cluster_roadmap.md` | Improve the 7-skill design cluster and `design-frontend` surface-profile selection from explicit user reports. | Concrete design-to-code, decomposition, layout translation, or profile-selection problems reported by the user. |
| 9.2.1 conditional reference disclosure | Six design `SKILL.md` files (`frontend`, `visual-regression`, `tokens`, `a11y-audit`, `component-mapper`, `layout-translator`) and their existing Markdown references | The bounded release set keeps selectors, evidence ceilings, policy ownership, and fail-closed decisions in each main body while selecting detail only for applicable work. Against `v9.2.0`, main bodies move 6,162→5,524 words (-638) and 47,072→42,349 bytes (-4,723); main plus Markdown references move 10,410→9,960 words (-450) and 78,661→75,477 bytes (-3,184). Fresh scoped admission observations cover visual regression and frontend only; admission for the other four remains unverified. | Observe real field admission, especially whether `design-layout-translator/references/layout-translation-map.md` is loaded for nearly every normal call. Do not infer universal equivalence or zero admission from static parity. |
| 9.2.0 skill diet closeout | `.codex/docs/skill_diet_protocol.md`, `.codex/eval/baselines/skill-diet-9.1.2.yaml` | All 66 canonical skill bodies are reduced; all 38 merge/delete candidates are resolved; generated targets agree with source. Forward and reviewer evidence remains scoped rather than universal quality proof. | Keep the 9.2.0 cut immutable. Continue conditional reference admission on a separate 9.2.1 line, with each move justified by a real default-context reduction and preserved fail-closed behavior. |
| Research negative routing | `.codex/eval/negative_routing_cases.yaml`, `.codex/eval/research_regression_cases.yaml` | Narrow routing when research terms appear in ordinary development or lightweight text work. | Explicit user reports of research-cluster over-triggering. |
| Coordination over-trigger | `coordination-handoff`, `handoff_cases.yaml`, `negative_routing_cases.yaml` | Narrow triggers to explicit DAG, handoff, lock-scope, multi-session coordination, or artifact-inventory intent. | Explicit user reports where ordinary work was expanded into coordination. |
| Project context lifecycle | `project-context.yaml`, Memory Bank skills, Knowledge Base skills, `project-context-checkpoint` | Improve explicit setup/doctor, bounded typed-path reads, overlap/provenance handling, and commit/closeout classification only from explicit user reports. | User-reported misses, duplicate identities/observations, false independent recurrence, broken history/relations, or wrong-store decisions during real work. |
| Heavy planning over-trigger | `plan-long-term-package`, `negative_routing_cases.yaml`, `skill_registry.md` | Require explicit package-style planning intent. | Requests containing phase, migration, rewrite, or handoff that should not create packages. |
| Local context retrieval | `memory-bank-harness`, `knowledge-base-read`, `llm-wiki-context`, `project_context_manifest.md` | Read the minimum declared source, prefer artifact-linked local knowledge, and never discover undeclared home/adjacent stores. | Real tasks where local rules were missed or an unrelated context store was admitted. |

## Non-Goals

- Do not use this backlog as a bundle validator.
- Do not calculate package readiness.
- Do not create deployment, signoff, rollback, or evidence-finality workflow from these tracks.

## Review Cadence

Update the registry, eval cases, or skill text only when the user explicitly reports a concrete problem or requests the change.
