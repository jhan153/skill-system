# Phase Context Carryover Gate

Run this gate only after the current phase has met its own exit conditions and the next phase has a different immediate purpose. Context optimization is not a reason to interrupt unfinished work.

First identify what the next phase must retain:

- primary artifacts and current paths;
- accepted decisions and the reasons that still constrain work;
- unresolved risks or evidence gaps;
- the next owner and whether live user steering is required; and
- information that is safe to discard because a canonical source replaces it.

Then evaluate the following outcomes in order. Select the first outcome whose conditions and host mechanism are both available.

| Order | Outcome | Select when | Do not select when |
| --- | --- | --- | --- |
| 1 | `continue` | The current task remains the owner, relevant reasoning still lives in context, and the remaining usable context can carry the next phase. | The next phase would predictably overflow or ownership must move. |
| 2 | `clear` | The next phase has no material dependency on the completed phase and its inputs are independently canonical. | A summary, diff, or artifact would omit a reason the next phase still needs. |
| 3 | `handoff` | Primary ownership, harness, repository, workspace, or person changes and a portable transfer packet is required. | The current task remains primary and only a bounded supporting unit needs separation. |
| 4 | `subagent` | The current task remains primary, while the next unit is bounded, agent-runnable without live steering, independently verifiable, and delegation is available and authorized. | The unit needs user judgment, shares an unsafe write scope, or delegation is unavailable. |
| 5 | `compact` | The same task and context remain relevant, user interaction must stay here, and the remaining context cannot safely hold the next phase. | A higher-ranked outcome already satisfies the boundary. |

`continue` preserves full conversational context. Every other outcome may lose ordering, emphasis, rejected alternatives, or uncertainty, so the record must name that loss. `compact` is the final same-owner fallback, not a routine cleanup step.

## Mechanism Boundary

This gate recommends a transition; it does not perform one. A handoff uses `plan-task-handoff` only when portability or ownership transfer is actually requested. A subagent still requires the host's delegation capability and current authority. Clear or compact must name a supported host action rather than assume one exists.

## Boundary Record

Record only:

```yaml
phase_context_transition:
  status: not_at_boundary | evaluated
  selected: none | continue | clear | handoff | subagent | compact
  basis: <first satisfied row and evidence>
  retain: []
  discardable: []
  mechanism: unavailable | <supported host action>
  loss_risk: <information that may be flattened or lost>
```

Re-run the gate at each later phase boundary. The previous selection is evidence about one transition, not a standing package policy.
