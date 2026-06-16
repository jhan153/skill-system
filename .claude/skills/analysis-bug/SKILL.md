---
name: analysis-bug
description: "Repro-and-evidence-first workflow for recurring, unclear, or high-risk failures: lock repro, collect evidence, choose one primary root cause, compare fixes, and verify."
---

# Deep Bug Analysis

## Routing Card
- role: primary
- intent_signature:
  - `deep-bug`, `deep-debug`, `root-cause`, `rca`, `원인 분석`, `버그 분석`
- use_when:
  - the user needs reproducibility, evidence collection, root-cause selection, fix comparison, or validation.
  - implementation is requested after a credible diagnosis.
- do_not_use_when:
  - the request is pure algorithm selection, pure architecture design, or a quick obvious patch.
- expected_inputs:
  - symptom or observed failure
  - expected behavior
  - repro steps or triggering condition when available
  - logs, failing output, or relevant source files when available
- expected_outputs:
  - repro contract, evidence, one primary root cause, fix options, validation result or plan
- context_targets:
  must_read:
    - symptom and expected behavior
    - repro steps or explicit `Unverified` gap
  read_if_needed:
    - relevant source files and tests
    - logs or command output
    - repo validation contract when implementation is requested
  do_not_load_by_default:
    - full repo
    - full memory bank
    - codebase-wide report artifacts
- risk_profile:
  reads:
    - READ_CODEBASE for targeted diagnosis
  writes:
    - WRITE_CODEBASE only in `diagnosis+fix` mode
  tools:
    - CALL_PROCESS only for targeted repro, test, or validation commands
  sensitive_resources:
    - credentials default deny; inspect only explicit non-secret config signals
- entry_scene:
  - PREPARE

## Related Skills
- `analysis-router`: router and backward-compatible entry point.
- `workflow-rigor`: owns execution rigor, review, and completion gates when implementation is requested.
- `report-qualitative`: owns final formal report shape when explicitly active.
- `analysis-algorithm`: use after diagnosis when the remaining question is which new approach should replace the current one.

## Trigger
- `deep-bug`
- `deep-debug`
- `root-cause`
- `rca`
- `why broke`
- `재현`
- `원인 분석`
- `버그 분석`

## Trigger Guard (Do Not Trigger)
- Pure algorithm/model/pattern selection with no current failure to diagnose.
- Pure architecture/HLD/LLD requests.
- Quick local patch requests where the failure and fix are already obvious.
- Information-only requests that do not need diagnosis or implementation.

## Goal
- Explain why the current behavior is wrong.
- Converge on one primary root cause.
- Compare credible fixes before changing code.
- Verify the selected fix against the original repro.

## Modes
- `diagnosis-only`: stop after root cause, fix options, and validation plan.
- `diagnosis+fix`: continue into implementation and verification when the user asks for the change.

## Required Inputs
- symptom or observed failure
- expected behavior
- repro steps or triggering condition when available
- environment or version context when relevant
- missing information must be marked `Unverified`

## Mandatory Sequence
1. Lock a repro contract.
2. Gather evidence from call path, state/data flow, and time/frequency when available.
3. Decide one primary root cause.
4. Compare 2-3 fix options.
5. If implementation is requested, follow runtime approval and execution rules.
6. Verify against the original repro and report the delta.

## Step 1) Repro Contract
- Lock all three:
  - repro behavior
  - failure condition
  - expected result
- If one is missing, ask one short clarifying question or mark it `Unverified`.

## Step 2) Evidence Collection
- Prefer these evidence classes:
  1. call path
  2. state/data flow
  3. time/frequency
- If one class is unavailable, say why and mark it `Unverified`.
- No fix recommendation without evidence.
- No implementation without enough evidence to justify the change.

## Step 3) Root Cause Decision
- State one primary root cause.
- List up to two secondary factors only if they materially affect the fix or recurrence risk.
- Do not report a basket of vague suspects as the final answer.

## Step 4) Fix Option Comparison
- Compare 2-3 credible fixes using:
  - change scope
  - recurrence risk
  - stability/performance impact
  - observability/debuggability impact
  - rollback cost
