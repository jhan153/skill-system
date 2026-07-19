from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class RuntimeContractTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
