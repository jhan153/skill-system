# Loop Verifier Catalog

Read this only when a condition needs a cross-domain, quality, human, or governance verifier. The runtime contract remains authoritative.

## Two-Layer Verifier Model

Every required `SC-NNN` has exactly one runtime verifier. Every receipt carries `kind`, `verifier_owner`, timezone-aware `observed_at`, `outcome`, and durable `artifact_ref` / `artifact_scope` / `artifact_sha256`; use only the schema vocabulary:

| runtime type | use | v2 receipt / closure |
| --- | --- | --- |
| `command_exit` | deterministic test/build/query command | common/artifact fields plus `command`, `exit_code`; local v2 rejects claimed pass without host attestation |
| `artifact_exists` | exact required file presence and digest only | common/artifact fields; the only local v2 auto-pass type |
| `diff_scope` | bounded changed-file/content scope | common/artifact fields plus `checked_path`; local v2 rejects claimed pass without host attestation |
| `manual_check` | user-only acceptance that cannot be automated | bound procedural event fields; local v2 keeps it open without host-authenticated user provenance |

Visual, accessibility, state, and review checks are optional **quality verifiers**, not runtime types:

```yaml
quality_verifier:
  owner: design-visual-regression
  type: visual|a11y|state_check|review
  evidence_target: path/to/review-report
```

A quality verifier should emit a durable report, screenshot set, or command result. In local v2 those outputs remain audit evidence: semantic `command_exit`/`manual_check`/`diff_scope` pass is fail-closed until a host-authenticated producer exists. `artifact_exists` can close only a separate “this exact artifact exists” condition. Do not encode `visual`, `a11y`, `review`, or `state_check` in the runtime contract.

## Evidence Choice

Use the strongest check that proves the statement without overclaiming:

1. deterministic command or state query;
2. current artifact/diff with digest and independent owner;
3. quality review over concrete artifacts;
4. explicit user acceptance when the evidence is private or subjective.

Maker self-report and free-form evidence references never prove pass. A receipt must match the canonical iteration-result schema and the condition's runtime verifier; `observed_at` must include a timezone and file-backed `artifact_ref` must be relative. `user-verification-needed`, `unverified`, and `blocked` remain open states.

## Independence

| level | meaning |
| --- | --- |
| `maker` | produced the change; useful context, insufficient alone where bias is possible |
| `checker` | separate command or skill evaluates the evidence; default for required quality gates |
| `external` | CI, browser, service, or source system observed the state |
| `human` | user accepted a named scope; requires a durable accepted manual receipt |

## Common Owners

| need | likely owner | evidence target |
| --- | --- | --- |
| build/test/schema | task owner or `workflow-validation` | command output and exit code |
| rendered route/smoke | browser/task owner | route response, console result, screenshot |
| repeated failure diagnosis | `workflow-recovery` | narrowed repro and failure fingerprint |
| plan/package structure | plan skill validator | artifact path and validation result |
| critical review | `report-critical` | anchored finding report |
| source/search claim | current task owner with one direct evidence lane, or `search-deep-evidence` when several independent lanes are required | cited source refs and gaps |
| memory/knowledge context | owning harness | admitted/excluded claim refs |
| live write/deploy | owning workflow plus approval gate | approval, idempotency key, result, rollback note |

### Design quality

| condition | quality owner | durable output for runtime evidence |
| --- | --- | --- |
| nonblank/framed render | `design-visual-regression` | viewport screenshot and finding report |
| layout/fidelity/responsiveness | `design-visual-regression` | comparison report plus screenshot/diff refs |
| keyboard/semantics/contrast | `design-a11y-audit` | a11y report with tool/manual observations |
| token/source mapping | `design-tokens` | mapping report and source refs |
| variants/states | `design-component-mapper` | state matrix |

Build success does not prove visual or accessibility quality. Artifact existence proves only that the quality report exists; naming an owner or pass statement does not make the runtime inspect the report. Use a verdict-producing command or accepted manual gate for the semantic condition.

## Unavailable Evidence

| situation | result |
| --- | --- |
| exact required artifact path exists and digest matches | `artifact_exists` may emit a passing receipt |
| command/manual/diff evidence exists but lacks host attestation | `unverified` or `user-verification-needed`; no pass |
| verifier ran and the fail signal is present | `fail` |
| known verifier cannot run here | `unverified` |
| user/private/manual acceptance is still needed | `user-verification-needed`, blocking |
| required input, permission, artifact, or environment is absent | `blocked` |

A procedural user event can be recorded as `manual_acceptance`, but local v2 cannot authenticate its actor and therefore does not convert the condition to pass. Never reinterpret an unavailable label as accepted evidence.

## Metrics And Anti-Gaming

Add metric verifiers only when the contract makes the claim:

| metric | anchor | reject |
| --- | --- | --- |
| improvement | condition/evidence delta | edit or tool-call count |
| safety | approval and unsafe-action record | hidden or implied approval |
| verifier health | coverage, freshness, status counts | confidence replacing a check |
| efficiency | iterations and repeated failures | more agents as progress |
| process | strategy/recovery/checkpoint events | unrecorded thrashing |
| outcome | required pass receipts and stop reason | proxy metric or open gate |

For every required condition, record pass/fail signals, freshness, owner, evidence target, unavailable behavior, and shortcuts that could falsely satisfy it. Do not weaken a condition, delete failing evidence, or substitute an easier proxy during execution.

## Mapping Workflow And Semantic Ceiling

For an existing condition slice, preserve `contract_id` and `SC-NNN`; split only conditions that combine independently failing material outcomes.

1. Label companion-only scope `structural`, `runtime`, `semantic`, or `user-only`, and oracle origin as user decision, canonical source, external contract, formal invariant, observed production behavior, or agent-authored evidence.
2. Assign exactly one runtime owner/type and name the real command/path/check, evidence target, pass/fail signals, freshness, receipt target, and unavailable behavior.
3. Add a separate quality verifier only when visual, accessibility, state, or review judgment is needed.
4. Preserve every `fail`, `needs_review`, `unverified`, `blocked`, or `user-verification-needed` state. Record one evidence-producing fallback only when one exists.

Evidence closes only the condition and scope it observes. `artifact_exists` closes only exact existence/digest conditions; never substitute it for semantic behavior. Agent-authored tests and mocks prove their encoded boundary, not a semantic or user-path oracle. Source selection, migration, transformation, external integration, and policy-owning adapters require authoritative input plus actual-path readback. A lower-scope pass cannot downgrade an unresolved higher-scope condition.

The local v2/v3 evaluator auto-passes only exact `artifact_exists` evidence. `command_exit`, `manual_check`, and `diff_scope` remain audit candidates without host-authenticated attestation. User-owned acceptance ends as `user_verification_needed`; contract changes require explicit re-acceptance.

## Quality Gate

- IDs are `SC-NNN` and align with the runtime contract.
- Exactly one runtime verifier uses one of the four schema types.
- Optional quality verifiers are separate and produce durable evidence.
- Maker/checker separation is explicit where bias is possible.
- Missing or user-only evidence blocks success.
- Every pass must be backed by a structured receipt, not agent confidence.
