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
    "schemas/quality-report.schema.json",
    "templates/API_CONTRACT.template.md",
    "templates/CONSTITUTION.template.md",
    "templates/DATA_MODEL.template.md",
    "templates/DECISIONS.template.md",
    "templates/FUNCTION_BLOCK.template.md",
    "templates/MISSION_BLOCK.template.md",
    "templates/PREFLIGHT_RESULT.template.md",
    "templates/QUALITY_MEMORY.template.md",
    "templates/QUALITY_REPORT.template.json",
    "templates/QUALITY_RULEBOOK.template.md",
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
    "QUALITY_RULEBOOK.md": [
        "# Quality Rulebook",
        "## Purpose",
        "## Profiles",
        "## Check Catalog",
        "## Waiver Rule",
    ],
    "QUALITY_MEMORY.md": [
        "# Quality Memory",
        "## Purpose",
        "## Stable Rules",
        "## Repeated Failure Patterns",
        "## Validated Good Patterns",
        "## High-Risk Areas",
        "## Recent Lessons",
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
    "active_function_block",
    "active_mission_block",
    "completed",
    "failed",
    "blocked_by",
    "action",
]

FUNCTION_FIELDS = [
    "fb_id",
    "title",
    "status",
    "business_objective",
    "user_value",
    "success_definition",
    "actor_status",
    "actor_description",
    "goal_status",
    "goal_description",
    "entity_status",
    "entity_description",
    "relation_status",
    "relation_description",
    "state_status",
    "state_description",
    "event_status",
    "event_description",
    "rule_status",
    "rule_description",
    "evidence_status",
    "evidence_description",
    "business_layer",
    "domain_layer",
    "flow_layer",
    "experience_layer",
    "application_layer",
    "service_layer",
    "data_layer",
    "quality_layer",
    "in_scope",
    "out_of_scope",
    "dependencies",
    "related_artifacts",
    "overall_risk",
    "quality_rulebook",
    "special_quality_concerns",
    "acceptance_criteria",
    "release_blockers",
    "planned_mbs",
    "completed_mbs",
    "failed_mbs",
    "open_questions",
    "next_recommended_mb",
]

MISSION_FIELDS = [
    "mb_id",
    "parent_fb_id",
    "status",
    "change_type",
    "parent_fb_ontology_ref",
    "acceptance_slice",
    "ontology_elements_in_scope",
    "affected_layers_in_scope",
    "deferred_ontology_elements",
    "deferred_layers",
    "alignment_notes",
    "goal",
    "hypothesis",
    "allowed_files",
    "forbidden_files",
    "change_budget",
    "risk_level",
    "user_visible_before",
    "checks_before",
    "known_problem_before",
    "artifact_state_before",
    "quality_profile",
    "selected_quality_checks",
    "waived_checks",
    "required_commands",
    "regression_rule",
    "pass_condition",
    "required_test_evidence",
    "required_artifact_updates",
    "required_quality_report",
    "checkpoint",
    "safe_revert_path",
    "changed_files",
    "outcome",
    "next_action",
]

REVIEW_ALLOWED_RISK = {"low", "medium", "high", "critical"}
QUALITY_ALLOWED_PROFILE = {"standard", "strict"}
QUALITY_ALLOWED_RESULT = {"pass", "fail", "rework_required"}
QUALITY_ALLOWED_STATUS = {"pass", "fail", "waived", "not_applicable"}
ONTOLOGY_ALLOWED_STATUS = {"confirmed", "assumed", "risk", "out_of_scope"}
SUPPORTED_SCENES = {"greenfield", "expansion", "continue", "review", "recovery"}


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


