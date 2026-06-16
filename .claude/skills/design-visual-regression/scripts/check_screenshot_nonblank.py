#!/usr/bin/env python3
"""Read-only PNG screenshot nonblank sanity check."""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def parse_png(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        return {"path": str(path), "supported": False, "reason": "not a PNG file"}

    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = None
    idat = bytearray()
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or bit_depth != 8:
        return {"path": str(path), "supported": False, "reason": "unsupported PNG metadata"}

    channels_by_type = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    channels = channels_by_type.get(color_type)
    if channels is None:
        return {"path": str(path), "supported": False, "reason": f"unsupported color type {color_type}"}

    row_len = width * channels
    bpp = max(1, channels)
    try:
        raw = zlib.decompress(bytes(idat))
    except Exception as exc:  # noqa: BLE001 - report decompression failure
        return {"path": str(path), "supported": False, "reason": f"decompress failed: {exc}"}

    rows: list[bytes] = []
    pos = 0
    prev = bytearray(row_len)
    sample_values: set[bytes] = set()
    for _ in range(height):
        if pos >= len(raw):
            break
        filter_type = raw[pos]
        pos += 1
        row = bytearray(raw[pos : pos + row_len])
        pos += row_len
        for i, value in enumerate(row):
            left = row[i - bpp] if i >= bpp else 0
            up = prev[i]
            up_left = prev[i - bpp] if i >= bpp else 0
            if filter_type == 1:
                row[i] = (value + left) & 0xFF
            elif filter_type == 2:
                row[i] = (value + up) & 0xFF
            elif filter_type == 3:
                row[i] = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                row[i] = (value + paeth(left, up, up_left)) & 0xFF
        rows.append(bytes(row))
        prev = row

    if not rows:
        return {"path": str(path), "supported": False, "reason": "no decoded rows"}

    for row in rows[:: max(1, len(rows) // 40)]:
        for i in range(0, len(row), max(1, bpp * max(1, width // 40))):
            sample_values.add(bytes(row[i : i + bpp]))

    unique_samples = len(sample_values)
    return {
        "path": str(path),
        "supported": True,
        "width": width,
        "height": height,
        "color_type": color_type,
        "unique_sample_count": unique_samples,
        "likely_blank": unique_samples <= 1,
        "note": "Read-only heuristic; nonblank does not prove visual fidelity.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PNG screenshots for likely blank output.")
    parser.add_argument("screenshots", nargs="+", help="PNG screenshots to inspect.")
    parser.add_argument("--output", help="Optional JSON output path. Defaults to stdout.")
    args = parser.parse_args()

    result = {"screenshots": [parse_png(Path(item)) for item in args.screenshots]}
    payload = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
