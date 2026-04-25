#!/usr/bin/env python3

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from jsonschema import Draft202012Validator


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_FILES = [
    "README.md",
    "docs/00_lifecycle.md",
    "docs/01_principles.md",
    "docs/02_artifacts.md",
    "docs/03_mission_blocks.md",
    "docs/04_review_recovery.md",
    "docs/05_operating_playbook.md",
    "docs/06_session_bootstrap.md",
    "docs/07_repository_layout.md",
    "docs/08_symphony_integration_plan.md",
    "docs/09_symphony_mb_adapter_contract.md",
    "docs/99_legacy_master_protocol_v4.md",
    "prompts/SPEC_ARCHITECT.system.md",
    "prompts/BUILDER.system.md",
    "prompts/REVIEWER.system.md",
    "schemas/aipd-gate-outcome.schema.json",
    "schemas/eval-asset.schema.json",
    "schemas/hook-event.schema.json",
    "schemas/quality-report.schema.json",
    "scripts/codex_exec_with_hooks.py",
    "scripts/hook_runtime.py",
    "scripts/memory_bridge.py",
    "scripts/post_tool_hook.py",
    "scripts/pre_tool_hook.py",
    "scripts/stop_hook.py",
    "templates/API_CONTRACT.template.md",
    "templates/CONSTITUTION.template.md",
    "templates/DATA_MODEL.template.md",
    "templates/DECISIONS.template.md",
    "templates/EXPERIENCE_PROMPT.template.md",
    "templates/FUNCTION_BLOCK.template.md",
    "templates/MISSION_BLOCK.template.md",
    "templates/PREFLIGHT_RESULT.template.md",
    "templates/QUALITY_MEMORY.template.md",
    "templates/QUALITY_REPORT.template.json",
    "templates/QUALITY_RULEBOOK.template.md",
    "templates/RESEARCH_NOTE.template.md",
    "templates/SCOPE.template.md",
    "templates/SESSION_STATE.template.md",
]

