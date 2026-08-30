# Local Plugin Marketplace

This repository distributes the same Skill System profiles to **Codex**, **Claude Code**,
**Grok**, and **Antigravity**. Codex and Claude use local marketplace catalogs:

```text
.agents/plugins/marketplace.json         # Codex
plugins/.claude-plugin/marketplace.json  # Claude Code
```

Plugin packages and both catalogs are generated from `source/distribution.json` and
`source/plugins/*.yaml` by `python3 source/tools/generate_targets.py --target plugins`.
The sections below that use `codex plugin ...` are the Codex flow. Claude uses its marketplace;
Grok and Antigravity install the portable package roots directly with their official CLIs.

These packages are installation profiles rather than user-facing skill families. Core is the
shared profile, Dev adds engineering work, and Design/Research/Testing add domain-specific
capabilities.

Codex packages keep their existing paths:

```text
plugins/skill-system-core
plugins/skill-system-dev
plugins/skill-system-design
plugins/skill-system-research
plugins/skill-system-testing
```

The paired Claude-compatible roots are also the portable Grok/Antigravity packages:

```text
plugins/claude/skill-system-core
plugins/claude/skill-system-dev
plugins/claude/skill-system-design
plugins/claude/skill-system-research
plugins/claude/skill-system-testing
```

## Ecosystem Parity

All four providers are reflected from the same canonical `source/` and receive the same skill
set. Codex has its native package set; Claude, Grok, and Antigravity share the portable set.

> Marketplace plugins ship **skills only**. Anything that can change execution
> policy — hooks, tools, rules, schemas — is **runtime companion payload**,
> enabled separately after a reviewed dry-run, never by a plugin install.

