#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from harness_common import (
    attempt_dir,
    initialize_runtime_memory,
    mission_machine_spec_path,
    mission_markdown_path,
    read_json,
    read_text,
    resolve_path,
    runtime_state_path,
    local_timestamp,
    write_json,
)
from preflight import mb_preflight
from scope_guard import changed_files, evaluate_scope, snapshot_workspace
from state_writer import append_failure_log, append_project_memory, load_state, sync_session_state, write_state
from verifier import run_verification


def next_attempt_id(project_root: Path, mb_id: str) -> str:
    root = project_root / "runtime" / "attempts" / mb_id
    if not root.exists():
        return "attempt-001"
    numbers = []
    for child in root.iterdir():
        if child.is_dir() and child.name.startswith("attempt-"):
            try:
                numbers.append(int(child.name.split("-")[-1]))
            except ValueError:
                continue
    next_number = (max(numbers) + 1) if numbers else 1
    return f"attempt-{next_number:03d}"


def build_verification_digest(report: dict[str, Any]) -> str:
    failed = [check for check in report["checks"] if check["status"] == "fail"]
    if not failed:
        return "All verification checks passed."
    parts = []
    for check in failed:
        parts.append(f"{check['check_id']}: {check['evidence']}")
    return " | ".join(parts)


def summarize_output(last_message_path: Path) -> str:
    if not last_message_path.exists():
        return "No final assistant message was produced."
    text = last_message_path.read_text(encoding="utf-8").strip()
    if not text:
        return "Assistant message was empty."
    return text[:400]


def classify_execution_failure(message_text: str, changed_files: list[str]) -> dict[str, str] | None:
    lower = message_text.lower()
    explicit_routes = {
        "state_drift": "state_drift",
        "environment_issue": "environment_issue",
        "review_context_gap": "review_context_gap",
        "spec_gap": "spec_gap",
    }
    for marker, failure_type in explicit_routes.items():
        if marker in lower:
            return {
                "failure_type": failure_type,
                "condition": f"Assistant explicitly reported {failure_type}.",
            }

    blocked_spec_gap_patterns = [
        r"blocked by protocol conflicts",
        r"upstream conflicts prevent a compliant run",
        r"required upstream inputs (are )?missing",
        r"required inputs are missing",
        r"contract fix before implementation",
        r"scope conflict needs resolution",
        r"missing upstream inputs",
    ]
    if not changed_files and "blocked" in lower:
        for pattern in blocked_spec_gap_patterns:
            if re.search(pattern, lower):
                return {
                    "failure_type": "spec_gap",
                    "condition": "Assistant reported a blocked contract or input conflict.",
                }
    return None


def build_prompt(project_root: Path, spec: dict[str, Any], state: dict[str, Any]) -> str:
    builder_prompt = read_text(Path(__file__).resolve().parent.parent / "prompts" / "BUILDER.system.md")
    mission_md = read_text(mission_markdown_path(project_root, spec["mb_id"]))
    context_sections = []
    for rel_path in spec["context_files"]:
        path = project_root / rel_path
        if path.is_file():
            context_sections.append(f"## Context File: {rel_path}\n\n```\n{read_text(path)}\n```")
    retry_section = ""
    if state["retry_count"] > 0:
        retry_parts = []
        if state.get("last_verification_digest"):
            retry_parts.append(f"Verification Digest: {state['last_verification_digest']}")
        if state.get("last_failure_reason"):
            retry_parts.append(f"Last Failure Reason: {state['last_failure_reason']}")
        retry_parts.append(f"Retry Count: {state['retry_count']}")
        retry_section = "## Retry Feedback\n\n" + "\n".join(f"- {line}" for line in retry_parts) + "\n"

    prompt = f"""{builder_prompt}

## Harness Mission Packet

- Timestamp: {local_timestamp()}
- MB ID: {spec["mb_id"]}
- Parent FB ID: {spec["parent_fb_id"]}
- Goal: {spec["goal"]}
- Allowed Touch: {", ".join(spec["allowed_touch"])}
- Forbidden Touch: {", ".join(spec["forbidden_touch"]) if spec["forbidden_touch"] else "none"}
- Acceptance Checks: {", ".join(check["check_id"] for check in spec["acceptance"])}

## Active Mission Markdown

```
{mission_md}
```

{retry_section}
## Execution Rules

- Stay strictly inside allowed touch.
- Do not edit files under forbidden touch.
- Use the retry feedback to fix only the failed checks.
- The workspace may not be a Git repository. Do not use git status or git diff just to report changed files.
- Report changed files from the files you directly edited.
- At the end, reply with a short summary and the changed files.

{chr(10).join(context_sections)}
"""
    return prompt


