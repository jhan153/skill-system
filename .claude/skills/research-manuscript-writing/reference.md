# Research Manuscript Writing Reference

## Source Material Note
This skill is part of the 6.0 Research Cluster. It may reuse contracts and guardrails extracted from `codex-research-lifecycle.zip`, but the source archive must not be installed as a monolithic skill.

## Owned Inputs
- evidence ledger
- literature review
- research plan
- experiment blueprint
- analysis report
- user manuscript

## Owned Outputs
- papers/draft/manuscript.md or main.tex when requested
- section draft
- citation gaps
- unverified claims

## Workflow Checklist
- PREPARE - identify target section and available evidence.
- GROUND - map claims to citations or mark placeholders.
- DRAFT - write coherent paragraphs unless outline is requested.
- SEPARATE - keep methods, results, and interpretation distinct.
- VERIFY - avoid invented citations/results/tables/figures.
- FINALIZE - provide draft text or artifact path when requested.

## Risk Checklist
- Artifact writes require explicit artifact intent.
- Network access is off by default except literature evidence search when needed and allowed.
- Dataset downloads, dependency installs, and training jobs are never implicit.
- `.system` is outside scope.

## Validation Checklist
- [ ] Correct research stage selected.
- [ ] Required source artifact or evidence is present or marked missing.
- [ ] No fabricated papers, citations, DOIs, datasets, metrics, or results.
- [ ] Development/implementation requests are returned to development mode.
- [ ] Output matches the declared artifact owner in `.codex/research-routing.md`.
