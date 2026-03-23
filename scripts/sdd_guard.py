#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_FILES = [
    "README.md",
    "docs/00-roadmap.md",
    "docs/01-principles.md",
    "docs/02-lifecycle.md",
    "docs/03-artifacts.md",
    "docs/04-mission-blocks.md",
    "docs/05-review-recovery.md",
    "docs/06-operating-playbook.md",
    "docs/07-repository-layout.md",
    "docs/08-session-bootstrap.md",
    "docs/SDD_MASTER_PROTOCOL_V4.md",
    "prompts/SPEC_ARCHITECT.system.md",
    "prompts/BUILDER.system.md",
    "prompts/REVIEWER.system.md",
    "schemas/audit-result.schema.json",
    "templates/API_CONTRACT.template.md",
    "templates/CONSTITUTION.template.md",
    "templates/DATA_MODEL.template.md",
    "templates/DECISIONS.template.md",
    "templates/MISSION_BLOCK.template.md",
    "templates/SCOPE.template.md",
    "templates/SESSION_STATE.template.md",
]

PROJECT_FILES = {
    "CONSTITUTION.md": [
        "# Project Constitution",
        "## Product Goal",
        "## Non-Negotiables",
        "## Current Architecture Direction",
        "## Quality Gates",
        "## Approval Rules",
    ],
    "SCOPE.md": [
        "# Scope",
        "## Product Surface",
        "## Version Target",
        "## Acceptance Definition",
        "## Out Of Scope",
    ],
    "DECISIONS.md": [
        "# Decisions",
        "## Decision Log",
    ],
    "SESSION_STATE.md": [
        "# Session State",
        "## Current Context",
        "## Latest Status",
        "## Required Reads",
        "## Next Single Action",
        "## Notes For The Next Session",
    ],
}

OPTIONAL_PROJECT_FILES = {
    "DATA_MODEL.md": [
        "# Data Model",
        "## Core Entities",
        "## Relationships",
        "## Persistence Rules",
    ],
    "API_CONTRACT.md": [
        "# API Contract",
        "## Endpoints",
        "## Error Rules",
        "## Contract Notes",
    ],
    "VERSION_LOG.md": [
        "# Version Log",
    ],
}

SESSION_STATE_FIELDS = [
    "project",
    "mode",
    "stage",
    "active_mission_block",
    "completed",
    "failed",
    "blocked_by",
    "action",
]

MISSION_FIELDS = [
    "id",
    "objective",
    "mode",
    "in_scope",
    "out_of_scope",
    "allowed_files",
    "forbidden_files",
    "change_budget",
    "dependencies",
    "required_artifacts",
    "constraints",
    "required_patterns",
    "commands",
    "tests",
    "review_conditions",
    "changed_files",
    "test_evidence",
    "open_risks",
    "checkpoint",
    "safe_revert_path",
]