def run_codex_cli(
    project_root: Path,
    prompt: str,
    attempt_root: Path,
    codex_command: str,
    model: str | None,
    dry_run: bool,
    stream_output: bool,
    json_output: bool,
) -> dict[str, Any]:
    last_message_path = attempt_root / "last_message.txt"
    command = [
        codex_command,
        "exec",
        "--cd",
        str(project_root),
        "--skip-git-repo-check",
        "--full-auto",
        "--ephemeral",
        "--color",
        "never",
        "--output-last-message",
        str(last_message_path),
        "-",
    ]
    if model:
        command[2:2] = ["-m", model]
    if json_output:
        command.insert(-2, "--json")

    if dry_run:
        last_message_path.write_text("DRY RUN: no Codex execution performed.\n", encoding="utf-8")
        return {"returncode": 0, "stdout": "", "stderr": "", "command": command}

    if not stream_output:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "command": command,
        }

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    def consume(stream: Any, buffer: list[str], sink: Any) -> None:
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            buffer.append(line)
            sink.write(line)
            sink.flush()
        stream.close()

    assert process.stdin is not None
    process.stdin.write(prompt)
    process.stdin.close()

    stdout_thread = threading.Thread(target=consume, args=(process.stdout, stdout_chunks, sys.stdout), daemon=True)
    stderr_thread = threading.Thread(target=consume, args=(process.stderr, stderr_chunks, sys.stderr), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    returncode = process.wait()
    stdout_thread.join()
    stderr_thread.join()

    return {
        "returncode": returncode,
        "stdout": "".join(stdout_chunks),
        "stderr": "".join(stderr_chunks),
        "command": command,
    }


def run_once(
    project_root: Path,
    mb_id: str,
    codex_command: str,
    model: str | None,
    dry_run: bool,
    stream_output: bool,
    json_output: bool,
) -> int:
    initialize_runtime_memory(project_root)
    preflight_result, preflight_errors = mb_preflight(project_root, mb_id)
    if preflight_errors:
        print("\n".join(preflight_errors))
        return 1
    if preflight_result["result"] != "ready":
        print(json.dumps(preflight_result, ensure_ascii=True, indent=2))
        return 1

    spec = read_json(mission_machine_spec_path(project_root, mb_id))
    state = load_state(project_root, mb_id)
    if state["status"] in {"passed", "routed_to_recovery"}:
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 0

    while True:
        attempt_id = next_attempt_id(project_root, mb_id)
        current_attempt_dir = attempt_dir(project_root, mb_id, attempt_id)
        current_attempt_dir.mkdir(parents=True, exist_ok=True)

        prompt = build_prompt(project_root, spec, state)
        prompt_path = current_attempt_dir / "prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")

        before = snapshot_workspace(project_root)
        before_path = current_attempt_dir / "before_snapshot.json"
        write_json(before_path, before)

        state.update(
            {
                "status": "running",
                "last_attempt_id": attempt_id,
                "next_action": "await_codex_result",
            }
        )
        write_state(project_root, state)

        execution = run_codex_cli(
            project_root,
            prompt,
            current_attempt_dir,
            codex_command,
            model,
            dry_run,
            stream_output,
            json_output,
        )
        write_json(current_attempt_dir / "execution_result.json", execution)
        (current_attempt_dir / "raw_output.txt").write_text(execution["stdout"], encoding="utf-8")
        (current_attempt_dir / "raw_error.txt").write_text(execution["stderr"], encoding="utf-8")

        after = snapshot_workspace(project_root)
        after_path = current_attempt_dir / "after_snapshot.json"
        write_json(after_path, after)

        changes = changed_files(before, after)
        write_json(current_attempt_dir / "changed_files.json", changes)
        scope_result = evaluate_scope(changes, spec["allowed_touch"], spec["forbidden_touch"])
        write_json(current_attempt_dir / "scope_guard.json", scope_result)

        if scope_result["status"] != "pass":
            state.update(
                {
                    "status": "routed_to_recovery",
                    "retry_count": state["retry_count"] + 1,
                    "last_failure_reason": "scope_violation",
                    "last_verification_report_path": None,
                    "last_verification_digest": None,
                    "next_action": "route_to_recovery",
                }
            )
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            append_failure_log(
                project_root,
                {
                    "mb_id": mb_id,
                    "attempt_id": attempt_id,
                    "failure_type": "scope_violation",
                    "condition": scope_result["summary"],
                    "attempted_fix": summarize_output(current_attempt_dir / "last_message.txt"),
                    "result": "routed_to_recovery",
                },
            )
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return 1

        assistant_message = summarize_output(current_attempt_dir / "last_message.txt")
        classified_failure = classify_execution_failure(assistant_message, changes)
        if classified_failure is not None:
            state.update(
                {
                    "status": "routed_to_recovery",
                    "last_failure_reason": classified_failure["failure_type"],
                    "next_action": "route_to_recovery",
                }
            )
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            append_failure_log(
                project_root,
                {
                    "mb_id": mb_id,
                    "attempt_id": attempt_id,
                    "failure_type": classified_failure["failure_type"],
                    "condition": classified_failure["condition"],
                    "attempted_fix": assistant_message,
                    "result": "routed_to_recovery",
                },
            )
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return 1

        state.update({"status": "verifying", "next_action": "run_verification"})
        write_state(project_root, state)

        report = run_verification(project_root, spec, attempt_id, changes, scope_result)
        report_path = current_attempt_dir / "verification_report.json"
        write_json(report_path, report)

        if report["result"] == "pass":
            state.update(
                {
                    "status": "passed",
                    "last_verification_report_path": str(report_path.relative_to(project_root)),
                    "last_verification_digest": build_verification_digest(report),
                    "last_failure_reason": None,
                    "next_action": "close_mb",
                }
            )
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            append_project_memory(project_root, spec["parent_fb_id"], mb_id, report)
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return 0

        state["retry_count"] += 1
        state["last_verification_report_path"] = str(report_path.relative_to(project_root))
        state["last_verification_digest"] = build_verification_digest(report)
        state["last_failure_reason"] = report["summary"]
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "attempt_id": attempt_id,
                "failure_type": "verification_failed",
                "condition": report["summary"],
                "attempted_fix": summarize_output(current_attempt_dir / "last_message.txt"),
                "result": "retry" if state["retry_count"] < spec["retry_policy"]["max_retries"] else "routed_to_recovery",
            },
        )

        if state["retry_count"] >= spec["retry_policy"]["max_retries"]:
            state["status"] = "routed_to_recovery"
            state["next_action"] = "route_to_recovery"
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return 1

        state["status"] = "failed"
        state["next_action"] = "retry"
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one MB through the harness loop using Codex CLI.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--codex-command", default="codex")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stream-codex-output", action="store_true")
    parser.add_argument("--codex-json", action="store_true")
    args = parser.parse_args()

    return run_once(
        resolve_path(args.project_root),
        args.mb_id,
        args.codex_command,
        args.model,
        args.dry_run,
        args.stream_codex_output,
        args.codex_json,
    )


if __name__ == "__main__":
    raise SystemExit(main())
