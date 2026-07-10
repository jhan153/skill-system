---
name: skill-system-repo-adapter
description: Integrate accepted skill behavior or pre-authored runtime companions into this Skill System repository by updating canonical source, repository metadata, generated targets, and bundle validation. Use only for repository integration after semantic authoring is owned by system skill-creator or another implementation owner; do not use for personal skills, authoring decisions, live runtimes, app-managed skills, or plugin caches.
---

# Skill System Repository Adapter

## Routing Card
- role: support
- intent_signature:
  - integrate accepted skill assets into this Skill System repository
- use_when:
  - a system `skill-creator` result belongs in this repository.
  - an already-authored skill or runtime companion needs canonical placement, registration, generation, or validation.
- do_not_use_when:
  - deciding skill meaning, triggers, workflow, examples, or output quality.
  - authoring a personal/home skill or editing `.system`, live homes, generated mirrors, or caches directly.
- expected_inputs:
  - accepted authored content or a pre-authored source change
  - target repository outcome and affected skill/runtime id
- expected_outputs:
  - canonical source integration, affected metadata/evals, generated targets, and repository validation evidence
- context_targets:
  must_read:
    - current repository request
    - affected canonical source
  read_if_needed:
    - only implicated plugin manifests, routing, registry, eval, generator, or validation instructions
  do_not_load_by_default:
    - unrelated skills/evals, generated targets, live homes, plugin caches, or app-managed skills
- risk_profile:
  reads:
    - affected canonical source and selected integration contracts
  writes:
    - canonical `source/`; generated targets only through repository generators
  tools:
    - focused search, generators, and repository validation
  sensitive_resources:
    - credentials, live runtimes, caches, and app-managed skills denied
- entry_scene:
  - PREPARE

## Ownership Gate
- New or revised skill behavior: system `skill-creator` owns semantics; this adapter integrates the accepted result.
- Pre-authored skill/runtime companion: the task implementation owner stays primary; this adapter performs repository projection.
- Personal/home or app-managed skill: do not attach this adapter.

Semantic ownership includes trigger wording, workflow, examples, output contract, and authoring-quality tests. Repository ownership includes canonical paths, repository policy fields, plugin membership, routing/registry/eval changes, generation, and bundle checks. Projection must not silently change accepted semantics.

## Workflow
1. Confirm the primary owner and accepted semantic outcome.
2. Read the affected canonical source completely; inspect one integration surface at a time.
3. Change only required `source/skills`, `source/shared`, `source/platform`, or `source/plugins` files.
4. Generate runtime and plugin targets; never repair mirrors manually.
5. Run focused checks, core bundle verification, and project-parent hygiene.
6. Report authoring evidence separately from repository-consistency evidence.

## Validation Commands
From the bundle root:

```bash
python3 source/tools/generate_targets.py --target runtime
python3 source/tools/generate_targets.py --target plugins
python3 source/platform/codex/tools/verify_bundle.py --root . --profile core --format text
```

From the project parent: `python3 tools/check_bundle_hygiene.py Skill-System`.

## Output Contract
- `primary_owner`
- `authoring_status`
- `canonical_source_changes`
- `integration_decisions`
- `generated_targets`
- `repository_validation`
- `remaining_risk`

This adapter proves repository consistency, not authored-skill quality.
