from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fees import total_with_fee


class FeeTests(unittest.TestCase):
    def test_total_includes_positive_fee(self) -> None:
        self.assertEqual(total_with_fee(10_000, 350), 10_350)


if __name__ == "__main__":
    unittest.main()
