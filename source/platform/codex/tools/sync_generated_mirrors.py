#!/usr/bin/env python3
"""Generate and verify Claude-side mirrors from Codex canonical files."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


MAPPINGS = [
    (Path(".codex/docs/source_registry.yaml"), Path(".claude/docs/source_registry.yaml"), "yaml"),
    (Path(".codex/eval/eval-case.schema.json"), Path(".claude/eval/eval-case.schema.json"), "json"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generated_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def yaml_mirror(canonical: Path, generated_from: str) -> str:
    body = canonical.read_text(encoding="utf-8")
    checksum = sha256_bytes(canonical.read_bytes())
    return "\n".join(
        [
            f"generated_from: {generated_from}",
            f"generated_at: {generated_at()}",
            f"source_checksum: {checksum}",
            "do_not_edit: true",
            "",
            body.rstrip(),
            "",
        ]
    )


def json_mirror(canonical: Path, generated_from: str) -> str:
    data = json.loads(canonical.read_text(encoding="utf-8"))
    mirrored = {
        "x_generated_from": generated_from,
        "x_generated_at": generated_at(),
        "x_source_checksum": sha256_bytes(canonical.read_bytes()),
        "x_do_not_edit": True,
    }
    mirrored.update(data)
    return json.dumps(mirrored, indent=2, ensure_ascii=True) + "\n"


def write_mirror(canonical: Path, mirror: Path, kind: str) -> None:
    mirror.parent.mkdir(parents=True, exist_ok=True)
    generated_from = canonical.as_posix()
    if kind == "yaml":
        content = yaml_mirror(canonical, generated_from)
    elif kind == "json":
        content = json_mirror(canonical, generated_from)
    else:
        raise ValueError(f"unknown mirror kind: {kind}")
    mirror.write_text(content, encoding="utf-8")


def check_yaml_mirror(canonical: Path, mirror: Path) -> list[str]:
    errors: list[str] = []
    text = mirror.read_text(encoding="utf-8", errors="replace")
    canonical_text = canonical.read_text(encoding="utf-8")
    expected_checksum = sha256_bytes(canonical.read_bytes())
    required = {
        "generated_from": canonical.as_posix(),
        "source_checksum": expected_checksum,
        "do_not_edit": "true",
    }
    for key, expected in required.items():
        marker = f"{key}: {expected}"
        if marker not in text:
            errors.append(f"{mirror}: missing or stale marker {marker!r}")
    parts = text.split("\n\n", 1)
    if len(parts) != 2:
        errors.append(f"{mirror}: missing generated header/body separator")
    elif parts[1].rstrip() != canonical_text.rstrip():
        errors.append(f"{mirror}: mirror body differs from canonical")
    return errors


def check_json_mirror(canonical: Path, mirror: Path) -> list[str]:
    errors: list[str] = []
    canonical_data = json.loads(canonical.read_text(encoding="utf-8"))
    data = json.loads(mirror.read_text(encoding="utf-8"))
    expected_checksum = sha256_bytes(canonical.read_bytes())
    if data.get("x_generated_from") != canonical.as_posix():
        errors.append(f"{mirror}: x_generated_from mismatch")
    if data.get("x_source_checksum") != expected_checksum:
        errors.append(f"{mirror}: x_source_checksum mismatch")
    if data.get("x_do_not_edit") is not True:
        errors.append(f"{mirror}: x_do_not_edit missing")
    body = {key: value for key, value in data.items() if not key.startswith("x_")}
    if body != canonical_data:
        errors.append(f"{mirror}: mirror body differs from canonical")
    return errors


def check_mirrors() -> list[str]:
    errors: list[str] = []
    for canonical, mirror, kind in MAPPINGS:
        if not canonical.exists():
            errors.append(f"missing canonical: {canonical}")
            continue
        if not mirror.exists():
            errors.append(f"missing generated mirror: {mirror}")
            continue
        if kind == "yaml":
            errors.extend(check_yaml_mirror(canonical, mirror))
        elif kind == "json":
            errors.extend(check_json_mirror(canonical, mirror))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        errors = check_mirrors()
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
            return 1
        print("PASS")
        return 0
    for canonical, mirror, kind in MAPPINGS:
        write_mirror(canonical, mirror, kind)
        print(f"wrote {mirror}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
