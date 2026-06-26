#!/usr/bin/env python3
"""Unit tests for analyze_harness_measurement (pure functions, no I/O).

Run: python3 .codex/tools/tests/test_harness_measurement.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_harness_measurement import holdout_arm, stratified_compare, sunset_status  # noqa: E402


def finalize(session_id, arm, would_fire=False, did_block=False, status="pass"):
    return {
        "neutral_event": "turn_finalize",
        "session_id": session_id,
        "status": status,
        "evidence": {"holdout_arm": arm, "would_fire": would_fire, "did_block": did_block},
    }


class HoldoutArmTests(unittest.TestCase):
    def test_deterministic(self) -> None:
        self.assertEqual(holdout_arm("session-xyz"), holdout_arm("session-xyz"))

    def test_empty_defaults_on(self) -> None:
        self.assertEqual(holdout_arm(""), "on")

    def test_split_is_roughly_eighty_twenty(self) -> None:
        arms = [holdout_arm(f"s{i}") for i in range(2000)]
        on_ratio = arms.count("on") / len(arms)
        self.assertTrue(0.74 < on_ratio < 0.86, on_ratio)


class StratifiedCompareTests(unittest.TestCase):
    def test_delta_none_without_both_arms(self) -> None:
        cmp = stratified_compare([finalize("s1", "on", status="fail")])
        self.assertIsNone(cmp["harness_paradox_fail_delta"])
        self.assertEqual(cmp["on"]["finalize_fail_rate"], 1.0)

    def test_delta_present_with_both_arms(self) -> None:
        events = [
            finalize("s1", "on", would_fire=True, did_block=True, status="fail"),
            finalize("s2", "on", status="pass"),
            finalize("s3", "off", would_fire=True, status="pass"),
            finalize("s4", "off", status="pass"),
        ]
        cmp = stratified_compare(events)
        self.assertEqual(cmp["on"]["finalize_fail_rate"], 0.5)
        self.assertEqual(cmp["off"]["finalize_fail_rate"], 0.0)
        self.assertEqual(cmp["harness_paradox_fail_delta"], 0.5)
        self.assertEqual(cmp["off"]["block_rate"], 0.0)  # off arm never blocks (baseline)
        self.assertEqual(cmp["off"]["would_fire_rate"], 0.5)

    def test_ignores_non_finalize_events(self) -> None:
        cmp = stratified_compare([{"neutral_event": "tool_result", "evidence": {"holdout_arm": "on"}}])
        self.assertIsNone(cmp["on"]["finalize_fail_rate"])


class SunsetTests(unittest.TestCase):
    def test_insufficient_keeps_collecting(self) -> None:
        st = sunset_status([finalize("s1", "on")], horizon=50)
        self.assertFalse(st["signal_present"])
        self.assertIn("collecting", st["recommendation"])

    def test_expired_recommends_remove(self) -> None:
        events = [finalize(f"s{i}", "on") for i in range(50)]  # one arm only -> no signal
        st = sunset_status(events, horizon=50)
        self.assertTrue(st["expired"])
        self.assertIn("remove", st["recommendation"])


if __name__ == "__main__":
    unittest.main()
