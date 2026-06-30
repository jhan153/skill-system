# Tool Hardening Profile

7.3.1 uses capability-based tool policy instead of a single mutually exclusive risk tier.

Tool policy is task-conditioned. A tool name alone is not enough to decide whether an invocation is safe.

For the human-readable operating catalog (`routine`, `risky`, `blocked`) and
representative tool-class examples, read `.codex/docs/tool_policy.md`.

## Policy Shape

```yaml
tool_policy:
  tool_id: Bash
  capabilities:
    - process
    - filesystem_write
    - network
  invocation_scope:
    workspace_roots: []
    network_hosts: []
    credential_classes: []
  decision:
    default: ask
    deny_when: []
    allow_when: []
  execution:
    timeout_seconds: 120
    retry_limit: 0
    output_size_limit: 1048576
  postconditions:
    capture_exit_status: true
    capture_changed_files: true
    capture_network_targets: true
    redact_sensitive_output: true
```

## Capabilities

Allowed capability labels:
- `read`
- `filesystem_write`
- `process`
- `network`
- `credential`
- `destructive`
- `browser`
- `mcp`

## Decisions

Allowed default decisions:
- `allow`
- `ask`
- `deny`

Policy decisions must not override configured sandboxing or approval policy. They provide preflight and postcondition records for verification.

## Postconditions

Postconditions are evidence capture obligations. They should record what happened after the tool call without exposing secrets.
