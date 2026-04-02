#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from harness_common import print_validation_result, read_json, resolve_path, validate_with_schema


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing file: {path}"]
    try:
        data = read_json(path)
    except Exception as exc:  # noqa: BLE001
        return [f"invalid json: {exc}"]
    errors.extend(validate_with_schema(data, "mb_machine_spec.schema.json"))
    if errors:
        return errors
    mb_id = data.get("mb_id")
    expected = path.name.removesuffix(".machine.json")
    if path.name.endswith(".machine.json") and mb_id != expected:
        errors.append(f"mb_id mismatch: expected {expected}, got {mb_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one MB machine spec JSON file.")
    parser.add_argument("path", help="Path to missions/<mb_id>.machine.json")
    args = parser.parse_args()

    path = resolve_path(args.path)
    return print_validation_result(f"mb machine spec {path}", validate_file(path))


if __name__ == "__main__":
    raise SystemExit(main())
