#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from harness_common import (
    failure_log_path,
    function_block_path,
    markdown_field,
    project_memory_path,
    read_json,
    resolve_path,
    runtime_state_path,
    local_timestamp,
    local_timezone_name,
    validate_with_schema,
    write_json,
)
from memory_bridge import sync_quality_memory


def normalize_failure_key(failure_type: str, condition: str) -> str:
    prefix = condition.strip().lower().replace("\n", " ")[:80]
    return f"{failure_type}:{prefix}"


def default_state(mb_id: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "mb_id": mb_id,
        "status": "ready",
        "retry_count": 0,
        "last_attempt_id": None,
        "last_verification_report_path": None,
        "last_verification_digest": None,
        "last_failure_reason": None,
        "last_failure_issue_type": None,
        "autonomy_level": "L2_auto_with_review",
        "approval_status": "not_required",
        "review_required": False,
        "next_action": "run",
        "provider_attempt_counts": {"codex": 0, "minimax": 0},
        "provider_failure_counts": {"codex": 0, "minimax": 0},
        "last_execution_provider": None,
        "updated_at": local_timestamp(),
        "timezone_name": local_timezone_name(),
    }


def load_state(project_root: Path, mb_id: str) -> dict[str, Any]:
    path = runtime_state_path(project_root, mb_id)
    if not path.exists():
        return default_state(mb_id)
    loaded = read_json(path)
    state = default_state(mb_id)
    state.update(loaded)
    return state


def write_state(project_root: Path, state: dict[str, Any]) -> Path:
    state["updated_at"] = local_timestamp()
    state["timezone_name"] = local_timezone_name()
    errors = validate_with_schema(state, "mb_state.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    path = runtime_state_path(project_root, state["mb_id"])
    write_json(path, state)
    return path


def sync_session_state(project_root: Path, parent_fb_id: str, state: dict[str, Any]) -> None:
    session_state_path = project_root / "SESSION_STATE.md"
    current_text_exists = session_state_path.exists()
    project = markdown_field(session_state_path, "project") if current_text_exists else project_root.name
    mode = markdown_field(session_state_path, "mode") if current_text_exists else "continue"
    stage = markdown_field(session_state_path, "stage") if current_text_exists else "SCENE_WORK"
    assumptions = markdown_field(session_state_path, "assumptions_still_active") if current_text_exists else "none"
    risks = markdown_field(session_state_path, "risks_to_watch") if current_text_exists else "none"

    content = f"""# Session State

## Current Context

- `project`: {project or project_root.name}
- `mode`: {mode or "continue"}
- `stage`: {stage or "SCENE_WORK"}
- `active_function_block`: {parent_fb_id}
- `active_mission_block`: {state["mb_id"]}

## Latest Status

- `completed`: {"latest attempt passed" if state["status"] == "passed" else "none"}
- `failed`: {state["last_failure_reason"] or "none"}
- `blocked_by`: {state["last_failure_reason"] or "none"}
- `autonomy_level`: {state["autonomy_level"]}
- `approval_status`: {state["approval_status"]}
- `review_required`: {"yes" if state["review_required"] else "no"}
- `last_execution_provider`: {state["last_execution_provider"] or "none"}
- `runtime_state_ref`: runtime/state/{state["mb_id"]}.state.json
- `last_attempt_id`: {state["last_attempt_id"] or "none"}
- `last_verification_report_path`: {state["last_verification_report_path"] or "none"}

## Required Reads

- artifact 1: missions/{state["mb_id"]}.md
- artifact 2: missions/{state["mb_id"]}.machine.json
- artifact 3: runtime/state/{state["mb_id"]}.state.json

## Next Single Action

- `action`: {state["next_action"]}

## Notes For The Next Session

- `assumptions_still_active`: {assumptions or "none"}
- `risks_to_watch`: {risks or "none"}
"""
    session_state_path.write_text(content, encoding="utf-8")


def append_project_memory(project_root: Path, parent_fb_id: str, mb_id: str, report: dict[str, Any]) -> None:
    path = project_memory_path(project_root)
    data = read_json(path)
    existing = [entry for entry in data["completed_mbs"] if entry["mb_id"] == mb_id]
    if existing:
        return
    recorded_at = local_timestamp()
    timezone_name = local_timezone_name()
    data["completed_mbs"].append(
        {
            "mb_id": mb_id,
            "parent_fb_id": parent_fb_id,
            "result": "passed",
            "validated_evidence": [report["summary"]],
            "key_decisions": [f"{mb_id} passed with machine verification."],
            "reusable_notes": [f"Prefer the verified repair path from {mb_id} when a similar MB appears."],
            "tags": [parent_fb_id, mb_id, "machine_verified"],
            "pattern_type": "validated_good_pattern",
            "applicability": {
                "mb_ids": [mb_id],
                "parent_fb_ids": [parent_fb_id],
                "notes": "Use when a similar mission re-enters the same bounded implementation pattern.",
            },
            "recorded_at": recorded_at,
            "timezone_name": timezone_name,
        }
    )
    errors = validate_with_schema(data, "project-memory.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    write_json(path, data)
    sync_quality_memory(project_root)


def append_failure_log(project_root: Path, entry: dict[str, Any]) -> None:
    path = failure_log_path(project_root)
    data = read_json(path)
    entry.setdefault("parent_fb_id", "unknown")
    entry.setdefault("root_cause_guess", entry["failure_type"])
    entry.setdefault("repeated_failure_key", normalize_failure_key(entry["failure_type"], entry["condition"]))
    entry.setdefault("tags", [entry["parent_fb_id"], entry["mb_id"], entry["failure_type"]])
    entry.setdefault("recorded_at", local_timestamp())
    entry.setdefault("timezone_name", local_timezone_name())
    data["failures"].append(entry)
    errors = validate_with_schema(data, "failure-log.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    write_json(path, data)
    sync_quality_memory(project_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or write one MB state file.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--status", default="ready")
    parser.add_argument("--next-action", default="run")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    state = default_state(args.mb_id)
    state["status"] = args.status
    state["next_action"] = args.next_action
    write_state(project_root, state)
    print(runtime_state_path(project_root, args.mb_id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
