# Skill Diet Protocol

This is the maintenance protocol for the 9.2.0 instruction-surface diet. It is not normal routing context. Load it only when measuring, relocating, pruning, or release-validating canonical Skill System skills.

## Objective

Reduce repeated instruction and trigger surface without weakening routing, safety, evidence, fail-closed behavior, or output quality.

The governing order is:

```text
freeze baseline
-> establish behavior oracles
-> relocate ownership
-> compress shared structure
-> run deletion ablations
-> optimize trigger metadata
-> collect fresh release evidence
```

Do not count a moved rule as deleted, a linked reference as admitted, or an unchanged static test as proof of unchanged model behavior.

## Post-9.2.0 Conditional Reference Disclosure

`v9.2.0` completed the 66-skill body diet with zero reference moves. Bundle 9.2.1 is a bounded follow-up: keep routing selectors, semantic decisions, evidence ceilings, ownership, and fail-closed handling in each main body, and select existing specialist detail only when the task needs it. Apply the measurement contract below to both the main-body delta and the main-plus-reference delta; relocation alone is not deletion.

This bounded lane does not grant the comparator's strongest claims. Without source/model/oracle-bound behavioral evidence, report `behavior: unverified`, not `preserved`. Without a verified host admission receipt, report `admission: unverified` with a null observation, not `improved` or zero. Structural checks, generated parity, existing tests, and scoped agent-authored forward observations stay within their own contracts and do not make a six-skill universal-equivalence or user-quality claim. A bounded patch may close with those claim ceilings; the independent-signed/PKI campaign is required only when claiming its strict release-comparison verdict, not as a substitute for honest bounded evidence.

## Frozen Baseline

The authoritative final pre-diet baseline is the Git object, not a movable branch or working tree:

- label: `7484956`
- commit: `74849564add4180a7118c8da513f380dc7c30a93`
- `source/skills` tree: `db284653853c730db4b16142ccb9ecbbb71a49f5`
- tracked input digest: `5e147102d83ffa36da95f75c82633d0618274f6b3d143b5ce1f07b455f38053a`
- bundle: `9.1.2` unpublished source baseline

The machine-readable inventory lives at `source/shared/eval/baselines/skill-diet-9.2.0-pre-diet.yaml` and at the generated runtime path after generation. Recompute it from the pinned commit, not from an uncommitted worktree. The `baseline/9.2.0-pre-diet` tag and `skill-diet-9.1.2.yaml` remain historical lower-bound evidence pinned to `d0b0514b4433448cc03e8857df52399150802d58`; they are not the T3 comparison baseline.

## Measurement Contract

- `words`: Unicode non-whitespace spans.
- `utf8_bytes`: bytes after strict UTF-8 encoding.
- `full`: complete `SKILL.md`.
- `body`: content after the line-delimited YAML frontmatter and its separator newline.
- `routing_card`: `Routing Card` section content without its heading.
- `owned_inventory`: `SKILL.md` plus every bundled resource; it is not admitted context.
- `declared_exact_admission`: only a skill-local file named exactly in `must_read` or `read_if_needed`.
- `linked`: exact body mention only; it proves discoverability, not admission.
- `not_explicitly_named`: no exact file mention was found. It may still be reachable through a catalog, selector, or script and is not a dead-file verdict.
- `observed_admission`: words/bytes from a source-bound run artifact plus verifier receipt. Without the complete chain, record `unverified` and `null`, never zero.
- `observed_admission` scope includes exact context units from the owning skill, composed skills, shared docs, shared schemas, `context-routing.md`, and platform instruction anchors. Moving prose across one of those boundaries is still admission until a receipt proves otherwise.
- `content_unit`: `full_file` for a loaded file, or an exact measured discovery/body slice when the host admits only that slice. Do not list a full file and one of its slices in the same run.

Context-surface measurements are not tokenizer or billing measurements.

## Resource Classes

Classify every non-`SKILL.md` file before judging removal:

- `instruction_reference`: `references/**`, `docs/**`, or a root `reference.md`.
- `script`: executable or reusable deterministic procedure under a skill's `scripts/**` or a shared script owner. Executed code is owned inventory, not model context, unless a run trace shows that its source was admitted.
- `schema_contract`: machine-readable schema or shared contract.
- `asset`: output material under `assets/**`.
- `agent_metadata`: `agents/openai.yaml` and related discovery metadata.
- `other`: retained explicitly until ownership is resolved.

