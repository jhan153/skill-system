# Grok Common Go Harness

Grok owns an independent Go module under `source/runtime/go/grok`. It receives the distributed
common harness baseline and builds `skill-system-grok-harness` for macOS arm64, Windows amd64,
and Linux amd64. The executable exposes version and project-context resolution only.

Orca remains the Grok worker lifecycle owner. This binary does not invent a Grok hook adapter,
poll a worker, or reuse Codex/Claude hook wire formats. Future Grok-native behavior belongs only
in the Grok module.