| Asset | Codex | Claude Code | Grok | Antigravity |
| --- | --- | --- | --- | --- |
| Skills | `plugins/<name>/skills` | `plugins/claude/<name>/skills` | same portable root | same portable root |
| Manifest | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` | Claude manifest compatibility | root `plugin.json` |
| Install | Codex marketplace | Claude marketplace | `grok plugin install <root>` | `agy plugin install <root>` |
| Global rules | `.codex/AGENTS.md` | `.claude/CLAUDE.md` | `.grok/AGENTS.md` | `.antigravity/GEMINI.md` |
| Lifecycle | Codex Go harness | Claude Go harness | Orca | Orca |

Plugin installation installs skills, not runtime policy. Global rules, docs/schemas, hooks, and
harnesses remain explicit runtime-companion deployment. Grok and Antigravity get no polling
harness; Orca owns dispatch/inbox/heartbeat/`worker_done` for those workers.

The former `.codex/skills` and `.claude/skills` repository mirrors are retired. Generated runtime
companions contain no skills; marketplace plugins are the sole skill distribution surface.

## Register On This Machine

Marketplace registration is local to each computer. Cloning this repository
copies the marketplace file, but it does not register it with that machine's
Codex installation.

From the repository root, run:

```bash
codex plugin marketplace add "$(pwd)"
codex plugin list
```

Expected result: `codex plugin list` shows entries such as:

```text
skill-system-core@skill-system-local
skill-system-dev@skill-system-local
skill-system-design@skill-system-local
skill-system-research@skill-system-local
skill-system-testing@skill-system-local
```

## Install Plugins

Install only the profiles you need. For development work, start with:

```bash
codex plugin add skill-system-core@skill-system-local
codex plugin add skill-system-dev@skill-system-local
```

Design, research, and testing plugins can be installed the same way:

```bash
codex plugin add skill-system-design@skill-system-local
codex plugin add skill-system-research@skill-system-local
codex plugin add skill-system-testing@skill-system-local
```

Start a new Codex thread after installing or reinstalling plugins so the new
skill set is picked up cleanly.

## Runtime Companion Payload

Plugins install skills. They do not automatically install or enable Codex runtime
files such as hooks, tools, rules, schemas, or harness assets. Install those files
only when the user explicitly requests runtime companion installation.

Runtime companion candidates are generated under `.codex/` from `source/`:

```text
.codex/AGENTS.md
.codex/context-routing.md
.codex/docs/
.codex/harness/
.codex/hooks.json
.codex/rules/skill-system.rules
.codex/schemas/
```

Do not copy app-managed or host-local state:

```text
.codex/skills/.system
.codex/config.toml
.codex/automations/
.codex/plugins/cache/
.codex/rules/default.rules
```

Use this prompt from the repository root when installation is wanted:

```text
Install the declared Skill System runtime companion files into my local Codex
home. Resolve the repository and Codex home on this computer, do not persist
absolute paths in shared data, and do not touch .codex/skills/.system,
config.toml, rules/default.rules, automations, plugins/cache, credentials, or
unrelated local state. Copy only rules/skill-system.rules from the generated
rules directory.
```

The Agent should copy only declared files and preserve local host-managed state.

If hook or rule files changed, review them against the local machine's policy
before enabling or trusting them in Codex. Runtime companion sync is intentionally
separate from `codex plugin add`.

## Update To A New Bundle Version

The marketplace registration is stable as long as the repo path and marketplace
name stay the same. A later bundle version only needs regenerated plugin
packages and reinstall commands.

After updating `source/` or `source/plugins/*.yaml`, regenerate:

```bash
python3 source/tools/generate_targets.py --target runtime
python3 source/tools/generate_targets.py --target plugins
```

Then reinstall the plugins you use:

```bash
codex plugin add skill-system-core@skill-system-local
codex plugin add skill-system-dev@skill-system-local
```

Installed plugins do not automatically refresh just because the repo files
changed.

If the new bundle changes runtime companion files, repeat the reviewed dry-run in
the Runtime Companion Payload section before copying hooks, tools, or rules into
`~/.codex`.

## Notes

- Do not copy these plugins directly into `~/.codex/plugins/cache`; Codex owns
  that cache.
- The marketplace entries use relative paths such as
  `./plugins/skill-system-core`, so clone location does not matter after the
  local marketplace is registered.
- If another marketplace named `skill-system-local` is already registered on the
  same computer, resolve that local-name conflict before adding this repo.

## Claude Code (Local Marketplace)

Claude Code reads the generated catalog at `plugins/.claude-plugin/marketplace.json`.
Each catalog entry points to `plugins/claude/<name>`, whose manifest lives at
`.claude-plugin/plugin.json`. Its `skills/<id>/SKILL.md` is projected from the same
canonical source as Codex, but explicit-only skills receive Claude's native
`disable-model-invocation: true` frontmatter. The separate package root prevents
Codex and Claude default discovery from loading each other's metadata.

### Register and install

Registration is local to each machine. In a Claude Code session, run the slash
commands (the marketplace directory is the repo's `plugins/` folder, which holds
`.claude-plugin/marketplace.json`):

```text
/plugin marketplace add /absolute/path/to/this/repo/plugins
/plugin marketplace list
/plugin install skill-system-core@skill-system-local
/plugin install skill-system-dev@skill-system-local
```

Add other roles the same way: `skill-system-design@skill-system-local`,
`skill-system-research@skill-system-local`, and `skill-system-testing@skill-system-local`.
After install / enable / disable, run
`/reload-plugins` to apply changes without restarting.

Plugin skills are namespaced by plugin name, e.g.
`/skill-system-dev:workflow-implementation` (project/user skills stay unprefixed).

### Team / project auto-config (settings.json)

To pre-wire the marketplace and enabled plugins for collaborators who trust the repo,
add to project `.claude/settings.json` (the catalog lives in the `plugins`
subdirectory, so a git-based source uses `git-subdir`):

```json
{
  "extraKnownMarketplaces": {
    "skill-system-local": {
      "source": { "source": "git-subdir", "url": "<repo-git-url>", "path": "plugins", "ref": "main" }
    }
  },
  "enabledPlugins": {
    "skill-system-core@skill-system-local": true,
    "skill-system-dev@skill-system-local": true
  }
}
```

For a purely local checkout, registering interactively with
`/plugin marketplace add <path>/plugins` is simplest. Managed/admin settings can
restrict which marketplaces are allowed with `strictKnownMarketplaces`.

### Update to a new bundle version

Regenerating rebuilds the Codex package set, the shared portable package set, and both catalogs:

```bash
python3 source/tools/generate_targets.py --target runtime
python3 source/tools/generate_targets.py --target plugins
```

Then in Claude Code refresh with `/plugin marketplace update skill-system-local`
and `/reload-plugins`, reinstalling any newly added plugins.

### Runtime companion payload — does hooking go into Claude too?

Yes. Hooks exist on the Claude side as a full peer to the Codex harness, but they
are **runtime companion payload, not part of the marketplace plugin**. `/plugin
install` brings skills only; it never installs or enables a hook. Claude's plugin
system can bundle hooks, but this bundle keeps execution-policy changes behind a
separate reviewed runtime installation.

The Claude companion uses `.claude/hooks/settings.example.json` to register the
packaged `.claude/bin/skill-system-claude-harness` for `SessionStart`,
`UserPromptSubmit`, `Stop`, and `Notification`. It shares bounded Go core packages
with Codex while retaining Claude-native event normalization. The old Python
ledger, transcript Output Gate, measurement, and notification adapters are not
part of 9.4.2; they were removed in 9.3.4.

Other Claude runtime-companion files generated under `.claude/` (docs,
`context-routing.md`, `schemas/`, hooks, and binaries) are likewise NOT installed by
`/plugin install`. Install them only on explicit request, resolving the Claude home
on that computer. Do not copy app-managed state (`.claude/skills/.system`) or
host-local `settings.json`.

## Grok (Portable Package)

Grok officially reads Claude Code plugins and skill frontmatter. Install selected profiles from the
portable roots; no Grok-specific skill copy or marketplace catalog is generated.

```bash
grok plugin install /absolute/path/to/this/repo/plugins/claude/skill-system-core
grok plugin install /absolute/path/to/this/repo/plugins/claude/skill-system-dev
grok plugin list
```

The optional rule companion is generated under `.grok/`. An explicit runtime deployment maps
`.grok/AGENTS.md`, `.grok/docs/`, and `.grok/schemas/` into the actual `GROK_HOME` while preserving
`config.toml`, credentials, sessions, memories, hooks, and plugin state.

## Antigravity (Portable Package)

Each portable package has a generated root `plugin.json` marker for Antigravity while retaining the
Claude manifest used by Claude and Grok.

```bash
agy plugin install /absolute/path/to/this/repo/plugins/claude/skill-system-core
agy plugin install /absolute/path/to/this/repo/plugins/claude/skill-system-dev
agy plugin list
```

The optional rule companion is generated under `.antigravity/`. An explicit runtime deployment maps
`GEMINI.md`, `docs/`, and `schemas/` to Antigravity's actual global root while preserving
`settings.json`, credentials, conversations, hooks, and plugin state.

For Grok and Antigravity, plugin/rule presence proves only package discovery. Orca lifecycle support
is confirmed per worker receipt and follows `docs/orca_worker_runtime_contract.md`: no automatic
Coordinator polling, transcript replay, fixed wait interval, or provider-local liveness loop.
