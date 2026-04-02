#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from harness_common import read_json, resolve_path, validate_with_schema, write_json


def resolve_json_pointer(payload: Any, pointer: str) -> Any:
    current = payload
    if pointer == "":
        return current
    for raw_part in pointer.lstrip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def run_verification(
    project_root: Path,
    spec: dict[str, Any],
    attempt_id: str,
    changed_files: list[str],
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for item in spec["acceptance"]:
        check_result: dict[str, Any] = {
            "check_id": item["check_id"],
            "type": item["type"],
            "status": "fail",
            "evidence": "",
        }
        if item["type"] == "command":
            completed = subprocess.run(
                item["command"],
                shell=True,
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            check_result.update(
                {
                    "command": item["command"],
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "status": "pass" if completed.returncode == 0 else "fail",
                    "evidence": f"command exited with code {completed.returncode}",
                }
            )
        elif item["type"] == "file_exists":
            path = project_root / item["path"]
            exists = path.exists()
            check_result.update(
                {
                    "path": item["path"],
                    "status": "pass" if exists else "fail",
                    "evidence": "path exists" if exists else "path missing",
                }
            )
        elif item["type"] == "json_field":
            path = project_root / item["path"]
            payload = read_json(path)
            actual = resolve_json_pointer(payload, item["json_pointer"])
            passed = actual == item["expected"]
            check_result.update(
                {
                    "path": item["path"],
                    "json_pointer": item["json_pointer"],
                    "expected": item["expected"],
                    "status": "pass" if passed else "fail",
                    "evidence": f"json field matched expected value: {passed}",
                }
            )
        elif item["type"] == "no_out_of_scope_changes":
            passed = scope_result["status"] == "pass"
            check_result.update(
                {
                    "status": "pass" if passed else "fail",
                    "evidence": f"changed_files={changed_files}",
                }
            )
        checks.append(check_result)

    failed = [check for check in checks if check["status"] == "fail"]
    result = "pass" if not failed else "fail"
    summary = "All verification checks passed." if not failed else "Failed checks: " + ", ".join(check["check_id"] for check in failed)
    report = {
        "schema_version": "1.0",
        "mb_id": spec["mb_id"],
        "attempt_id": attempt_id,
        "result": result,
        "summary": summary,
        "checks": checks,
    }
    schema_errors = validate_with_schema(report, "verification-report.schema.json")
    if schema_errors:
        raise ValueError("; ".join(schema_errors))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run machine verification for one MB attempt.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--changed-files-json", required=True)
    parser.add_argument("--scope-result-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    spec = read_json(resolve_path(args.spec))
    changed = read_json(resolve_path(args.changed_files_json))
    scope_result = read_json(resolve_path(args.scope_result_json))
    report = run_verification(project_root, spec, args.attempt_id, changed, scope_result)
    write_json(resolve_path(args.output), report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
