#!/usr/bin/env python3
"""Verify the 9.3.3 platform-separated runtime contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


sys.dont_write_bytecode = True

EVENTS = {
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "Stop",
    "PreCompact",
    "PostCompact",
}

REQUIRED_FILES = [
    ".codex/bin/skill-system-harness",
    ".codex/bin/skill-system-harness.exe",
    ".codex/bin/skill-system-notify-overlay",
    ".codex/hooks.json",
    ".codex/docs/harness_lifecycle_hooks.md",
    ".claude/docs/harness_lifecycle_hooks.md",
    ".claude/hooks/claude_hook_adapter.py",
    ".claude/tools/hook_runtime.py",
    ".codex/docs/project_context_manifest.md",
    ".codex/skills/project-context-init/SKILL.md",
    ".codex/skills/project-context-update/SKILL.md",
    ".codex/schemas/loop/loop-run.schema.json",
    ".codex/tools/evaluate_loop_run.py",
    ".codex/tools/task_ledger.py",
    ".codex/tools/validate_task_run.py",
    ".codex/research/ledger.yaml",
]

FORBIDDEN_CODEX_FILES = [
    ".codex/hooks/codex_base_hook.py",
    ".codex/hooks/codex_hook_adapter.py",
    ".codex/tools/hook_runtime.py",
    ".codex/tools/init_agent_run.py",
    ".codex/tools/validate_agent_run_artifact.py",
    ".codex/tools/recovery_guard.py",
    ".codex/tools/reference_monitor.py",
    ".codex/tools/analyze_harness_measurement.py",
    ".codex/tools/compare_harness_versions.py",
    ".codex/tools/notify_desktop.py",
    ".codex/docs/agent_output_validation.md",
    ".codex/schemas/harness/agent-run.schema.json",
    ".codex/schemas/harness/lifecycle-event.schema.json",
    ".codex/eval/harness_versions.json",
    ".codex/eval/release_forward_cases.yaml",
]


def load_hooks(path: Path) -> tuple[dict, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, [f"invalid hooks.json: {exc}"]
    hooks = value.get("hooks") if isinstance(value, dict) else None
    if not isinstance(hooks, dict):
        return {}, ["hooks.json requires a hooks object"]
    return hooks, []


def validate_hooks(hooks: dict) -> list[str]:
    errors: list[str] = []
    names = set(hooks)
    if names != EVENTS:
        errors.append(f"hook event set mismatch: missing={sorted(EVENTS - names)} extra={sorted(names - EVENTS)}")
    for event, groups in hooks.items():
        if not isinstance(groups, list) or len(groups) != 1:
            errors.append(f"{event}: requires exactly one hook group")
            continue
        commands = groups[0].get("hooks") if isinstance(groups[0], dict) else None
        if not isinstance(commands, list) or len(commands) != 1 or not isinstance(commands[0], dict):
            errors.append(f"{event}: requires exactly one command hook")
            continue
        command = str(commands[0].get("command") or "")
        windows = str(commands[0].get("commandWindows") or "")
        if not command.endswith('/bin/skill-system-harness\"'):
            errors.append(f"{event}: POSIX command is not the direct Go harness")
        windows_lower = windows.lower()
        if not windows_lower.startswith("cmd.exe /d /s /c "):
            errors.append(f"{event}: Windows command lacks the bounded CODEX_HOME resolver")
        if "%codex_home%\\bin\\skill-system-harness.exe" not in windows_lower:
            errors.append(f"{event}: Windows command ignores CODEX_HOME")
        if "%userprofile%\\.codex\\bin\\skill-system-harness.exe" not in windows_lower:
            errors.append(f"{event}: Windows command lacks the default CODEX_HOME fallback")
        timeout = commands[0].get("timeout")
        expected_timeout = 12 if event == "Stop" else 3
        if timeout != expected_timeout:
            errors.append(f"{event}: timeout {timeout!r} != {expected_timeout}")
        launchers = ("python", "zsh", "bash", "powershell", "codex_base_hook", "codex_hook_adapter")
        lowered = (command + " " + windows).lower()
        if any(token in lowered for token in launchers):
            errors.append(f"{event}: command contains a launcher or legacy adapter")
    return errors


def validate_binary(path: Path, kind: str) -> list[str]:
    if not path.is_file():
        return []
    header = path.read_bytes()[:4]
    if kind == "mach-o" and header not in {b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"}:
        return [f"{path}: not a Mach-O executable"]
    if kind == "pe" and not header.startswith(b"MZ"):
        return [f"{path}: not a Windows PE executable"]
    return []


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    errors = [f"missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    errors.extend(f"removed Codex legacy asset is still packaged: {path}" for path in FORBIDDEN_CODEX_FILES if (root / path).exists())

    hooks, hook_errors = load_hooks(root / ".codex" / "hooks.json")
    errors.extend(hook_errors)
    if not hook_errors:
        errors.extend(validate_hooks(hooks))
    errors.extend(validate_binary(root / ".codex" / "bin" / "skill-system-harness", "mach-o"))
    errors.extend(validate_binary(root / ".codex" / "bin" / "skill-system-harness.exe", "pe"))
    errors.extend(validate_binary(root / ".codex" / "bin" / "skill-system-notify-overlay", "mach-o"))

    harness = root / ".codex" / "bin" / "skill-system-harness"
    if harness.is_file() and b"osascript" in harness.read_bytes():
        errors.append("Codex harness regressed to the removed macOS osascript notification path")

    for plugin_hooks in (root / "plugins").glob("*/hooks"):
        if plugin_hooks.exists():
            errors.append(f"plugin duplicates base hook ownership: {plugin_hooks.relative_to(root)}")

    claude_adapter = root / ".claude" / "hooks" / "claude_hook_adapter.py"
    if claude_adapter.is_file():
        text = claude_adapter.read_text(encoding="utf-8")
        if 'ROOT / ".claude" / "tools"' not in text or 'ROOT / ".codex" / "tools"' in text:
            errors.append("Claude adapter does not own its runtime dependency")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: Codex Go harness, platform ownership, and retained explicit ledgers are structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