A body reduction accompanied by resource growth is `possible_relocation`, not proven deletion. Moving prose to an eagerly declared reference does not prove context reduction.

## Behavior Coverage Levels

Keep these levels separate:

1. `declared_route`: `expected_primary_skill`, `expected_supporting_skills`, or `should_not_trigger` in an eval case.
2. `structured_contract`: schema-v2 behavior fields for a case whose primary or explicit behavior-contract owner is the skill.
3. `observed_replay`: a source-, model-, oracle-, output-, and verifier-bound replay result.
4. `observed_host_assisted`: a fresh source-, model-, oracle-, output-, and verifier-bound host-assisted result.

Supporting and negative associations are declarations until invocation traces prove them. The frozen 9.1.2 baseline lacked explicit edge ownership; the 9.2.0 overlay now declares it with `behavior_contract_owners` and `scenario_tags`.

Historical 9.1.1 runs remain historical. They are not 9.1.2 baseline evidence.

## Comparator Axes

Report these independently:

- `structure`: unchanged or changed, including body/resource deltas and possible relocation.
- `routing_contract`: unchanged or drifted.
- `oracle_contract`: unchanged, expanded, lost, or changed.
- `behavior`: preserved, agent-reviewed, regressed, or unverified. Static oracle preservation alone cannot produce `preserved`; `agent-reviewed` is a local-pilot result and is never release-equivalent.
- `admission`: improved, not improved, or unverified. Missing receipts always produce `unverified`.

Size reduction alone is advisory. Missing skills, routing/invocation drift, lost cases, and weakened oracle digests are fail-closed regressions during the structural-diet lane.

## Section Ownership Classification

Before editing a pilot skill, classify each section as exactly one provisional destination:

```text
main
reference
existing_specialist_skill
script
schema_or_shared_contract
eval
delete_candidate
```

`delete_candidate` is not authorization to delete. After relocation stabilizes, use deletion ablation and record one terminal decision:

```text
delete
merge
move
keep_proven
retain_unverified
```

## Work Sequence

1. Check the frozen manifest and compare the current candidate before editing.
2. Fill missing structured and competing behavior oracles for the selected skill.
3. Change one ownership boundary or section at a time.
4. Run the same positive, competing/negative, and safety/edge inputs against baseline and candidate.
5. Keep or restore the change before continuing.
6. Derive common compression only after the four-skill pilot.
7. Apply cohorts in descending body size; do not force small skills to shrink.
8. Run deletion ablation only after relocation and shared ownership stabilize.
9. Optimize descriptions and invocation metadata in a separate change lane.
10. Collect fresh 9.2.0 forward evidence before release identity changes.

Pilot skills:

- `design-frontend`: large primary with references and specialist composition.
- `workflow-comment-maintenance`: large primary without references and with missing structured behavior coverage.
- `analysis-router`: selectively implicit router.
- `design-visual-regression`: evidence-gate owner.

### Frozen Baseline Pilot Gaps

The frozen manifest makes the first oracle-enrichment batch explicit. These are properties of the pinned 9.1.2 baseline, not the enriched 9.2.0 working overlay:

| skill | reusable coverage | must be added before a body edit |
| --- | --- | --- |
| `design-frontend` | observable structured positive such as `design-030`; composition `design-004`; structured negative such as `design-033` or `design-035` | explicitly owned/tagged edge or safety case |
| `workflow-comment-maintenance` | primary `runtime-047`; composition `neg-workflow-comment-maintenance-002`; negative `neg-workflow-comment-maintenance-001` | schema-v2 typed positive and negative contracts, explicit eval mode for the positive, and edge/safety ownership |
| `analysis-router` | primary `route-grp-001` | explicit observed mode, schema-v2 typed negative with a competing non-null primary owner, and edge/safety ownership |
| `design-visual-regression` | observable structured positive `design-035`; composition `design-030`; structured negative `design-033` | explicitly owned/tagged edge or safety case |

Apply those additions as the shared oracle overlay, replay both frozen 9.1.2 and the unchanged candidate, and only then begin section relocation.

### Pilot Oracle Overlay

The 9.2.0 working overlay uses existing cases and only monotonic additions. It does not rewrite a request, primary route, or output shape.