GATE_OUTCOME_EXAMPLE_FILES = [
    "schemas/examples/aipd-gate-outcome/start-pass.json",
    "schemas/examples/aipd-gate-outcome/start-reject.json",
    "schemas/examples/aipd-gate-outcome/finish-pass.json",
    "schemas/examples/aipd-gate-outcome/finish-retry.json",
    "schemas/examples/aipd-gate-outcome/finish-recovery.json",
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

FUNCTION_REQUIRED_HEADINGS = [
    "# Function Block",
    "## Metadata",
    "## Product Goal",
    "## Ontology Frame",
    "## Impact Map",
    "## Experience Delivery",
    "## Scope",
    "## Acceptance",
    "## Mission Plan",
    "## Usage Rules",
]

FUNCTION_CORE_FIELDS = [
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
    "experience_delivery_mode",
    "in_scope",
    "out_of_scope",
    "acceptance_criteria",
    "planned_mbs",
    "next_recommended_mb",
]

MISSION_REQUIRED_HEADINGS = [
    "# Mission Block",
    "## Metadata",
    "## Parent FB Alignment",
    "## Goal",
    "## Inputs",
    "## Boundaries",
    "## Quality Plan",
    "## Evidence Required",
    "## Result",
    "## Usage Rules",
]

MISSION_CORE_FIELDS = [
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
    "goal",
    "input_artifacts",
    "allowed_files",
    "quality_profile",
    "selected_quality_checks",
    "required_commands",
    "pass_condition",
    "required_test_evidence",
    "required_artifact_updates",
    "required_quality_report",
    "outcome",
    "next_action",
]

REVIEW_ALLOWED_RISK = {"low", "medium", "high", "critical"}
QUALITY_ALLOWED_PROFILE = {"standard", "strict"}
QUALITY_ALLOWED_RESULT = {"pass", "fail", "rework_required"}
QUALITY_ALLOWED_STATUS = {"pass", "fail", "waived", "not_applicable"}
ONTOLOGY_ALLOWED_STATUS = {"confirmed", "assumed", "risk", "out_of_scope"}
EXPERIENCE_ALLOWED_MODE = {"builder_generated", "external_ui_package", "hybrid", "not_applicable"}
SUPPORTED_SCENES = {"greenfield", "expansion", "continue", "review", "recovery"}
RESEARCH_ALLOWED_TRIGGER = {"user_triggered", "system_triggered"}
RESEARCH_ALLOWED_APPROVAL_REQUIRED = {"yes", "no"}
RESEARCH_ALLOWED_APPROVAL_STATUS = {"approved", "not_required"}
EXPERIENCE_PROMPT_ALLOWED_TOOL = {"figma", "stitch", "other"}
EXPERIENCE_PROMPT_ALLOWED_STATUS = {"draft", "approved_for_handoff", "superseded"}
EXPERIENCE_PROMPT_ALLOWED_GOAL = {"canonical_shell", "state_variant", "family_extension", "independent_screen"}
EXPERIENCE_PROMPT_ALLOWED_CONSISTENCY = {"same_family_strict", "same_family_adaptive", "not_applicable"}
EXPERIENCE_PROMPT_ALLOWED_PROFILE = {
    "stitch_first_pass",
    "stitch_iterative_refine",
    "figma_structured_handoff",
    "general_structured_handoff",
}
FLAG_ALLOWED_VALUES = {"yes", "no"}

PROTOCOL_REQUIRED_HEADINGS = {
    "docs/00_lifecycle.md": [
        "## Research Rule",
        "## External Tool Prompt And Intake Rule",
    ],
    "docs/02_artifacts.md": [
        "## Research Note Rule",
        "## Experience Prompt Rule",
    ],
    "docs/03_mission_blocks.md": [
        "## Research Support Rule",
        "## UI Reference And Prompt Rule",
    ],
    "docs/05_operating_playbook.md": [
        "## Research In Practice",
        "## UI Prompt Generation In Practice",
        "## Stitch Prompt Strategy In Practice",
    ],
    "templates/RESEARCH_NOTE.template.md": [
        "# Research Note",
        "## Metadata",
        "## Query",
        "## Findings",
        "## Candidate Options",
        "## Impact And Adoption",
        "## Approval",
        "## Usage Rules",
    ],
    "templates/EXPERIENCE_PROMPT.template.md": [
        "# Experience Prompt",
        "## Metadata",
        "## Confirmed Direction",
        "## Family Consistency Contract",
        "## Scope",
        "## Build Instructions",
        "## Expected Return",
        "## Prompt Strategy",
        "## Copy-Paste Prompt",
        "## Usage Rules",
    ],
}

PROTOCOL_REQUIRED_SNIPPETS = {
    "docs/00_lifecycle.md": [
        "Prompt requirements are context-relative",
        "page family",
        "plain-language, screen-focused prompts",
        "AIPD gate outcome",
        "schemas/aipd-gate-outcome.schema.json",
        "Fail-closed",
    ],
    "docs/02_artifacts.md": [
        "<PROJECT_ROOT>/experience_prompts/*.md",
        "`external_tool_prompt_ref`",
        "copy-paste-ready prompt",
        "`prompt_goal_type`",
        "`page_family_id`",
        "`tool_guidance_profile`",
    ],
    "docs/03_mission_blocks.md": [
        "experience_prompts/*.md",
        "`external_tool_prompt_ref`",
        "`page_family_id`",
        "forbidden drift",
        "blocked_by_mbs",
        "defer_retry",
    ],
    "docs/05_operating_playbook.md": [
        "screen by screen",
        "plain language",
        "`state_variant`",
        "`canonical_shell`",
        "`stitch_iterative_refine`",
        "check-gate-outcome",
    ],
    "docs/09_symphony_mb_adapter_contract.md": [
        "tracker.kind = aipd_mb",
        "runtime/state/<mb_id>.state.json",
        "attempt_start",
        "attempt_finish",
        "Unknown actions fail closed.",
    ],
    "prompts/SPEC_ARCHITECT.system.md": [
        "experience prompt artifact",
        "external-tool UI prompt",
        "major UI decisions",
        "page_family_id",
        "shared-shell contract",
    ],
    "prompts/BUILDER.system.md": [
        "experience prompt artifacts",
        "RESEARCH_NOTE",
        "forbidden_drift",
    ],
    "prompts/REVIEWER.system.md": [
        "external_tool_prompt_ref",
        "research artifacts",
        "shared shell",
    ],
    "templates/FUNCTION_BLOCK.template.md": [
        "`research_needed`:",
        "`research_questions`:",
        "`experience_prompt_needed`:",
    ],
    "templates/MISSION_BLOCK.template.md": [
        "`research_inputs`:",
        "`external_tool_prompt_ref`:",
    ],
    "templates/RESEARCH_NOTE.template.md": [
        "`trigger_type`:",
        "`user_approval_required`:",
        "`user_approval_status`:",
    ],
    "templates/EXPERIENCE_PROMPT.template.md": [
        "`page_family_id`:",
        "`prompt_goal_type`:",
        "`consistency_mode`:",
        "`family_source_refs`:",
        "`tool_guidance_profile`:",
        "`target_tool`:",
        "`visual_direction`:",
        "`design_core`:",
        "`shared_shell_scope`:",
        "`allowed_variation`:",
        "`forbidden_drift`:",
        "`prompt_requirements`:",
        "`expected_return_artifacts`:",
        "## Copy-Paste Prompt",
    ],
}

RESEARCH_REQUIRED_HEADINGS = [
    "# Research Note",
    "## Metadata",
    "## Query",
    "## Findings",
    "## Candidate Options",
    "## Impact And Adoption",
    "## Approval",
    "## Usage Rules",
]

RESEARCH_CORE_FIELDS = [
    "research_id",
    "trigger_type",
    "owner_role",
    "date",
    "query",
    "why_now",
    "sources",
    "facts",
    "candidates",
    "recommendation",
    "impact_on_fb_or_mb",
    "adopted_decision_ref",
    "deferred_questions",
    "user_approval_required",
    "user_approval_status",
]

EXPERIENCE_PROMPT_REQUIRED_HEADINGS = [
    "# Experience Prompt",
    "## Metadata",
    "## Confirmed Direction",
    "## Family Consistency Contract",
    "## Scope",
    "## Build Instructions",
    "## Expected Return",
    "## Prompt Strategy",
    "## Copy-Paste Prompt",
    "## Usage Rules",
]

EXPERIENCE_PROMPT_CORE_FIELDS = [
    "prompt_id",
    "parent_fb_id",
    "related_mb_ids",
    "page_family_id",
    "prompt_goal_type",
    "consistency_mode",
    "family_source_refs",
    "tool_guidance_profile",
    "target_tool",
    "status",
    "source_artifacts",
    "adopted_reference_refs",
    "visual_direction",
    "design_core",
    "information_density",
    "layout_direction",
    "component_style_direction",
    "color_direction",
    "typography_direction",
    "interaction_direction",
    "motion_direction",
    "responsive_priority",
    "accessibility_rules",
    "references_to_avoid",
    "shared_shell_scope",
    "must_preserve",
    "allowed_variation",
    "forbidden_drift",
    "component_contract_expectations",
    "page_or_component_goal",
    "states_and_branches",
    "required_flows",
    "style_direction",
    "must_do",
    "must_not_do",
    "expected_return_artifacts",
    "downstream_intake_notes",
    "prompt_requirements",
    "tool_specific_notes",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


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


def require_snippets(path: Path, snippets: list[str], errors: list[str], base: Optional[Path] = None) -> None:
    text = read_text(path)
    for snippet in snippets:
        if snippet not in text:
            fail(f"{display_path(path, base)} missing snippet: {snippet}", errors)


def require_section_body(path: Path, heading: str, errors: list[str], base: Optional[Path] = None) -> None:
    text = read_text(path)
    pattern = re.compile(rf"^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if match is None:
        fail(f"{display_path(path, base)} missing heading: {heading}", errors)
        return
    body = match.group("body").strip()
    if not body:
        fail(f"{display_path(path, base)} has empty section: {heading}", errors)


def find_markdown_value(path: Path, field: str, errors: list[str], base: Optional[Path] = None) -> Optional[str]:
    text = read_text(path)
    match = re.search(rf"^- `{re.escape(field)}`:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        fail(f"{display_path(path, base)} missing field: {field}", errors)
        return None
    value = match.group(1).strip()
    if not value:
        fail(f"{display_path(path, base)} has empty field: {field}", errors)
        return None
    return value


def optional_markdown_value(path: Path, field: str) -> Optional[str]:
    text = read_text(path)
    match = re.search(rf"^- `{re.escape(field)}`:\s*(.+)$", text, re.MULTILINE)
    if match is None:
        return None
    value = match.group(1).strip()
    return value or None


def require_markdown_fields(path: Path, fields: list[str], errors: list[str], base: Optional[Path] = None) -> None:
    for field in fields:
        find_markdown_value(path, field, errors, base)


def validate_protocol(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in PROTOCOL_FILES:
        path = root / rel_path
        require_file(path, errors, root)
        if path.is_file():
            if rel_path in PROTOCOL_REQUIRED_HEADINGS:
                require_headings(path, PROTOCOL_REQUIRED_HEADINGS[rel_path], errors, root)
            if rel_path in PROTOCOL_REQUIRED_SNIPPETS:
                require_snippets(path, PROTOCOL_REQUIRED_SNIPPETS[rel_path], errors, root)
    errors.extend(validate_gate_outcome_examples(root))
    return errors


def format_schema_error(error: object) -> str:
    path_parts = getattr(error, "absolute_path", [])
    path = ".".join(str(part) for part in path_parts)
    message = getattr(error, "message", str(error))
    if path:
        return f"{path}: {message}"
    return message


def validate_json_with_schema_file(instance: object, schema_path: Path) -> list[str]:
    try:
        schema = read_json(schema_path)
        Draft202012Validator.check_schema(schema)
    except json.JSONDecodeError as exc:
        return [f"{display_path(schema_path)} is not valid JSON: {exc}"]
    except Exception as exc:
        return [f"{display_path(schema_path)} is not a valid JSON schema: {exc}"]

    validator = Draft202012Validator(schema)
    return [format_schema_error(err) for err in validator.iter_errors(instance)]


def validate_gate_outcome(path: Path, base: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing gate outcome file: {display_path(path, base)}", errors)
        return errors
    try:
        data = read_json(path)
    except json.JSONDecodeError as exc:
        fail(f"{display_path(path, base)} is not valid JSON: {exc}", errors)
        return errors

    schema_errors = validate_json_with_schema_file(data, PROTOCOL_ROOT / "schemas" / "aipd-gate-outcome.schema.json")
    errors.extend(f"{display_path(path, base)} {err}" for err in schema_errors)
    return errors


def validate_gate_outcome_examples(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in GATE_OUTCOME_EXAMPLE_FILES:
        path = root / rel_path
        require_file(path, errors, root)
        if path.is_file():
            errors.extend(validate_gate_outcome(path, root))
    return errors


def parse_reference_list(value: str) -> list[str]:
    normalized = value.strip()
    if normalized.lower() == "none":
        return []
    return [item.strip() for item in normalized.split(",") if item.strip()]


def validate_relative_file_refs(
    path: Path,
    field: str,
    value: str,
    errors: list[str],
    project_root: Optional[Path],
    allowed_prefixes: Optional[tuple[str, ...]] = None,
) -> None:
    if project_root is None:
        return
    refs = parse_reference_list(value)
    if not refs:
        fail(f"{display_path(path, project_root)} has invalid {field}: none", errors)
        return

    root = project_root.resolve()
    for ref in refs:
        ref_path = Path(ref)
        if ref_path.is_absolute():
            fail(f"{display_path(path, project_root)} {field} must use project-relative paths: {ref}", errors)
            continue
        if ".." in ref_path.parts:
            fail(f"{display_path(path, project_root)} {field} must not escape project root: {ref}", errors)
            continue
        normalized_ref = ref_path.as_posix()
        if allowed_prefixes and not any(
            normalized_ref == prefix.rstrip("/") or normalized_ref.startswith(prefix) for prefix in allowed_prefixes
        ):
            fail(f"{display_path(path, project_root)} {field} has invalid reference location: {ref}", errors)
            continue
        target = (project_root / ref_path).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            fail(f"{display_path(path, project_root)} {field} must stay within project root: {ref}", errors)
            continue
        if not target.is_file():
            fail(f"{display_path(path, project_root)} {field} points to a missing file: {ref}", errors)


def validate_flag(path: Path, field: str, value: str, errors: list[str], project_root: Optional[Path]) -> None:
    if value not in FLAG_ALLOWED_VALUES:
        fail(f"{display_path(path, project_root)} has invalid {field}: {value}", errors)


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
                fail("SESSION_STATE.md points to an active function block that does not exist", errors)
        if active_mission and active_mission.lower() != "none":
            mission_matches = sorted((project_root / "missions").glob(f"{active_mission}*.md"))
            if not mission_matches:
                fail("SESSION_STATE.md points to an active mission block that does not exist", errors)

    for directory in ["function_blocks", "missions", "reviews"]:
        path = project_root / directory
        if not path.is_dir():
            fail(f"missing directory: {display_path(path, project_root)}", errors)

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
    foundational_dirs = ["function_blocks", "missions", "reviews"]

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
        auto_actions.extend([f"initialize {name}" for name in missing_items])
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

    require_headings(path, FUNCTION_REQUIRED_HEADINGS, errors, project_root)
    require_markdown_fields(path, FUNCTION_CORE_FIELDS, errors, project_root)

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
        value = find_markdown_value(path, field, errors, project_root)
        if value is not None and value not in ONTOLOGY_ALLOWED_STATUS:
            fail(f"{display_path(path, project_root)} has invalid {field}: {value}", errors)

    mode = find_markdown_value(path, "experience_delivery_mode", errors, project_root)
    if mode is not None and mode not in EXPERIENCE_ALLOWED_MODE:
        fail(f"{display_path(path, project_root)} has invalid experience_delivery_mode: {mode}", errors)

    if mode in {"external_ui_package", "hybrid"}:
        require_markdown_fields(
            path,
            ["experience_input_artifacts", "experience_builder_scope"],
            errors,
            project_root,
        )
        for field in ["experience_input_artifacts", "experience_builder_scope"]:
            value = optional_markdown_value(path, field)
            if value is not None and value.lower() == "none":
                fail(f"{display_path(path, project_root)} has invalid {field}: none", errors)

    research_needed = optional_markdown_value(path, "research_needed")
    if research_needed is not None:
        validate_flag(path, "research_needed", research_needed, errors, project_root)

    experience_prompt_needed = optional_markdown_value(path, "experience_prompt_needed")
    if experience_prompt_needed is not None:
        validate_flag(path, "experience_prompt_needed", experience_prompt_needed, errors, project_root)
        if experience_prompt_needed == "yes" and mode not in {"external_ui_package", "hybrid"}:
            fail(
                f"{display_path(path, project_root)} cannot require an experience prompt when experience_delivery_mode is {mode}",
                errors,
            )

    research_questions = optional_markdown_value(path, "research_questions")
    if research_needed == "yes" and research_questions is None:
        fail(f"{display_path(path, project_root)} missing field: research_questions", errors)

    return errors


def validate_mission(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing mission file: {path}", errors)
        return errors

    require_headings(path, MISSION_REQUIRED_HEADINGS, errors, project_root)
    require_markdown_fields(path, MISSION_CORE_FIELDS, errors, project_root)

    quality_profile = find_markdown_value(path, "quality_profile", errors, project_root)
    if quality_profile is not None and quality_profile not in QUALITY_ALLOWED_PROFILE:
        fail(f"{display_path(path, project_root)} has invalid quality_profile: {quality_profile}", errors)

    input_artifacts = find_markdown_value(path, "input_artifacts", errors, project_root)
    if input_artifacts is not None and input_artifacts.lower() != "none":
        ready_check = find_markdown_value(path, "input_ready_check", errors, project_root)
        if ready_check is not None and ready_check.lower() == "none":
            fail(f"{display_path(path, project_root)} has invalid input_ready_check: none", errors)

    research_inputs = optional_markdown_value(path, "research_inputs")
    if research_inputs is not None and research_inputs.lower() != "none":
        validate_relative_file_refs(
            path,
            "research_inputs",
            research_inputs,
            errors,
            project_root,
            allowed_prefixes=("research/",),
        )

    external_tool_prompt_ref = optional_markdown_value(path, "external_tool_prompt_ref")
    if external_tool_prompt_ref is not None and external_tool_prompt_ref.lower() != "none":
        refs = parse_reference_list(external_tool_prompt_ref)
        if len(refs) != 1:
            fail(
                f"{display_path(path, project_root)} external_tool_prompt_ref must contain exactly one project-relative file reference",
                errors,
            )
        validate_relative_file_refs(
            path,
            "external_tool_prompt_ref",
            external_tool_prompt_ref,
            errors,
            project_root,
            allowed_prefixes=("experience_prompts/",),
        )

    required_artifact_updates = optional_markdown_value(path, "required_artifact_updates")
    machine_spec_ref = optional_markdown_value(path, "machine_spec_ref")
    if (
        required_artifact_updates is not None
        and "SESSION_STATE.md" in required_artifact_updates
        and machine_spec_ref is not None
        and machine_spec_ref.lower() != "none"
    ):
        fail(
            f"{display_path(path, project_root)} must not list SESSION_STATE.md in required_artifact_updates for a runnable MB; session state is runtime-managed",
            errors,
        )

    return errors


def validate_research_note(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing research note file: {path}", errors)
        return errors

    require_headings(path, RESEARCH_REQUIRED_HEADINGS, errors, project_root)
    require_markdown_fields(path, RESEARCH_CORE_FIELDS, errors, project_root)

    trigger_type = find_markdown_value(path, "trigger_type", errors, project_root)
    if trigger_type is not None and trigger_type not in RESEARCH_ALLOWED_TRIGGER:
        fail(f"{display_path(path, project_root)} has invalid trigger_type: {trigger_type}", errors)

    approval_required = find_markdown_value(path, "user_approval_required", errors, project_root)
    if approval_required is not None and approval_required not in RESEARCH_ALLOWED_APPROVAL_REQUIRED:
        fail(f"{display_path(path, project_root)} has invalid user_approval_required: {approval_required}", errors)

    approval_status = find_markdown_value(path, "user_approval_status", errors, project_root)
    if approval_status is not None and approval_status not in RESEARCH_ALLOWED_APPROVAL_STATUS:
        fail(f"{display_path(path, project_root)} has invalid user_approval_status: {approval_status}", errors)

    if trigger_type == "system_triggered":
        if approval_required != "yes":
            fail(
                f"{display_path(path, project_root)} system_triggered research must set user_approval_required to yes",
                errors,
            )
        if approval_status != "approved":
            fail(
                f"{display_path(path, project_root)} system_triggered research must record user_approval_status as approved",
                errors,
            )

    if trigger_type == "user_triggered":
        if approval_required != "no":
            fail(
                f"{display_path(path, project_root)} user_triggered research must set user_approval_required to no",
                errors,
            )
        if approval_status != "not_required":
            fail(
                f"{display_path(path, project_root)} user_triggered research must record user_approval_status as not_required",
                errors,
            )

    return errors


def validate_experience_prompt(path: Path, project_root: Optional[Path] = None) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        fail(f"missing experience prompt file: {path}", errors)
        return errors

    require_headings(path, EXPERIENCE_PROMPT_REQUIRED_HEADINGS, errors, project_root)
    require_markdown_fields(path, EXPERIENCE_PROMPT_CORE_FIELDS, errors, project_root)

    target_tool = find_markdown_value(path, "target_tool", errors, project_root)
    if target_tool is not None and target_tool not in EXPERIENCE_PROMPT_ALLOWED_TOOL:
        fail(f"{display_path(path, project_root)} has invalid target_tool: {target_tool}", errors)

    status = find_markdown_value(path, "status", errors, project_root)
    if status is not None and status not in EXPERIENCE_PROMPT_ALLOWED_STATUS:
        fail(f"{display_path(path, project_root)} has invalid status: {status}", errors)

    prompt_goal_type = find_markdown_value(path, "prompt_goal_type", errors, project_root)
    if prompt_goal_type is not None and prompt_goal_type not in EXPERIENCE_PROMPT_ALLOWED_GOAL:
        fail(f"{display_path(path, project_root)} has invalid prompt_goal_type: {prompt_goal_type}", errors)

    consistency_mode = find_markdown_value(path, "consistency_mode", errors, project_root)
    if consistency_mode is not None and consistency_mode not in EXPERIENCE_PROMPT_ALLOWED_CONSISTENCY:
        fail(f"{display_path(path, project_root)} has invalid consistency_mode: {consistency_mode}", errors)

    tool_guidance_profile = find_markdown_value(path, "tool_guidance_profile", errors, project_root)
    if tool_guidance_profile is not None and tool_guidance_profile not in EXPERIENCE_PROMPT_ALLOWED_PROFILE:
        fail(f"{display_path(path, project_root)} has invalid tool_guidance_profile: {tool_guidance_profile}", errors)

    source_artifacts = find_markdown_value(path, "source_artifacts", errors, project_root)
    if source_artifacts is not None:
        validate_relative_file_refs(path, "source_artifacts", source_artifacts, errors, project_root)

    adopted_reference_refs = find_markdown_value(path, "adopted_reference_refs", errors, project_root)
    if adopted_reference_refs is not None and adopted_reference_refs.lower() != "none":
        validate_relative_file_refs(path, "adopted_reference_refs", adopted_reference_refs, errors, project_root)

    family_source_refs = find_markdown_value(path, "family_source_refs", errors, project_root)
    if family_source_refs is not None and family_source_refs.lower() != "none":
        validate_relative_file_refs(path, "family_source_refs", family_source_refs, errors, project_root)

    page_family_id = find_markdown_value(path, "page_family_id", errors, project_root)
    normalized_page_family_id = page_family_id.lower() if page_family_id is not None else None
    normalized_family_source_refs = family_source_refs.lower() if family_source_refs is not None else None

    if prompt_goal_type == "independent_screen":
        if consistency_mode is not None and consistency_mode != "not_applicable":
            fail(
                f"{display_path(path, project_root)} independent_screen prompt must set consistency_mode to not_applicable",
                errors,
            )
        if normalized_page_family_id != "not_applicable":
            fail(
                f"{display_path(path, project_root)} independent_screen prompt must set page_family_id to not_applicable",
                errors,
            )
        if normalized_family_source_refs != "none":
            fail(
                f"{display_path(path, project_root)} independent_screen prompt must set family_source_refs to none",
                errors,
            )

    if target_tool == "stitch" and tool_guidance_profile not in {"stitch_first_pass", "stitch_iterative_refine"}:
        fail(
            f"{display_path(path, project_root)} stitch prompt must use a stitch-specific tool_guidance_profile",
            errors,
        )

    if target_tool == "figma" and tool_guidance_profile != "figma_structured_handoff":
        fail(
            f"{display_path(path, project_root)} figma prompt must use tool_guidance_profile figma_structured_handoff",
            errors,
        )

    if target_tool == "other" and tool_guidance_profile == "figma_structured_handoff":
        fail(
            f"{display_path(path, project_root)} non-figma prompt cannot use figma_structured_handoff",
            errors,
        )

    if prompt_goal_type in {"canonical_shell", "state_variant", "family_extension"}:
        if normalized_page_family_id in {None, "", "none", "not_applicable"}:
            fail(
                f"{display_path(path, project_root)} {prompt_goal_type} prompt must set a real page_family_id",
                errors,
            )

    if prompt_goal_type == "canonical_shell" and consistency_mode == "not_applicable":
        fail(
            f"{display_path(path, project_root)} canonical_shell prompt must declare a same-family consistency mode",
            errors,
        )

    if prompt_goal_type in {"state_variant", "family_extension"}:
        if consistency_mode == "not_applicable":
            fail(
                f"{display_path(path, project_root)} {prompt_goal_type} prompt must declare a same-family consistency mode",
                errors,
            )
        if normalized_family_source_refs in {None, "none"}:
            fail(
                f"{display_path(path, project_root)} {prompt_goal_type} prompt must reference family_source_refs",
                errors,
            )

    require_section_body(path, "## Copy-Paste Prompt", errors, project_root)

    return errors


def validate_project_artifacts(project_root: Path) -> list[str]:
    errors: list[str] = []

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

    research_dir = project_root / "research"
    if research_dir.is_dir():
        for research_path in sorted(research_dir.glob("*.md")):
            errors.extend(validate_research_note(research_path, project_root))

    experience_prompt_dir = project_root / "experience_prompts"
    if experience_prompt_dir.is_dir():
        for prompt_path in sorted(experience_prompt_dir.glob("*.md")):
            errors.extend(validate_experience_prompt(prompt_path, project_root))

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

    preflight_parser = subparsers.add_parser("check-preflight", help="Run project preflight for one scene.")
    preflight_parser.add_argument("project_root", help="Path to the external project root.")
    preflight_parser.add_argument("scene", help="Scene to evaluate.")

    function_parser = subparsers.add_parser("check-function", help="Validate one function block.")
    function_parser.add_argument("path", help="Path to the function block Markdown file.")

    mission_parser = subparsers.add_parser("check-mission", help="Validate one mission block.")
    mission_parser.add_argument("path", help="Path to the mission block Markdown file.")

    research_parser = subparsers.add_parser("check-research-note", help="Validate one research note Markdown file.")
    research_parser.add_argument("path", help="Path to the research note Markdown file.")

    prompt_parser = subparsers.add_parser("check-experience-prompt", help="Validate one experience prompt Markdown file.")
    prompt_parser.add_argument("path", help="Path to the experience prompt Markdown file.")

    quality_parser = subparsers.add_parser("check-quality-report", help="Validate one quality report JSON file.")
    quality_parser.add_argument("path", help="Path to the quality report JSON file.")

    review_parser = subparsers.add_parser("check-review", help="Validate one quality report JSON file.")
    review_parser.add_argument("path", help="Path to the quality report JSON file.")

    gate_parser = subparsers.add_parser("check-gate-outcome", help="Validate one AIPD gate outcome JSON file.")
    gate_parser.add_argument("path", help="Path to the AIPD gate outcome JSON file.")

    all_parser = subparsers.add_parser("check-all", help="Validate protocol files and one external project root.")
    all_parser.add_argument("project_root", nargs="?", help="Optional path to the external project root.")

    args = parser.parse_args()

    if args.command == "check-protocol":
        return print_result(validate_protocol(PROTOCOL_ROOT), "protocol repository")

    if args.command == "check-project":
        project_root = resolve_path(args.project_root)
        errors = validate_project(project_root)
        errors.extend(validate_project_artifacts(project_root))
        return print_result(errors, f"project {project_root}")

    if args.command == "check-preflight":
        project_root = resolve_path(args.project_root)
        return print_preflight(args.scene, project_root)

    if args.command == "check-function":
        path = resolve_path(args.path)
        return print_result(validate_function(path, path.parent.parent), f"function block {path}")

    if args.command == "check-mission":
        path = resolve_path(args.path)
        return print_result(validate_mission(path, path.parent.parent), f"mission {path}")

    if args.command == "check-research-note":
        path = resolve_path(args.path)
        return print_result(validate_research_note(path, path.parent.parent), f"research note {path}")

    if args.command == "check-experience-prompt":
        path = resolve_path(args.path)
        return print_result(validate_experience_prompt(path, path.parent.parent), f"experience prompt {path}")

    if args.command in {"check-quality-report", "check-review"}:
        path = resolve_path(args.path)
        return print_result(validate_quality_report(path, path.parent.parent), f"quality report {path}")

    if args.command == "check-gate-outcome":
        path = resolve_path(args.path)
        return print_result(validate_gate_outcome(path, path.parent.parent), f"AIPD gate outcome {path}")

    if args.command == "check-all":
        errors = validate_protocol(PROTOCOL_ROOT)
        label = "protocol repository"
        if args.project_root:
            project_root = resolve_path(args.project_root)
            errors.extend(validate_project(project_root))
            errors.extend(validate_project_artifacts(project_root))
            label = f"protocol repository and project {project_root}"
        return print_result(errors, label)

    return 1


if __name__ == "__main__":
    sys.exit(main())
