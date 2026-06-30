#!/usr/bin/env python3
"""Best-effort desktop notification helper for Skill-System hooks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


sys.dont_write_bytecode = True

MAX_MESSAGE = 240
OVERLAY_SOURCE = r'''
import Cocoa

let title = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Claude approval requested"
let message = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "Permission needed."
let duration = CommandLine.arguments.count > 3 ? Double(CommandLine.arguments[3]) ?? 4.0 : 4.0
let topic = CommandLine.arguments.count > 4 ? CommandLine.arguments[4] : ""

func monokaiAccent(_ topic: String) -> NSColor {
    switch topic {
    case "done": return NSColor(srgbRed: 166/255.0, green: 226/255.0, blue: 46/255.0, alpha: 1.0)
    case "error": return NSColor(srgbRed: 249/255.0, green: 38/255.0, blue: 114/255.0, alpha: 1.0)
    case "approval", "input": return NSColor(srgbRed: 102/255.0, green: 217/255.0, blue: 239/255.0, alpha: 1.0)
    case "progress": return NSColor(srgbRed: 230/255.0, green: 219/255.0, blue: 116/255.0, alpha: 1.0)
    case "kanboard": return NSColor(srgbRed: 174/255.0, green: 129/255.0, blue: 255/255.0, alpha: 1.0)
    default: return NSColor(srgbRed: 248/255.0, green: 248/255.0, blue: 242/255.0, alpha: 1.0)
    }
}
let accent = monokaiAccent(topic)

final class OverlayApp: NSObject, NSApplicationDelegate {
    var window: NSWindow?
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let screen = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let width: CGFloat = 460
        let height: CGFloat = 92
        let rect = NSRect(x: screen.maxX - width - 24, y: screen.maxY - height - 24, width: width, height: height)
        let panel = NSPanel(contentRect: rect, styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.level = .floating
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .transient]
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = true
        panel.ignoresMouseEvents = false

        let root = NSView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        root.wantsLayer = true
        root.layer?.cornerRadius = 14
        // Monokai theme
        root.layer?.backgroundColor = NSColor(srgbRed: 39/255.0, green: 40/255.0, blue: 34/255.0, alpha: 0.97).cgColor
        root.layer?.borderWidth = 2.0
        root.layer?.borderColor = accent.withAlphaComponent(0.85).cgColor

        let titleField = NSTextField(labelWithString: title)
        titleField.frame = NSRect(x: 20, y: 52, width: width - 40, height: 24)
        titleField.font = NSFont.systemFont(ofSize: 15, weight: .semibold)
        titleField.textColor = accent
        titleField.lineBreakMode = .byTruncatingTail
        root.addSubview(titleField)

        let messageField = NSTextField(labelWithString: message)
        messageField.frame = NSRect(x: 20, y: 22, width: width - 40, height: 24)
        messageField.font = NSFont.systemFont(ofSize: 13, weight: .regular)
        messageField.textColor = NSColor(srgbRed: 248/255.0, green: 248/255.0, blue: 242/255.0, alpha: 1.0)
        messageField.lineBreakMode = .byTruncatingTail
        root.addSubview(messageField)

        panel.contentView = root
        panel.alphaValue = 0
        panel.orderFrontRegardless()
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.12
            panel.animator().alphaValue = 1
        }
        self.window = panel
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.18
                panel.animator().alphaValue = 0
            }, completionHandler: {
                panel.close()
                NSApp.terminate(nil)
            })
        }
    }
}

let app = NSApplication.shared
let delegate = OverlayApp()
app.delegate = delegate
app.run()
'''


_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def strip_markdown(value: object) -> str:
    """Remove common markdown so notifications show plain text.

    Strips bold/italic/code/strike markers, heading/blockquote/list line
    prefixes, and reduces [text](url) to text. Preserves snake_case `_` and
    leaves bracket pairs alone (the [app]-[topic] tag is added later).
    """
    text = str(value or "")
    text = _MD_LINK.sub(r"\1", text)
    for token in ("**", "__", "~~", "`", "*"):
        text = text.replace(token, "")
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s{0,3}>\s?", "", text)
    text = re.sub(r"(?m)^\s{0,3}[-+]\s+", "", text)
    return text


def clean(value: str, limit: int = MAX_MESSAGE) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 15].rstrip() + "...<truncated>"


def emit(report: dict[str, object]) -> int:
    print(json.dumps(report, sort_keys=True))
    return 0


def overlay_cache_paths() -> tuple[Path, Path]:
    source_hash = hashlib.sha256(OVERLAY_SOURCE.encode("utf-8")).hexdigest()[:12]
    cache_dir = Path(os.environ.get("SKILL_SYSTEM_NOTIFY_CACHE", "/private/tmp/skill-system-notify-overlay"))
    return cache_dir / f"overlay-{source_hash}.swift", cache_dir / f"overlay-{source_hash}"


def compile_overlay() -> tuple[Path | None, dict[str, object] | None]:
    swiftc = shutil.which("swiftc")
    if swiftc is None:
        return None, {"status": "skipped", "platform": "Darwin", "reason": "swiftc not found"}
    source, binary = overlay_cache_paths()
    try:
        source.parent.mkdir(parents=True, exist_ok=True)
        if not binary.exists():
            source.write_text(OVERLAY_SOURCE, encoding="utf-8")
            completed = subprocess.run(
                [swiftc, str(source), "-o", str(binary)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=15,
            )
            if completed.returncode != 0:
                return None, {
                    "status": "error",
                    "platform": "Darwin",
                    "method": "swift_overlay_compile",
                    "returncode": completed.returncode,
                    "reason": clean(completed.stderr or completed.stdout, 160),
                }
            binary.chmod(0o700)
    except subprocess.TimeoutExpired:
        return None, {"status": "error", "platform": "Darwin", "method": "swift_overlay_compile", "reason": "compile timed out"}
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "error", "platform": "Darwin", "method": "swift_overlay_compile", "reason": clean(str(exc), 160)}
    return binary, None


def notify_macos_overlay(title: str, message: str, duration: float = 4.0, topic: str = "") -> dict[str, object]:
    binary, error = compile_overlay()
    if error is not None or binary is None:
        return error or {"status": "error", "platform": "Darwin", "method": "swift_overlay", "reason": "missing overlay binary"}
    try:
        subprocess.Popen(
            [str(binary), title, message, str(duration), topic],
            cwd="/",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "platform": "Darwin", "method": "swift_overlay", "reason": clean(str(exc), 160)}
    return {"status": "sent", "platform": "Darwin", "method": "swift_overlay"}


def notify_windows(title: str, message: str) -> dict[str, object]:
    executable = shutil.which("powershell") or shutil.which("pwsh")
    if executable is None:
        return {"status": "skipped", "platform": "Windows", "reason": "PowerShell not found"}
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "Add-Type -AssemblyName System.Drawing;"
        "$n = New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon = [System.Drawing.SystemIcons]::Information;"
        "$n.BalloonTipTitle = $args[0];"
        "$n.BalloonTipText = $args[1];"
        "$n.Visible = $true;"
        "$n.ShowBalloonTip(4000);"
        "Start-Sleep -Milliseconds 4500;"
        "$n.Dispose();"
    )
    completed = subprocess.run(
        [executable, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script, title, message],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=7,
    )
    if completed.returncode == 0:
        return {"status": "sent", "platform": "Windows", "method": "powershell_notifyicon"}
    return {
        "status": "error",
        "platform": "Windows",
        "method": "powershell_notifyicon",
        "returncode": completed.returncode,
        "reason": clean(completed.stderr or completed.stdout, 160),
    }


def notify_linux(title: str, message: str) -> dict[str, object]:
    if shutil.which("notify-send") is None:
        return {"status": "skipped", "platform": "Linux", "reason": "notify-send not found"}
    completed = subprocess.run(
        ["notify-send", "-a", "Claude", title, message],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=2,
    )
    if completed.returncode == 0:
        return {"status": "sent", "platform": "Linux", "method": "notify-send"}
    return {
        "status": "error",
        "platform": "Linux",
        "method": "notify-send",
        "returncode": completed.returncode,
        "reason": clean(completed.stderr or completed.stdout, 160),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--mode", choices=["auto", "native", "overlay"], default=os.environ.get("SKILL_SYSTEM_NOTIFY_MODE", "auto"))
    parser.add_argument("--topic", default="", help="approval|error|done|idle|input|progress|kanboard")
    parser.add_argument("--app", default="claude", help="codex|claude|shell|kanboard|other")
    parser.add_argument("--model", default="", help="short model label for the [stat]-[model]-[session] title")
    parser.add_argument("--session", default="", help="short session label for the [stat]-[model]-[session] title")
    parser.add_argument("--duration", type=float, default=float(os.environ.get("SKILL_SYSTEM_NOTIFY_DURATION", "4")))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    title = clean(strip_markdown(args.title), 80)
    message = clean(strip_markdown(args.message))
    model = clean(strip_markdown(args.model), 24)
    session = clean(strip_markdown(args.session), 24)
    if model or session:
        # Compact title line: [stat]-[model]-[session]
        stat = args.topic or args.app
        segments = [seg for seg in (stat, model, session) if seg]
        shown_title = clean("-".join(f"[{seg}]" for seg in segments), 100)
    else:
        tag = f"[{args.app}]-[{args.topic}]" if args.topic else f"[{args.app}]"
        shown_title = clean(f"{tag} {title}", 100)
    system = platform.system()
    if args.dry_run:
        return emit({"event": args.event, "topic": args.topic, "app": args.app, "mode": args.mode, "status": "dry_run", "platform": system, "title": title, "display_title": shown_title, "message": message})
    try:
        if system == "Darwin":
            # macOS uses the Swift overlay only; osascript/Script Editor delivery removed.
            report = notify_macos_overlay(shown_title, message, args.duration, args.topic)
        elif system == "Windows":
            report = notify_windows(shown_title, message)
        elif system == "Linux":
            report = notify_linux(shown_title, message)
        else:
            report = {"status": "skipped", "platform": system, "reason": "unsupported platform"}
    except subprocess.TimeoutExpired:
        report = {"status": "error", "platform": system, "reason": "notification command timed out"}
    except Exception as exc:  # noqa: BLE001 - notifications must not break hooks.
        report = {"status": "error", "platform": system, "reason": clean(str(exc), 160)}
    report["event"] = args.event
    if args.topic:
        report["topic"] = args.topic
    report["app"] = args.app
    report["display_title"] = shown_title
    return emit(report)


if __name__ == "__main__":
    raise SystemExit(main())
