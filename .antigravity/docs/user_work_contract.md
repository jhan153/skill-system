# User Work Contract

The user work contract is the execution authority shared by direct work and canonical
Plan/Handoff execution. It is formed from explicit natural-language intent; users do not need to
author YAML or know field names. A portable machine shape remains available at
`schemas/task/work-contract.schema.json`.

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

## Contract Identity And Lifecycle

The physical runtime state may be namespaced by a host session, but that storage key is not the
semantic contract identity. Each active contract has an opaque, content-free `contract_id` that
survives ordinary same-goal turns and compaction.

- A leading `/goal` or explicit work-contract rebind starts a new generation from defaults plus the
  policy stated in that prompt. It clears the prior active intent, deferred intents, continuation
  count, and exclusions instead of copying them under a new ID.
- A normal policy update changes the active generation in place and preserves its `contract_id`.
- An ordinary or new-looking prompt without an explicit rebind marker remains in the current
  generation. Hosts must not infer identity from prompt similarity, transcript content, turn IDs,
  or optional display labels.
- An explicit reset leaves no active generation and is idempotent. A later activation receives a
  fresh ID.
- A legacy identity-less runtime projection may preserve its existing restrictions only as a typed
  transitional `legacy_session`; explicit reset or rebind retires it. Missing or malformed current
  identity never causes the runtime to invent authority.

Generation-relative reads and writes are one serialized transition. A preflight or continuation
writer that began around a reset/rebind must observe the current generation before it can publish;
it cannot restore an old generation or recreate cleared state.

Lifecycle commands are directives, not quoted data. Documentation, examples, and quoted mentions
of `/goal`, `/work-contract rebind`, `/work-contract reset`, or natural-language equivalents do not
change contract identity.

## Attended Versus Unattended Execution

A provider-owned automatic reviewer may resolve eligible approvals before this portable fallback;
that reviewer selection is host configuration, not a Work Contract field.

`interaction.mode: forbidden` becomes a runtime non-waiting deny only when the active
natural-language projection also declares `execution.mode: unattended_goal_loop`. A plan, graph,
or mention of a loop does not convert an `attended` contract into this profile. Ordinary attended
work and Goal/Loop contracts that allow interaction retain the host's normal fallback behavior.

Without a provider reviewer, an unattended Goal/Loop approval or question is denied/deferred before
the UI wait begins. The executor then continues other required runnable work. If none remains, it
reports `blocked` with the exact unmet requirement instead of asking repeatedly.

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

Host hooks may persist a bounded projection containing an opaque contract ID, typed identity kind,
normalized execution mode, verification owner, interaction mode, excluded action classes, prompt
digest, and deferred intent keys. They must not derive the ID from or persist raw prompts, command
text, transcripts, credentials, optional task labels, turn IDs, or graph state. Durable node and
condition state belongs only to the canonical Plan/Handoff pair.
