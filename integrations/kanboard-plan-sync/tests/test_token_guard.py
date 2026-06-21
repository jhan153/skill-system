import tempfile
import unittest
from pathlib import Path

from kanboard_plan_sync.token_guard import scan_text, scan_workspace

CLEAN_CONFIG = """
workspace:
  name: ws
kanboard:
  url: http://127.0.0.1:8080/jsonrpc.php
  token_env: KANBOARD_API_TOKEN
plans: []
"""

LEAKY_CONFIG = """
workspace:
  name: ws
kanboard:
  url: http://127.0.0.1:8080/jsonrpc.php
  token: super-secret-value
plans: []
"""


class SecretScanTextTest(unittest.TestCase):
    def test_token_assignment_flagged(self):
        self.assertTrue(scan_text("token: abc"))
        self.assertTrue(scan_text("api_token = abc"))
        self.assertTrue(scan_text("password: hunter2"))

    def test_token_env_not_flagged(self):
        self.assertEqual(scan_text("token_env: KANBOARD_API_TOKEN"), [])

    def test_prose_not_flagged(self):
        # mid-line mention of 'token' is not an assignment
        self.assertEqual(scan_text("- 대응: token은 환경변수만 허용한다"), [])

    def test_literal_token_value_flagged(self):
        self.assertTrue(scan_text("note deadbeef here", env_token="deadbeef"))


class SecretScanWorkspaceTest(unittest.TestCase):
    def test_clean_workspace_ok(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".kanboard-plan.yml").write_text(CLEAN_CONFIG, encoding="utf-8")
            report = scan_workspace(d)
            self.assertTrue(report["ok"])
            self.assertEqual(report["findings"], [])

    def test_leaky_config_detected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".kanboard-plan.yml").write_text(LEAKY_CONFIG, encoding="utf-8")
            report = scan_workspace(d)
            self.assertFalse(report["ok"])
            self.assertTrue(any("token" in f["issue"] for f in report["findings"]))


if __name__ == "__main__":
    unittest.main()
