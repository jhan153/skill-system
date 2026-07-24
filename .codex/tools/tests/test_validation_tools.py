from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class RuntimeContractTests(unittest.TestCase):
    def test_default_rules_keep_network_shell_and_mutating_state_reviewable(self) -> None:
        rules = (ROOT / ".codex" / "rules" / "default.rules").read_text(encoding="utf-8")
        self.assertIn(
            'prefix_rule(pattern=["curl"], decision="prompt"',
            rules,
        )
        self.assertNotIn(
            'prefix_rule(pattern=[["mmdc", "rg", "curl"]], decision="allow")',
            rules,
        )
        self.assertNotIn('exec curl "$@"', rules)
        self.assertIn(
            'prefix_rule(pattern=[["sh", "bash", "zsh", "/bin/sh", "/bin/bash", "/bin/zsh"], ["-c", "-lc"]], decision="prompt"',
            rules,
        )
        self.assertIn(
            'prefix_rule(pattern=["git", ["add", "apply", "commit", "fetch", "ls-remote", "pull", "push", "rebase", "merge", "switch"]], decision="prompt"',
            rules,
        )
        self.assertIn(
            'prefix_rule(pattern=["git", "branch", ["-D", "-f", "-m"]], decision="prompt"',
            rules,
        )
        self.assertIn(
            'prefix_rule(pattern=[["codex", "claude"], "plugin"], decision="prompt"',
            rules,
        )
        self.assertIn(
            'prefix_rule(pattern=["git", ["status", "merge-tree"]], decision="allow")',
            rules,
        )
        self.assertNotIn("# User-approved Git workflows.", rules)
        self.assertNotIn("install_runtime.py", rules)
        self.assertNotIn("task_ledger.py", rules)
        self.assertNotIn("fetch-codex-manual.mjs", rules)
        self.assertNotIn(
            'prefix_rule(pattern=["git", ["add", "apply", "commit"',
            "\n".join(line for line in rules.splitlines() if 'decision="allow"' in line),
        )

    def test_runtime_terms_reference_the_actual_hook_topology(self) -> None:
        terms = (ROOT / ".codex" / "docs" / "runtime_terms.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / ".codex" / "docs" / "harness_lifecycle_hooks.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("default Codex hook map is empty", terms)
        self.assertIn("bounded eight-event topology", terms)
        self.assertIn("all eight supported lifecycle events", lifecycle)

    def test_codex_hooks_use_one_direct_go_command_for_eight_events(self) -> None:
        payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        hooks = payload["hooks"]
        self.assertEqual(
            set(hooks),
            {
                "SessionStart",
                "UserPromptSubmit",
                "PreToolUse",
                "PermissionRequest",
                "PostToolUse",
                "Stop",
                "PreCompact",
                "PostCompact",
            },
        )
        for event, groups in hooks.items():
            command = groups[0]["hooks"][0]
            self.assertTrue(command["command"].endswith('/bin/skill-system-harness"'))
            windows = command["commandWindows"].lower()
            self.assertTrue(windows.startswith("cmd.exe /d /s /c "))
            self.assertIn("%codex_home%\\bin\\skill-system-harness.exe", windows)
            self.assertIn("%userprofile%\\.codex\\bin\\skill-system-harness.exe", windows)
            self.assertNotIn("python", command["command"].lower())
            self.assertEqual(command["timeout"], 12 if event == "Stop" else 3)

    def test_codex_macos_notification_uses_packaged_swift_overlay(self) -> None:
        harness = (ROOT / ".codex" / "bin" / "skill-system-harness").read_bytes()
        overlay = ROOT / ".codex" / "bin" / "skill-system-notify-overlay"
        self.assertTrue(overlay.is_file())
        self.assertIn(overlay.read_bytes()[:4], {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"})
        self.assertNotIn(b"osascript", harness)

    def test_codex_legacy_diagnostic_stack_is_not_packaged(self) -> None:
        removed = [
            ".codex/research",
            ".codex/hooks/codex_base_hook.py",
            ".codex/hooks/codex_hook_adapter.py",
            ".codex/tools/hook_runtime.py",
            ".codex/tools/init_agent_run.py",
            ".codex/tools/validate_agent_run_artifact.py",
            ".codex/tools/recovery_guard.py",
            ".codex/tools/reference_monitor.py",
            ".codex/tools/compare_harness_versions.py",
        ]
        self.assertEqual([path for path in removed if (ROOT / path).exists()], [])

    def test_claude_uses_four_direct_go_events_without_legacy_runtime(self) -> None:
        payload = json.loads((ROOT / ".claude" / "hooks" / "settings.example.json").read_text(encoding="utf-8"))
        hooks = payload["hooks"]
        self.assertEqual(set(hooks), {"SessionStart", "UserPromptSubmit", "Stop", "Notification"})
        for groups in hooks.values():
            command = groups[0]["hooks"][0]
            self.assertEqual(command["command"], "__ABSOLUTE_SKILL_SYSTEM_CLAUDE_HARNESS__")
            self.assertEqual(command["args"], [])
            self.assertNotIn("shell", command)
            self.assertEqual(command["timeout"], 3)

        binaries = {
            ".claude/bin/skill-system-claude-harness": {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"},
            ".claude/bin/skill-system-claude-harness.exe": {b"MZ"},
            ".claude/bin/skill-system-claude-harness-linux-amd64": {b"\x7fELF"},
            ".claude/bin/skill-system-notify-overlay": {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"},
        }
        for rel, headers in binaries.items():
            path = ROOT / rel
            self.assertTrue(path.is_file(), rel)
            raw = path.read_bytes()[:4]
            self.assertTrue(any(raw.startswith(header) for header in headers), rel)

        removed = [
            ".claude/hooks/claude_hook_adapter.py",
            ".claude/tools",
            ".claude/docs/agent_output_validation.md",
            ".claude/schemas/harness/lifecycle-event.schema.json",
        ]
        self.assertEqual([path for path in removed if (ROOT / path).exists()], [])

    def test_skill_invocation_policy_is_projected_per_platform(self) -> None:
        explicit_skill = "research-experiment-scaffold"
        implicit_skill = "search-deep-evidence"

        codex_explicit = (ROOT / ".codex" / "skills" / explicit_skill / "SKILL.md").read_text(encoding="utf-8")
        claude_explicit = (ROOT / ".claude" / "skills" / explicit_skill / "SKILL.md").read_text(encoding="utf-8")
        claude_implicit = (ROOT / ".claude" / "skills" / implicit_skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("disable-model-invocation:", codex_explicit)
        self.assertIn("disable-model-invocation: true", claude_explicit)
        self.assertNotIn("disable-model-invocation:", claude_implicit)

        plugin = ROOT / "plugins" / "skill-system-research"
        claude_plugin = ROOT / "plugins" / "claude" / "skill-system-research"
        codex_manifest = json.loads((plugin / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((claude_plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(codex_manifest["skills"], "./skills/")
        self.assertEqual(claude_manifest["skills"], "./skills/")
        plugin_codex = (plugin / "skills" / explicit_skill / "SKILL.md").read_text(encoding="utf-8")
        plugin_claude = (claude_plugin / "skills" / explicit_skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("disable-model-invocation:", plugin_codex)
        self.assertIn("disable-model-invocation: true", plugin_claude)

    def test_claude_skill_paths_are_projected_without_changing_codex_paths(self) -> None:
        codex_read = (ROOT / ".codex" / "skills" / "knowledge-base-read" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        claude_read = (ROOT / ".claude" / "skills" / "knowledge-base-read" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(".codex/docs/project_context_manifest.md", codex_read)
        self.assertIn(".claude/docs/project_context_manifest.md", claude_read)

        claude_skill_files = list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
        claude_skill_files.extend((ROOT / "plugins" / "claude").glob("*/skills/*/SKILL.md"))
        self.assertTrue(claude_skill_files)
        for skill_file in claude_skill_files:
            self.assertNotIn(
                ".codex/",
                skill_file.read_text(encoding="utf-8"),
                skill_file.relative_to(ROOT).as_posix(),
            )


if __name__ == "__main__":
    unittest.main()