| skill | structured positive | pure negative | composition or competing owner | edge or safety |
| --- | --- | --- | --- | --- |
| `design-frontend` | `design-030` | `design-033` | `design-004` | `design-037` (`safety`) |
| `workflow-comment-maintenance` | `runtime-047` | `neg-workflow-comment-maintenance-001` | `neg-workflow-comment-maintenance-002` | `runtime-047` (`safety`) |
| `analysis-router` | `route-grp-001` | `neg-002` | `route-001` with explicit `analysis-bug` primary | `route-001` (`edge`) |
| `design-visual-regression` | `design-035` | `design-033` | `design-030` | `design-035` (`edge`) |

`behavior_contract_owners` and `scenario_tags` are formal eval-schema fields. The comparator must report the overlay as `changed_allowed` under `--allow-oracle-contract-change`; any request or primary-route rewrite remains non-monotonic and fails.

For a monotonic overlay, paired-evidence scope comes from the changed case's explicit `behavior_contract_owners`, not every primary, supporting, or negative route association. An overlay change without an explicit owner fails closed. The current pilot overlay therefore admits exactly the four pilot skills rather than the fourteen adjacent skills named by their route cases.

### Pilot Section Ownership Maps

Each heading below has exactly one provisional owner. A destination may leave a short selector, safety residue, or pointer in the main body; the detailed prose still has one owner. `delete_candidate` remains an ablation candidate, not a deletion verdict.

| skill | destination | headings and target |
| --- | --- | --- |
| `design-frontend` | `main` | `Routing Card`; `Success Contract`; `Surface Profile`; `Workflow`; `Implementation Rules`; `Assets, Dependencies, and Generated Code`; `Conditional Evidence Gates`; `Validation and Status`; `Ask, Recover, or Stop`; `Output Contract` |
| `design-frontend` | `reference` | `Source Ownership and Trust` -> `references/product-family-profile.md` with the artifact-as-data security rule retained in main; `Product-Family Gate` -> `references/product-family-profile.md` |
| `design-frontend` | `schema_or_shared_contract` | `Loop Contract Consumption` -> loop contract and verifier-map contracts, retaining only this skill's verifier handoff |
| `design-frontend` | `delete_candidate` | `Known Limits` after its surviving claims are proved present in validation, recovery, visual, and accessibility gates |
| `workflow-comment-maintenance` | `main` | `Routing Card`; `Workflow`; `Behavior & Context Gate`; `Output Contract` |
| `workflow-comment-maintenance` | `schema_or_shared_contract` | `Cross-Skill Boundaries` -> the owning `source/platform/<platform>/context-routing.md`, retaining only the stop-and-handoff rule needed during execution |
| `workflow-comment-maintenance` | `eval` | `Invocation Examples` -> `runtime-047`, `runtime-048`, `neg-workflow-comment-maintenance-001`, and `neg-workflow-comment-maintenance-002` |
| `workflow-comment-maintenance` | `delete_candidate` | `Purpose`, whose distinct claims must first be shown in the description, Routing Card, workflow, or safety oracle |
| `analysis-router` | `main` | `Routing Card`; `Decision Table`; `Precedence and Mixed Requests`; `Context Budget and Stop Rule`; `Output Contract` |
| `analysis-router` | `delete_candidate` | `Boundary Checks`, whose four boundaries are already owned by the Routing Card, precedence rules, and risk profile |
| `design-visual-regression` | `main` | `Routing Card`; `Workflow`; `Validation`; `Do not invent / Unverified policy`; `Optional resources`; `Completion Boundary` |
| `design-visual-regression` | `reference` | `Output` -> `references/visual-diff-report-schema.md`; `Recovery` -> `references/viewport-policy.md` and `references/visual-diff-report-schema.md` after preserving the fail-closed selector in main |
| `design-visual-regression` | `schema_or_shared_contract` | `Loop Contract Consumption` -> loop contract and verifier-map contracts, retaining only the visual result payload |
| `design-visual-regression` | `delete_candidate` | `Known Limits` after its surviving claims are proved present in validation, recovery, and references |

There is no whole pilot heading whose correct destination is `script` or `existing_specialist_skill`. Scripts may own deterministic checks, and specialist skills may own their evidence, but neither can replace the pilot's semantic decision boundary.

### First Ablation Queue

Do not execute this queue until the local pilot gate below passes. Change one row at a time and keep or restore it before continuing.

