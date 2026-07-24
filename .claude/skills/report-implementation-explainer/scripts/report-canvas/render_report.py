#!/usr/bin/env python3
"""Render one self-contained Skill System Report Canvas HTML artifact.

The renderer is deliberately deterministic and dependency-free. It validates the
bundled JSON Schema plus rendering invariants, embeds only local vendored assets,
and inlines Three.js only for ``spatial`` reports.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import html
import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "template.html"
SCHEMA = ROOT / "report-model.schema.json"
STATIC = ROOT / "static"
VENDOR = ROOT / "vendor"

_SCHEMA_ANNOTATION_KEYS = {"$schema", "$id", "title", "description"}
_SCHEMA_VALIDATION_KEYS = {
    "$defs",
    "$ref",
    "additionalProperties",
    "const",
    "enum",
    "items",
    "maxItems",
    "maxLength",
    "minItems",
    "minimum",
    "minLength",
    "oneOf",
    "pattern",
    "properties",
    "required",
    "type",
    "uniqueItems",
}
_JSON_TYPE_NAMES = {
    "array",
    "boolean",
    "integer",
    "null",
    "number",
    "object",
    "string",
}


class ModelError(ValueError):
    """Raised when a report model violates a rendering invariant."""


def _json_path(parts: tuple[str | int, ...]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part):
            result += f".{part}"
        else:
            result += f"[{json.dumps(part, ensure_ascii=False)}]"
    return result


def _schema_path(parts: tuple[str, ...]) -> str:
    return "#" + "".join(
        f"/{part.replace('~', '~0').replace('/', '~1')}" for part in parts
    )


def _schema_error(parts: tuple[str, ...], message: str) -> ModelError:
    return ModelError(
        f"unsupported or invalid Report Canvas schema at "
        f"{_schema_path(parts)}: {message}"
    )


def _require_non_negative_integer(value: Any, path: tuple[str, ...]) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _schema_error(path, "must be a non-negative integer")


def _validate_schema_definition(schema: Any, path: tuple[str, ...] = ()) -> None:
    """Fail closed when the bundled schema uses a keyword this renderer cannot enforce."""
    if not isinstance(schema, dict):
        raise _schema_error(path, "schema node must be an object")
    unknown = sorted(
        set(schema) - _SCHEMA_ANNOTATION_KEYS - _SCHEMA_VALIDATION_KEYS
    )
    if unknown:
        raise _schema_error(path, f"unsupported keyword(s): {', '.join(unknown)}")

    schema_type = schema.get("type")
    if schema_type is not None:
        type_names = schema_type if isinstance(schema_type, list) else [schema_type]
        if (
            not type_names
            or any(
                not isinstance(name, str) or name not in _JSON_TYPE_NAMES
                for name in type_names
            )
            or len(set(type_names)) != len(type_names)
        ):
            raise _schema_error(path + ("type",), "contains an invalid JSON type declaration")

    reference = schema.get("$ref")
    if reference is not None and (
        not isinstance(reference, str) or not reference.startswith("#/")
    ):
        raise _schema_error(path + ("$ref",), "only local JSON Pointer references are supported")

    for keyword in ("minLength", "maxLength", "minItems", "maxItems"):
        if keyword in schema:
            _require_non_negative_integer(schema[keyword], path + (keyword,))
    if "minimum" in schema and (
        isinstance(schema["minimum"], bool)
        or not isinstance(schema["minimum"], (int, float))
        or not math.isfinite(schema["minimum"])
    ):
        raise _schema_error(path + ("minimum",), "must be a finite number")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise _schema_error(path + ("pattern",), "must be a string")
        try:
            re.compile(schema["pattern"])
        except re.error as exc:
            raise _schema_error(
                path + ("pattern",), f"invalid regular expression: {exc}"
            ) from exc
    if "uniqueItems" in schema and not isinstance(schema["uniqueItems"], bool):
        raise _schema_error(path + ("uniqueItems",), "must be a boolean")
    if "enum" in schema and (
        not isinstance(schema["enum"], list) or not schema["enum"]
    ):
        raise _schema_error(path + ("enum",), "must be a non-empty array")
    if "required" in schema and (
        not isinstance(schema["required"], list)
        or any(not isinstance(name, str) for name in schema["required"])
        or len(set(schema["required"])) != len(schema["required"])
    ):
        raise _schema_error(path + ("required",), "must contain unique string names")

    for keyword in ("properties", "$defs"):
        if keyword not in schema:
            continue
        children = schema[keyword]
        if not isinstance(children, dict):
            raise _schema_error(path + (keyword,), "must be an object")
        for name, child in children.items():
            _validate_schema_definition(child, path + (keyword, name))

    if "items" in schema:
        _validate_schema_definition(schema["items"], path + ("items",))
    if "additionalProperties" in schema:
        additional = schema["additionalProperties"]
        if not isinstance(additional, bool):
            _validate_schema_definition(additional, path + ("additionalProperties",))
    if "oneOf" in schema:
        branches = schema["oneOf"]
        if not isinstance(branches, list) or not branches:
            raise _schema_error(path + ("oneOf",), "must be a non-empty array")
        for index, branch in enumerate(branches):
            _validate_schema_definition(branch, path + ("oneOf", str(index)))


def _load_schema() -> dict[str, Any]:
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ModelError(f"cannot read Report Canvas schema: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ModelError(f"Report Canvas schema is not valid JSON: {exc}") from exc
    _validate_schema_definition(schema)
    return schema


def _resolve_reference(reference: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    current: Any = root_schema
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            raise ModelError(f"Report Canvas schema reference does not resolve: {reference}")
        current = current[part]
    if not isinstance(current, dict):
        raise ModelError(f"Report Canvas schema reference is not an object: {reference}")
    return current


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _matches_type(value: Any, type_name: str) -> bool:
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "integer":
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, float) and math.isfinite(value) and value.is_integer()
    if type_name == "null":
        return value is None
    if type_name == "number":
        return _is_number(value)
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "string":
        return isinstance(value, str)
    return False


def _json_equal(left: Any, right: Any) -> bool:
    if _is_number(left) and _is_number(right):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key]) for key in left
        )
    return left == right


def _validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: tuple[str | int, ...] = (),
) -> None:
    reference = schema.get("$ref")
    if reference is not None:
        _validate_schema_value(
            value,
            _resolve_reference(reference, root_schema),
            root_schema,
            path,
        )

    if "oneOf" in schema:
        matches = 0
        branch_errors: list[str] = []
        for branch in schema["oneOf"]:
            try:
                _validate_schema_value(value, branch, root_schema, path)
            except ModelError as exc:
                branch_errors.append(str(exc))
            else:
                matches += 1
        if matches != 1:
            detail = f"; first mismatch: {branch_errors[0]}" if branch_errors else ""
            raise ModelError(
                f"{_json_path(path)} must match exactly one allowed schema "
                f"(matched {matches}){detail}"
            )

    if "const" in schema and not _json_equal(value, schema["const"]):
        raise ModelError(f"{_json_path(path)} must equal {schema['const']!r}")
    if "enum" in schema and not any(
        _json_equal(value, item) for item in schema["enum"]
    ):
        raise ModelError(f"{_json_path(path)} is not one of the allowed values")

    schema_type = schema.get("type")
    if schema_type is not None:
        type_names = schema_type if isinstance(schema_type, list) else [schema_type]
        if not any(_matches_type(value, name) for name in type_names):
            raise ModelError(
                f"{_json_path(path)} must have type {' or '.join(type_names)}"
            )

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ModelError(
                f"{_json_path(path)} must contain at least {schema['minLength']} characters"
            )
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ModelError(
                f"{_json_path(path)} exceeds {schema['maxLength']} characters"
            )
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise ModelError(f"{_json_path(path)} does not match the required pattern")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise ModelError(
                f"{_json_path(path)} must contain at least {schema['minItems']} items"
            )
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ModelError(
                f"{_json_path(path)} must contain at most {schema['maxItems']} items"
            )
        if schema.get("uniqueItems") and any(
            _json_equal(value[left], value[right])
            for left in range(len(value))
            for right in range(left + 1, len(value))
        ):
            raise ModelError(f"{_json_path(path)} must contain unique items")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema_value(
                    item, schema["items"], root_schema, path + (index,)
                )

    if isinstance(value, dict):
        required = schema.get("required", [])
        missing = [name for name in required if name not in value]
        if missing:
            raise ModelError(
                f"{_json_path(path)} is missing required field(s): {', '.join(missing)}"
            )
        properties = schema.get("properties", {})
        for name, child_schema in properties.items():
            if name in value:
                _validate_schema_value(
                    value[name], child_schema, root_schema, path + (name,)
                )
        extras = [name for name in value if name not in properties]
        additional = schema.get("additionalProperties", True)
        if additional is False and extras:
            raise ModelError(
                f"{_json_path(path)} contains unsupported field(s): {', '.join(sorted(extras))}"
            )
        if isinstance(additional, dict):
            for name in extras:
                _validate_schema_value(
                    value[name], additional, root_schema, path + (name,)
                )

    if "minimum" in schema:
        if not _is_number(value) or value < schema["minimum"]:
            raise ModelError(
                f"{_json_path(path)} must be at least {schema['minimum']}"
            )


def _validate_unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
    identifiers: set[str] = set()
    for item in items:
        identifier = item["id"]
        if identifier in identifiers:
            raise ModelError(f"duplicate {label} id: {identifier}")
        identifiers.add(identifier)
    return identifiers


def _validate_evidence_refs(
    refs: list[str] | None,
    evidence_ids: set[str],
    label: str,
) -> None:
    missing = sorted(set(refs or []) - evidence_ids)
    if missing:
        raise ModelError(
            f"{label} references missing evidence id(s): {', '.join(missing)}"
        )


def _validate_gltf_resources(
    document: dict[str, Any],
    label: str,
    *,
    has_binary_chunk: bool,
) -> None:
    asset = document.get("asset")
    if not isinstance(asset, dict) or asset.get("version") != "2.0":
        raise ModelError(f"{label} must declare glTF asset.version 2.0")

    for collection in ("buffers", "images"):
        items = document.get(collection, [])
        if not isinstance(items, list):
            raise ModelError(f"{label} {collection} must be an array")
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ModelError(f"{label} {collection}[{index}] must be an object")
            uri = item.get("uri")
            if uri is not None:
                if (
                    not isinstance(uri, str)
                    or not uri.startswith("data:")
                    or "," not in uri
                ):
                    raise ModelError(
                        f"{label} {collection}[{index}] uses an external or invalid URI; "
                        "use embedded data or GLB for an offline report"
                    )
                continue
            if collection == "buffers":
                if not has_binary_chunk or index != 0:
                    raise ModelError(
                        f"{label} buffers[{index}] has no embedded data URI or GLB BIN chunk"
                    )
            elif not isinstance(item.get("bufferView"), int):
                raise ModelError(
                    f"{label} images[{index}] has no embedded data URI or bufferView"
                )


def _decode_glb_document(data_base64: str, label: str) -> dict[str, Any]:
    try:
        payload = base64.b64decode(data_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ModelError(f"{label} data_base64 must be valid base64") from exc

    if len(payload) < 20 or payload[:4] != b"glTF":
        raise ModelError(f"{label} must contain a valid GLB header")
    version = int.from_bytes(payload[4:8], "little")
    declared_length = int.from_bytes(payload[8:12], "little")
    if version != 2:
        raise ModelError(f"{label} must use GLB version 2")
    if declared_length != len(payload):
        raise ModelError(
            f"{label} GLB length header does not match the decoded payload"
        )

    chunks: list[tuple[int, bytes]] = []
    offset = 12
    while offset < len(payload):
        if offset + 8 > len(payload):
            raise ModelError(f"{label} contains a truncated GLB chunk header")
        chunk_length = int.from_bytes(payload[offset : offset + 4], "little")
        chunk_type = int.from_bytes(payload[offset + 4 : offset + 8], "little")
        chunk_end = offset + 8 + chunk_length
        if chunk_length % 4 or chunk_end > len(payload):
            raise ModelError(f"{label} contains an invalid GLB chunk length")
        chunks.append((chunk_type, payload[offset + 8 : chunk_end]))
        offset = chunk_end

    json_chunk_type = 0x4E4F534A
    bin_chunk_type = 0x004E4942
    if not chunks or chunks[0][0] != json_chunk_type:
        raise ModelError(f"{label} GLB first chunk must be JSON")
    if len(chunks) > 2 or (
        len(chunks) == 2 and chunks[1][0] != bin_chunk_type
    ):
        raise ModelError(f"{label} GLB may contain only JSON and one optional BIN chunk")

    try:
        document = json.loads(chunks[0][1].rstrip(b" \t\r\n").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModelError(f"{label} GLB JSON chunk must be valid UTF-8 JSON") from exc
    if not isinstance(document, dict):
        raise ModelError(f"{label} GLB JSON root must be an object")
    _validate_gltf_resources(
        document,
        label,
        has_binary_chunk=len(chunks) == 2,
    )
    return document


def _parse_embedded_gltf(
    asset: dict[str, Any],
    label: str,
) -> dict[str, Any] | None:
    if "path" in asset:
        return None
    if asset["format"] == "glb":
        return _decode_glb_document(asset["data_base64"], label)
    if asset["format"] != "gltf":
        return None
    try:
        document = json.loads(asset["data_text"])
    except json.JSONDecodeError as exc:
        raise ModelError(f"{label} data_text must be valid JSON") from exc
    if not isinstance(document, dict):
        raise ModelError(f"{label} data_text root must be an object")
    _validate_gltf_resources(document, label, has_binary_chunk=False)
    return document


def _collection_item(
    collection: Any,
    index: Any,
    label: str,
) -> dict[str, Any]:
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not isinstance(collection, list)
        or index < 0
        or index >= len(collection)
        or not isinstance(collection[index], dict)
    ):
        raise ModelError(f"{label} contains an invalid glTF index")
    return collection[index]


def _gltf_geometry_bounds(
    document: dict[str, Any],
    label: str,
) -> tuple[int, int]:
    scenes = document.get("scenes")
    scene_index = document.get("scene", 0)
    scene = _collection_item(scenes, scene_index, f"{label} scene")
    root_nodes = scene.get("nodes", [])
    if not isinstance(root_nodes, list):
        raise ModelError(f"{label} scene.nodes must be an array")

    nodes = document.get("nodes", [])
    meshes = document.get("meshes", [])
    accessors = document.get("accessors", [])
    pending = list(reversed(root_nodes))
    visited: set[int] = set()
    mesh_index: int | None = None
    while pending:
        node_index = pending.pop()
        node = _collection_item(nodes, node_index, f"{label} node")
        if node_index in visited:
            continue
        visited.add(node_index)
        if "mesh" in node:
            mesh_index = node["mesh"]
            break
        children = node.get("children", [])
        if not isinstance(children, list):
            raise ModelError(f"{label} node.children must be an array")
        pending.extend(reversed(children))

    if mesh_index is None:
        raise ModelError(f"{label} default scene must contain at least one mesh")
    mesh = _collection_item(meshes, mesh_index, f"{label} mesh")
    primitives = mesh.get("primitives")
    if not isinstance(primitives, list) or not primitives:
        raise ModelError(f"{label} first mesh must contain a primitive")
    primitive = primitives[0]
    if not isinstance(primitive, dict):
        raise ModelError(f"{label} first mesh primitive must be an object")
    attributes = primitive.get("attributes")
    if not isinstance(attributes, dict) or "POSITION" not in attributes:
        raise ModelError(f"{label} first mesh primitive requires POSITION")
    position_accessor = _collection_item(
        accessors,
        attributes["POSITION"],
        f"{label} POSITION accessor",
    )
    vertex_count = position_accessor.get("count")
    if (
        isinstance(vertex_count, bool)
        or not isinstance(vertex_count, int)
        or vertex_count <= 0
    ):
        raise ModelError(f"{label} POSITION accessor requires a positive count")

    primitive_mode = primitive.get("mode", 4)
    face_count = 0
    if primitive_mode == 4:
        if "indices" in primitive:
            index_accessor = _collection_item(
                accessors,
                primitive["indices"],
                f"{label} index accessor",
            )
            index_count = index_accessor.get("count")
            if (
                isinstance(index_count, bool)
                or not isinstance(index_count, int)
                or index_count <= 0
                or index_count % 3
            ):
                raise ModelError(
                    f"{label} triangle index accessor requires a positive multiple-of-three count"
                )
            face_count = index_count // 3
        else:
            if vertex_count % 3:
                raise ModelError(
                    f"{label} non-indexed triangle POSITION count must be a multiple of three"
                )
            face_count = vertex_count // 3
    return vertex_count, face_count


def _validate_buffer_geometry(
    geometry: dict[str, Any],
    label: str,
) -> tuple[int, int]:
    positions = geometry["positions"]
    if len(positions) < 9 or len(positions) % 3:
        raise ModelError(f"{label} positions must contain complete xyz triples")
    vertex_count = len(positions) // 3
    normals = geometry.get("normals")
    if normals is not None and len(normals) != len(positions):
        raise ModelError(f"{label} normals must match positions")

    indices = geometry.get("indices")
    if indices is not None:
        if not indices or len(indices) % 3 or any(
            value >= vertex_count for value in indices
        ):
            raise ModelError(f"{label} indices must be non-empty in-range triangles")
        face_count = len(indices) // 3
    else:
        if vertex_count % 3:
            raise ModelError(
                f"{label} non-indexed positions must describe complete triangles"
            )
        face_count = vertex_count // 3

    identity_contracts = (
        ("vertex_ids", vertex_count),
        ("face_ids", face_count),
    )
    for field, expected_count in identity_contracts:
        identifiers = geometry.get(field)
        if identifiers is None:
            continue
        if len(identifiers) != expected_count:
            raise ModelError(
                f"{label} {field} must contain exactly {expected_count} entries"
            )
        if any(
            _json_equal(identifiers[left], identifiers[right])
            for left in range(len(identifiers))
            for right in range(left + 1, len(identifiers))
        ):
            raise ModelError(f"{label} {field} must contain unique identities")
    return vertex_count, face_count


def _validate_spatial_asset(
    asset: dict[str, Any],
    label: str,
) -> tuple[int, int] | None:
    if asset["format"] == "buffer_geometry":
        return _validate_buffer_geometry(asset["geometry"], label)
    document = _parse_embedded_gltf(asset, label)
    if document is None:
        return None
    return _gltf_geometry_bounds(document, label)


def _validate_trace_visual(
    visual: dict[str, Any],
    evidence_ids: set[str],
) -> None:
    nodes = visual["nodes"]
    node_ids = _validate_unique_ids(nodes, "trace node")
    lifecycle_nodes = [
        index for index, node in enumerate(nodes) if "lifecycle_status" in node
    ]
    if visual["trace_kind"] == "lifecycle":
        missing_lifecycle_status = sorted(set(range(len(nodes))) - set(lifecycle_nodes))
        if missing_lifecycle_status:
            raise ModelError(
                "lifecycle trace requires lifecycle_status on every node; "
                f"missing node index(es): {', '.join(map(str, missing_lifecycle_status))}"
            )
    elif lifecycle_nodes:
        raise ModelError(
            "causal trace nodes cannot declare lifecycle_status; "
            "use trace_kind 'lifecycle'"
        )
    for index, node in enumerate(nodes):
        _validate_evidence_refs(
            node.get("evidence_refs"),
            evidence_ids,
            f"trace node[{index}]",
        )
    for index, edge in enumerate(visual["edges"]):
        missing = sorted({edge["from"], edge["to"]} - node_ids)
        if missing:
            raise ModelError(
                f"trace edge[{index}] references missing node id(s): {', '.join(missing)}"
            )


def _validate_overlay_bounds(
    overlay: dict[str, Any],
    bounds: tuple[int, int],
    label: str,
) -> None:
    vertex_count, face_count = bounds
    edges = overlay.get("edges")
    if edges is not None:
        if not edges or len(edges) % 2:
            raise ModelError(f"{label} edges must contain complete vertex-index pairs")
        if any(index >= vertex_count for index in edges):
            raise ModelError(f"{label} edge index exceeds the target vertex range")
    vertices = overlay.get("vertices")
    if vertices is not None and any(index >= vertex_count for index in vertices):
        raise ModelError(f"{label} vertex index exceeds the target vertex range")
    faces = overlay.get("faces")
    if faces is not None and any(index >= face_count for index in faces):
        raise ModelError(f"{label} face index exceeds the target face range")


def _validate_spatial_visual(
    visual: dict[str, Any],
    evidence_ids: set[str],
) -> None:
    main_bounds = _validate_spatial_asset(visual["asset"], "spatial asset")
    states = visual.get("states", [])
    state_ids = _validate_unique_ids(states, "spatial state")
    state_bounds: dict[str, tuple[int, int] | None] = {
        state["id"]: _validate_spatial_asset(
            state["asset"],
            f"spatial state {state['id']!r} asset",
        )
        for state in states
    }

    initial_state = visual.get("initial_state")
    if initial_state is not None:
        if not states:
            raise ModelError("spatial initial_state requires declared states")
        if initial_state not in state_ids:
            raise ModelError(
                f"spatial initial_state references missing state id: {initial_state}"
            )

    for index, overlay in enumerate(visual.get("overlays", [])):
        label = f"spatial overlay[{index}]"
        _validate_evidence_refs(
            overlay.get("evidence_refs"),
            evidence_ids,
            label,
        )
        if not any(overlay.get(field) for field in ("edges", "vertices", "faces")):
            raise ModelError(f"{label} must identify at least one edge, vertex, or face")

        state_refs = overlay.get("state_refs")
        if state_refs is not None:
            if not states:
                raise ModelError(f"{label} state_refs require declared states")
            missing = sorted(set(state_refs) - state_ids)
            if missing:
                raise ModelError(
                    f"{label} references missing state id(s): {', '.join(missing)}"
                )
            target_bounds = [state_bounds[state_id] for state_id in state_refs]
        elif states:
            target_bounds = list(state_bounds.values())
        else:
            target_bounds = [main_bounds]

        edges = overlay.get("edges")
        if edges is not None and (not edges or len(edges) % 2):
            raise ModelError(f"{label} edges must contain complete vertex-index pairs")
        for bounds in target_bounds:
            if bounds is not None:
                _validate_overlay_bounds(overlay, bounds, label)


def _validate_model(model: dict[str, Any]) -> None:
    schema = _load_schema()
    _validate_schema_value(model, schema, schema)

    mode = model["mode"]
    evidence_ids = _validate_unique_ids(model.get("evidence", []), "evidence")
    for index, finding in enumerate(model.get("findings", [])):
        _validate_evidence_refs(
            finding.get("evidence_refs"),
            evidence_ids,
            f"finding[{index}]",
        )

    visual = model.get("visual")
    if visual is not None and visual.get("type") != mode:
        raise ModelError("visual.type must match mode")
    if mode == "decision" and isinstance(visual, dict):
        _validate_unique_ids(visual["choices"], "decision choice")
    elif mode == "trace" and isinstance(visual, dict):
        _validate_trace_visual(visual, evidence_ids)
    elif mode == "spatial":
        if not isinstance(visual, dict):
            raise ModelError("spatial mode requires visual")
        _validate_spatial_visual(visual, evidence_ids)


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ModelError(f"missing Report Canvas asset: {path}")
    return path.read_text(encoding="utf-8")


def _embed_asset(asset: dict[str, Any], model_dir: Path) -> None:
    path_value = asset.pop("path", None)
    if path_value is None:
        return
    if asset.get("data_base64") is not None or asset.get("data_text") is not None:
        raise ModelError("spatial asset cannot combine path with embedded data")
    source = (model_dir / str(path_value)).resolve()
    try:
        source.relative_to(model_dir.resolve())
    except ValueError as exc:
        raise ModelError(f"spatial asset escapes the model directory: {path_value}") from exc
    if not source.is_file():
        raise ModelError(f"missing spatial asset: {source}")
    asset_format = asset.get("format")
    if asset_format == "gltf":
        asset["data_text"] = source.read_text(encoding="utf-8")
        asset.setdefault("mime_type", "model/gltf+json")
    elif asset_format == "glb":
        asset["data_base64"] = base64.b64encode(source.read_bytes()).decode("ascii")
        asset.setdefault("mime_type", "model/gltf-binary")
    else:
        raise ModelError("path embedding is supported only for glb or gltf assets")


def _prepare_model(model: dict[str, Any], model_dir: Path) -> dict[str, Any]:
    # JSON round-trip gives the renderer an isolated, JSON-compatible copy.
    prepared = json.loads(json.dumps(model, ensure_ascii=False))
    visual = prepared.get("visual")
    if prepared.get("mode") == "spatial" and isinstance(visual, dict):
        _embed_asset(visual["asset"], model_dir)
        for state in visual.get("states", []):
            if isinstance(state, dict) and isinstance(state.get("asset"), dict):
                _embed_asset(state["asset"], model_dir)
    return prepared


def _json_for_script(model: dict[str, Any]) -> str:
    payload = json.dumps(
        model,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        payload.replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(model_path: Path, output_path: Path, *, force: bool = False) -> None:
    model_path = model_path.resolve()
    output_path = output_path.resolve()
    if model_path == output_path:
        raise ModelError("report input and output paths must be different")
    if output_path.exists() and not force:
        raise ModelError(
            f"report output already exists: {output_path}; pass --force to replace it"
        )

    model = json.loads(model_path.read_text(encoding="utf-8"))
    if not isinstance(model, dict):
        raise ModelError("report model root must be an object")
    _validate_model(model)
    prepared = _prepare_model(model, model_path.parent)
    _validate_model(prepared)

    template = _read_text(TEMPLATE)
    replacements = {
        "__REPORT_LANGUAGE__": html.escape(str(prepared["language"]), quote=True),
        "__REPORT_TITLE__": html.escape(str(prepared["title"]), quote=False),
        "__PICO_CSS__": _read_text(VENDOR / "pico.min.css"),
        "__CANVAS_CSS__": _read_text(STATIC / "report-canvas.css"),
        "__REPORT_DATA__": _json_for_script(prepared),
        "__CANVAS_JS__": _read_text(STATIC / "report-canvas.js"),
        "__SPATIAL_DEPENDENCIES__": "",
    }
    if prepared["mode"] == "spatial":
        spatial_scripts = "\n".join(
            [
                "<script>" + _read_text(VENDOR / "three-spatial.min.js") + "</script>",
                "<script>" + _read_text(STATIC / "report-spatial.js") + "</script>",
            ]
        )
        replacements["__SPATIAL_DEPENDENCIES__"] = spatial_scripts

    rendered = template
    for marker, value in replacements.items():
        rendered = rendered.replace(marker, value)
    unresolved = [marker for marker in replacements if marker in rendered]
    if unresolved:
        raise ModelError(f"unresolved template markers: {unresolved}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if force:
        output_path.write_text(rendered, encoding="utf-8")
        return
    try:
        with output_path.open("x", encoding="utf-8") as output_file:
            output_file.write(rendered)
    except FileExistsError as exc:
        raise ModelError(
            f"report output already exists: {output_path}; pass --force to replace it"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Report model JSON")
    parser.add_argument("--output", required=True, type=Path, help="Self-contained HTML output")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing output file intentionally",
    )
    args = parser.parse_args()
    try:
        render(args.input, args.output, force=args.force)
    except (OSError, json.JSONDecodeError, ModelError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
