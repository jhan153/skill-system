# Skill System 10.0 Runtime Payload Policy

## Canonical Boundary

`source/` is canonical. Generated `.codex/`, `.claude/`, `.grok/`, `.antigravity/`, and `plugins/`
paths are replaceable distribution output and are never edited by hand.

## Skill Distribution

Skills ship through marketplace plugins only:

- Codex: `plugins/skill-system-*`
- Claude: `plugins/claude/skill-system-*`
- Grok: the same Claude-compatible package roots
- Antigravity: the same package roots with generated root `plugin.json` markers

The former `.codex/skills` and `.claude/skills` full mirrors are retired. Runtime companion
generation removes them. Grok and Antigravity reuse the Claude-compatible package set instead of
creating two more copies of every skill.

Plugins are installation profiles, not user-facing families. The registry's nine families own
routing language; the five plugin profiles own convenient installation boundaries.

## Shared Plugin Payloads

Small contracts and Core Cards may be projected into each consuming skill so plugin packages remain
self-contained. Large executable assets are plugin-shared instead:

- Report Markdown contracts remain skill-local.
- Core carries one `shared/report-canvas` renderer payload per packaging provider.
- Report skills never carry their own Three.js/renderer copy.

## Runtime Companions

Runtime companions contain host policy and executable integration only: provider instructions,
routing, hooks, rules where applicable, portable docs/schemas, and one provider-owned Go harness
module/binary set. The former common Go implementation is distributed into four independent
modules. Codex receives the common baseline through its Codex-native hook delivery; model-side
direct-command selection and sandboxing handle ordinary local work without per-command
natural-language grants, while portable prompt/forbidden rules and an effective host `auto_review`
configuration evaluate approval-gated commands without a user-click wait. Claude, Grok, and
Antigravity receive the common baseline, with Claude
retaining its native event handler. Grok and Antigravity expose only version and project-context
CLI surfaces while Orca remains their worker lifecycle owner. No companion contains a skill
mirror, Python validator, eval corpus, lifecycle ledger, or installation state.

Plugin installation never enables runtime companions automatically. Runtime companion installation
is a separate explicit operation that preserves host-owned configuration and credentials.
For Codex, `rules/skill-system.rules` is generated policy while `rules/default.rules` is
user/Codex-owned approval state and is never copied, replaced, or pruned by Skill System.

## Provider Boundary

- Codex has a native Codex package set. Claude, Grok, and Antigravity share one portable
  Claude-compatible package set.
- All four providers own separate Go harness modules and build digests. Codex and Claude retain
  provider-native hook handlers. Grok and Antigravity receive the distributed common harness
  surface without a fabricated native hook adapter and use Orca for dispatch, inbox/follow-up,
  heartbeat, and `worker_done` delivery.
- Plugin or global-rule installation never proves Orca capability. The current worker receipt does,
  under `docs/orca_worker_runtime_contract.md`.

## Portability

Shared files contain no developer-machine absolute paths. Installation resolves repository and host
roots on each computer. Multi-platform harness binaries remain tracked for personal multi-PC use.

## Validation Boundary

- Four repository contract tests cover Core Cards and Skill System packaging/wiring.
- Direct Go component tests live in each provider module and run only for the changed provider
  harness surface.
- There is no persistent per-skill quality suite, runtime Python validator, automatic all-suite
  command, release identity gate, or hygiene pipeline.