def find_markdown_value(path: Path, field: str, errors: list[str], base: Path) -> Optional[str]:
    text = read_text(path)
    match = re.search(rf"^- `{re.escape(field)}`:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        fail(f"{display_path(path, base)} missing {field} value", errors)
        return None
    value = match.group(1).strip()
    if not value:
        fail(f"{display_path(path, base)} has empty {field} value", errors)
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
        active_function = find_markdown_value(session_state, "active_function_block", errors, project_root)
        active_mission = find_markdown_value(session_state, "active_mission_block", errors, project_root)
        if active_function and active_function.lower() != "none":
            function_matches = sorted((project_root / "function_blocks").glob(f"{active_function}*.md"))
            if not function_matches:
                fail(
                    "SESSION_STATE.md points to an active function block that does not exist",
                    errors,
                )
        if active_mission and active_mission.lower() != "none":
            mission_matches = sorted((project_root / "missions").glob(f"{active_mission}*.md"))
            if not mission_matches:
                fail(
                    "SESSION_STATE.md points to an active mission block that does not exist",
                    errors,
                )

    function_dir = project_root / "function_blocks"
    if not function_dir.is_dir():
        fail(f"missing directory: {display_path(function_dir, project_root)}", errors)

    mission_dir = project_root / "missions"
    if not mission_dir.is_dir():
        fail(f"missing directory: {display_path(mission_dir, project_root)}", errors)

    review_dir = project_root / "reviews"
    if not review_dir.is_dir():
        fail(f"missing directory: {display_path(review_dir, project_root)}", errors)

    return errors


def evaluate_preflight(project_root: Path, scene: str) -> tuple[str, list[str], list[str], list[str], list[str], bool]:
    checked_items: list[str] = []
    missing_items: list[str] = []
    auto_actions: list[str] = []
    blocking_items: list[str] = []

    if not project_root.exists():
        blocking_items.append("project root does not exist")
        return "blocked", checked_items, missing_items, auto_actions, blocking_items, False
    if not project_root.is_dir():
        blocking_items.append("project root is not a directory")
        return "blocked", checked_items, missing_items, auto_actions, blocking_items, False

    foundational_files = [
        "CONSTITUTION.md",
        "SCOPE.md",
        "DECISIONS.md",
        "QUALITY_RULEBOOK.md",
        "QUALITY_MEMORY.md",
        "SESSION_STATE.md",
    ]
    foundational_dirs = [
        "function_blocks",
        "missions",
        "reviews",
    ]

    existing_files = {name for name in foundational_files if (project_root / name).is_file()}
    existing_dirs = {name for name in foundational_dirs if (project_root / name).is_dir()}

    for name in foundational_files + foundational_dirs:
        checked_items.append(name)
        path = project_root / name
        if name in foundational_files and not path.is_file():
            missing_items.append(name)
        if name in foundational_dirs and not path.is_dir():
            missing_items.append(name)

    if scene == "greenfield":
        for name in missing_items:
            auto_actions.append(f"initialize {name}")
        result = "ready" if not missing_items else "bootstrap_required"
        return result, checked_items, missing_items, auto_actions, blocking_items, True

    business_files = {"CONSTITUTION.md", "SCOPE.md", "DECISIONS.md"}
    quality_files = {"QUALITY_RULEBOOK.md", "QUALITY_MEMORY.md", "SESSION_STATE.md"}
    quality_dirs = {"function_blocks", "missions", "reviews"}

    if scene == "expansion":
        for name in sorted(business_files - existing_files):
            blocking_items.append(f"missing {name}")
        for name in sorted((quality_files - existing_files) | (quality_dirs - existing_dirs)):
            auto_actions.append(f"initialize {name}")
        if blocking_items:
            return "blocked", checked_items, missing_items, auto_actions, blocking_items, False
        if auto_actions:
            return "bootstrap_required", checked_items, missing_items, auto_actions, blocking_items, True
        return "ready", checked_items, missing_items, auto_actions, blocking_items, True

    if scene == "continue":
        session_state = project_root / "SESSION_STATE.md"
        if not session_state.is_file():
            blocking_items.append("missing SESSION_STATE.md")
        else:
            state_errors: list[str] = []
            active_function = find_markdown_value(session_state, "active_function_block", state_errors, project_root)
            active_mission = find_markdown_value(session_state, "active_mission_block", state_errors, project_root)
            if active_function and active_function.lower() != "none":
                if not sorted((project_root / "function_blocks").glob(f"{active_function}*.md")):
                    blocking_items.append("active_function_block points to a missing function block")
            else:
                blocking_items.append("missing active function block reference")
            if active_mission and active_mission.lower() != "none":
                if not sorted((project_root / "missions").glob(f"{active_mission}*.md")):
                    blocking_items.append("active_mission_block points to a missing mission block")
            else:
                blocking_items.append("missing active mission block reference")
        for name in sorted(({"QUALITY_RULEBOOK.md", "QUALITY_MEMORY.md"} - existing_files) | ({"reviews"} - existing_dirs)):
            auto_actions.append(f"initialize {name}")
        if blocking_items:
            return "blocked", checked_items, missing_items, auto_actions, blocking_items, False
        if auto_actions:
            return "bootstrap_required", checked_items, missing_items, auto_actions, blocking_items, True
        return "ready", checked_items, missing_items, auto_actions, blocking_items, True

    if scene == "review":
        for name in sorted({"CONSTITUTION.md", "SCOPE.md"} - existing_files):
            blocking_items.append(f"missing {name}")
        if "function_blocks" not in existing_dirs:
            blocking_items.append("missing function_blocks directory")
        if "missions" not in existing_dirs:
            blocking_items.append("missing missions directory")
        for name in sorted(({"QUALITY_RULEBOOK.md", "QUALITY_MEMORY.md", "SESSION_STATE.md"} - existing_files) | ({"reviews"} - existing_dirs)):
            auto_actions.append(f"initialize {name}")
        if blocking_items:
            return "blocked", checked_items, missing_items, auto_actions, blocking_items, False
        if auto_actions:
            return "bootstrap_required", checked_items, missing_items, auto_actions, blocking_items, True
        return "ready", checked_items, missing_items, auto_actions, blocking_items, True

    if scene == "recovery":
        if not (project_root / "SESSION_STATE.md").is_file() and not (project_root / "VERSION_LOG.md").is_file():
            blocking_items.append("missing both SESSION_STATE.md and VERSION_LOG.md")
        for name in sorted(({"QUALITY_RULEBOOK.md", "QUALITY_MEMORY.md"} - existing_files) | (quality_dirs - existing_dirs)):
            auto_actions.append(f"initialize {name}")
        if blocking_items:
            return "blocked", checked_items, missing_items, auto_actions, blocking_items, False
        if auto_actions:
            return "bootstrap_required", checked_items, missing_items, auto_actions, blocking_items, True
        return "ready", checked_items, missing_items, auto_actions, blocking_items, True

    blocking_items.append(f"unsupported scene: {scene}")
    return "blocked", checked_items, missing_items, auto_actions, blocking_items, False


def validate_function(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing function block file: {path}", errors)
        return errors

    require_headings(
        path,
        [
            "# Function Block",
            "## Metadata",
            "## Product Goal",
            "## Ontology Frame",
            "## Impact Map",
            "## Scope",
            "## Quality Context",
            "## Acceptance",
            "## Mission Plan",
            "## Notes",
            "## Usage Rules",
        ],
        errors,
        project_root,
    )
    require_markdown_fields(path, FUNCTION_FIELDS, errors, project_root)
    for field in [
        "actor_status",
        "goal_status",
        "entity_status",
        "relation_status",
        "state_status",
        "event_status",
        "rule_status",
        "evidence_status",
    ]:
        value = find_markdown_value(path, field, errors, project_root or PROTOCOL_ROOT)
        if value is not None and value not in ONTOLOGY_ALLOWED_STATUS:
            fail(
                f"{display_path(path, project_root)} has invalid {field}: {value}",
                errors,
            )
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
            "## Parent FB Alignment",
            "## Boundaries",
            "## Goal",
            "## Baseline",
            "## Quality Plan",
            "## Evidence Required",
            "## Rollback",
            "## Result",
            "## Usage Rules",
        ],
        errors,
        project_root,
    )
    require_markdown_fields(path, MISSION_FIELDS, errors, project_root)
    return errors


