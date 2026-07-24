# User Work Contract

The user work contract is the execution authority shared by direct work,
TaskRun, and LoopRun. It is formed from explicit natural-language intent; users
do not need to author YAML or know field names. Persisted execution artifacts
use `schemas/task/work-contract.schema.json`.

## Priority And Ownership

Safety and platform-enforced constraints remain authoritative. Inside that
boundary, apply:

1. explicit user goal, scope, exclusions, verification owner, interaction
   mode, and stop terms;
2. mandatory project contracts;
3. selected workflow or skill;
4. generic validation guidance;
5. agent-selected quality improvements.

A later workflow may refine an unspecified field but must not relax an explicit
exclusion, change verification ownership, or turn optional support work into a
required deliverable.

## Work Classes

- `core`: a user-requested deliverable;
- `required_prerequisite`: work without which a core deliverable cannot be
  produced;
- `agent_validation`: agent-run checking or runtime observation;
- `test_authoring`: tests added as supporting evidence rather than a requested
  deliverable;
- `validation_artifact`: wrappers, harnesses, fixtures, probes, traces, or
  surrogate apps created to validate;
- `optional_quality`: review or improvement beyond the requested outcome;
- `meta`: staging, checkpoint, reporting, cleanup, or orchestration management.

`core` and genuinely necessary prerequisites are required by default. The
other classes are optional unless the accepted user/project contract explicitly
makes one a deliverable or exit gate.

## Local Deferral

Before scheduling an action or asking for permission:

1. classify its purpose, requiredness, dependencies, and interaction need;
2. prune actions excluded by the active contract before they become runnable;
3. when one action is blocked, mark that action `deferred` and reevaluate the
   remaining graph;
4. continue any independent required runnable action;
5. use global `blocked` only when no required runnable action remains.

A mixed plan is rewritten non-blockingly when at least one in-contract item
remains: excluded or already-deferred items are removed, their semantic
purposes are recorded as deferred, and the remaining plan proceeds. A plan
containing no in-contract item is denied as a last resort. Side-effecting tools
are never rewritten into no-ops because that would misreport skipped work as
success; an unexpected execution attempt remains a deny boundary.

A deferred purpose keeps one stable semantic `intent_key`. Changing the tool,
command form, wrapper, or validation method does not create a new intent.
Deferred work is not successful work.

## Attended Versus Unattended Execution

`interaction.mode: forbidden` becomes a runtime non-waiting deny only when the
active natural-language or accepted v3 LoopRun projection also declares
`execution.mode: unattended_goal_loop`. LoopRun activation alone does not
convert an `attended` contract into this profile. Ordinary attended work and
Goal/Loop contracts that allow interaction retain the host's normal approval
behavior.

In an unattended Goal/Loop, an approval or question is denied/deferred before
the UI wait begins. The executor then continues other required runnable work.
If none remains, it reports `blocked` with the exact unmet requirement instead
of asking repeatedly.

## Completion And Evidence

Deliverable completion and verification outcome are separate:

- implementation complete + matching evidence → `agent-verified`;
- implementation complete + user-owned check outstanding →
  `user-verification-needed`;
- implementation complete + evidence unavailable without a user-only check →
  `unverified`;
- required deliverable or prerequisite cannot proceed and no independent
  required work remains → `blocked`.

`user-verification-needed` and `unverified` never mean verifier pass. They are
normal handoff labels and must not trigger new tests or validation artifacts
solely to promote the label.

## Runtime Projection And Privacy

Host hooks may persist a bounded projection containing normalized execution
mode, verification owner, interaction mode, excluded action classes, prompt
digest, and deferred intent keys. They must not persist raw prompts, command
text, transcripts, or credentials. TaskRun and LoopRun own their explicit
contract references and condition/step state.