- Select one primary fix.
- If the user asked only for analysis, stop after recommending the fix and validation plan.

## Step 5) Implementation Rules
- Implementation is optional and only applies in `diagnosis+fix` mode.
- Respect runtime approval and sandbox policy before mutating files or state.
- Prefer the smallest fix that resolves the primary root cause without hiding it.
- Avoid patch-chaining and indefinite dual paths.

## Step 6) Verification Rules
- Always split verification into:
  - `validation_agent`
  - `validation_user`
- `validation_agent`: checks the agent actually ran.
- `validation_user`: runtime or manual checks still needed from the user, or `N/A` with reason.
- Include a short before/after delta with behavior or numbers.
- If a check could not be run, mark it `Unverified`.

## Resource and Risk Boundary
- Reads: targeted code paths, tests, logs, and repro evidence.
- Writes: none in `diagnosis-only`; code writes only in `diagnosis+fix` after root cause selection and repo validation context.
- Tool/process calls: limited to repro, targeted tests, static checks, and non-destructive diagnostics.
- Network access: none by default; require data boundary awareness if repro depends on external services.
- Credential access: default deny.
- Generated artifacts: only temporary evidence or requested fix artifacts.
- Destructive actions: never use as diagnosis shortcuts; require explicit user intent and runtime policy approval.
- Required checkpoints: root cause evidence before edits, command purpose before CALL_PROCESS, validation contract before WRITE_CODEBASE.

## Recovery and Context Expansion
- If repo structure is unclear, read repo source outline first.
- If test command is unclear, read repo validation contract.
- If architecture boundary is unclear, read nearby module docs or architecture rules.
- If user goal is unclear, state the assumption rather than loading unrelated context.
- If verification fails, read the failing output and changed hunk before expanding wider.
- If the issue is actually approach selection, return to scheduling and use `analysis-algorithm`.
- Never recover by loading all memory, all repo docs, or all skills at once.

## Output Contract
1. Problem summary
2. Repro contract
3. Evidence
4. Primary root cause
5. Fix options considered
6. Recommended or implemented fix
7. Verification
8. Remaining risks or missing info

## Output Templates
### Problem Summary Template
```markdown
problem summary
- symptom:
- expected behavior:
- current impact:
```

### Repro Contract Template
```markdown
repro contract
- repro behavior:
- failure condition:
- expected result:
```

### Evidence Template
```markdown
evidence
- call path:
- state/data flow:
- time/frequency:
```

### Root Cause Template
```markdown
root cause
- primary:
- secondary factors:
```

### Fix Comparison Template
```markdown
fix option A
- change scope:
- recurrence risk:
- stability/performance impact:
- observability impact:
- rollback cost:

fix option B
- change scope:
- recurrence risk:
- stability/performance impact:
- observability impact:
- rollback cost:

selected fix
- recommendation:
- selection reason:
```

### Verification Template
```markdown
verification
- validation_agent:
- validation_user:
- before/after delta:
```

## Effectiveness Metrics
- `repro_defined_rate`
- `evidence_complete_rate`
- `single_root_cause_rate`
- `fix_option_comparison_rate`
- `verification_presence_rate`
- `recurrence_after_fix`

## Metrics Logging Rules
- Include one `metrics:` line only when the user asked for a formal or structured report.
- Example:
  `metrics: repro_defined_rate=5/5, evidence_complete_rate=4/5, single_root_cause_rate=5/5, fix_option_comparison_rate=5/5, verification_presence_rate=5/5, recurrence_after_fix=Unverified`

## Anti-Patterns
- Code edits before a credible root cause is identified.
- "Maybe one of these three things" as the final root cause.
- Test-passing-only fake fixes.
- Treating missing runtime verification as passed.
- Reporting LOC or churn instead of causal evidence.

## Known Limits
- Root cause cannot be confirmed without repro, log, test, or direct observation evidence.
- Static inspection may miss runtime, environment, concurrency, or generated-code behavior.
- If context targets are insufficient, return to scheduling before broad scans.
- Do not weaken tests or add bypasses to hide the symptom.
