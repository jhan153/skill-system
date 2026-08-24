# Orchestration Capability Contract

This contract records whether a host can run durable orchestration such as
cron, webhook, queue, automation, or event-triggered agent work. It is not an
orchestrator implementation.

Use this layer when a durable Plan/Handoff or automation request depends on a
runtime capability outside the current turn.

## Provider Roles

- `packaging_provider`: has a declared generated plugin package surface. Codex uses its native
  package; Claude, Grok, and Antigravity share one Claude-compatible portable package so canonical
  skills are not copied two additional times.
- `native_harness_provider`: ships a provider-owned lifecycle harness. Current owners are Codex and
  Claude.
- `rule_companion_provider`: ships portable global rules and shared docs/schemas but no lifecycle
  binary. Current owners are Grok and Antigravity.
- `orca_execution_provider`: can receive an Orca-dispatched node when the current worker receipt
  proves lifecycle delivery. All four providers may hold this role for a task.

Plugin or rule installation never proves Orca execution support. Orca support is evidenced per
worker and follows `orca_worker_runtime_contract.md`; it does not change Workflow or Plan/Handoff
ownership.

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

- Do not infer cron, webhook, queue, automation, daemon, or event-trigger support from a Plan,
  hook registration, or schema alone.
- Use `external_host_dependent` when the host may provide the runtime but no
  current evidence is available.
- Use `unsupported` when the bundle has no runtime and the host surface is not
  available.
- A repeated-work profile may require this contract before execution, but runtime support does not
  make repeated verifier steering useful by itself.
- Stop-hook observation is a separate capability from durable scheduling or event triggers and
  never owns continuation.

## Schema And Example

Repository authoring uses:

- `source/shared/schemas/orchestration/orchestration-capability.schema.json`
- `source/shared/schemas/orchestration/examples/orchestration-capability.external-host.yaml`

An installed provider runtime resolves the projected `schemas/orchestration/` path from its own
declared runtime root. Do not hard-code a Codex, Claude, Grok, Antigravity, home, or plugin-cache
path into a portable capability record.
