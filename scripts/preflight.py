#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness_common import (
    REQUIRED_PROJECT_FILES,
    execution_policy_errors,
    execution_policy_path,
    function_block_path,
    initialize_runtime_memory,
    markdown_field,
    mb_preflight_path,
    mission_machine_spec_path,
    mission_markdown_path,
    normalize_relpath,
    print_validation_result,
    read_json,
    resolve_path,
    runtime_state_path,
    session_preflight_path,
    local_timestamp,
    local_timezone_name,
    validate_with_schema,
    write_json,
)


def record_declared_path_check(
    project_root: Path,
    rel_path: str,
    field_name: str,
    checks: list[dict[str, str]],
    blocking_items: list[str],
    *,
    must_exist: bool,
) -> None:
    try:
        target = normalize_relpath(project_root, rel_path)
    except ValueError as exc:
        blocking_items.append(f"{field_name} invalid: {rel_path} ({exc})")
        checks.append({"name": field_name, "status": "fail", "detail": rel_path})
        return

    if must_exist and not target.exists():
        blocking_items.append(f"{field_name} missing: {rel_path}")
        checks.append({"name": field_name, "status": "fail", "detail": rel_path})
        return

    checks.append({"name": field_name, "status": "pass", "detail": rel_path})


def runtime_mission_contract_errors(project_root: Path, mission_path: Path, mb_id: str) -> list[str]:
    errors: list[str] = []
    machine_spec_ref = markdown_field(mission_path, "machine_spec_ref")
    expected_spec_ref = f"missions/{mb_id}.machine.json"
    if machine_spec_ref is None:
        errors.append("mission missing machine_spec_ref")
    elif machine_spec_ref != expected_spec_ref:
        errors.append(f"mission machine_spec_ref mismatch: {machine_spec_ref}")
    else:
        try:
            normalize_relpath(project_root, machine_spec_ref)
        except ValueError as exc:
            errors.append(f"mission machine_spec_ref invalid: {exc}")

    required_artifact_updates = markdown_field(mission_path, "required_artifact_updates")
    if (
        required_artifact_updates is not None
        and "SESSION_STATE.md" in required_artifact_updates
        and machine_spec_ref is not None
        and machine_spec_ref.lower() != "none"
    ):
        errors.append(
            "mission must not list SESSION_STATE.md in required_artifact_updates for a runnable MB"
        )
    return errors


def build_result(level: str, project_root: Path, mb_id: str | None, result: str, summary: str, missing_items: list[str], blocking_items: list[str], checks: list[dict[str, str]], autonomy_decision: str | None = None) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "level": level,
        "project_root": str(project_root),
        "mb_id": mb_id,
        "result": result,
        "autonomy_decision": autonomy_decision,
        "summary": summary,
        "missing_items": missing_items,
        "blocking_items": blocking_items,
        "checks": checks,
        "generated_at": local_timestamp(),
        "timezone_name": local_timezone_name(),
    }


def finalize_result(result: dict[str, object], path: Path) -> tuple[dict[str, object], list[str]]:
    errors = validate_with_schema(result, "preflight-result.schema.json")
    if not errors:
        write_json(path, result)
    return result, errors


def session_preflight(project_root: Path) -> tuple[dict[str, object], list[str]]:
    initialize_runtime_memory(project_root)
    checks: list[dict[str, str]] = []
    missing_items: list[str] = []
    blocking_items: list[str] = []

    for rel_path in REQUIRED_PROJECT_FILES:
        target = project_root / rel_path
        if target.exists():
            checks.append({"name": rel_path, "status": "pass", "detail": "present"})
        else:
            checks.append({"name": rel_path, "status": "warn", "detail": "missing"})
            missing_items.append(rel_path)

    session_state = project_root / "SESSION_STATE.md"
    if session_state.exists():
        active_fb = markdown_field(session_state, "active_function_block")
        active_mb = markdown_field(session_state, "active_mission_block")
        runtime_ref = markdown_field(session_state, "runtime_state_ref")
        if active_fb and active_fb.lower() != "none" and not function_block_path(project_root, active_fb).is_file():
            blocking_items.append(f"active function block missing: {active_fb}")
            checks.append({"name": "active_function_block", "status": "fail", "detail": active_fb})
        if active_mb and active_mb.lower() != "none" and not mission_markdown_path(project_root, active_mb).is_file():
            blocking_items.append(f"active mission block missing: {active_mb}")
            checks.append({"name": "active_mission_block", "status": "fail", "detail": active_mb})
        if runtime_ref and runtime_ref.lower() != "none":
            runtime_state = normalize_relpath(project_root, runtime_ref)
            if not runtime_state.is_file():
                blocking_items.append(f"runtime state missing: {runtime_ref}")
                checks.append({"name": "runtime_state_ref", "status": "fail", "detail": runtime_ref})

    if blocking_items:
        result = "blocked"
        summary = "Project has blocking state mismatches."
    elif missing_items:
        result = "bootstrap_required"
        summary = "Project is missing required bootstrap files."
    else:
        result = "ready"
        summary = "Project session preflight passed."

    return finalize_result(
        build_result("session", project_root, None, result, summary, missing_items, blocking_items, checks),
        session_preflight_path(project_root),
    )


