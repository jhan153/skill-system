#!/usr/bin/env python3
"""Deterministic verifier for a search-deep-evidence evidence ledger.

Turns "evidence quality" into a command_exit signal a loop can converge toward.
A ledger PASSES only when every RETAINED claim is fully resolved:
verified + confirmed + at least one source. Refuted/dropped claims (retained:
false) are excluded. This is the verifier a search-deep-evidence loop contract
points its success condition at.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.dont_write_bytecode = True

CITATION_STATUSES = {"verified", "unverified", "fabricated-risk"}
VERDICTS = {"confirmed", "refuted", "partial"}


def load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(ledger: dict[str, Any], min_claims: int) -> list[str]:
    errors: list[str] = []
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["ledger has no claims"]
    retained = [c for c in claims if isinstance(c, dict) and c.get("retained", True)]
    if len(retained) < min_claims:
        errors.append(f"only {len(retained)} retained claims; need >= {min_claims}")
    for claim in retained:
        cid = claim.get("id", "<no-id>")
        status = claim.get("citation_status")
        verdict = claim.get("verdict")
        sources = claim.get("sources") or []
        if status not in CITATION_STATUSES:
            errors.append(f"{cid}: citation_status must be one of {sorted(CITATION_STATUSES)} (got {status!r})")
        if verdict not in VERDICTS:
            errors.append(f"{cid}: verdict must be one of {sorted(VERDICTS)} (got {verdict!r})")
        if status == "fabricated-risk":
            errors.append(f"{cid}: retained claim still flagged fabricated-risk")
        if status == "unverified":
            errors.append(f"{cid}: retained claim still unverified")
        if verdict in VERDICTS and verdict != "confirmed":
            # A retained claim is only resolved when confirmed. refuted/partial must
            # not count as a PASS, or the loop converges on unresolved evidence.
            if verdict == "refuted":
                errors.append(f"{cid}: refuted claim must not be retained (set retained: false)")
            else:
                errors.append(f"{cid}: retained claim must be confirmed, not {verdict} (unresolved claims keep the loop running)")
        if status == "verified" and not (isinstance(sources, list) and sources):
            errors.append(f"{cid}: verified claim needs at least one source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--min-claims", type=int, default=1)
    args = parser.parse_args()
    if not args.ledger.exists():
        print(f"FAIL: ledger not found: {args.ledger}")
        return 2
    ledger = load(args.ledger)
    if not isinstance(ledger, dict):
        print("FAIL: ledger must be a mapping")
        return 2
    errors = check(ledger, args.min_claims)
    print("FAIL" if errors else "PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
