# Antigravity Common Go Harness

Antigravity owns an independent Go module under `source/runtime/go/antigravity`. It receives the
distributed common harness baseline and builds `skill-system-antigravity-harness` for macOS arm64,
Windows amd64, and Linux amd64. The executable exposes version and project-context resolution only.

Orca remains the Antigravity worker lifecycle owner. This binary does not invent an Antigravity
hook adapter, poll a worker, or reuse Codex/Claude hook wire formats. Future Antigravity-native
behavior belongs only in the Antigravity module.