def mb_preflight(project_root: Path, mb_id: str) -> tuple[dict[str, object], list[str]]:
    initialize_runtime_memory(project_root)
    checks: list[dict[str, str]] = []
    missing_items: list[str] = []
    blocking_items: list[str] = []
    autonomy_decision: str | None = None

    policy_path = execution_policy_path()
    policy_errors = execution_policy_errors(policy_path)
    if policy_errors:
        blocking_items.extend(policy_errors)
        checks.append({"name": "execution_policy", "status": "fail", "detail": "; ".join(policy_errors)})
    else:
        checks.append({"name": "execution_policy", "status": "pass", "detail": str(policy_path)})

    mission_md = mission_markdown_path(project_root, mb_id)
    spec_path = mission_machine_spec_path(project_root, mb_id)
    if mission_md.is_file():
        checks.append({"name": "mission_markdown", "status": "pass", "detail": str(mission_md.relative_to(project_root))})
        mission_errors = runtime_mission_contract_errors(project_root, mission_md, mb_id)
        if mission_errors:
            blocking_items.extend([f"mission markdown invalid: {err}" for err in mission_errors])
            checks.append({"name": "mission_markdown_contract", "status": "fail", "detail": "; ".join(mission_errors)})
        else:
            checks.append({"name": "mission_markdown_contract", "status": "pass", "detail": "valid"})
    else:
        blocking_items.append(f"mission markdown missing: {mission_md.name}")
        checks.append({"name": "mission_markdown", "status": "fail", "detail": mission_md.name})

    spec_data = None
    if spec_path.is_file():
        checks.append({"name": "machine_spec", "status": "pass", "detail": str(spec_path.relative_to(project_root))})
        try:
            spec_data = read_json(spec_path)
            schema_errors = validate_with_schema(spec_data, "mb_machine_spec.schema.json")
            if schema_errors:
                blocking_items.extend([f"machine spec invalid: {err}" for err in schema_errors])
                checks.append({"name": "machine_spec_schema", "status": "fail", "detail": "; ".join(schema_errors)})
            else:
                checks.append({"name": "machine_spec_schema", "status": "pass", "detail": "valid"})
        except Exception as exc:  # noqa: BLE001
            blocking_items.append(f"machine spec unreadable: {exc}")
            checks.append({"name": "machine_spec_schema", "status": "fail", "detail": str(exc)})
    else:
        blocking_items.append(f"machine spec missing: {spec_path.name}")
        checks.append({"name": "machine_spec", "status": "fail", "detail": spec_path.name})

    if spec_data:
        if spec_data.get("mb_id") != mb_id:
            blocking_items.append(f"machine spec mb_id mismatch: {spec_data.get('mb_id')}")
        parent_fb_id = spec_data.get("parent_fb_id")
        parent_fb_path = function_block_path(project_root, parent_fb_id)
        if not parent_fb_path.is_file():
            blocking_items.append(f"parent function block missing: {parent_fb_id}")
            checks.append({"name": "parent_fb", "status": "fail", "detail": str(parent_fb_id)})
        else:
            checks.append({"name": "parent_fb", "status": "pass", "detail": str(parent_fb_id)})

        for rel_path in spec_data.get("context_files", []):
            record_declared_path_check(
                project_root,
                rel_path,
                "context_file",
                checks,
                blocking_items,
                must_exist=True,
            )

        for rel_path in spec_data.get("input_artifacts", []):
            record_declared_path_check(
                project_root,
                rel_path,
                "input_artifact",
                checks,
                blocking_items,
                must_exist=True,
            )

        for rel_path in spec_data.get("eval_refs", []):
            record_declared_path_check(
                project_root,
                rel_path,
                "eval_asset",
                checks,
                blocking_items,
                must_exist=True,
            )

        for field_name in ("allowed_touch", "forbidden_touch"):
            for rel_path in spec_data.get(field_name, []):
                record_declared_path_check(
                    project_root,
                    rel_path,
                    field_name,
                    checks,
                    blocking_items,
                    must_exist=False,
                )

        concurrency = spec_data.get("concurrency") or {}
        for field_name in ("exclusive_touch", "shared_read_artifacts", "shared_write_artifacts"):
            for rel_path in concurrency.get(field_name, []):
                record_declared_path_check(
                    project_root,
                    rel_path,
                    field_name,
                    checks,
                    blocking_items,
                    must_exist=False,
                )

        for item in spec_data.get("acceptance", []):
            if item.get("type") in {"file_exists", "json_field"}:
                record_declared_path_check(
                    project_root,
                    item["path"],
                    f"acceptance_{item['type']}_path",
                    checks,
                    blocking_items,
                    must_exist=False,
                )
        if not spec_data.get("acceptance") and not spec_data.get("eval_refs"):
            blocking_items.append("mission has no acceptance or eval refs")
            checks.append({"name": "verification_inputs", "status": "fail", "detail": "at least one acceptance or eval ref is required"})

        autonomy_level = spec_data.get("autonomy_level", "L2_auto_with_review")
        checks.append({"name": "autonomy_level", "status": "pass", "detail": autonomy_level})
        if autonomy_level == "L1_human_approval":
            autonomy_decision = "human_approval_required_before_execution"
        elif autonomy_level == "L2_auto_with_review":
            autonomy_decision = "auto_execute_then_review"
        else:
            autonomy_decision = "full_auto_allowed"

        state_path = runtime_state_path(project_root, mb_id)
        if state_path.exists():
            state_data = read_json(state_path)
            state_errors = validate_with_schema(state_data, "mb_state.schema.json")
            if state_errors:
                blocking_items.extend([f"runtime state invalid: {err}" for err in state_errors])
                checks.append({"name": "runtime_state_schema", "status": "fail", "detail": "; ".join(state_errors)})
            else:
                checks.append({"name": "runtime_state_schema", "status": "pass", "detail": str(state_path.relative_to(project_root))})
                retry_limit = int(spec_data["retry_policy"]["max_retries"])
                if int(state_data.get("retry_count", 0)) >= retry_limit and state_data.get("status") in {"failed", "blocked", "routed_to_recovery"}:
                    blocking_items.append(f"retry limit reached for {mb_id}")
                    checks.append({"name": "retry_limit", "status": "fail", "detail": f"{state_data.get('retry_count')} >= {retry_limit}"})
                else:
                    checks.append({"name": "retry_limit", "status": "pass", "detail": f"< {retry_limit}"})
                if autonomy_level == "L1_human_approval":
                    approval_status = state_data.get("approval_status", "pending")
                    checks.append(
                        {
                            "name": "approval_status",
                            "status": "warn" if approval_status != "approved" else "pass",
                            "detail": approval_status,
                        }
                    )
        else:
            missing_items.append(f"runtime/state/{mb_id}.state.json")
            checks.append({"name": "runtime_state_schema", "status": "warn", "detail": "state file will be initialized on first run"})

    result = "blocked" if blocking_items else "ready"
    summary = "MB preflight passed." if result == "ready" else "MB preflight found blocking issues."
    return finalize_result(
        build_result("mb", project_root, mb_id, result, summary, missing_items, blocking_items, checks, autonomy_decision),
        mb_preflight_path(project_root, mb_id),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run session or MB harness preflight.")
    parser.add_argument("--level", choices=["session", "mb"], required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)

    if args.level == "session":
        result, errors = session_preflight(project_root)
    else:
        if not args.mb_id:
            parser.error("--mb-id is required for --level mb")
        result, errors = mb_preflight(project_root, args.mb_id)

    if errors:
        return print_validation_result("preflight result schema", errors)

    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
