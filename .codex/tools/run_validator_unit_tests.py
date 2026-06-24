#!/usr/bin/env python3
"""Run validator unit tests without writing Python bytecode caches."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    start_dir = root / ".codex" / "tools" / "tests"
    suite = unittest.defaultTestLoader.discover(str(start_dir))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
