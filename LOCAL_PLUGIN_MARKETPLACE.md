# Local Plugin Marketplace

This repository can be used as a local plugin marketplace for both **Codex** and
**Claude Code**. The marketplace catalogs are stored in the repo at:

```text
.agents/plugins/marketplace.json         # Codex
plugins/.claude-plugin/marketplace.json  # Claude Code
```

Plugin packages and the Claude catalog are generated from `source/plugins/*.yaml` by
`python3 source/tools/generate_targets.py --target plugins`; the stable Codex catalog
keeps its local source entries in `.agents/plugins/marketplace.json`. The sections below that
use `codex plugin ...` are the Codex flow; see the **Claude Code (Local Marketplace)**
section near the end for the `/plugin ...` equivalents.

Codex packages keep their existing paths:

```text
plugins/skill-system-core
plugins/skill-system-dev
plugins/skill-system-design
plugins/skill-system-research
plugins/skill-system-quality
plugins/skill-system-maintainer
```

Claude packages use paired platform-owned roots with the same names and versions:

```text
plugins/claude/skill-system-core
plugins/claude/skill-system-dev
plugins/claude/skill-system-design
plugins/claude/skill-system-research
plugins/claude/skill-system-quality
plugins/claude/skill-system-maintainer
```

## Ecosystem Parity

Both Codex and Claude Code are reflected from the same canonical `source/`, and
both receive the same skill set. Their manifests, package roots, and invocation
frontmatter are projected per host. The rule holds for both ecosystems:

> Marketplace plugins ship **skills only**. Anything that can change execution
> policy — hooks, tools, rules, schemas — is **runtime companion payload**,
> enabled separately after a reviewed dry-run, never by a plugin install.

| Asset | Codex | Claude Code | How it ships |
| --- | --- | --- | --- |
| Skills | `plugins/<name>/.codex-plugin/` + `skills/` | `plugins/claude/<name>/.claude-plugin/` + `skills/` | **Marketplace plugin** — one canonical body with host-native invocation metadata |
| Plugin manifest | `.codex-plugin/plugin.json` | `.claude-plugin/plugin.json` | generated per package |
| Marketplace catalog | `.agents/plugins/marketplace.json` | `plugins/.claude-plugin/marketplace.json` | generated |
| Hooks | `.codex/hooks.json` + `.codex/bin/skill-system-harness*` | `.claude/hooks/settings.example.json` + `.claude/bin/skill-system-claude-harness*` | **Runtime companion** — host registration is separate, NOT via plugin install |
| Runtime docs / rules / schemas | `.codex/...` | `.claude/...` | runtime companion |
| MCP integration | `integrations/kanboard-plan-sync` | same (MCP is runtime-agnostic) | separate integration, not in plugins |
| Slash commands / subagents | — | supported by Claude, unused here | bundle expresses everything as skills |

So `codex plugin add` and `/plugin install` both install **skills and nothing
else**. The two marketplaces are full peers; neither carries hooks.

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
skill-system-quality@skill-system-local
skill-system-maintainer@skill-system-local
```

## Install Plugins

Install only the profiles you need. For development work, start with:

```bash
codex plugin add skill-system-core@skill-system-local
codex plugin add skill-system-dev@skill-system-local
```

Add quality support when validation-matrix and QA workflow skills are needed:

```bash
codex plugin add skill-system-quality@skill-system-local
```

Design, research, and maintainer plugins can be installed the same way:

```bash
codex plugin add skill-system-design@skill-system-local
codex plugin add skill-system-research@skill-system-local
codex plugin add skill-system-maintainer@skill-system-local
```

Start a new Codex thread after installing or reinstalling plugins so the new
skill set is picked up cleanly.

## Runtime Companion Payload

Plugins install skills. They do not automatically install or enable Codex runtime
files such as hooks, tools, rules, schemas, research ledgers, or harness assets.
Those files can affect local execution policy and should be copied only after a
reviewed dry-run.

Runtime companion candidates are generated under `.codex/` from `source/`:

```text
.codex/AGENTS.md
.codex/context-routing.md
.codex/docs/
.codex/eval/
.codex/field-feedback/
.codex/harness/
.codex/hooks.json
.codex/hooks/
.codex/research-routing.md
.codex/research/
.codex/rules/default.rules
.codex/schemas/
.codex/tools/
```

Do not copy app-managed or host-local state:

```text
.codex/skills/.system
.codex/config.toml
.codex/automations/
.codex/plugins/cache/
```

Recommended workflow: ask an Agent to inspect the companion payload before it
writes anything to `~/.codex`.

Use this prompt from the repository root:

```text
Review the Skill System runtime companion payload for my local Codex home.
Compare this repo's generated .codex runtime files against ~/.codex, including
hooks.json, hooks/, tools/, rules/default.rules, schemas/, research/, harness/,
field-feedback/, context-routing.md, docs/, eval/, and AGENTS.md.

First show a dry-run summary and the exact files that would be added, changed,
or skipped. Do not copy anything yet. Do not touch .codex/skills/.system,
config.toml, automations, plugins/cache, credentials, or unrelated local state.
Ask me for explicit approval before applying the sync.
```

After approval, the Agent should copy only the reviewed files, preserve local
host-managed state, and run a focused verification such as:

```bash
python3 .codex/tools/verify_bundle.py --root . --profile core --format text
python3 .codex/tools/verify_bundle.py --root . --profile execution --format text
```

If hook or rule files changed, review them against the local machine's policy
before enabling or trusting them in Codex. Runtime companion sync is intentionally
separate from `codex plugin add`.

## Update To A New Bundle Version

The marketplace registration is stable as long as the repo path and marketplace
name stay the same. A later bundle version only needs regenerated plugin
packages and reinstall commands.

After updating `source/` or `source/plugins/*.yaml`, regenerate and verify:

```bash
python3 source/tools/generate_targets.py --target plugins
python3 source/tools/check_generated_targets.py --target plugins --baseline
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

Add other roles the same way: `skill-system-quality@skill-system-local`,
`skill-system-design@skill-system-local`, `skill-system-research@skill-system-local`,
`skill-system-maintainer@skill-system-local`. After install / enable / disable, run
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

Regenerating rebuilds both the Codex and Claude catalogs at once:

```bash
python3 source/tools/generate_targets.py --target plugins
python3 source/tools/check_generated_targets.py --target plugins --baseline
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
part of 9.3.4.

Other Claude runtime-companion files generated under `.claude/` (docs,
`context-routing.md`, `eval/`, `schemas/`, hooks, and binaries) are likewise NOT installed by
`/plugin install`. Sync them the same review-gated way as the Codex companion
payload above: ask an Agent for a dry-run diff against your `~/.claude` first,
approve, then copy only the reviewed files. Do not copy app-managed state
(`.claude/skills/.system`) or host-local `settings.json`.