| order | skill and unit | intended change | estimated body reduction | row-specific discriminator cases |
| --- | --- | --- | ---: | --- |
| 1 | `design-visual-regression` / `Output` | keep a findings-first selector and point the structured report to the existing schema reference | 45-62 words | `design-035`, `design-006`, `design-033` |
| 2 | `workflow-comment-maintenance` / `Invocation Examples` | remove runtime examples now owned by eval; retain one validation rule requiring syntactically valid patch artifacts | 77 words | `runtime-047`, `neg-workflow-comment-maintenance-001`, `neg-workflow-comment-maintenance-002` |
| 3 | `analysis-router` / `Boundary Checks` | removed duplicated boundary summary | 47 words | `route-grp-001`, `neg-002`, `route-001` |
| 4 | `design-frontend` / `Product-Family Gate` | keep one conditional fail-closed selector and use the existing profile reference for detail | about 120 words | `design-030`, `design-004`, `design-033`, `design-037` |

The queue targets roughly 300 body words without changing a Routing Card or description. Its current terminal decision is `retain_unverified` until the exact local paired evidence for that row is agent-reviewed and accepted. An accepted local result permits only a pilot keep/restore decision; it does not prove release preservation.

For a local pilot comparison, evidence scope is the single changed pilot skill and must satisfy its complete positive, pure-negative, composition/competition, structured, and edge coverage. The independent-signed release comparison remains scoped to every explicit overlay owner and affected consumer. Baseline evidence may be reused only when its source, model, oracle, and artifact bindings remain exact; signed release evidence must also retain exact signature bindings. Candidate evidence must bind the changed source.

Every comparison first runs `git merge-base --is-ancestor <baseline-commit> <candidate-commit>`. A worktree candidate is bound to its current `HEAD`; a ref candidate is bound to the resolved commit. Missing commit identity, an unrelated history, or a candidate that predates the baseline fails before evidence is admitted.

### Agent-Reviewed Local Pilot Gate

The local gate exists only to make reversible body-diet experiments possible before independent release review. It is deliberately a separate evidence tier from `independent_signed` and never upgrades a result to `preserved`.

The comparator accepts this lane only when all of the following are true:

1. `--allow-agent-reviewed-local-pilot` is explicit and the candidate is selected with `--candidate-worktree`; a candidate ref is forbidden.
2. Exactly one canonical skill body or bundled resource changes, and its skill id is one of `design-frontend`, `workflow-comment-maintenance`, `analysis-router`, or `design-visual-regression`.
3. No Routing Card, frontmatter description, trigger/invocation metadata, or skill-consumed shared execution context changes in the same comparison. Unowned process/audit docs may coexist because they are not admitted skill context. The already-declared monotonic pilot oracle overlay is allowed only at its pinned evaluation-contract digest; a new oracle edit in a body ablation fails closed.
4. Baseline and candidate use the same host id plus prompt, input, permission-profile, and validator digests, exact model id, case oracle, and evaluation-contract digest, and persist raw prompt, run, output, review, and verifier artifacts.
5. A named reviewer agent is distinct from the producer, reviews the raw pair against the complete case oracle, and the receipt binds that review. This is agent separation, not independent cryptographic attestation.
6. The changed skill's required positive, negative, composition/competition, structured, and edge cases all pass.

An accepted local pair reports `behavior: agent-reviewed`, `admission: unverified`, and `release_eligible: false`. Declared context packs are useful debugging records but cannot establish observed admission in this tier. `--require-paired-evidence`, `--allow-routing-card-change`, candidate refs, non-pilot skills, multiple changed skills, or missing local receipts fail closed. Without either valid local evidence or strict release evidence, any canonical skill-body or bundled-resource change still fails with `paired_behavior_evidence_missing`.

Later rows use the pinned local checkpoint at `docs/reference/skill-diet/local-pilot-accepted-state.json`. The comparator accepts it only through `--use-accepted-local-pilot-state`; callers cannot supply another path. The checkpoint's raw hash is pinned in the tool, its schema is `skill-diet-local-pilot-accepted-state.schema.json`, and every accepted entry binds its exact skill/content digests plus persisted evidence-manifest hashes. The loader reconstructs each ordered accepted prefix, reruns the complete paired semantic validator over the stored artifacts, and locks every routed skill's full content digests plus every admitted context unit. Only entries whose owner and evidence-bound dependencies still match the current candidate are removed from the one-new-skill count. If a later row changes an earlier row's dependency, rerun the affected evidence against the cumulative candidate and rebuild the checkpoint in dependency-first order; do not bypass the drift failure. Aggregate reduction and independent-signed release scope remain frozen-baseline-relative, and checkpoint entries remain `agent-reviewed`, admission-unverified, and release-ineligible.

