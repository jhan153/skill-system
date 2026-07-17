---
name: skill-system-repo-adapter
description: Integrate directly requested or already accepted skill changes into this Skill System repository by updating canonical source, repository metadata, generated targets, and bundle validation. Use only for repository integration after the user request or current implementation owner establishes the intended behavior; do not use for personal skills, app-managed skills, live runtimes, or plugin caches.
---

# Skill System Repository Adapter

## Routing Card
- role: support
- intent_signature: integrate accepted skill assets into this Skill System repository
- use_when: a directly requested repository skill change or pre-authored runtime companion needs canonical placement, registration, generation, or validation
- do_not_use_when: the request does not establish the intended behavior; exclude personal/app-managed skills, live runtimes, mirrors, and caches
- expected_inputs: user-requested behavior or accepted authored source, current task owner, affected id, and target repository outcome
- expected_outputs: canonical integration, required metadata, generated targets, readback, and repository-validation evidence
- context_targets: read the request and affected canonical source; load only implicated manifests, routing, registry, eval, generator, or validation contracts
- risk_profile: write canonical `source/` only; generate mirrors through repository generators; credentials, live state, caches, and app-managed skills denied
- entry_scene: PREPARE

## Integration Contract
- The current task implementation owner retains skill semantics, canonical input selection, domain policy, and fallback behavior. This adapter owns only repository placement and projection.
- Do not invoke or hand off to system `skill-creator` merely because the artifact is a skill. Use it only when the user explicitly names it or asks to create a personal skill outside this repository.
- Personal and app-managed skill work stays outside this repository adapter. Never edit `.system` or app-managed skill assets.
- Require identifiable requested behavior or an accepted source plus an owner. If these are missing or conflict with the requested projection, return the unresolved decision; never reconstruct semantics or substitute stale input.
- When semantics are undecided, return the question to the current task owner. Reserve `blocked` for missing/conflicting integration input or denied live mutation.
- Change canonical `source/` and required repository metadata only. Never hand-edit generated targets to manufacture consistency.
- After generation, read back the affected canonical and generated paths. A successful command or generic bundle pass does not replace source-to-target agreement or authoring evidence.

## Workflow
1. Confirm the current task owner, requested behavior or accepted source, affected id, and requested projection.
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
