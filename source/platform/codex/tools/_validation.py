#!/usr/bin/env python3
"""Shared lightweight validation helpers for bundle verifier tools."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by host environment.
    raise SystemExit("FAIL: PyYAML is required for bundle validation") from exc

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ModuleNotFoundError:  # pragma: no cover - local fallback path.
    Draft202012Validator = None
    FormatChecker = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_json_file(path: Path) -> dict[str, Any]:
    data = json.loads(read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected top-level JSON object")
    return data


def load_yaml_file(path: Path) -> Any:
    data = yaml.safe_load(read_text(path))
    return data


def is_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_iso_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate JSON Schema with jsonschema when available, otherwise use the local subset."""

    if Draft202012Validator is not None and FormatChecker is not None:
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        return sorted(format_jsonschema_error(error) for error in validator.iter_errors(instance))
    return validate_schema_subset(instance, schema, path)


def format_jsonschema_error(error: Any) -> str:
    parts = ["$"]
    for item in error.absolute_path:
        if isinstance(item, int):
            parts[-1] = f"{parts[-1]}[{item}]"
        else:
            parts.append(str(item))
    return f"{'.'.join(parts)}: {error.message}"


def jsonschema_available() -> bool:
    return Draft202012Validator is not None


def validate_schema_subset(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the small JSON Schema subset used by this repository."""

    errors: list[str] = []

    if "allOf" in schema:
        for idx, subschema in enumerate(schema["allOf"]):
            errors.extend(validate_schema_subset(instance, subschema, f"{path}.allOf[{idx}]"))

    if "if" in schema:
        if not validate_schema_subset(instance, schema["if"], path):
            if "then" in schema:
                errors.extend(validate_schema_subset(instance, schema["then"], path))
        return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    expected_type = schema.get("type")
    if expected_type is not None and not _type_matches(instance, expected_type):
        errors.append(f"{path}: expected type {_type_label(expected_type)}, got {_instance_type(instance)}")
        return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        if not isinstance(required, list):
            errors.append(f"{path}: schema required must be an array")
        else:
            for key in required:
                if key not in instance:
                    errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if properties and not isinstance(properties, dict):
            errors.append(f"{path}: schema properties must be an object")
        elif isinstance(properties, dict):
            for key, subschema in properties.items():
                if key in instance:
                    errors.extend(validate_schema_subset(instance[key], subschema, f"{path}.{key}"))
            if schema.get("additionalProperties") is False:
                allowed = set(properties)
                for key in sorted(set(instance) - allowed):
                    errors.append(f"{path}: unexpected property {key!r}")

    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(instance)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors.extend(validate_schema_subset(item, item_schema, f"{path}[{idx}]"))

    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: expected minLength {min_length}, got {len(instance)}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, instance) is None:
            errors.append(f"{path}: value {instance!r} does not match pattern {pattern!r}")
        if schema.get("format") == "date" and not is_iso_date(instance):
            errors.append(f"{path}: expected ISO date, got {instance!r}")
        if schema.get("format") == "date-time" and not is_iso_datetime(instance):
            errors.append(f"{path}: expected ISO datetime, got {instance!r}")

    if isinstance(instance, int) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: expected minimum {minimum}, got {instance}")

    return errors


def _type_matches(instance: Any, expected_type: object) -> bool:
    if isinstance(expected_type, list):
        return any(_type_matches(instance, item) for item in expected_type)
    if expected_type == "object":
        return isinstance(instance, dict)
    if expected_type == "array":
        return isinstance(instance, list)
    if expected_type == "string":
        return isinstance(instance, str)
    if expected_type == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected_type == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected_type == "boolean":
        return isinstance(instance, bool)
    if expected_type == "null":
        return instance is None
    return True


def _type_label(expected_type: object) -> str:
    if isinstance(expected_type, list):
        return "|".join(str(item) for item in expected_type)
    return str(expected_type)


def _instance_type(instance: Any) -> str:
    if instance is None:
        return "null"
    if isinstance(instance, bool):
        return "boolean"
    if isinstance(instance, dict):
        return "object"
    if isinstance(instance, list):
        return "array"
    if isinstance(instance, str):
        return "string"
    if isinstance(instance, int):
        return "integer"
    if isinstance(instance, float):
        return "number"
    return type(instance).__name__
