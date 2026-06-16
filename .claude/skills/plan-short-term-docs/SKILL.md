---
name: plan-short-term-docs
description: docs/plan 하위의 지속 플랜 문서를 생성·갱신하고, 질의/결정/TODO를 동기화하며, 현재 활성 플랜 범위 안에서 구현 전환을 관리한다. 사용자가 실제 플랜 문서나 active plan artifact를 원할 때 사용하며, "플랜" 단독 언급만으로는 발동하지 않는다.
---

# Plan Short Term Docs

## Routing Card
- role: primary
- intent_signature:
  - persisted docs/plan artifact, active plan document, 플랜 문서 생성/갱신, 플랜 구현 전환 관리
- use_when:
  - the user asks to create or update a persisted plan document under `docs/plan`.
  - an active planning conversation already owns a plan artifact.
- do_not_use_when:
  - `플랜` is a casual mention without artifact intent.
  - the user asks to execute or implement an active plan without requesting plan artifact synchronization; use the task-specific implementation workflow and treat this skill as secondary status tracking only when needed.
  - the task is a small local edit, one-off conceptual explanation, or heavy phase package request.
- expected_inputs:
  - planning goal
  - repo root and active plan path when available
  - questions, decisions, TODOs, risks, validation strategy
- expected_outputs:
  - updated plan artifact, synchronized Q&A/TODO/status, implementation transition state
- context_targets:
  must_read:
    - active plan file or plan template
    - current planning request
  read_if_needed:
    - repo source outline for code-impacting plans
    - relevant memory cards
    - validation contract
  do_not_load_by_default:
    - phase package templates
    - full memory bank
    - full repo
- risk_profile:
  reads:
    - active plan and targeted repo context
  writes:
    - docs/plan artifacts only before implementation transition
  tools:
    - none by default
  sensitive_resources:
    - credentials default deny
- entry_scene:
  - PREPARE

## Core Objective
- Use `docs/plan` as the single source of truth during planning conversations.
- Keep the plan document synchronized with user feedback and newly discovered work.
- Enforce implementation start only after clear current-task approval and runtime permission.

## Activation
- Activate when the user requests a persisted plan artifact, asks to create/update `docs/plan`, or continues an active plan document.
- Do not activate from a casual `플랜` mention unless the surrounding request asks for a real plan artifact or active plan synchronization.
- Continue using this workflow for plan synchronization until the user clearly closes or switches scope.
- After clear implementation transition, this workflow becomes a support tracker; it must not displace the task-specific implementation workflow.

## Related Skills
- `workflow-rigor`: owns runtime approval/sandbox compliance, execution rigor, validation, and review when implementation starts.
- `report-qualitative`: owns the final formal report shape when the user explicitly asks for it.
- `report-critical`: use as a QA gate for plan artifacts when the user asks for review.
- `research-hypothesis-planning`: owns research hypothesis, experiment, ablation, loss, and training-plan content before this skill writes a persisted `docs/plan` artifact.

## Research Plan Boundary
- If the requested plan is a research hypothesis, experiment, ablation, loss, or training plan, `research-hypothesis-planning` owns the plan content.
- Use this skill only as the persisted artifact writer when the user explicitly asks to store the research plan under `docs/plan`. Research Cluster artifact chains remain owned by their narrow research skills.
- If the user asks for an implementation plan for already chosen development work, do not route to `research-hypothesis-planning` merely because the plan mentions model, metric, experiment, or loss.

## Implementation Transition Gate
- Use clear current-task implementation intent as the transition signal from planning to implementation.
- Common examples include:
  - `구현 시작`
  - `플랜 구현해`
  - `플랜 작업해`
  - `플랜 승인 후 구현`
  - `이 플랜대로 구현 시작`
- These are task-local intent markers, not the source of runtime permission by themselves.
- Avoid treating one-word replies such as `승인`, `작업해`, `구현해` as sufficient by themselves unless the active plan scope is explicitly restated in the surrounding context.
- Before transition:
  - Do not edit production code.
  - Update only plan artifacts.