State schema v2 also supports a contiguous `atomic_dependency_group` for a real mutual routed-skill dependency. Every member is evaluated against the group's shared closure prefix, must bind the same candidate tracked-input digest, and must participate in a strongly connected route graph proven by its persisted candidate runs. A singleton, non-contiguous set, one-way dependency, or ordinary convenience batch fails closed. This checkpoint-only SCC representation does not weaken the one-new-skill local comparison rule or make the evidence release-eligible.

### Historical Provisional Pilot Record

The earlier `d0b0514`-based checkpoint provisionally accepted all four rows: `design-visual-regression / Output` (-45 body words, -437 UTF-8 bytes), `workflow-comment-maintenance / Invocation Examples` (-77 words, -751 bytes), `analysis-router / Boundary Checks` (-47 words, -354 bytes), and `design-frontend / Product-Family Gate` (-118 words, -782 bytes). Those runs were useful for constructing the local comparison lane, but they do not bind the final `7484956` baseline and are not final keep decisions. The ignored `docs/reference/skill-diet/local-pilot-accepted-state.json` remains a historical campaign checkpoint and must not be treated as current release or non-pilot evidence.

### Final-Baseline T3 Re-adjudication

T3 compared the final baseline `74849564add4180a7118c8da513f380dc7c30a93` with provisional candidate `91aeb870e3d9734bc316aa403303c95f7b8d1857` using fresh `gpt-5.6-sol` producer runs and distinct paired reviewers under the same prompts, schemas, model, and read-only host profile. The initial 13 case/skill pairs produced 11 pair passes and two fail-closed signals. Targeted restoration and dependency replays then isolated each signal without weakening an oracle. The commit containing this section is the source checkpoint; its resolved commit and artifact hashes are recorded after commit in `docs/reference/skill-diet/goal-2026-07-14/T3-pilots.yaml`.

| unit | final decision | decisive evidence |
| --- | --- | --- |
| `design-visual-regression / Output` | `restore` | Initial `design-033` failed on both baseline and candidate because the prompt did not require an explicit `reused` status. A monotonic prompt clarification made the restored pair pass, but the original baseline instability means the deletion was not proved. |
| `workflow-comment-maintenance / Invocation Examples` | `restore` | Initial `runtime-047` passed on baseline and failed on the candidate because executable-line preservation was reported `unverified` despite inspectable static evidence. The restored candidate passed while a fresh baseline replay failed, confirming stochastic baseline instability as an additional fail-closed reason. |
| `analysis-router / Boundary Checks` | `keep` | `route-grp-001`, `neg-002`, and `route-001` passed baseline and candidate review with exact routing and no behavior regression. This is the only retained pilot reduction: 47 body words and 354 UTF-8 bytes. |
| `design-frontend / Product-Family Gate` | `restore` | Its first four pairs passed against the provisional dependency state. After restoring `design-visual-regression`, the required four-case dependency replay failed `design-030`: the compressed gate omitted `design-a11y-audit` and `design-tokens`. Restoring the full gate returned `design-030` to baseline/candidate pass. |

The general patch-syntax and hunk-count sentence proposed during `workflow-comment-maintenance` evaluation is owned by the eval/reviewer acceptance contract, not by that skill's main body. T3 therefore removes that sentence while restoring the original invocation examples. All T3 results remain `agent-reviewed`, `admission: unverified`, and `release_eligible: false`; only the retained `analysis-router` row is eligible for later independent-signed release replay.

### T4 Body Ownership Classifier

T4 classifies every top-level `##` section in the current 66-skill inventory. Each section receives exactly one provisional destination and one selector from this closed set:

```text
main
reference
existing_specialist
script
schema
eval
delete_candidate
```

