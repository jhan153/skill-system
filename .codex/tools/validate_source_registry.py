#!/usr/bin/env python3
"""Validate the canonical source registry used by the skill bundle."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.dont_write_bytecode = True

from _validation import is_iso_date, load_yaml_file, read_text


REQUIRED_FIELDS = {
    "source_id",
    "source_type",
    "stable_locator",
    "repository",
    "path",
    "revision",
    "retrieved_at",
    "license",
    "verification_status",
    "local_consumers",
    "local_modifications",
}
ALLOWED_SOURCE_TYPES = {"web_url", "github_raw", "arxiv", "repo_local_artifact", "transient_source"}
ALLOWED_STATUS = {"agent-verified", "user-verification-needed", "archived", "transient-excluded"}
LOCAL_PATH_RE = re.compile(r"(^|[\"'\s])/(Users|private|tmp|var)/")
# Consumers under these prefixes are local-only / source-project paths (see project AGENTS.md);
# they are intentionally excluded from the distributable bundle, so existence is not enforced here.
LOCAL_ONLY_CONSUMER_PREFIXES = ("docs/", ".github/", ".kanboard-plan")


def repo_root_for(registry: Path) -> Path:
    resolved = registry.resolve()
    if resolved.parent.name == "docs" and resolved.parent.parent.name == ".codex":
        return resolved.parent.parent.parent
    return Path(".").resolve()


def is_url(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_source(source: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    sid = source.get("source_id", "")
    label = sid if isinstance(sid, str) and sid else "<missing source_id>"
    for field in sorted(REQUIRED_FIELDS):
        if field not in source:
            errors.append(f"{label}: missing field {field}")
    if not isinstance(sid, str) or not sid:
        errors.append("source_id must be a non-empty string")
    source_type = source.get("source_type")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{label}: invalid source_type {source_type!r}")
    status = source.get("verification_status")
    if status not in ALLOWED_STATUS:
        errors.append(f"{label}: invalid verification_status {status!r}")
    retrieved_at = source.get("retrieved_at")
    if not is_iso_date(retrieved_at):
        errors.append(f"{label}: retrieved_at must be ISO date")
    stable = source.get("stable_locator")
    if source_type == "transient_source":
        if stable not in {None, ""}:
            errors.append(f"{label}: transient source must not use stable_locator")
        if not isinstance(source.get("transient_locator"), str) or not source.get("transient_locator"):
            errors.append(f"{label}: transient source requires transient_locator")
    elif source_type in {"web_url", "github_raw", "arxiv"}:
        if not is_url(stable):
            errors.append(f"{label}: stable_locator must be an http(s) URL")
        if source_type == "arxiv" and isinstance(stable, str) and not stable.startswith("https://arxiv.org/abs/"):
            errors.append(f"{label}: arxiv stable_locator must use https://arxiv.org/abs/")
    consumers = source.get("local_consumers")
    if not isinstance(consumers, list) or not consumers:
        errors.append(f"{label}: local_consumers must be a non-empty list")
    elif all(isinstance(item, str) for item in consumers):
        for consumer in consumers:
            if consumer.startswith("/"):
                errors.append(f"{label}: local consumer must be repo-relative: {consumer}")
                continue
            if consumer.startswith(LOCAL_ONLY_CONSUMER_PREFIXES):
                continue
            if not (root / consumer).exists():
                errors.append(f"{label}: local consumer not found: {consumer}")
    else:
        errors.append(f"{label}: local_consumers entries must be strings")
    return errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = read_text(path)
    if LOCAL_PATH_RE.search(text):
        errors.append("registry contains an absolute local filesystem path")
    try:
        data = load_yaml_file(path)
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return [f"{path}: expected top-level mapping"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        return errors
    seen: set[str] = set()
    root = repo_root_for(path)
    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{idx}] must be a mapping")
            continue
        sid = source.get("source_id")
        if isinstance(sid, str):
            if sid in seen:
                errors.append(f"duplicate source_id: {sid}")
            seen.add(sid)
        errors.extend(validate_source(source, root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    if not args.registry.exists():
        print(f"FAIL: missing registry: {args.registry}")
        return 2
    errors = validate(args.registry)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
