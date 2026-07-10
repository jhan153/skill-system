from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


TOOLS = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "evidence-ledgers"
MODULE_PATH = TOOLS / "check_evidence_ledger.py"
SPEC = importlib.util.spec_from_file_location("check_evidence_ledger_source", MODULE_PATH)
assert SPEC and SPEC.loader
ledger_tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger_tool)


def find_v2_reference() -> Path:
    relative = Path("skills/search-deep-evidence/references/evidence-ledger-v2.md")
    for parent in Path(__file__).resolve().parents:
        for candidate in (parent / relative, parent / ".codex" / relative, parent / "source" / relative):
            if candidate.is_file():
                return candidate
    raise RuntimeError("could not locate evidence-ledger-v2.md")


class EvidenceLedgerCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.legacy = yaml.safe_load(
            (FIXTURES / "legacy-v1.yaml").read_text(encoding="utf-8")
        )

    def test_v1_migration_preserves_uncertainty_and_legacy_fields(self) -> None:
        migrated = ledger_tool.migrate_v1_ledger(self.legacy)

        self.assertEqual(migrated["schema_version"], 2)
        self.assertTrue(migrated["migration"]["review_required"])
        self.assertEqual(ledger_tool.check(migrated, min_claims=3), [])
        self.assertEqual(self.legacy["schema_version"], 1, "migration must not mutate its input")

        confirmed, refuted, partial = migrated["claims"]
        for claim in migrated["claims"]:
            self.assertEqual(claim["conclusion"], "insufficient")
            self.assertTrue(claim["missing_evidence"])
        self.assertEqual(confirmed["legacy_v1"]["verdict"], "confirmed")
        self.assertEqual(confirmed["evidence"][0]["claim_relation"], "not_assessed")
        self.assertEqual(confirmed["evidence"][0]["source_status"], "metadata_partial")
        self.assertEqual(refuted["legacy_v1"]["verdict"], "refuted")
        self.assertNotEqual(refuted["conclusion"], "contradicted")
        self.assertIn("exclusion_reason", refuted)
        self.assertEqual(partial["legacy_v1"]["citation_status"], "fabricated-risk")
        self.assertEqual(partial["evidence"][0]["source_status"], "unverified")

    def test_cli_dual_reads_v1_and_can_print_reviewable_v2(self) -> None:
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        checked = subprocess.run(
            [sys.executable, str(MODULE_PATH), str(FIXTURES / "legacy-v1.yaml")],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertTrue(checked.stdout.startswith("PASS"), checked.stdout)
        self.assertIn("conclusions remain insufficient", checked.stdout)

        printed = subprocess.run(
            [
                sys.executable,
                str(MODULE_PATH),
                str(FIXTURES / "legacy-v1.yaml"),
                "--print-migrated-v2",
            ],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(printed.returncode, 0, printed.stdout + printed.stderr)
        migrated = yaml.safe_load(printed.stdout)
        self.assertEqual(migrated["schema_version"], 2)
        self.assertEqual({claim["conclusion"] for claim in migrated["claims"]}, {"insufficient"})

    def test_schema_versions_are_exact_integers(self) -> None:
        for ambiguous_version in (True, 1.0):
            with self.subTest(version=ambiguous_version):
                ambiguous = dict(self.legacy, schema_version=ambiguous_version)
                normalized, note = ledger_tool.normalize_ledger(ambiguous)
                self.assertIs(normalized, ambiguous)
                self.assertIsNone(note)
                self.assertIn("schema_version must be 2", ledger_tool.check(normalized, 1))

        v2_float = ledger_tool.migrate_v1_ledger(self.legacy)
        v2_float["schema_version"] = 2.0
        self.assertIn("schema_version must be 2", ledger_tool.check(v2_float, 1))

    def test_resolved_relation_must_come_from_the_usable_record(self) -> None:
        for conclusion, usable_relation, unusable_relation, expected_error in (
            ("supported", "mentions", "supports", "supporting evidence"),
            ("contradicted", "mentions", "contradicts", "contradicting evidence"),
            ("mixed", "supports", "contradicts", "supporting and contradicting evidence"),
        ):
            with self.subTest(conclusion=conclusion):
                ledger = {
                    "schema_version": 2,
                    "claims": [
                        {
                            "id": "C-SPLIT",
                            "statement": "A split-record reward hack must fail.",
                            "conclusion": conclusion,
                            "evidence": [
                                {
                                    "acquisition_status": "not_acquired",
                                    "source_status": "unverified",
                                    "claim_relation": unusable_relation,
                                    "evidence_basis": "metadata_only",
                                },
                                {
                                    "acquisition_status": "acquired",
                                    "source_status": "verified_identity",
                                    "claim_relation": usable_relation,
                                    "evidence_basis": "full_text",
                                    "locator": "https://example.invalid/usable-record",
                                },
                            ],
                        }
                    ],
                }

                errors = ledger_tool.check(ledger, min_claims=1)
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )

    def test_conditional_v2_reference_example_matches_verifier(self) -> None:
        reference = find_v2_reference().read_text(encoding="utf-8")
        example = reference.split("```yaml\n", 1)[1].split("\n```", 1)[0]
        ledger = yaml.safe_load(example)
        self.assertEqual(ledger_tool.check(ledger, min_claims=1), [])


if __name__ == "__main__":
    unittest.main()
