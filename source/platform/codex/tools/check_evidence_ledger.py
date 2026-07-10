#!/usr/bin/env python3
"""Validate a resolved claim–evidence ledger without rewarding confirmation bias.

The verifier checks traceability and resolution quality, not whether claims are
positive. Supported, contradicted, mixed, and explicitly insufficient outcomes
can all be valid. Excluding a claim never erases its evidence record.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.dont_write_bytecode = True

SCHEMA_VERSION = 2
LEGACY_SCHEMA_VERSION = 1
ACQUISITION_STATUSES = {"acquired", "partial", "inaccessible", "not_acquired"}
SOURCE_STATUSES = {
    "verified_identity",
    "metadata_partial",
    "duplicate_version",
    "corrected",
    "retracted",
    "unverified",
}
CLAIM_RELATIONS = {"supports", "contradicts", "mixed", "mentions", "not_assessed"}
CONCLUSIONS = {"supported", "contradicted", "mixed", "insufficient"}


def load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def migrate_v1_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    """Conservatively project a v1 ledger into the v2 shape.

    V1 stored claim-level citation status and verdicts, not source-level evidence
    basis or claim relations. Migration therefore preserves the legacy fields but
    leaves every conclusion insufficient until a reviewer supplies that evidence.
    """

    migrated: dict[str, Any] = {"schema_version": SCHEMA_VERSION}
    for key, value in ledger.items():
        if key not in {"schema_version", "claims", "migration"}:
            migrated[key] = copy.deepcopy(value)
    migrated["migration"] = {
        "from_schema_version": LEGACY_SCHEMA_VERSION,
        "review_required": True,
        "limitation": (
            "Schema v1 did not record source-level evidence_basis or claim_relation; "
            "legacy verdicts were not promoted to resolved v2 conclusions."
        ),
    }

    raw_claims = ledger.get("claims")
    if not isinstance(raw_claims, list):
        migrated["claims"] = copy.deepcopy(raw_claims)
        return migrated

    migrated_claims: list[Any] = []
    for raw_claim in raw_claims:
        if not isinstance(raw_claim, dict):
            migrated_claims.append(copy.deepcopy(raw_claim))
            continue

        legacy_status = raw_claim.get("citation_status")
        legacy_verdict = raw_claim.get("verdict")
        raw_sources = raw_claim.get("sources", [])
        source_values = raw_sources if isinstance(raw_sources, list) else []
        evidence: list[dict[str, Any]] = []
        unusable_source_count = 0
        for source in source_values:
            if not _nonempty(source):
                unusable_source_count += 1
                continue
            identity_was_claimed = legacy_status == "verified"
            evidence.append(
                {
                    "acquisition_status": "partial" if identity_was_claimed else "not_acquired",
                    "source_status": "metadata_partial" if identity_was_claimed else "unverified",
                    "claim_relation": "not_assessed",
                    "evidence_basis": "legacy_source_reference",
                    "locator": source,
                    "limitation": (
                        "Migrated from schema v1; this source had no source-level evidence basis "
                        "or claim relation and requires review."
                    ),
                }
            )

        missing_evidence = [
            "Review each legacy source and record its evidence_basis and claim_relation."
        ]
        if not evidence:
            missing_evidence.append("Acquire or identify a retrievable source for this claim.")
        if not isinstance(raw_sources, list) or unusable_source_count:
            missing_evidence.append("Resolve legacy source entries that were not usable locators.")
        if legacy_verdict is not None:
            missing_evidence.append(
                f"Reassess legacy verdict {legacy_verdict!r}; v1 did not retain its source-level rationale."
            )

        migrated_claim: dict[str, Any] = {
            "id": copy.deepcopy(raw_claim.get("id")),
            "statement": copy.deepcopy(raw_claim.get("statement")),
            "conclusion": "insufficient",
            "missing_evidence": missing_evidence,
            "evidence": evidence,
            "legacy_v1": {
                key: copy.deepcopy(value)
                for key, value in raw_claim.items()
                if key not in {"id", "statement", "retained", "exclusion_reason"}
            },
        }
        if "retained" in raw_claim:
            migrated_claim["retained"] = copy.deepcopy(raw_claim["retained"])
        if raw_claim.get("retained") is False:
            migrated_claim["exclusion_reason"] = copy.deepcopy(
                raw_claim.get("exclusion_reason")
                or "Schema v1 marked retained=false but did not record an exclusion reason."
            )
        elif _nonempty(raw_claim.get("exclusion_reason")):
            migrated_claim["exclusion_reason"] = copy.deepcopy(raw_claim["exclusion_reason"])
        migrated_claims.append(migrated_claim)

    migrated["claims"] = migrated_claims
    return migrated


def normalize_ledger(ledger: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    version = ledger.get("schema_version")
    if type(version) is int and version == LEGACY_SCHEMA_VERSION:
        return (
            migrate_v1_ledger(ledger),
            "schema v1 was conservatively migrated in memory; all legacy conclusions remain insufficient pending review",
        )
    return ledger, None


def _check_evidence(claim_id: str, records: object) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    usable_relations: set[str] = set()
    if not isinstance(records, list):
        return [f"{claim_id}: evidence must be a list"], usable_relations
    for index, record in enumerate(records):
        label = f"{claim_id}: evidence[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be a mapping")
            continue
        acquisition = record.get("acquisition_status")
        source_status = record.get("source_status")
        relation = record.get("claim_relation")
        if acquisition not in ACQUISITION_STATUSES:
            errors.append(f"{label} invalid acquisition_status {acquisition!r}")
        if source_status not in SOURCE_STATUSES:
            errors.append(f"{label} invalid source_status {source_status!r}")
        if relation not in CLAIM_RELATIONS:
            errors.append(f"{label} invalid claim_relation {relation!r}")
        if not _nonempty(record.get("evidence_basis")):
            errors.append(f"{label} missing evidence_basis")
        if acquisition in {"acquired", "partial"} and not _nonempty(record.get("locator")):
            errors.append(f"{label} acquired evidence needs locator")
        if (
            relation in CLAIM_RELATIONS
            and acquisition in {"acquired", "partial"}
            and source_status != "unverified"
        ):
            usable_relations.add(relation)
        if (acquisition == "partial" or source_status == "metadata_partial") and not _nonempty(
            record.get("limitation")
        ):
            errors.append(f"{label} partial evidence needs limitation")
    return errors, usable_relations


def check(ledger: dict[str, Any], min_claims: int) -> list[str]:
    errors: list[str] = []
    version = ledger.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        return errors + ["ledger has no claims"]
    if len(claims) < min_claims:
        errors.append(f"only {len(claims)} claims; need >= {min_claims}")

    seen_ids: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be a mapping")
            continue
        claim_id = claim.get("id")
        if not _nonempty(claim_id):
            claim_id = f"claims[{index}]"
            errors.append(f"{claim_id}: missing id")
        elif claim_id in seen_ids:
            errors.append(f"{claim_id}: duplicate id")
        else:
            seen_ids.add(claim_id)
        if not _nonempty(claim.get("statement")):
            errors.append(f"{claim_id}: missing statement")

        conclusion = claim.get("conclusion")
        if conclusion not in CONCLUSIONS:
            errors.append(f"{claim_id}: conclusion must be one of {sorted(CONCLUSIONS)}")
        evidence_errors, usable_relations = _check_evidence(
            str(claim_id), claim.get("evidence", [])
        )
        errors.extend(evidence_errors)

        if conclusion == "supported" and "supports" not in usable_relations:
            errors.append(
                f"{claim_id}: supported conclusion needs acquired, identified supporting evidence"
            )
        elif conclusion == "contradicted" and "contradicts" not in usable_relations:
            errors.append(
                f"{claim_id}: contradicted conclusion needs acquired, identified contradicting evidence"
            )
        elif conclusion == "mixed" and not {"supports", "contradicts"}.issubset(
            usable_relations
        ):
            errors.append(
                f"{claim_id}: mixed conclusion needs acquired, identified supporting and contradicting evidence"
            )
        if conclusion == "insufficient" and not (
            isinstance(claim.get("missing_evidence"), list) and claim.get("missing_evidence")
        ):
            errors.append(f"{claim_id}: insufficient conclusion needs missing_evidence")

        if claim.get("retained") is False and not _nonempty(claim.get("exclusion_reason")):
            errors.append(f"{claim_id}: excluded claim needs exclusion_reason; evidence is still validated")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--min-claims", type=int, default=1)
    parser.add_argument(
        "--print-migrated-v2",
        action="store_true",
        help="print the normalized v2 YAML without modifying the input ledger",
    )
    args = parser.parse_args()
    if not args.ledger.exists():
        print(f"FAIL: ledger not found: {args.ledger}")
        return 2
    ledger = load(args.ledger)
    if not isinstance(ledger, dict):
        print("FAIL: ledger must be a mapping")
        return 2
    normalized, compatibility_note = normalize_ledger(ledger)
    errors = check(normalized, args.min_claims)
    if args.print_migrated_v2:
        if errors:
            print("FAIL", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(yaml.safe_dump(normalized, sort_keys=False, allow_unicode=True), end="")
        return 0
    print("FAIL" if errors else "PASS")
    if compatibility_note:
        print(f"- compatibility: {compatibility_note}")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
