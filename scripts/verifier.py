#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from harness_common import eval_asset_path, local_timestamp, local_timezone_name, normalize_relpath, read_json, resolve_path, validate_with_schema, write_json


SHELL_CONTROL_TOKENS = {"&&", "||", "|", ";", "&", ">", ">>", "<", "2>", "1>", "2>&1"}


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


def verification_items(project_root: Path, spec: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    items: list[tuple[str, str, dict[str, Any]]] = []
    for item in spec.get("acceptance", []):
        items.append(("inline_acceptance", "acceptance", item))
    for ref in spec.get("eval_refs", []):
        payload = read_json(eval_asset_path(project_root, ref))
        schema_errors = validate_with_schema(payload, "eval-asset.schema.json")
        if schema_errors:
            raise ValueError(f"invalid eval asset {ref}: {'; '.join(schema_errors)}")
        items.append(("eval_asset", ref, payload["check"]))
    return items


def run_api_scenario(item: dict[str, Any]) -> dict[str, Any]:
    headers = dict(item.get("headers") or {})
    body_bytes = None
    if "request_json" in item:
        body_bytes = json.dumps(item["request_json"]).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(
        item["url"],
        data=body_bytes,
        headers=headers,
        method=item["method"].upper(),
    )
    response_status = None
    response_body = ""
    try:
        with urllib.request.urlopen(request) as response:
            response_status = response.getcode()
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        response_status = exc.code
        response_body = exc.read().decode("utf-8")
    except urllib.error.URLError as exc:
        response_body = str(exc.reason)

    passed = response_status == item["expected_status"]
    evidence = f"status matched expected: {passed}"
    if passed and item.get("response_json_pointer") is not None:
        payload = json.loads(response_body or "null")
        actual = resolve_json_pointer(payload, item["response_json_pointer"])
        passed = actual == item.get("expected_json")
        evidence = f"json field matched expected value: {passed}"

    return {
        "method": item["method"].upper(),
        "url": item["url"],
        "expected_status": item["expected_status"],
        "response_status": response_status,
        "response_body": response_body,
        "status": "pass" if passed else "fail",
        "evidence": evidence,
    }


def parse_command_argv(command: str) -> list[str]:
    argv = shlex.split(command, posix=True)
    if not argv:
        raise ValueError("verification command is empty")
    bad_tokens = sorted({token for token in argv if token in SHELL_CONTROL_TOKENS})
    if bad_tokens:
        raise ValueError(
            "verification command uses unsupported shell control tokens: "
            + ", ".join(bad_tokens)
        )
    return argv


def run_verification(
    project_root: Path,
    spec: dict[str, Any],
    attempt_id: str,
    changed_files: list[str],
    scope_result: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for source_kind, source_ref, item in verification_items(project_root, spec):
        check_result: dict[str, Any] = {
            "check_id": item["check_id"],
            "type": item["type"],
            "source_kind": source_kind,
            "source_ref": source_ref,
            "status": "fail",
            "evidence": "",
        }
        try:
            if item["type"] == "command":
                argv = parse_command_argv(item["command"])
                completed = subprocess.run(
                    argv,
                    shell=False,
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
                path = normalize_relpath(project_root, item["path"])
                exists = path.exists()
                check_result.update(
                    {
                        "path": item["path"],
                        "status": "pass" if exists else "fail",
                        "evidence": "path exists" if exists else "path missing",
                    }
                )
            elif item["type"] == "json_field":
                path = normalize_relpath(project_root, item["path"])
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
            elif item["type"] == "api_scenario":
                check_result.update(run_api_scenario(item))
        except Exception as exc:  # noqa: BLE001
            check_result.update(
                {
                    "status": "fail",
                    "evidence": f"verification check errored: {exc}",
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
        "generated_at": local_timestamp(),
        "timezone_name": local_timezone_name(),
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
