---
name: skill-system-repo-adapter
description: Integrate accepted skill behavior or pre-authored runtime companions into this Skill System repository by updating canonical source, repository metadata, generated targets, and bundle validation. Use only for repository integration after semantic authoring is owned by system skill-creator or another implementation owner; do not use for personal skills, authoring decisions, live runtimes, app-managed skills, or plugin caches.
---

# Skill System Repository Adapter

## Routing Card
- role: support
- intent_signature: integrate accepted skill assets into this Skill System repository
- use_when: accepted skill behavior or a pre-authored runtime companion needs canonical placement, registration, generation, or validation
- do_not_use_when: meaning, triggers, workflow, domain policy, source/fallback choice, or output quality is undecided; exclude personal/app-managed skills, live runtimes, mirrors, and caches
- expected_inputs: accepted authored source, its semantic owner, affected id, and target repository outcome
- expected_outputs: canonical integration, required metadata, generated targets, readback, and repository-validation evidence
- context_targets: read the request and affected canonical source; load only implicated manifests, routing, registry, eval, generator, or validation contracts
- risk_profile: write canonical `source/` only; generate mirrors through repository generators; credentials, live state, caches, and app-managed skills denied
- entry_scene: PREPARE

## Integration Contract
- `skill-creator` or the task implementation owner retains skill semantics, canonical input selection, domain policy, and fallback behavior. This adapter owns only repository placement and projection.
- Require an identifiable accepted source and owner. If either is missing or disagrees with the requested projection, fail closed and return the decision; never reconstruct semantics or substitute stale input.
- When another valid owner can continue, return a handoff rather than marking the whole task blocked. Reserve `blocked` for missing/conflicting integration input or denied live mutation.
- Change canonical `source/` and required repository metadata only. Never hand-edit generated targets to manufacture consistency.
- After generation, read back the affected canonical and generated paths. A successful command or generic bundle pass does not replace source-to-target agreement or authoring evidence.

## Workflow
1. Confirm the semantic owner, accepted source, affected id, and requested projection.
2. Read the canonical source completely and change one required integration surface at a time.
3. Generate runtime and plugin targets, then read back the affected mirrors.
4. Run focused checks, core bundle verification, and project-parent hygiene.
5. Report semantic evidence, source-to-target evidence, and generic repository checks separately.

## Validation Commands
From the bundle root:

```bash
python3 source/tools/generate_targets.py --target runtime
python3 source/tools/generate_targets.py --target plugins
python3 source/platform/codex/tools/verify_bundle.py --root . --profile core --format text
```

From the project parent: `python3 tools/check_bundle_hygiene.py Skill-System`.

## Output Contract
Return `primary_owner`, `authoring_status`, `canonical_source_changes`, `integration_decisions`, `generated_targets`, `source_target_readback`, `repository_validation`, and `remaining_risk`. This adapter can prove repository projection, not authored-skill quality.
