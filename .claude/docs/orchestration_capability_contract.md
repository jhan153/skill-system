# Orchestration Capability Contract

This contract records whether a host can run durable orchestration such as
cron, webhook, queue, automation, or event-triggered agent work. It is not an
orchestrator implementation.

Use this layer when a plan, loop contract, or automation request depends on a
runtime capability outside the current turn.

## Support States

| support_state | meaning | allowed claim |
| --- | --- | --- |
| `unsupported` | The bundle does not provide this runtime and no host evidence is available. | Do not claim capability; mark execution `unverified` or `blocked`. |
| `external_host_dependent` | The capability may exist in the host, but the current run has not verified it. | State dependency and required verification. |
| `supported` | The host advertises the capability, but current task evidence has not proven it works. | May plan against it with `user-verification-needed`. |
| `verified` | A current, task-relevant evidence ref proves the capability is available. | May use as a runtime premise within the approved scope. |

## Required Evidence

An orchestration capability claim needs:

- capability id and type
- support state
- host owner or runtime surface
- verification method
- evidence reference, or an explicit reason why evidence is unavailable
- task scope where the claim applies
- expiry or review condition when host state can drift

Runtime support is per environment. A capability verified on one machine,
profile, connector, or project cannot be treated as portable package behavior.

## Agent Rules

- Do not infer cron, webhook, queue, automation, daemon, or event-trigger support
  from LoopRun, Kanboard, hooks, or schemas alone.
- Use `external_host_dependent` when the host may provide the runtime but no
  current evidence is available.
- Use `unsupported` when the bundle has no runtime and the host surface is not
  available.
- A loop may require this contract before execution, but the contract does not
  make a task loop-worthy by itself.
- Stop-hook loop evaluation is a separate capability from durable scheduling or
  event triggers.

## Schema And Example

- Schema: `.codex/schemas/orchestration/orchestration-capability.schema.json`
- Example: `.codex/schemas/orchestration/examples/orchestration-capability.external-host.yaml`
