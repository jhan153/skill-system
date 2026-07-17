from __future__ import annotations

import importlib.util
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

    def test_claude_strict_gate_behavior_remains_platform_owned(self) -> None:
        adapter = ROOT / ".claude" / "hooks" / "claude_hook_adapter.py"
        spec = importlib.util.spec_from_file_location("claude_hook_adapter_test", adapter)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        blocked, _ = module.strict_block("result: agent-verified", [{"is_error": True}])
        self.assertTrue(blocked)
        blocked, _ = module.strict_block("result: unverified", [{"is_error": True}])
        self.assertFalse(blocked)
        source = adapter.read_text(encoding="utf-8")
        self.assertIn('ROOT / ".claude" / "tools"', source)
        self.assertNotIn('ROOT / ".codex" / "tools"', source)


if __name__ == "__main__":
    unittest.main()