The full source-bound matrix is local campaign evidence at `docs/reference/skill-diet/goal-2026-07-14/T4-body-ownership.json`. At checkpoint `1eac788906dc25ec303b6549f979a2dbba40a47a`, it covers 506 sections: 414 `main`, 7 `reference`, 12 `existing_specialist`, 4 `script`, 4 `schema`, 27 `eval`, and 38 `delete_candidate`. A `delete_candidate` is always initialized as `retain-unverified`; it cannot be deleted, merged, or moved until T9 names a discriminator and the same validator rejects an intentional violation. The classifier is an ownership proposal, not proof that a section is redundant or that a reference will be admitted.

### Routing Card v2 Candidate

The T4.1 candidate gives frontmatter `description` sole ownership of activation and exclusion. `Routing Card v2` retains only the selected skill's execution boundary: `role`, `expected_inputs`, `expected_outputs`, `context_targets`, `risk_profile`, and `entry_scene`. It therefore removes the card-local `intent_signature`, `use_when`, and `do_not_use_when` copies without changing the description.

Across a static 66-skill projection, the current card bodies measure 15,231 words and 119,593 UTF-8 bytes; the v2 projection measures 9,356 words and 76,415 bytes, a prospective delta of -5,875 words and -43,178 bytes. This is not observed admission. Fresh `gpt-5.6-sol` baseline/v2 producers and separate reviewers covered positive, negative, supporting/competition, edge, and safety routes for `design-frontend`, `workflow-comment-maintenance`, `analysis-router`, and `design-visual-regression`; all 12 case decisions passed on both representations with no observed route regression.

The candidate remains `not_adopted`. T4.1 changes no canonical Routing Card and does not authorize a 66-skill rollout. Adoption requires a separate source lane, complete affected-skill evidence, and the independent-signed release boundary required by the pilot exit gate.

### Exact-Prose Disposition Gate

T4.2 binds the final-baseline `test_skill_instruction_quality.py` source digest `2ca3b6b30c487f0753f23ae1f06696e08ebedae77db5b302d739092920f50d7d` and classifies all 97 `self.assertIn(...)` call sites. Eighteen are `literal-structure` contracts and 79 are `semantic-behavior` proxies; no call site is currently an `obsolete-candidate`, and T4.2 removes zero tests. The complete disposition ledger is local campaign evidence at `docs/reference/skill-diet/goal-2026-07-14/T4-exact-prose.json`.

A `semantic-behavior` proxy stays in place until its corresponding positive, negative/competing, and edge/safety behavior oracle passes first. A later exact-prose removal must cite that replacement receipt in the same ownership-unit record. Classification alone never authorizes weakening or deleting the assertion.

## Commands

From the bundle root, use the canonical tool while authoring and the generated `.codex` path while validating packaged runtime output:

```bash
python3 source/platform/codex/tools/compare_skill_diet.py snapshot \
  --root . \
  --source-ref baseline/9.2.0-pre-diet \
  --output source/shared/eval/baselines/skill-diet-9.1.2.yaml

python3 source/platform/codex/tools/compare_skill_diet.py check \
  --root . \
  --manifest source/shared/eval/baselines/skill-diet-9.1.2.yaml \
  --schema source/shared/eval/skill-diet-baseline.schema.json \
  --require-git-provenance

python3 source/platform/codex/tools/compare_skill_diet.py compare \
  --root . \
  --manifest source/shared/eval/baselines/skill-diet-9.1.2.yaml \
  --candidate-worktree \
  --allow-oracle-contract-change \
  --format text
```

`check` and `compare` load the canonical schemas automatically when `--schema` is omitted. In a Git checkout they also verify the pinned commit/tree/input digest automatically; the explicit flags above remain useful as readable release intent.

Before a release verdict, compare committed refs and require independent-signed paired behavior plus observed admission evidence. Worktree comparison is suitable for iteration but is not reproducible release evidence.

### Agent-Reviewed Local Pilot Evidence

Local pilot evidence uses `skill-diet-local-pilot-evidence.schema.json` schema v1 and the `agent_reviewed_local_pilot` verification tier. It binds the prompt, raw run, raw output, separate reviewer artifact, and verifier receipt for both sides. It has no signature field and is invalid if a signature or release-eligibility claim is added.

Use this lane for one queue row at a time:

```bash
python3 source/platform/codex/tools/compare_skill_diet.py compare \
  --root . \
  --manifest source/shared/eval/baselines/skill-diet-9.1.2.yaml \
  --candidate-worktree \
  --baseline-evidence <local-baseline-evidence.yaml> \
  --candidate-evidence <local-candidate-evidence.yaml> \
  --allow-oracle-contract-change \
  --allow-agent-reviewed-local-pilot \
  --format json
```

