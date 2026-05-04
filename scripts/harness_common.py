#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent
EXECUTION_POLICY_ENV = "AIPD_EXECUTION_POLICY_PATH"
REQUIRED_PROJECT_FILES = [
    "CONSTITUTION.md",
    "SCOPE.md",
    "DECISIONS.md",
    "SESSION_STATE.md",
    "QUALITY_RULEBOOK.md",
    "QUALITY_MEMORY.md",
]


def resolve_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False,
            suffix=".tmp",
        ) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, ensure_ascii=True, indent=2) + "\n")


def local_timestamp() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def local_timezone_name() -> str:
    return datetime.now().astimezone().tzinfo.key if hasattr(datetime.now().astimezone().tzinfo, "key") else datetime.now().astimezone().tzname() or "local"


def load_schema(name: str) -> dict[str, Any]:
    return read_json(PROTOCOL_ROOT / "schemas" / name)


def validate_with_schema(instance: Any, schema_name: str) -> list[str]:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    return [format_error(err) for err in validator.iter_errors(instance)]


def format_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    if path:
        return f"{path}: {error.message}"
    return error.message


def print_validation_result(label: str, errors: list[str]) -> int:
    if errors:
        print(f"FAIL: {label}")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"PASS: {label}")
    return 0


def mission_markdown_path(project_root: Path, mb_id: str) -> Path:
    return project_root / "missions" / f"{mb_id}.md"


def mission_machine_spec_path(project_root: Path, mb_id: str) -> Path:
    return project_root / "missions" / f"{mb_id}.machine.json"


def function_block_path(project_root: Path, fb_id: str) -> Path:
    return project_root / "function_blocks" / f"{fb_id}.md"


def quality_memory_path(project_root: Path) -> Path:
    return project_root / "QUALITY_MEMORY.md"


def evals_dir(project_root: Path) -> Path:
    return project_root / "evals"


def eval_asset_path(project_root: Path, raw_ref: str) -> Path:
    return normalize_relpath(project_root, raw_ref)


def execution_policy_path() -> Path:
    override = os.environ.get(EXECUTION_POLICY_ENV)
    if override:
        return resolve_path(override)
    return PROTOCOL_ROOT / "config" / "execution_policy.json"


def execution_policy_errors(path: Path | None = None) -> list[str]:
    target = path or execution_policy_path()
    if not target.is_file():
        return [f"missing execution policy: {target}"]
    try:
        payload = read_json(target)
    except Exception as exc:  # noqa: BLE001
        return [f"execution policy unreadable: {exc}"]
    schema_errors = validate_with_schema(payload, "execution-policy.schema.json")
    if schema_errors:
        return [f"execution policy invalid: {error}" for error in schema_errors]
    return []


def load_execution_policy(path: Path | None = None) -> dict[str, Any]:
    target = path or execution_policy_path()
    errors = execution_policy_errors(target)
    if errors:
        raise ValueError("; ".join(errors))
    return read_json(target)


def resolve_execution_policy(policy: dict[str, Any], mb_id: str | None, attempt_id: str | None) -> dict[str, Any]:
    resolved = deepcopy(policy)
    replacements = {
        "mb_id": mb_id or "{mb_id}",
        "attempt_id": attempt_id or "{attempt_id}",
    }
    for key in ("forbidden_path_prefixes", "protected_runtime_prefixes", "ignored_runtime_prefixes"):
        values = resolved.get(key, [])
        resolved[key] = [value.format(**replacements) for value in values]
    return resolved


def runtime_dir(project_root: Path) -> Path:
    return project_root / "runtime"


def runtime_state_path(project_root: Path, mb_id: str) -> Path:
    return runtime_dir(project_root) / "state" / f"{mb_id}.state.json"


def attempts_root(project_root: Path, mb_id: str) -> Path:
    return runtime_dir(project_root) / "attempts" / mb_id


def attempt_dir(project_root: Path, mb_id: str, attempt_id: str) -> Path:
    return attempts_root(project_root, mb_id) / attempt_id


def runtime_memory_dir(project_root: Path) -> Path:
    return runtime_dir(project_root) / "memory"


def project_memory_path(project_root: Path) -> Path:
    return runtime_memory_dir(project_root) / "project_memory.json"


def failure_log_path(project_root: Path) -> Path:
    return runtime_memory_dir(project_root) / "failure_log.json"


def preflight_dir(project_root: Path) -> Path:
    return runtime_dir(project_root) / "preflight"


def session_preflight_path(project_root: Path) -> Path:
    return preflight_dir(project_root) / "session_preflight.json"


def mb_preflight_path(project_root: Path, mb_id: str) -> Path:
    return preflight_dir(project_root) / f"mb_preflight_{mb_id}.json"


def markdown_field(path: Path, field: str) -> str | None:
    text = read_text(path)
    match = re.search(rf"^- `{re.escape(field)}`:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        return None
    value = match.group(1).strip()
    return value or None


def normalize_relpath(project_root: Path, raw: str) -> Path:
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        raise ValueError(f"path must be project-relative: {raw}")
    resolved = (project_root / candidate).resolve()
    root = project_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path must stay within project root: {raw}") from exc
    return resolved


def initialize_runtime_memory(project_root: Path) -> None:
    pm_path = project_memory_path(project_root)
    if not pm_path.exists():
        write_json(pm_path, {"schema_version": "1.0", "completed_mbs": []})
    fl_path = failure_log_path(project_root)
    if not fl_path.exists():
        write_json(fl_path, {"schema_version": "1.0", "failures": []})
