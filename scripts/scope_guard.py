#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from harness_common import mission_machine_spec_path, read_json, resolve_path, write_json


EXCLUDED_DIRS = {".git", "runtime", "__pycache__", ".pytest_cache"}


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_workspace(project_root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(project_root).parts)
        if parts & EXCLUDED_DIRS:
            continue
        rel = path.relative_to(project_root).as_posix()
        snapshot[rel] = file_digest(path)
    return snapshot


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def _matches(path: str, pattern: str) -> bool:
    normalized = pattern.rstrip("/")
    return path == normalized or path.startswith(f"{normalized}/")


def evaluate_scope(changes: list[str], allowed_touch: list[str], forbidden_touch: list[str]) -> dict[str, Any]:
    violating: list[str] = []
    for changed in changes:
        if any(_matches(changed, pattern) for pattern in forbidden_touch):
            violating.append(changed)
            continue
        if not any(_matches(changed, pattern) for pattern in allowed_touch):
            violating.append(changed)
    return {
        "status": "pass" if not violating else "violation",
        "changed_files": changes,
        "violating_files": violating,
        "summary": "All file changes stayed within allowed_touch." if not violating else "One or more file changes violated scope.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two workspace snapshots against one MB machine spec.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--before-snapshot", required=True)
    parser.add_argument("--after-snapshot", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    spec = read_json(mission_machine_spec_path(project_root, args.mb_id))
    before = read_json(resolve_path(args.before_snapshot))
    after = read_json(resolve_path(args.after_snapshot))
    result = evaluate_scope(changed_files(before, after), spec["allowed_touch"], spec["forbidden_touch"])
    if args.output:
        write_json(resolve_path(args.output), result)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