- When implementation is requested:
  - Verify runtime approval and sandbox policy before mutating files or state.
  - Hand execution to the task-specific implementation workflow; use the active plan as input.
  - Start implementation only for the active plan scope.
  - Do not satisfy the implementation request by only editing `docs/plan`, TODO status, questions, or transition metadata.
  - Keep logging additional findings and follow-up tasks back into the plan TODO list as secondary bookkeeping.
  - Completion requires source, test, runtime config/build, or executable scaffold changes tied to the plan, unless the user explicitly narrowed the request to documentation only or a blocker prevents implementation.

## Plan File Rules
- Create or update a task plan file under `docs/plan/`.
- Prefer filename format: `docs/plan/YYYY-MM-DD-<task-slug>.md`.
- Reuse the existing active plan file for the same task.
- Keep all plan sections current; never leave contradictory states between sections.

## Mandatory Plan Content
- Include these sections at minimum:
  - Changed file list
  - Change summary (`what` and `why`)
  - Risks
  - Validation procedure
  - Questions and answers (`질의`)
  - TODO list with status
  - Implementation transition status
- Use a Mermaid diagram only when runtime interaction, control flow, or concurrency is materially relevant, or when the user explicitly asks for one.
- If a sequence diagram is included for LLD, it must describe runtime interactions rather than agent workflow steps.

## Evidence Rules
- Always show current state and planned next state for meaningful changes.
- For code changes, always use two separate markdown code blocks.
- Never merge code before/after into one block.

Use this exact structure for code evidence:

### 변경 전
```cpp
printf("");
```

### 변경 후
```cpp
std::cout << "";
```

For formula changes, separate old/new formulas clearly:

### 수식 변경 전
$$f_{old}(x) = x^2 + 1$$

### 수식 변경 후
$$f_{new}(x) = x^2 + 2$$

For structural changes, recommend suitable diagrams by context:
- Class design change: class diagram
- Interaction flow change: sequence diagram
- System boundary/component change: architecture diagram
- Data model change: ERD

Recommendation is context-driven, not a hard requirement for every minor edit.

## Conversation Update Loop
- On each planning turn:
  - Capture new user questions in `질의`.
  - Provide detailed answers in the plan document, not only in chat.
  - Add discovered implementation tasks into TODO with owner/status.
  - Reflect decisions and constraints immediately.
- During implementation:
  - If new ambiguity or additional scope appears, append TODO and related question item.
  - Request user direction through updated plan items.

## Resource and Risk Boundary
- Reads: active plan, plan template, narrow repo source outline, relevant memory cards, and validation contract when needed.
- Writes: `docs/plan` artifacts only until clear implementation transition; production code writes belong to the implementation workflow.
- Tool/process calls: none by default; validation commands require command purpose and repo validation context.
- Network access: none by default.
- Credential access: default deny.
- Generated artifacts: single active plan file unless the user requests a broader package.
- Destructive actions: out of scope.
- Required checkpoints: artifact intent before plan writes, implementation intent before code writes, runtime policy before mutation.

## Recovery and Context Expansion
- If active plan path is unclear, search only `docs/plan` for the relevant current plan.
- If repo structure is unclear, read repo source outline first.
- If validation command is unclear, read repo validation contract.
- If user goal is unclear, state the assumption or ask one focused question rather than loading unrelated context.
- If the task needs multi-phase cross-session package docs, return to scheduling and use `plan-long-term-package`.
- Never recover by loading the full repo, full memory bank, or all planning packages at once.

## Implementation Transition
- When clear current-task implementation approval is detected and runtime policy allows mutation:
  - Mark the transition as approved with timestamp.
  - Freeze current plan baseline.
  - Start the corresponding source, test, runtime config/build, or executable scaffold work in TODO order.
  - Continue to update TODO statuses (`todo`, `doing`, `done`, `blocked`).

## Reference
- Use `references/plan-template.md` as the default skeleton.

## Known Limits
- Plan artifacts reflect known decisions; they do not prove implementation feasibility without validation.
- Casual `플랜` mentions do not activate this workflow by themselves.
- Active plan context may be stale; confirm the current task scope before implementation transition.
- Return to scheduling for phase packages, repo-wide reports, or implementation ownership.
- Markdown-only plan edits are not implementation completion unless the user explicitly requested plan/document work only.
