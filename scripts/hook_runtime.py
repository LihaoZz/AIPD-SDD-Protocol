#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from harness_common import (
    execution_policy_path,
    load_execution_policy,
    local_timestamp,
    local_timezone_name,
    read_json,
    resolve_execution_policy,
    resolve_path,
    validate_with_schema,
    write_json,
)


def _hook_event(
    hook_name: str,
    status: str,
    summary: str,
    mb_id: str | None,
    attempt_id: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "schema_version": "1.0",
        "hook_name": hook_name,
        "status": status,
        "summary": summary,
        "mb_id": mb_id,
        "attempt_id": attempt_id,
        "generated_at": local_timestamp(),
        "timezone_name": local_timezone_name(),
        "details": details,
    }
    errors = validate_with_schema(event, "hook-event.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    return event


def _write_hook_event(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    write_json(path, event)
    return event


def run_pre_tool_hook(
    project_root: Path,
    spec: dict[str, Any],
    attempt_root: Path,
    command: list[str],
    tool_name: str = "codex_exec",
) -> dict[str, Any]:
    action_text = " ".join(command)
    status = "pass"
    summary = "Pre-tool checks passed."
    policy_path = execution_policy_path()
    matched_forbidden_patterns: list[str] = []
    matched_forbidden_path_prefixes: list[str] = []
    sandbox_requested = None
    sandbox_ok = False
    policy_error = None

    try:
        policy = resolve_execution_policy(
            load_execution_policy(policy_path),
            spec.get("mb_id"),
            attempt_root.name,
        )
    except Exception as exc:  # noqa: BLE001
        policy = None
        policy_error = str(exc)
        status = "block"
        summary = "Blocked execution because execution policy is missing or invalid."

    if policy is not None:
        matched_forbidden_patterns = [
            pattern for pattern in policy["forbidden_command_patterns"] if pattern in action_text
        ]
        if matched_forbidden_patterns:
            status = "block"
            summary = "Blocked execution because the command matched forbidden execution policy patterns."

        matched_forbidden_path_prefixes = [
            prefix for prefix in policy["forbidden_path_prefixes"] if prefix in action_text
        ]
        if matched_forbidden_path_prefixes:
            status = "block"
            summary = "Blocked execution because the command referenced forbidden path prefixes."

        if "--dangerously-bypass-approvals-and-sandbox" in command and not policy["sandbox"]["allow_bypass"]:
            status = "block"
            summary = "Blocked execution because sandbox bypass is forbidden by execution policy."

        if "--sandbox" in command:
            sandbox_index = command.index("--sandbox")
            if sandbox_index + 1 < len(command):
                sandbox_requested = command[sandbox_index + 1]
        sandbox_ok = sandbox_requested == policy["sandbox"]["mode"]
        if not sandbox_ok:
            status = "block"
            summary = "Blocked execution because the command does not request the required sandbox mode."

    if status == "pass" and not spec.get("allowed_touch"):
        status = "block"
        summary = "Blocked execution because allowed_touch is empty."
    elif status == "pass" and set(spec.get("allowed_touch", [])) & set(spec.get("forbidden_touch", [])):
        status = "block"
        summary = "Blocked execution because allowed_touch overlaps forbidden_touch."

    event = _hook_event(
        "pre_tool_hook",
        status,
        summary,
        spec.get("mb_id"),
        attempt_root.name,
        {
            "tool_name": tool_name,
            "project_root": str(project_root),
            "command": command,
            "allowed_touch": spec.get("allowed_touch", []),
            "forbidden_touch": spec.get("forbidden_touch", []),
            "policy_path": str(policy_path),
            "policy_error": policy_error,
            "matched_forbidden_command_patterns": matched_forbidden_patterns,
            "matched_forbidden_path_prefixes": matched_forbidden_path_prefixes,
            "sandbox_required": policy["sandbox"]["mode"] if policy is not None else None,
            "sandbox_requested": sandbox_requested,
            "sandbox_ok": sandbox_ok,
            "allow_bypass": policy["sandbox"]["allow_bypass"] if policy is not None else None,
        },
    )
    return _write_hook_event(attempt_root / "pre_tool_hook.json", event)


def run_post_tool_hook(
    spec: dict[str, Any],
    attempt_root: Path,
    execution: dict[str, Any],
    changed_files: list[str],
) -> dict[str, Any]:
    event = _hook_event(
        "post_tool_hook",
        "pass",
        "Captured Codex execution audit trace.",
        spec.get("mb_id"),
        attempt_root.name,
        {
            "returncode": execution.get("returncode"),
            "changed_files": changed_files,
            "stdout_excerpt": (execution.get("stdout") or "")[:400],
            "stderr_excerpt": (execution.get("stderr") or "")[:400],
        },
    )
    return _write_hook_event(attempt_root / "post_tool_hook.json", event)


def run_stop_hook(
    spec: dict[str, Any],
    attempt_root: Path,
    final_status: str,
    verification_report_path: Path | None,
) -> dict[str, Any]:
    status = "pass"
    summary = "Stop gate passed."
    details: dict[str, Any] = {"final_status": final_status}

    if final_status == "passed":
        if verification_report_path is None or not verification_report_path.exists():
            status = "block"
            summary = "Stop gate blocked completion because verification evidence is missing."
        else:
            report = read_json(verification_report_path)
            details["verification_report_path"] = str(verification_report_path)
            details["verification_result"] = report.get("result")
            if report.get("result") != "pass":
                status = "block"
                summary = "Stop gate blocked completion because verification did not pass."

    event = _hook_event(
        "stop_hook",
        status,
        summary,
        spec.get("mb_id"),
        attempt_root.name,
        details,
    )
    return _write_hook_event(attempt_root / "stop_hook.json", event)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one harness hook in isolation.")
    parser.add_argument("--hook", choices=["pre", "post", "stop"], required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--tool-name", default="codex_exec")
    parser.add_argument("--tool-action")
    parser.add_argument("--execution-result")
    parser.add_argument("--changed-files-json")
    parser.add_argument("--final-status")
    parser.add_argument("--verification-report")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    spec = read_json(resolve_path(args.spec))
    attempt_root = resolve_path(args.attempt_dir)

    if args.hook == "pre":
        command = [args.tool_action] if args.tool_action else [args.tool_name]
        event = run_pre_tool_hook(project_root, spec, attempt_root, command, args.tool_name)
    elif args.hook == "post":
        if not args.execution_result or not args.changed_files_json:
            parser.error("--execution-result and --changed-files-json are required for --hook post")
        event = run_post_tool_hook(
            spec,
            attempt_root,
            read_json(resolve_path(args.execution_result)),
            read_json(resolve_path(args.changed_files_json)),
        )
    else:
        if not args.final_status:
            parser.error("--final-status is required for --hook stop")
        report_path = resolve_path(args.verification_report) if args.verification_report else None
        event = run_stop_hook(spec, attempt_root, args.final_status, report_path)

    print(json.dumps(event, ensure_ascii=True, indent=2))
    return 0 if event["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
