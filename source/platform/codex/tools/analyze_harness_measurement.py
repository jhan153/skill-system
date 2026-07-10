#!/usr/bin/env python3
"""Out-of-band harness measurement for the observed-evidence gate.

Answers the harness-paradox question: does the strict gate help, hurt, or do
nothing vs a gate-off baseline? Reads one hash-chained hook event ledger or the
default per-run ledger family (hook_runtime), groups `turn_finalize` events by
holdout arm, and reports per-arm evidence-gate and Recovery Guard fire/block
rates, finalize-fail rates, and a sunset recommendation.

Read-only: never writes, never touches the gate. Pure functions (`holdout_arm`,
`stratified_compare`, `sunset_status`) are unit-testable without I/O. Holdout
assignment and event tagging are done by the hook adapters; this tool only
aggregates. Richer outcome signals (reverts, re-instructions) need a
host-specific transcript/git collector and are out of scope here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

SUNSET_SESSIONS = 50
ARMS = ("on", "off")


def holdout_arm(session_id: str, on_ratio: float = 0.8) -> str:
    """Deterministic, model-blind arm assignment from the session id."""
    if not session_id:
        return "on"
    digest = hashlib.sha256(str(session_id).encode("utf-8", "replace")).hexdigest()
    bucket = int(digest[:8], 16) / float(0xFFFFFFFF)
    return "on" if bucket < on_ratio else "off"


def _finalize_events(events: list) -> list[dict[str, Any]]:
    # A measured finalize event: a turn_finalize OR turn_finalize_attempt that
    # carries a holdout arm tag. The Codex adapter records strict-block turns
    # (validation_code != 0) as turn_finalize_attempt, so reading only
    # turn_finalize would miss exactly the blocked cases. The early untagged
    # turn_finalize_attempt has no holdout_arm and is excluded.
    finalize = {"turn_finalize", "turn_finalize_attempt"}
    out: list[dict[str, Any]] = []
    for e in events:
        if not isinstance(e, dict) or e.get("neutral_event") not in finalize:
            continue
        ev = e.get("evidence")
        if isinstance(ev, dict) and ev.get("holdout_arm") is not None:
            out.append(e)
    return out


def stratified_compare(events: list) -> dict:
    sessions = {a: set() for a in ARMS}
    fire = {a: 0 for a in ARMS}
    block = {a: 0 for a in ARMS}
    recovery_audit = {a: 0 for a in ARMS}
    recovery_block = {a: 0 for a in ARMS}
    fail = {a: 0 for a in ARMS}
    total = {a: 0 for a in ARMS}
    for e in _finalize_events(events):
        ev = e.get("evidence") or {}
        arm = ev.get("holdout_arm")
        if arm not in ARMS:
            continue
        total[arm] += 1
        sessions[arm].add(e.get("session_id"))
        if ev.get("would_fire"):
            fire[arm] += 1
        if ev.get("did_block"):
            block[arm] += 1
        if ev.get("recovery_would_audit"):
            recovery_audit[arm] += 1
        if ev.get("recovery_did_block"):
            recovery_block[arm] += 1
        if e.get("status") == "fail":
            fail[arm] += 1
    res: dict[str, Any] = {}
    for a in ARMS:
        t = total[a]
        res[a] = {
            "sessions": len(sessions[a]),
            "finalizes": t,
            "would_fire_rate": (fire[a] / t) if t else None,
            "block_rate": (block[a] / t) if t else None,
            "recovery_would_audit_rate": (recovery_audit[a] / t) if t else None,
            "recovery_block_rate": (recovery_block[a] / t) if t else None,
            "finalize_fail_rate": (fail[a] / t) if t else None,
        }
    on_f, off_f = res["on"]["finalize_fail_rate"], res["off"]["finalize_fail_rate"]
    res["harness_paradox_fail_delta"] = None if on_f is None or off_f is None else on_f - off_f
    return res


def sunset_status(events: list, horizon: int = SUNSET_SESSIONS) -> dict:
    n = len({e.get("session_id") for e in _finalize_events(events) if e.get("session_id")})
    signal = stratified_compare(events)["harness_paradox_fail_delta"] is not None
    expired = (n >= horizon) and not signal
    if expired:
        rec = "remove (sunset reached, no comparable on/off signal)"
    elif signal:
        rec = "keep (comparable on/off signal — analyze)"
    else:
        rec = "keep collecting (insufficient data)"
    return {"distinct_sessions": n, "horizon": horizon, "signal_present": signal,
            "expired": expired, "recommendation": rec}


def load_events(path: Path) -> list:
    if not path.exists():
        return []
    out: list = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def discover_ledgers(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("hook-events.jsonl") if path.is_file())


def load_events_from_root(root: Path) -> list:
    events: list = []
    for ledger in discover_ledgers(root):
        events.extend(load_events(ledger))
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--ledger", type=Path, default=None)
    source.add_argument("--ledger-root", type=Path, default=None)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from hook_runtime import configured_ledger, default_ledger_root  # noqa: PLC0415

    ledger = args.ledger
    ledger_root = args.ledger_root
    if ledger is None and ledger_root is None:
        ledger = configured_ledger()
        if ledger is None:
            ledger_root = default_ledger_root()

    if ledger is not None:
        ledgers = [ledger] if ledger.is_file() else []
        events = load_events(ledger)
    else:
        assert ledger_root is not None
        ledgers = discover_ledgers(ledger_root)
        events = load_events_from_root(ledger_root)
    print(json.dumps({
        "ledger": str(ledger) if ledger is not None else None,
        "ledger_root": str(ledger_root) if ledger_root is not None else None,
        "ledger_count": len(ledgers),
        "stratified_compare": stratified_compare(events),
        "sunset_status": sunset_status(events),
    }, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
