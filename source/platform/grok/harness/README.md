# Grok Common Go Harness

Grok owns an independent Go module under `source/runtime/go/grok`. It receives the distributed
common harness baseline and builds `skill-system-grok-harness` for macOS arm64, Windows amd64,
and Linux amd64. The executable exposes version, project-context resolution, and Grok-native
`Notification` forwarding to the redacted OS notifier / `skill-system-notify-overlay`.

Orca remains the Grok worker lifecycle owner. This binary does not poll a worker, reuse
Codex/Claude hook wire formats, or register SessionStart/Stop gates. Desktop alerts use Grok's
own `Notification` event (`permission_prompt`, `idle_prompt`, `task_complete`) through a
materialized `hooks/skill-system.json`, which merges with host/Orca hook files instead of replacing
them.

`hooks/skill-system.json.in` is a non-discovered portable template. During explicit runtime
deployment, copy it to `<GROK_HOME>/hooks/skill-system.json` and replace only
`__SKILL_SYSTEM_GROK_HARNESS_FILENAME__` with the selected platform artifact name:
`skill-system-grok-harness` on macOS arm64, `skill-system-grok-harness-linux-amd64` on Linux amd64,
or `skill-system-grok-harness.exe` on Windows amd64. The installed relative command must resolve
from `<GROK_HOME>/hooks/` to that exact file under `<GROK_HOME>/bin/`; do not install the unresolved
template, leave a `.json` file with the placeholder in a project `.grok/hooks/` directory, or create
a shell/PowerShell wrapper.
