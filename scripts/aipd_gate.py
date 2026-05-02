#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from harness_common import (
    attempt_dir,
    initialize_runtime_memory,
    mission_machine_spec_path,
    read_json,
    resolve_path,
    runtime_dir,
    runtime_state_path,
    write_json,
)
from hook_runtime import run_post_tool_hook, run_stop_hook
from mb_runner import (
    attempt_start,
    build_verification_digest,
    classify_execution_failure,
    effective_autonomy_level,
    issue_route,
    record_attempt_finish_outcome,
    record_attempt_start_rejection,
    increment_provider_counter,
    provider_command,
    selected_execution_provider,
    set_failure_issue_type,
)
from preflight import mb_preflight
from scope_guard import changed_files, evaluate_scope, snapshot_workspace
from state_writer import append_failure_log, append_project_memory, load_state, sync_session_state, write_state
from verifier import run_verification


def prepare_state(project_root: Path, mb_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    initialize_runtime_memory(project_root)
    preflight_result, preflight_errors = mb_preflight(project_root, mb_id)
    if preflight_errors:
        raise ValueError("\n".join(preflight_errors))
    if preflight_result["result"] != "ready":
        raise RuntimeError(json.dumps(preflight_result, ensure_ascii=True, indent=2))

    spec = read_json(mission_machine_spec_path(project_root, mb_id))
    state = load_state(project_root, mb_id)
    autonomy_level = effective_autonomy_level(spec)
    state["autonomy_level"] = autonomy_level
    if autonomy_level == "L1_human_approval":
        state["approval_status"] = state.get("approval_status", "pending")
        if state["approval_status"] == "not_required":
            state["approval_status"] = "pending"
    else:
        state["approval_status"] = "not_required"
    state["review_required"] = autonomy_level in {"L1_human_approval", "L2_auto_with_review"} and state["status"] == "passed"
    return spec, state, autonomy_level


def sync_workspace_changes(workspace_root: Path, project_root: Path, changes: list[str]) -> None:
    for rel_path in changes:
        source = workspace_root / rel_path
        target = project_root / rel_path
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        elif target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()


def run_attempt_start(
    project_root: Path,
    mb_id: str,
    agent_command: str,
    minimax_command: str | None,
    deepseek_command: str | None,
) -> int:
    spec, state, autonomy_level = prepare_state(project_root, mb_id)
    if state["status"] in {"passed", "routed_to_recovery"}:
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 0

    if autonomy_level == "L1_human_approval" and state["approval_status"] != "approved":
        state.update(
            {
                "status": "blocked",
                "last_failure_reason": "human_approval_required",
                "last_failure_issue_type": "review_context_gap",
                "review_required": True,
                "next_action": "await_human_approval",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        record_attempt_start_rejection(
            project_root,
            mb_id,
            "review_context_gap",
            "current_scene_lead",
            "await_human_approval",
            "pause_wait_human",
            "Human approval is required before this L1 MB can start.",
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 1

    start_result = attempt_start(
        project_root,
        mb_id,
        spec,
        state,
        agent_command,
        minimax_command,
        deepseek_command,
        None,
        False,
    )
    if start_result["status"] == "ready":
        attempt_gate = read_json(start_result["attempt_dir"] / "attempt_start_gate_outcome.json")
        gate_archive = runtime_dir(project_root) / "gate_outcomes" / mb_id / "attempt_start.json"
        write_json(gate_archive, attempt_gate)
    payload = {
        "status": start_result["status"],
        "attempt_id": start_result.get("attempt_id"),
        "attempt_dir": str(start_result.get("attempt_dir")) if start_result.get("attempt_dir") else None,
        "exit_code": start_result.get("exit_code"),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return int(start_result.get("exit_code", 0) or 0) if start_result["status"] == "stop" else 0


def run_attempt_finish(project_root: Path, workspace_root: Path, mb_id: str, attempt_id: str, summary: str | None) -> int:
    spec, state, autonomy_level = prepare_state(project_root, mb_id)
    current_attempt_dir = attempt_dir(project_root, mb_id, attempt_id)
    if not current_attempt_dir.exists():
        raise FileNotFoundError(f"missing attempt dir: {current_attempt_dir}")

    before = read_json(current_attempt_dir / "before_snapshot.json")
    after = snapshot_workspace(workspace_root)
    write_json(current_attempt_dir / "workspace_after_snapshot.json", after)

    changes = changed_files(before, after)
    write_json(current_attempt_dir / "changed_files.json", changes)
    current_provider = state.get("last_execution_provider") or selected_execution_provider(spec, state)[0]
    execution = {
        "returncode": 0,
        "stdout": summary or "",
        "stderr": "",
        "command": [current_provider, "app-server"],
    }
    write_json(current_attempt_dir / "execution_result.json", execution)
    (current_attempt_dir / "last_message.txt").write_text((summary or "") + "\n", encoding="utf-8")
    run_post_tool_hook(spec, current_attempt_dir, execution, changes)

    scope_result = evaluate_scope(changes, spec["allowed_touch"], spec["forbidden_touch"])
    scope_path = current_attempt_dir / "scope_guard.json"
    write_json(scope_path, scope_result)

    if scope_result["status"] != "pass":
        state.update(
            {
                "status": "routed_to_recovery",
                "retry_count": state["retry_count"] + 1,
                "last_failure_reason": "scope_violation",
                "last_failure_issue_type": "state_drift",
                "last_verification_report_path": None,
                "last_verification_digest": None,
                "review_required": False,
                "next_action": "route_to_recovery",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "parent_fb_id": spec["parent_fb_id"],
                "attempt_id": attempt_id,
                "failure_type": "scope_violation",
                "condition": scope_result["summary"],
                "attempted_fix": summary or "Symphony workspace changes violated scope.",
                "result": "routed_to_recovery",
            },
        )
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", None)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "routed_to_recovery",
            "state_drift",
            "recovery_coordinator",
            "route_to_recovery",
            "stop_and_route_recovery",
            False,
            None,
            scope_result["summary"],
            [str(scope_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 1

    classified_failure = classify_execution_failure(summary or "", changes)
    if classified_failure is not None:
        issue_type = classified_failure["failure_type"]
        route_to = issue_route(issue_type)
        action = "stop_and_route_owner" if issue_type == "spec_gap" else "stop_and_route_recovery"
        status = "routed_to_owner" if issue_type == "spec_gap" else "routed_to_recovery"
        state.update(
            {
                "status": "routed_to_recovery",
                "last_failure_reason": issue_type,
                "last_failure_issue_type": issue_type,
                "review_required": False,
                "next_action": "route_to_recovery",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "parent_fb_id": spec["parent_fb_id"],
                "attempt_id": attempt_id,
                "failure_type": issue_type,
                "condition": classified_failure["condition"],
                "attempted_fix": summary or "",
                "result": "routed_to_recovery",
            },
        )
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", None)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            status,
            issue_type,
            route_to,
            "route_to_recovery",
            action,
            False,
            None,
            classified_failure["condition"],
            [str(current_attempt_dir.joinpath("last_message.txt").relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 1

    sync_workspace_changes(workspace_root, project_root, changes)
    synced_after = snapshot_workspace(project_root)
    write_json(current_attempt_dir / "after_snapshot.json", synced_after)

    report = run_verification(project_root, spec, attempt_id, changes, scope_result)
    report_path = current_attempt_dir / "verification_report.json"
    write_json(report_path, report)

    if report["result"] == "pass":
        stop_hook = run_stop_hook(spec, current_attempt_dir, "passed", report_path)
        if stop_hook["status"] != "pass":
            state.update(
                {
                    "status": "blocked",
                    "last_failure_reason": "stop_hook_blocked",
                    "last_failure_issue_type": "environment_issue",
                    "review_required": False,
                    "next_action": "inspect_stop_hook",
                }
            )
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            append_failure_log(
                project_root,
                {
                    "mb_id": mb_id,
                    "parent_fb_id": spec["parent_fb_id"],
                    "attempt_id": attempt_id,
                    "failure_type": "stop_hook_blocked",
                    "condition": stop_hook["summary"],
                    "attempted_fix": summary or "Symphony finish bridge reported missing verification evidence.",
                    "result": "blocked",
                },
            )
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return 1

        next_action = "handoff_to_review" if autonomy_level in {"L1_human_approval", "L2_auto_with_review"} else "close_mb"
        state.update(
            {
                "status": "passed",
                "last_verification_report_path": str(report_path.relative_to(project_root)),
                "last_verification_digest": build_verification_digest(report),
                "last_failure_reason": None,
                "last_failure_issue_type": None,
                "review_required": autonomy_level in {"L1_human_approval", "L2_auto_with_review"},
                "next_action": next_action,
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_project_memory(project_root, spec["parent_fb_id"], mb_id, report)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "passed",
            None,
            None,
            next_action,
            "release_to_review" if state["review_required"] else "close_mb",
            False,
            None,
            report["summary"],
            [str(report_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 0

    state["retry_count"] += 1
    state["last_verification_report_path"] = str(report_path.relative_to(project_root))
    state["last_verification_digest"] = build_verification_digest(report)
    state["last_failure_reason"] = report["summary"]
    state["last_failure_issue_type"] = "implementation_bug"
    state["review_required"] = False
    if state.get("last_execution_provider") in {"codex", "minimax", "deepseek"}:
        increment_provider_counter(state, "provider_failure_counts", state["last_execution_provider"])
    retry_limit_reached = state["retry_count"] >= spec["retry_policy"]["max_retries"]
    append_failure_log(
        project_root,
        {
            "mb_id": mb_id,
            "parent_fb_id": spec["parent_fb_id"],
            "attempt_id": attempt_id,
            "failure_type": "verification_failed",
            "condition": report["summary"],
            "attempted_fix": summary or "Symphony workspace verification failed.",
            "result": "routed_to_recovery" if retry_limit_reached else "retry",
        },
    )

    if retry_limit_reached:
        state["status"] = "routed_to_recovery"
        state["next_action"] = "route_to_recovery"
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", report_path)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "routed_to_recovery",
            "implementation_bug",
            issue_route("implementation_bug"),
            "route_to_recovery",
            "stop_and_route_recovery",
            False,
            None,
            report["summary"],
            [str(report_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 1

    state["status"] = "failed"
    state["next_action"] = "retry"
    write_state(project_root, state)
    sync_session_state(project_root, spec["parent_fb_id"], state)
    record_attempt_finish_outcome(
        project_root,
        spec,
        attempt_id,
        current_attempt_dir,
        "retry_allowed",
        "implementation_bug",
        issue_route("implementation_bug"),
        "retry_with_verification_feedback",
        "schedule_semantic_retry",
        True,
        0,
        report["summary"],
        [str(report_path.relative_to(project_root))],
    )
    print(json.dumps(state, ensure_ascii=True, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AIPD gate bridge for bundled Symphony integration.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("attempt-start", help="Generate and validate one attempt_start gate outcome.")
    start_parser.add_argument("--project-root", required=True)
    start_parser.add_argument("--mb-id", required=True)
    start_parser.add_argument("--agent-command", default="codex app-server")
    start_parser.add_argument("--codex-command", dest="agent_command")
    start_parser.add_argument("--minimax-command")
    start_parser.add_argument("--deepseek-command")

    finish_parser = subparsers.add_parser("attempt-finish", help="Apply one Symphony workspace result to AIPD state.")
    finish_parser.add_argument("--project-root", required=True)
    finish_parser.add_argument("--workspace-root", required=True)
    finish_parser.add_argument("--mb-id", required=True)
    finish_parser.add_argument("--attempt-id", required=True)
    finish_parser.add_argument("--summary")

    args = parser.parse_args()

    if args.command == "attempt-start":
        return run_attempt_start(
            resolve_path(args.project_root),
            args.mb_id,
            args.agent_command,
            args.minimax_command,
            args.deepseek_command,
        )

    return run_attempt_finish(
        resolve_path(args.project_root),
        resolve_path(args.workspace_root),
        args.mb_id,
        args.attempt_id,
        args.summary,
    )


if __name__ == "__main__":
    raise SystemExit(main())