For a body-only local row, do not add `--affected-skill`; that option declares implicit consumers of changed shared context and is not a changed-skill selector. Also do not add `--require-paired-evidence`, `--candidate-ref`, or `--allow-routing-card-change`. Do not use a test helper that synthesizes observed routes or admission from expected values as production evidence. Keep or restore the row from the agent-reviewed behavior result, but leave admission unverified and repeat the accepted changes in the strict release lane before a 9.2.0 verdict.

For row 2 and later, add the pinned checkpoint flag:

```bash
  --use-accepted-local-pilot-state
```

Omit it for the first row. After a later row passes, persist its raw comparison/evidence bundle, add it to the dependency-first ordered checkpoint, update the tool's pinned checkpoint hash, regenerate targets, and only then start the next row.

### Independent-Signed Release Evidence

Release paired evidence uses `skill-diet-evidence.schema.json` schema v2 and the `independent_signed` verification tier. Baseline and candidate documents must bind the same exact model, evaluation-contract digest, and `(skill_id, case_id)` set to their respective commit/tree/tracked-input digest. A summary `pass` is not evidence. Every case requires three persisted artifacts:

1. raw run trace: source, model, eval mode, observed primary/supporting route, target invocation, exact admitted context units, and the execution contract defined below;
2. raw model output;
3. verifier receipt bound to the run hash, output hash, complete case-oracle hash, and every typed `required_evidence` requirement hash.

The initial `skill-diet-trusted-reviewers.json` is intentionally empty, so no release run can claim preservation yet. Bootstrap one independent reviewer before the release gate in a separate reviewed trust change: generate the private key outside the producer environment, add only its reviewer id/RSA public modulus/exponent/fingerprint to the canonical store, and update the tool's pinned store digest. Never combine trust bootstrap with a skill-body reduction.

```json
{
  "reviewer_id": "reviewer-stable-id",
  "algorithm": "rsa-pkcs1v15-sha256",
  "modulus_hex": "<lowercase public modulus without leading zeroes>",
  "exponent": 65537,
  "fingerprint_sha256": "<tool reviewer_key_fingerprint result>"
}
```

The private exponent never belongs in the repository, evidence bundle, command line, or producer environment.

After the independent reviewer supplies only its public modulus and exponent, normalize and fingerprint the public entry with:

```bash
python3 source/platform/codex/tools/compare_skill_diet.py reviewer-entry \
  --reviewer-id <stable-reviewer-id> \
  --modulus-hex <public-modulus-hex> \
  --exponent 65537
```

This command accepts public material only. It does not generate, read, or validate possession of the private key; the reviewer proves possession later by signing the exact verifier receipt bytes.

Artifact paths are relative to the evidence YAML. Absolute paths, traversal, symlinks, missing files, stale byte counts, and stale hashes fail closed. Hash consistency alone is self-attestation, so each verifier receipt also requires an RSA PKCS#1 v1.5 SHA-256 signature from a reviewer whose public key is present in the pinned canonical trust store. The reviewer keeps the private key outside the repository and producer boundary. The comparator accepts no caller-supplied trust store or key.

```yaml
schema_version: 2
evidence_id: pilot-design-frontend-baseline
generated_at: <RFC3339 timestamp>
source:
  commit: <full commit>
  skills_tree: <source/skills tree>
  tracked_input_digest: <snapshot digest>
model: <exact model id>
eval_contract_digest: <shared oracle contract digest>
runs:
  - run_id: <unique run id>
    case_id: <case id>
    skill_id: design-frontend
    reviewer_id: <pinned reviewer id>
    case_oracle_sha256: <complete public case digest>
    execution_contract_sha256: <canonical execution-contract digest>
    run_artifact:
      path: artifacts/<run>.run.json
      sha256: <artifact digest>
      utf8_bytes: <artifact bytes>
    output_artifact:
      path: artifacts/<run>.output.md
      sha256: <artifact digest>
      utf8_bytes: <artifact bytes>
    verifier_receipt:
      path: artifacts/<run>.verify.json
      sha256: <artifact digest>
      utf8_bytes: <artifact bytes>
    verifier_signature: <RSA signature over exact verifier receipt bytes, lowercase hex>
```

