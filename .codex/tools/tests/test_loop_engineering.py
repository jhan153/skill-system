#!/usr/bin/env python3
"""Loop-engineering invariants added in the 8.2 bounded-loop hardening.

Covers: activation bridge (session pointer), monotonic iteration, terminal
immutability, idempotent replay, iterations/ audit records, and explicit resume.
Run: python3 .codex/tools/tests/test_loop_engineering.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / ".codex" / "tools"
FIXTURE = TOOLS / "tests" / "fixtures" / "loop-runs" / "valid"


def run(tool: str, *args: str, **kw) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *args],
        cwd=str(TOOLS),
        text=True,
        capture_output=True,
        check=False,
        **kw,
    )


def write_result(
    path: Path,
    iteration: int,
    rid: str,
    status: str,
    evidence=(),
    receipts=(),
    side_effects=(),
    loop_run_id: str = "LR-20260623-010",
) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 2,
                "loop_run_id": loop_run_id,
                "iteration": iteration,
                "iteration_result_id": rid,
                "condition_results": [
                    {
                        "condition_id": "SC-001",
                        "status": status,
                        "evidence_refs": list(evidence),
                        "evidence": list(receipts),
                    }
                ],
                "side_effects": list(side_effects),
            }
        ),
        encoding="utf-8",
    )


class LoopEngineeringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(__import__("tempfile").mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.loop = self.tmp / "loop"
        shutil.copytree(FIXTURE, self.loop)
        for rel in ["state.yaml", "checkpoints/0000.yaml"]:
            path = self.loop / rel
            state = yaml.safe_load(path.read_text(encoding="utf-8"))
            state["workspace"]["root"] = str(self.loop)
            path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        self.ir = self.tmp / "ir.yaml"

    def evaluate(self) -> subprocess.CompletedProcess[str]:
        return run("evaluate_loop_run.py", str(self.loop), "--iteration-result", str(self.ir), "--format", "json")

    def state(self) -> dict:
        return yaml.safe_load((self.loop / "state.yaml").read_text(encoding="utf-8"))

    def write_state_and_checkpoint(self, state: dict) -> None:
        for path in [
            self.loop / "state.yaml",
            self.loop / "checkpoints" / f"{int(state.get('iteration', 0)):04d}.yaml",
        ]:
            path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")

    def artifact_receipt(self, name: str = "primary.ok", *, digest: str | None = None) -> dict:
        artifact = self.loop / "artifacts" / name
        artifact.write_text("complete\n", encoding="utf-8")
        return {
            "kind": "artifact_exists",
            "verifier_owner": "agent:codex",
            "observed_at": self.state()["started_at"],
            "outcome": "pass",
            "artifact_ref": f"artifacts/{name}",
            "artifact_scope": "workspace",
            "artifact_sha256": digest or hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }

    # --- P2: monotonic sequencing -------------------------------------------
    def test_monotonic_rejects_iteration_skip(self) -> None:
        write_result(self.ir, 2, "IR-skip", "fail")  # state is at iteration 0; expected 1
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("sequence conflict", result.stdout)
        self.assertEqual(self.state()["iteration"], 0)

    # --- P2: terminal immutability ------------------------------------------
    def test_terminal_loop_rejects_new_result(self) -> None:
        receipt = self.artifact_receipt()
        write_result(self.ir, 1, "IR-pass", "pass", receipts=[receipt])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["status"], "success")
        write_result(self.ir, 2, "IR-late", "fail")
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("terminal", result.stdout)
        self.assertEqual(self.state()["status"], "success")  # not reopened

    # --- P2: idempotent replay ----------------------------------------------
    def test_replay_is_idempotent_and_does_not_duplicate_side_effects(self) -> None:
        write_result(self.ir, 1, "IR-x", "fail", side_effects=["wrote X"])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["side_effect_journal"], ["wrote X"])
        # resubmit the same result id
        replay = self.evaluate()
        self.assertEqual(replay.returncode, 0)
        self.assertTrue(json.loads(replay.stdout).get("replay"))
        self.assertEqual(self.state()["side_effect_journal"], ["wrote X"])  # no duplication

    def test_replay_id_reused_with_different_payload_is_conflict(self):
        write_result(self.ir, 1, "IR-c", "fail")
        self.assertEqual(self.evaluate().returncode, 0)
        # Same iteration_result_id, different payload (pass vs fail) -> conflict.
        write_result(self.ir, 1, "IR-c", "pass", evidence=["artifacts/x"])
        result = self.evaluate()
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("conflict", result.stdout)

    # --- P2: iterations/ audit ----------------------------------------------
    def test_iterations_audit_records_input_and_decision(self) -> None:
        write_result(self.ir, 1, "IR-a", "fail")
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertTrue((self.loop / "iterations" / "0001.input.yaml").is_file())
        self.assertTrue((self.loop / "iterations" / "0001.decision.yaml").is_file())
        self.assertTrue((self.loop / "iterations" / "0001.checkpoint.yaml").is_file())

    # --- P2: explicit resume ------------------------------------------------
    def test_resume_reopens_terminal_loop(self) -> None:
        receipt = self.artifact_receipt()
        write_result(self.ir, 1, "IR-pass", "pass", receipts=[receipt])
        self.assertEqual(self.evaluate().returncode, 0)
        self.assertEqual(self.state()["status"], "success")
        resumed = run("resume_loop_run.py", str(self.loop), "--reason", "manual retry")
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(self.state()["status"], "active")
        self.assertEqual(self.state()["resumes"][0]["from"], "success")

    # --- Evidence integrity -------------------------------------------------
    def test_arbitrary_evidence_ref_cannot_make_required_condition_pass(self) -> None:
        write_result(self.ir, 1, "IR-fake", "pass", evidence=["looks-real.txt"])
        result = self.evaluate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("structured evidence receipt", result.stdout)
        self.assertEqual(self.state()["iteration"], 0)
        self.assertEqual(self.state()["status"], "active")

    def test_tampered_artifact_receipt_digest_is_rejected(self) -> None:
        receipt = self.artifact_receipt(digest="0" * 64)
        write_result(self.ir, 1, "IR-tampered", "pass", receipts=[receipt])
        result = self.evaluate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("artifact_sha256 does not match", result.stdout)

    def test_receipt_owner_timestamp_and_outcome_are_enforced(self) -> None:
        cases = [
            ("verifier_owner", "other-owner", "owner"),
            ("observed_at", "2026-06-23T00:10:00", "timestamp"),
            ("observed_at", "2020-01-01T00:00:00Z", "stale"),
            ("outcome", "user-verification-needed", "outcome"),
        ]
        for field, value, label in cases:
            with self.subTest(field=field):
                receipt = self.artifact_receipt(name="primary.ok")
                receipt[field] = value
                write_result(self.ir, 1, f"IR-{label}", "pass", receipts=[receipt])
                result = self.evaluate()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_loop_validator_detects_receipt_artifact_tampering(self) -> None:
        receipt = self.artifact_receipt()
        write_result(self.ir, 1, "IR-durable", "pass", receipts=[receipt])
        self.assertEqual(self.evaluate().returncode, 0)
        (self.loop / "artifacts" / "primary.ok").write_text("tampered\n", encoding="utf-8")
        validated = run("validate_loop_run.py", str(self.loop))
        self.assertEqual(validated.returncode, 1, validated.stdout + validated.stderr)
        self.assertIn("artifact_sha256 does not match", validated.stdout)

    def test_replay_revalidates_persisted_artifact_evidence(self) -> None:
        receipt = self.artifact_receipt()
        write_result(self.ir, 1, "IR-replay-tamper", "pass", receipts=[receipt])
        self.assertEqual(self.evaluate().returncode, 0)
        (self.loop / "artifacts" / "primary.ok").write_text("tampered\n", encoding="utf-8")
        replay = self.evaluate()
        self.assertEqual(replay.returncode, 3, replay.stdout + replay.stderr)
        self.assertIn("integrity validation failed", replay.stdout)

    def test_validator_rejects_iteration_zero_fabricated_success(self) -> None:
        state = self.state()
        receipt = self.artifact_receipt()
        state["condition_results"][0] = {
            "condition_id": "SC-001",
            "status": "pass",
            "evidence_refs": ["artifacts/primary.ok"],
            "evidence": [receipt],
        }
        state["status"] = "success"
        state["progress"]["required_passed"] = 1
        fingerprint_body = {
            "required": [{"id": "SC-001", "status": "pass", "failure_fingerprint": None}],
            "iteration": 0,
        }
        state["progress"]["state_hash"] = hashlib.sha256(
            json.dumps(
                fingerprint_body,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        self.write_state_and_checkpoint(state)
        validated = run("validate_loop_run.py", str(self.loop))
        self.assertEqual(validated.returncode, 1, validated.stdout + validated.stderr)
        self.assertIn("iteration 0 cannot contain a required pass", validated.stdout)

    def test_validator_binds_iteration_input_to_checkpoint(self) -> None:
        write_result(self.ir, 1, "IR-audit-bind", "fail")
        self.assertEqual(self.evaluate().returncode, 0)
        state = self.state()
        state["condition_results"][0]["status"] = "blocked"
        self.write_state_and_checkpoint(state)
        validated = run("validate_loop_run.py", str(self.loop))
        self.assertEqual(validated.returncode, 1, validated.stdout + validated.stderr)
        self.assertIn("condition_results does not match the latest immutable iteration checkpoint", validated.stdout)

    def test_receipt_kind_must_match_contract_verifier(self) -> None:
        artifact = self.loop / "artifacts" / "wrong-kind.txt"
        artifact.write_text("not a command receipt\n", encoding="utf-8")
        receipt = {
            "kind": "diff_scope",
            "verifier_owner": "agent:codex",
            "observed_at": "2026-06-23T00:10:00Z",
            "outcome": "pass",
            "artifact_ref": "artifacts/wrong-kind.txt",
            "artifact_scope": "loop_run",
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }
        write_result(self.ir, 1, "IR-wrong-kind", "pass", receipts=[receipt])
        result = self.evaluate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("does not match contract verifier", result.stdout)

    # --- P1: activation bridge ----------------------------------------------
    def test_activation_pointer_roundtrip(self) -> None:
        env = {**os.environ, "CODEX_HOME": str(self.tmp / "codexhome")}
        act = run("activate_loop_run.py", "--session-id", "SESS-1", "--loop-run-dir", str(self.loop), env=env)
        self.assertEqual(act.returncode, 0, act.stdout + act.stderr)
        pointer = self.tmp / "codexhome" / "harness" / "active-loops" / "SESS-1.json"
        self.assertTrue(pointer.is_file())
        self.assertEqual(json.loads(pointer.read_text())["status"], "active")
        deact = run("deactivate_loop_run.py", "--session-id", "SESS-1", env=env)
        self.assertEqual(deact.returncode, 0, deact.stdout + deact.stderr)
        self.assertEqual(json.loads(pointer.read_text())["status"], "inactive")

    # --- P5: wall-time enforcement + precedence vocabulary ------------------
    def _init_contract(self, max_wall: int) -> Path:
        contract = self.tmp / "wc.yaml"
        contract.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 2,
                    "contract_id": "LC-20260623-777",
                    "activation": "explicit",
                    "goal": {
                        "statement": "wall-time test",
                        "success_conditions": [
                            {
                                "id": "SC-001",
                                "statement": "primary",
                                "required": True,
                                "verifier": {
                                    "type": "command_exit",
                                    "owner": "ci:wall-time",
                                    "command": "true",
                                    "expected_exit_code": 0,
                                },
                            }
                        ],
                    },
                    "control": {
                        "max_iterations": 99,
                        "max_wall_time_seconds": max_wall,
                        "no_progress_limit": 99,
                        "same_failure_limit": 99,
                        "max_stop_continuations": 99,
                    },
                    "termination": {
                        "precedence": [
                            "unsafe", "fatal", "blocked", "success",
                            "approval_required", "stalled", "budget_exhausted", "recover", "continue",
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )
        out = run("init_loop_run.py", str(contract), "--output-root", str(self.tmp / "runs"), "--workspace-root", str(self.tmp))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return Path(json.loads(out.stdout)["loop_run_dir"])

    def _init_manual_contract(self) -> Path:
        contract = self.tmp / "manual-contract.yaml"
        contract.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 2,
                    "contract_id": "LC-20260623-778",
                    "activation": "explicit",
                    "goal": {
                        "statement": "manual acceptance test",
                        "success_conditions": [
                            {
                                "id": "SC-001",
                                "statement": "The user explicitly accepts the result.",
                                "required": True,
                                "verifier": {
                                    "type": "manual_check",
                                    "owner": "user-42",
                                    "acceptance_scope": "SC-001",
                                },
                            }
                        ],
                    },
                    "control": {
                        "max_iterations": 3,
                        "max_wall_time_seconds": 0,
                        "no_progress_limit": 2,
                        "same_failure_limit": 2,
                        "max_stop_continuations": 3,
                    },
                    "termination": {"precedence": ["blocked", "success", "budget_exhausted", "continue"]},
                }
            ),
            encoding="utf-8",
        )
        out = run("init_loop_run.py", str(contract), "--output-root", str(self.tmp / "runs"), "--workspace-root", str(self.tmp))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        return Path(json.loads(out.stdout)["loop_run_dir"])

    def test_claimed_command_log_cannot_self_attest_success(self) -> None:
        loop = self._init_contract(max_wall=0)
        log = loop / "artifacts" / "claimed-command.log"
        log.write_text("claimed exit_code=0\n", encoding="utf-8")
        observed_at = yaml.safe_load((loop / "state.yaml").read_text(encoding="utf-8"))["started_at"]
        receipt = {
            "kind": "command_exit",
            "verifier_owner": "ci:wall-time",
            "observed_at": observed_at,
            "outcome": "pass",
            "artifact_ref": "artifacts/claimed-command.log",
            "artifact_scope": "loop_run",
            "artifact_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
            "command": "true",
            "exit_code": 0,
        }
        write_result(
            self.ir,
            1,
            "IR-command-claim",
            "pass",
            receipts=[receipt],
            loop_run_id="LR-20260623-777",
        )
        result = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(self.ir), "--format", "json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("not runtime-authenticated", result.stdout)

    def test_claimed_diff_scope_log_cannot_self_attest_success(self) -> None:
        contract = yaml.safe_load((FIXTURE / "contract.yaml").read_text(encoding="utf-8"))
        contract["contract_id"] = "LC-20260623-779"
        contract["goal"]["success_conditions"] = [
            {
                "id": "SC-001",
                "statement": "The checked diff stays under target.txt.",
                "required": True,
                "verifier": {"type": "diff_scope", "owner": "agent:codex", "path": "target.txt"},
            }
        ]
        contract_path = self.tmp / "diff-contract.yaml"
        contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        workspace = self.tmp / "diff-workspace"
        workspace.mkdir()
        (workspace / "target.txt").write_text("changed\n", encoding="utf-8")
        initialized = run(
            "init_loop_run.py",
            str(contract_path),
            "--output-root",
            str(self.tmp / "diff-runs"),
            "--workspace-root",
            str(workspace),
        )
        self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
        loop = Path(json.loads(initialized.stdout)["loop_run_dir"])
        claim = loop / "artifacts" / "claimed-diff.log"
        claim.write_text("claimed in scope\n", encoding="utf-8")
        state = yaml.safe_load((loop / "state.yaml").read_text(encoding="utf-8"))
        receipt = {
            "kind": "diff_scope",
            "verifier_owner": "agent:codex",
            "observed_at": state["started_at"],
            "outcome": "pass",
            "artifact_ref": "artifacts/claimed-diff.log",
            "artifact_scope": "loop_run",
            "artifact_sha256": hashlib.sha256(claim.read_bytes()).hexdigest(),
            "checked_path": "target.txt",
        }
        result_path = self.tmp / "diff-result.yaml"
        write_result(
            result_path,
            1,
            "IR-diff-claim",
            "pass",
            receipts=[receipt],
            loop_run_id=state["loop_run_id"],
        )
        result = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(result_path), "--format", "json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("scope logs are not runtime-authenticated", result.stdout)

    def test_init_rejects_optional_only_duplicate_and_unbound_invariant_contracts(self) -> None:
        base = yaml.safe_load((FIXTURE / "contract.yaml").read_text(encoding="utf-8"))
        cases: list[tuple[str, dict, str]] = []

        optional = yaml.safe_load(yaml.safe_dump(base))
        for condition in optional["goal"]["success_conditions"]:
            condition["required"] = False
        cases.append(("optional", optional, "at least one success condition must be required"))

        duplicate = yaml.safe_load(yaml.safe_dump(base))
        duplicate["goal"]["success_conditions"].append(
            yaml.safe_load(yaml.safe_dump(duplicate["goal"]["success_conditions"][0]))
        )
        cases.append(("duplicate", duplicate, "duplicate success condition ids"))

        invariant = yaml.safe_load(yaml.safe_dump(base))
        invariant["goal"]["invariants"] = [
            {"id": "INV-001", "statement": "Must remain true.", "verifier": {}}
        ]
        cases.append(("invariant", invariant, "promote them to required success conditions"))

        for index, (name, contract, expected) in enumerate(cases, start=1):
            with self.subTest(name=name):
                contract["contract_id"] = f"LC-20260624-{index:03d}"
                path = self.tmp / f"{name}.yaml"
                path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
                initialized = run(
                    "init_loop_run.py",
                    str(path),
                    "--output-root",
                    str(self.tmp / f"{name}-runs"),
                    "--workspace-root",
                    str(self.tmp),
                )
                self.assertEqual(initialized.returncode, 1, initialized.stdout + initialized.stderr)
                self.assertIn(expected, initialized.stdout)

    def test_user_verification_needed_requires_explicit_manual_acceptance(self) -> None:
        loop = self._init_manual_contract()
        pending = self.tmp / "manual-pending.yaml"
        write_result(
            pending,
            1,
            "IR-manual-pending",
            "unverified",
            evidence=["user-verification-needed"],
            loop_run_id="LR-20260623-778",
        )
        first = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(pending), "--format", "json")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertNotEqual(json.loads(first.stdout)["decision"]["action"], "success")

        observed_at = yaml.safe_load((loop / "state.yaml").read_text(encoding="utf-8"))["started_at"]
        acceptance = loop / "artifacts" / "manual-acceptance.yaml"
        acceptance.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "event_type": "user_acceptance",
                    "contract_id": "LC-20260623-778",
                    "loop_run_id": "LR-20260623-778",
                    "condition_id": "SC-001",
                    "actor": "user-42",
                    "scope": "SC-001",
                    "accepted": True,
                    "observed_at": observed_at,
                    "source": "user_input",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        receipt = {
            "kind": "manual_acceptance",
            "verifier_owner": "user-42",
            "observed_at": observed_at,
            "outcome": "pass",
            "artifact_ref": "artifacts/manual-acceptance.yaml",
            "artifact_scope": "loop_run",
            "artifact_sha256": hashlib.sha256(acceptance.read_bytes()).hexdigest(),
            "actor": "user-42",
            "actor_type": "user",
            "accepted_scope": "SC-001",
            "accepted": True,
        }
        accepted = self.tmp / "manual-accepted.yaml"
        write_result(
            accepted,
            2,
            "IR-manual-accepted",
            "pass",
            receipts=[receipt],
            loop_run_id="LR-20260623-778",
        )
        second = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(accepted), "--format", "json")
        self.assertEqual(second.returncode, 1, second.stdout + second.stderr)
        self.assertIn("host-authenticated user provenance", second.stdout)

    def test_wall_time_budget_is_enforced(self) -> None:
        loop = self._init_contract(max_wall=1)
        state_path = loop / "state.yaml"
        state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        state["started_at"] = "2020-01-01T00:00:00Z"  # far in the past
        for path in [state_path, loop / "checkpoints" / f"{int(state.get('iteration', 0)):04d}.yaml"]:
            path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")
        ir = self.tmp / "irw.yaml"
        ir.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 2,
                    "loop_run_id": "LR-20260623-777",
                    "iteration": 1,
                    "iteration_result_id": "IR-w1",
                    "condition_results": [{"condition_id": "SC-001", "status": "fail", "evidence_refs": []}],
                }
            ),
            encoding="utf-8",
        )
        result = run("evaluate_loop_run.py", str(loop), "--iteration-result", str(ir), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        decision = json.loads(result.stdout)["decision"]
        self.assertEqual(decision["action"], "budget_exhausted")
        self.assertEqual(decision["reason_code"], "wall_time_exhausted")

    def test_precedence_vocabulary_accepts_recover_and_blocked(self) -> None:
        # A contract listing the controller's real vocabulary (recover/blocked)
        # validates and runs — the vocabulary is coherent end-to-end.
        loop = self._init_contract(max_wall=0)
        self.assertTrue((loop / "state.yaml").is_file())

    # --- P3: convergence verifier soundness ---------------------------------
    def test_evidence_ledger_accepts_resolved_contradiction_without_rewarding_confirmation(self) -> None:
        for conclusion, relation in (("supported", "supports"), ("contradicted", "contradicts")):
            ledger = self.tmp / f"ledger-{conclusion}.yaml"
            ledger.write_text(
                yaml.safe_dump(
                    {
                        "schema_version": 2,
                        "claims": [
                            {
                                "id": "C-001",
                                "statement": "A falsifiable claim",
                                "conclusion": conclusion,
                                "evidence": [
                                    {
                                        "acquisition_status": "acquired",
                                        "source_status": "verified_identity",
                                        "claim_relation": relation,
                                        "evidence_basis": "full_text",
                                        "locator": "https://example.com/s#section-2",
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run("check_evidence_ledger.py", str(ledger))
            self.assertEqual(result.returncode, 0, f"{conclusion}: {result.stdout}")

    def test_evidence_ledger_rejects_unsupported_positive_and_unexplained_exclusion(self) -> None:
        ledger = self.tmp / "ledger-reward-hack.yaml"
        ledger.write_text(
            yaml.safe_dump(
                {
                    "schema_version": 2,
                    "claims": [
                        {
                            "id": "C-001",
                            "statement": "Unsupported positive claim",
                            "conclusion": "supported",
                            "retained": False,
                            "evidence": [],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result = run("check_evidence_ledger.py", str(ledger))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("supporting evidence", result.stdout)
        self.assertIn("exclusion_reason", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
