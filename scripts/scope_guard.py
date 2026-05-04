#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from harness_common import (
    load_execution_policy,
    mission_machine_spec_path,
    read_json,
    resolve_execution_policy,
    resolve_path,
    write_json,
)


EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache"}


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


def diff_snapshots(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    before_keys = set(before)
    after_keys = set(after)
    added = sorted(after_keys - before_keys)
    deleted = sorted(before_keys - after_keys)
    modified = sorted(key for key in before_keys & after_keys if before[key] != after[key])
    return {
        "added_files": added,
        "modified_files": modified,
        "deleted_files": deleted,
    }


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    diff = diff_snapshots(before, after)
    return sorted(diff["added_files"] + diff["modified_files"] + diff["deleted_files"])


def _matches(path: str, pattern: str) -> bool:
    normalized = pattern.rstrip("/")
    return path == normalized or path.startswith(f"{normalized}/")


def evaluate_scope(
    diff: dict[str, list[str]],
    allowed_touch: list[str],
    forbidden_touch: list[str],
    policy: dict[str, Any],
) -> dict[str, Any]:
    all_changes = sorted(diff["added_files"] + diff["modified_files"] + diff["deleted_files"])
    ignored_files: list[str] = []
    protected_runtime_touches: list[str] = []
    violating: list[str] = []

    for changed in all_changes:
        if any(_matches(changed, pattern) for pattern in policy["ignored_runtime_prefixes"]):
            ignored_files.append(changed)
            continue
        if any(_matches(changed, pattern) for pattern in policy["protected_runtime_prefixes"]):
            protected_runtime_touches.append(changed)
            violating.append(changed)
            continue
        if any(_matches(changed, pattern) for pattern in forbidden_touch):
            violating.append(changed)
            continue
        if not any(_matches(changed, pattern) for pattern in allowed_touch):
            violating.append(changed)

    if protected_runtime_touches:
        summary = "One or more file changes touched protected runtime paths."
    elif violating:
        summary = "One or more file changes violated scope."
    else:
        summary = "All non-ignored file changes stayed within allowed_touch."

    return {
        "status": "pass" if not violating else "violation",
        "added_files": diff["added_files"],
        "modified_files": diff["modified_files"],
        "deleted_files": diff["deleted_files"],
        "ignored_files": ignored_files,
        "protected_runtime_touches": protected_runtime_touches,
        "violating_files": sorted(set(violating)),
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two workspace snapshots against one MB machine spec.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--before-snapshot", required=True)
    parser.add_argument("--after-snapshot", required=True)
    parser.add_argument("--attempt-id")
    parser.add_argument("--output")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    spec = read_json(mission_machine_spec_path(project_root, args.mb_id))
    before = read_json(resolve_path(args.before_snapshot))
    after = read_json(resolve_path(args.after_snapshot))
    policy = resolve_execution_policy(load_execution_policy(), args.mb_id, args.attempt_id)
    result = evaluate_scope(
        diff_snapshots(before, after),
        spec["allowed_touch"],
        spec["forbidden_touch"],
        policy,
    )
    if args.output:
        write_json(resolve_path(args.output), result)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