REVIEW_ALLOWED_RISK = {"low", "medium", "high", "critical"}
REVIEW_ALLOWED_FINDING_TYPES = {
    "logic",
    "security",
    "scope",
    "evidence",
    "style",
    "performance",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def display_path(path: Path, base: Optional[Path] = None) -> str:
    if base is not None:
        try:
            return str(path.relative_to(base))
        except ValueError:
            pass
    try:
        return str(path.relative_to(PROTOCOL_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path, errors: list[str], base: Optional[Path] = None) -> None:
    if not path.is_file():
        fail(f"missing file: {display_path(path, base)}", errors)


def require_headings(path: Path, headings: list[str], errors: list[str], base: Optional[Path] = None) -> None:
    text = read_text(path)
    for heading in headings:
        if re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is None:
            fail(f"{display_path(path, base)} missing heading: {heading}", errors)


def require_markdown_fields(path: Path, fields: list[str], errors: list[str], base: Optional[Path] = None) -> None:
    text = read_text(path)
    for field in fields:
        pattern = rf"^- `{re.escape(field)}`:\s*(.+)$"
        match = re.search(pattern, text, re.MULTILINE)
        if match is None:
            fail(f"{display_path(path, base)} missing field: {field}", errors)
            continue
        if not match.group(1).strip():
            fail(f"{display_path(path, base)} has empty field: {field}", errors)


def find_active_mission(path: Path, errors: list[str], base: Path) -> Optional[str]:
    text = read_text(path)
    match = re.search(r"^- `active_mission_block`:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        fail(f"{display_path(path, base)} missing active_mission_block value", errors)
        return None
    value = match.group(1).strip()
    if not value:
        fail(f"{display_path(path, base)} has empty active_mission_block value", errors)
        return None
    return value


def validate_protocol(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in PROTOCOL_FILES:
        require_file(root / rel_path, errors, root)
    return errors


def validate_project(project_root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path, headings in PROJECT_FILES.items():
        path = project_root / rel_path
        require_file(path, errors, project_root)
        if path.is_file():
            require_headings(path, headings, errors, project_root)

    for rel_path, headings in OPTIONAL_PROJECT_FILES.items():
        path = project_root / rel_path
        if path.is_file():
            require_headings(path, headings, errors, project_root)

    session_state = project_root / "SESSION_STATE.md"
    if session_state.is_file():
        require_markdown_fields(session_state, SESSION_STATE_FIELDS, errors, project_root)
        active_mission = find_active_mission(session_state, errors, project_root)
        if active_mission and active_mission.lower() != "none":
            mission_matches = sorted((project_root / "missions").glob(f"{active_mission}*.md"))
            if not mission_matches:
                fail(
                    "SESSION_STATE.md points to an active mission block that does not exist",
                    errors,
                )

    mission_dir = project_root / "missions"
    if not mission_dir.is_dir():
        fail(f"missing directory: {display_path(mission_dir, project_root)}", errors)

    review_dir = project_root / "reviews"
    if not review_dir.is_dir():
        fail(f"missing directory: {display_path(review_dir, project_root)}", errors)

    return errors


def validate_mission(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing mission file: {path}", errors)
        return errors

    require_headings(
        path,
        [
            "# Mission Block",
            "## Metadata",
            "## Scope",
            "## Boundaries",
            "## Inputs",
            "## Implementation Notes",
            "## Acceptance Checks",
            "## Evidence Required",
            "## Rollback Notes",
        ],
        errors,
        project_root,
    )
    require_markdown_fields(path, MISSION_FIELDS, errors, project_root)
    return errors


def validate_review(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing review file: {path}", errors)
        return errors

    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{display_path(path, project_root)} is not valid JSON: {exc}", errors)
        return errors

    required_top_level = {
        "pass": bool,
        "risk_level": str,
        "summary": str,
        "checks": dict,
        "findings": list,
        "required_actions": list,
        "manual_review_required": bool,
    }
    for key, expected_type in required_top_level.items():
        if key not in data:
            fail(f"{display_path(path, project_root)} missing key: {key}", errors)
            continue
        if not isinstance(data[key], expected_type):
            fail(f"{display_path(path, project_root)} has invalid type for key: {key}", errors)

    if "risk_level" in data and data["risk_level"] not in REVIEW_ALLOWED_RISK:
        fail(f"{display_path(path, project_root)} has invalid risk_level", errors)

    if isinstance(data.get("summary"), str) and not data["summary"].strip():
        fail(f"{display_path(path, project_root)} has empty summary", errors)

    checks = data.get("checks")
    if isinstance(checks, dict):
        required_checks = [
            "contract_aligned",
            "scope_respected",
            "tests_verified",
            "artifact_drift",
        ]
        for key in required_checks:
            if key not in checks:
                fail(f"{display_path(path, project_root)} missing checks.{key}", errors)
            elif not isinstance(checks[key], bool):
                fail(f"{display_path(path, project_root)} has invalid type for checks.{key}", errors)

    findings = data.get("findings")
    if isinstance(findings, list):
        for index, finding in enumerate(findings):
            prefix = f"{display_path(path, project_root)} findings[{index}]"
            if not isinstance(finding, dict):
                fail(f"{prefix} must be an object", errors)
                continue
            for key in ["type", "severity", "file", "line", "description"]:
                if key not in finding:
                    fail(f"{prefix} missing key: {key}", errors)
            if "type" in finding and finding["type"] not in REVIEW_ALLOWED_FINDING_TYPES:
                fail(f"{prefix} has invalid type", errors)
            if "severity" in finding and finding["severity"] not in REVIEW_ALLOWED_RISK:
                fail(f"{prefix} has invalid severity", errors)
            if "line" in finding and (not isinstance(finding["line"], int) or finding["line"] < 1):
                fail(f"{prefix} has invalid line", errors)
            for text_key in ["file", "description"]:
                if text_key in finding and (
                    not isinstance(finding[text_key], str) or not finding[text_key].strip()
                ):
                    fail(f"{prefix} has empty {text_key}", errors)

    required_actions = data.get("required_actions")
    if isinstance(required_actions, list):
        for index, action in enumerate(required_actions):
            if not isinstance(action, str) or not action.strip():
                fail(f"{display_path(path, project_root)} required_actions[{index}] must be a non-empty string", errors)

    return errors


def print_result(errors: list[str], label: str) -> int:
    if errors:
        print(f"FAIL: {label}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {label}")
    return 0


def resolve_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the SDD protocol repository or an external project root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check-protocol", help="Validate protocol repository files.")

    project_parser = subparsers.add_parser("check-project", help="Validate an external project root.")
    project_parser.add_argument("project_root", help="Path to the external project root.")

    mission_parser = subparsers.add_parser("check-mission", help="Validate one mission block.")
    mission_parser.add_argument("path", help="Path to the mission block Markdown file.")

    review_parser = subparsers.add_parser("check-review", help="Validate one review JSON file.")
    review_parser.add_argument("path", help="Path to the review JSON file.")

    all_parser = subparsers.add_parser("check-all", help="Validate protocol files and one external project root.")
    all_parser.add_argument("project_root", nargs="?", help="Optional path to the external project root.")

    args = parser.parse_args()

    if args.command == "check-protocol":
        return print_result(validate_protocol(PROTOCOL_ROOT), "protocol repository")

    if args.command == "check-project":
        project_root = resolve_path(args.project_root)
        return print_result(validate_project(project_root), f"project {project_root}")

    if args.command == "check-mission":
        path = resolve_path(args.path)
        return print_result(validate_mission(path, path.parent.parent), f"mission {path}")

    if args.command == "check-review":
        path = resolve_path(args.path)
        return print_result(validate_review(path, path.parent.parent), f"review {path}")

    if args.command == "check-all":
        errors = validate_protocol(PROTOCOL_ROOT)
        label = "protocol repository"
        if args.project_root:
            project_root = resolve_path(args.project_root)
            errors.extend(validate_project(project_root))
            mission_dir = project_root / "missions"
            if mission_dir.is_dir():
                for mission_path in sorted(mission_dir.glob("*.md")):
                    errors.extend(validate_mission(mission_path, project_root))
            review_dir = project_root / "reviews"
            if review_dir.is_dir():
                for review_path in sorted(review_dir.glob("*.json")):
                    errors.extend(validate_review(review_path, project_root))
            label = f"protocol repository and project {project_root}"
        return print_result(errors, label)

    return 1


if __name__ == "__main__":
    sys.exit(main())