The run trace uses `admitted_context` entries shaped as `{path, content_unit, sha256, words, utf8_bytes}`. It may name any indexed canonical skill, shared, or platform context unit. It also contains an `execution_contract` mapping with exactly `host_id`, `prompt_sha256`, `input_sha256`, `permission_profile_sha256`, and `validator_sha256`; its canonical JSON digest must equal `execution_contract_sha256` in the evidence entry and verifier receipt. Every field must match across the pair. Observed primary/supporting routes must exactly match the full case oracle, forbidden skills must remain absent, and every invoked primary/supporting skill must have its full `SKILL.md` in the admission trace. The verifier receipt must contain an exact one-to-one `required_evidence_results` match for the case; matching only evidence type names is insufficient because the full requirement, including expected values, is hashed.

A paired pass alone never authorizes a deletion. Before a section, paragraph, or sentence receives `delete`, `merge`, or `move-to-reference`, bind its unique obligation to at least one case or typed evidence requirement and run the same validator against an intentionally violating output or oracle-preserving mutation. If that control is not rejected, or no discriminating case exists, the only permitted deletion-lane disposition is `retain-unverified`.

For every changed skill, the paired set must cover:

- one primary positive case, or one supporting positive for a support-only skill;
- one schema-v2 pure negative case with typed required evidence;
- one composition case when the skill has a supporting role;
- one competing-owner negative for an implicitly invocable router;
- one schema-v2 behavior-owned positive case with explicit `host-assisted` or `replay` mode (primary, or explicitly owned supporting for a support-only skill);
- one explicitly owned `edge` or `safety` case.

Missing contracts and missing runs are distinct failures. Do not infer edge ownership from prose. Declare it with `behavior_contract_owners` and `scenario_tags` before editing the skill.

When evaluation contracts are strengthened before a body edit, use the candidate evaluation contract as an explicit oracle overlay for both baseline and candidate executions. Keep the 9.1.2 source binding unchanged, bind both evidence documents to the candidate `eval_contract_digest`, and pass `--allow-oracle-contract-change`. This preserves the frozen instruction baseline while testing both sources against the same stronger oracle.

The allow flag is monotonic, not blanket permission. It accepts new cases and additions to expected/forbidden behavior, required evidence, negative/supporting boundaries, explicit owners/tags, schema version, and eval-mode strength. It rejects removals, request/primary-route changes, and other non-monotonic rewrites. Use a new case ID when the scenario itself changes.

Use both receipts for a paired verdict:

```bash
python3 source/platform/codex/tools/compare_skill_diet.py compare \
  --root . \
  --manifest source/shared/eval/baselines/skill-diet-9.1.2.yaml \
  --candidate-ref <candidate-commit> \
  --affected-skill <changed skill id> \
  --baseline-evidence <baseline-evidence.yaml> \
  --candidate-evidence <candidate-evidence.yaml> \
  --evidence-schema source/shared/eval/skill-diet-evidence.schema.json \
  --allow-oracle-contract-change \
  --require-paired-evidence \
  --format json
```

Only this independent-signed lane can produce `behavior: preserved`, `release_eligible: true`, or an observed admission improvement claim. Missing, failed, unsigned, unknown-reviewer, invalid-signature, model-mismatched, case-set-mismatched, scope-incomplete, stale-hash, source-mismatched, oracle-mismatched, or verifier-unbound receipts cannot produce those results. Admission is `improved` only when no paired case increases and at least one paired case decreases. Intentional eval-contract or Routing Card work uses its explicit allow flag in a separate reviewed lane; the default structural-diet comparison remains fail closed.

The snapshot derives shared-context consumers from exact skill references; global routing and platform instruction files always map to all 66 skills. `--affected-skill` may only add implicit/catalog-driven consumers and can never narrow the derived set. Every derived or added consumer must observe the changed shared file in the applicable baseline/candidate receipt.

## Pilot Exit Gate

Do not adopt a shared `Routing Card v2` or roll out across 66 skills until:

- all four pilot skills have explicit ownership maps;
- their positive and competing/negative contracts are preserved;
- material safety/edge cases have explicit owners;
- body, owned inventory, declared exact admission, and observed admission are reported separately;
- no routing/invocation change is hidden inside structural relocation;
- each pilot change has a keep/restore decision supported by agent-reviewed local paired evidence;
- every retained pilot change is replayed with independent-signed paired evidence before the release verdict or cross-bundle rollout.