def validate_quality_report(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing quality report file: {path}", errors)
        return errors

    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{display_path(path, project_root)} is not valid JSON: {exc}", errors)
        return errors

    required_top_level = {
        "fb_id": str,
        "mb_id": str,
        "quality_profile": str,
        "result": str,
        "risk_level": str,
        "baseline_summary": str,
        "changed_files": list,
        "scope_respected": bool,
        "checks": dict,
        "regression_found": bool,
        "open_risks": list,
        "lessons": list,
        "required_actions": list,
        "manual_review_required": bool,
    }
    for key, expected_type in required_top_level.items():
        if key not in data:
            fail(f"{display_path(path, project_root)} missing key: {key}", errors)
            continue
        if not isinstance(data[key], expected_type):
            fail(f"{display_path(path, project_root)} has invalid type for key: {key}", errors)

    if "quality_profile" in data and data["quality_profile"] not in QUALITY_ALLOWED_PROFILE:
        fail(f"{display_path(path, project_root)} has invalid quality_profile", errors)

    if "result" in data and data["result"] not in QUALITY_ALLOWED_RESULT:
        fail(f"{display_path(path, project_root)} has invalid result", errors)

    if "risk_level" in data and data["risk_level"] not in REVIEW_ALLOWED_RISK:
        fail(f"{display_path(path, project_root)} has invalid risk_level", errors)

    for field in ["fb_id", "mb_id", "baseline_summary"]:
        if isinstance(data.get(field), str) and not data[field].strip():
            fail(f"{display_path(path, project_root)} has empty {field}", errors)

    checks = data.get("checks")
    if isinstance(checks, dict):
        if not checks:
            fail(f"{display_path(path, project_root)} checks must not be empty", errors)
        for key, check in checks.items():
            prefix = f"{display_path(path, project_root)} checks.{key}"
            if not isinstance(check, dict):
                fail(f"{prefix} must be an object", errors)
                continue
            for required_key, expected_type in {
                "required": bool,
                "status": str,
                "evidence": str,
                "note": str,
            }.items():
                if required_key not in check:
                    fail(f"{prefix} missing key: {required_key}", errors)
                elif not isinstance(check[required_key], expected_type):
                    fail(f"{prefix} has invalid type for {required_key}", errors)
            if isinstance(check.get("status"), str) and check["status"] not in QUALITY_ALLOWED_STATUS:
                fail(f"{prefix} has invalid status", errors)

    for list_key in ["changed_files", "open_risks", "lessons", "required_actions"]:
        values = data.get(list_key)
        if isinstance(values, list):
            for index, value in enumerate(values):
                if not isinstance(value, str) or not value.strip():
                    fail(f"{display_path(path, project_root)} {list_key}[{index}] must be a non-empty string", errors)

    return errors


def print_result(errors: list[str], label: str) -> int:
    if errors:
        print(f"FAIL: {label}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {label}")
    return 0


def print_preflight(scene: str, project_root: Path) -> int:
    normalized_scene = scene.strip().lower()
    if normalized_scene not in SUPPORTED_SCENES:
        print(f"BLOCKED: unsupported scene '{scene}'")
        return 1

    result, checked_items, missing_items, auto_actions, blocking_items, can_enter_scene = evaluate_preflight(
        project_root, normalized_scene
    )
    print(f"PREFLIGHT: {result}")
    print(f"- scene: {normalized_scene}")
    print(f"- project_root: {project_root}")
    print(f"- can_enter_scene: {'true' if can_enter_scene else 'false'}")
    print(f"- checked_items: {', '.join(checked_items) if checked_items else 'none'}")
    print(f"- missing_items: {', '.join(missing_items) if missing_items else 'none'}")
    print(f"- auto_actions: {', '.join(auto_actions) if auto_actions else 'none'}")
    print(f"- blocking_items: {', '.join(blocking_items) if blocking_items else 'none'}")
    return 0 if result in {"ready", "bootstrap_required"} else 1


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

    preflight_parser = subparsers.add_parser(
        "check-preflight",
        help="Run project preflight for one scene and classify readiness.",
    )
    preflight_parser.add_argument("project_root", help="Path to the external project root.")
    preflight_parser.add_argument("scene", help="Scene to evaluate.")

    function_parser = subparsers.add_parser("check-function", help="Validate one function block.")
    function_parser.add_argument("path", help="Path to the function block Markdown file.")

    mission_parser = subparsers.add_parser("check-mission", help="Validate one mission block.")
    mission_parser.add_argument("path", help="Path to the mission block Markdown file.")

    quality_parser = subparsers.add_parser("check-quality-report", help="Validate one quality report JSON file.")
    quality_parser.add_argument("path", help="Path to the quality report JSON file.")

    review_parser = subparsers.add_parser("check-review", help="Validate one quality report JSON file.")
    review_parser.add_argument("path", help="Path to the quality report JSON file.")

    all_parser = subparsers.add_parser("check-all", help="Validate protocol files and one external project root.")
    all_parser.add_argument("project_root", nargs="?", help="Optional path to the external project root.")

    args = parser.parse_args()

    if args.command == "check-protocol":
        return print_result(validate_protocol(PROTOCOL_ROOT), "protocol repository")

    if args.command == "check-project":
        project_root = resolve_path(args.project_root)
        return print_result(validate_project(project_root), f"project {project_root}")

    if args.command == "check-preflight":
        project_root = resolve_path(args.project_root)
        return print_preflight(args.scene, project_root)

    if args.command == "check-function":
        path = resolve_path(args.path)
        return print_result(validate_function(path, path.parent.parent), f"function block {path}")

    if args.command == "check-mission":
        path = resolve_path(args.path)
        return print_result(validate_mission(path, path.parent.parent), f"mission {path}")

    if args.command in {"check-quality-report", "check-review"}:
        path = resolve_path(args.path)
        return print_result(validate_quality_report(path, path.parent.parent), f"quality report {path}")

    if args.command == "check-all":
        errors = validate_protocol(PROTOCOL_ROOT)
        label = "protocol repository"
        if args.project_root:
            project_root = resolve_path(args.project_root)
            errors.extend(validate_project(project_root))
            function_dir = project_root / "function_blocks"
            if function_dir.is_dir():
                for function_path in sorted(function_dir.glob("*.md")):
                    errors.extend(validate_function(function_path, project_root))
            mission_dir = project_root / "missions"
            if mission_dir.is_dir():
                for mission_path in sorted(mission_dir.glob("*.md")):
                    errors.extend(validate_mission(mission_path, project_root))
            review_dir = project_root / "reviews"
            if review_dir.is_dir():
                for review_path in sorted(review_dir.glob("*.json")):
                    errors.extend(validate_quality_report(review_path, project_root))
            label = f"protocol repository and project {project_root}"
        return print_result(errors, label)

    return 1


if __name__ == "__main__":
    sys.exit(main())
