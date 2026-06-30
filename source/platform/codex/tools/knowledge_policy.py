#!/usr/bin/env python3
"""Shared Knowledge Store admission policy."""

from __future__ import annotations

from typing import Any


def is_admissible_claim(claim: dict[str, Any]) -> bool:
    return claim.get("freshness") == "current" and claim.get("verification_state") != "unverified"


def admissible_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [claim for claim in claims if is_admissible_claim(claim)]


def is_admissible_edge(edge: dict[str, Any]) -> bool:
    return edge.get("verification_state") != "unverified"
