#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from harness_common import (
    failure_log_path,
    local_timestamp,
    local_timezone_name,
    project_memory_path,
    quality_memory_path,
    read_json,
    resolve_path,
)


DEFAULT_MEMORY_POLICY = {
    "inject_failure_patterns": True,
    "inject_validated_patterns": True,
    "max_memory_items": 3,
}


def effective_memory_policy(spec: dict[str, Any]) -> dict[str, Any]:
    policy = dict(DEFAULT_MEMORY_POLICY)
    policy.update(spec.get("memory_policy") or {})
    return policy


def _slice_recent(entries: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    return list(reversed(entries))[:limit]


def _matching_failure_entries(
    failures: list[dict[str, Any]],
    mb_id: str,
    parent_fb_id: str,
    last_failure_reason: str | None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in reversed(failures):
        if entry.get("mb_id") == mb_id:
            matches.append(entry)
            continue
        if entry.get("parent_fb_id") == parent_fb_id:
            matches.append(entry)
            continue
        if last_failure_reason and last_failure_reason in {
            entry.get("failure_type"),
            entry.get("root_cause_guess"),
            entry.get("repeated_failure_key"),
        }:
            matches.append(entry)
    return matches


def _matching_project_entries(
    completed_mbs: list[dict[str, Any]],
    mb_id: str,
    parent_fb_id: str,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for entry in reversed(completed_mbs):
        if entry.get("mb_id") == mb_id or entry.get("parent_fb_id") == parent_fb_id:
            matches.append(entry)
    return matches


def lookup_memory_context(project_root: Path, spec: dict[str, Any], state: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    policy = effective_memory_policy(spec)
    context: dict[str, list[dict[str, str]]] = {
        "failure_patterns": [],
        "validated_patterns": [],
    }
    max_items = int(policy["max_memory_items"])

    if policy["inject_failure_patterns"]:
        failure_data = read_json(failure_log_path(project_root))
        failures = _matching_failure_entries(
            failure_data["failures"],
            spec["mb_id"],
            spec["parent_fb_id"],
            state.get("last_failure_reason"),
        )
        for entry in _slice_recent(failures, max_items):
            context["failure_patterns"].append(
                {
                    "pattern": entry["condition"],
                    "avoid_next_time": entry.get("attempted_fix", "avoid repeating the same failed fix"),
                    "source_ref": f"{entry['mb_id']}:{entry['attempt_id']}",
                }
            )

    if policy["inject_validated_patterns"]:
        project_data = read_json(project_memory_path(project_root))
        validated = _matching_project_entries(
            project_data["completed_mbs"],
            spec["mb_id"],
            spec["parent_fb_id"],
        )
        for entry in _slice_recent(validated, max_items):
            notes = entry.get("reusable_notes") or entry.get("validated_evidence") or ["validated pattern"]
            context["validated_patterns"].append(
                {
                    "pattern": notes[0],
                    "use_when": entry.get("pattern_type", "similar MBs"),
                    "source_ref": entry["mb_id"],
                }
            )

    return context


def render_memory_context(context: dict[str, list[dict[str, str]]]) -> str:
    failure_patterns = context.get("failure_patterns", [])
    validated_patterns = context.get("validated_patterns", [])
    if not failure_patterns and not validated_patterns:
        return ""

    lines = ["## Memory Context", ""]
    if failure_patterns:
        lines.append("### Relevant Failure Patterns")
        for item in failure_patterns:
            lines.append(
                f"- Avoid: {item['pattern']} | Prior failed fix: {item['avoid_next_time']} | Source: {item['source_ref']}"
            )
        lines.append("")
    if validated_patterns:
        lines.append("### Validated Patterns")
        for item in validated_patterns:
            lines.append(
                f"- Prefer: {item['pattern']} | Use When: {item['use_when']} | Source: {item['source_ref']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def sync_quality_memory(project_root: Path) -> Path:
    project_data = read_json(project_memory_path(project_root))
    failure_data = read_json(failure_log_path(project_root))
    target = quality_memory_path(project_root)

    repeated_failures = _slice_recent(list(reversed(failure_data["failures"])), 5)
    validated_patterns = _slice_recent(list(reversed(project_data["completed_mbs"])), 5)

    failure_counts = Counter(entry.get("failure_type", "unknown") for entry in failure_data["failures"])
    top_risks = failure_counts.most_common(3)

    stable_rules = [
        "- `rule`: Retry only with verification feedback and relevant memory context.",
        "- `why`: Blind retries hide repeated failure modes instead of resolving them.",
        "- `source_refs`: runtime/memory/failure_log.json, runtime/memory/project_memory.json",
    ]

    repeated_failure_lines = ["- none"]
    if repeated_failures:
        repeated_failure_lines = [
            f"- `pattern`: {entry['condition']} | `seen_in`: {entry['mb_id']}:{entry['attempt_id']} | `avoid_next_time`: {entry.get('attempted_fix', 'avoid repeating the same failed fix')}"
            for entry in repeated_failures
        ]

    validated_pattern_lines = ["- none"]
    if validated_patterns:
        validated_pattern_lines = [
            f"- `pattern`: {(entry.get('reusable_notes') or entry.get('validated_evidence') or ['validated pattern'])[0]} | `use_when`: {entry.get('pattern_type', 'similar MBs')} | `evidence_refs`: {entry['mb_id']}"
            for entry in validated_patterns
        ]

    high_risk_lines = ["- none"]
    if top_risks:
        high_risk_lines = [
            f"- `area`: {failure_type} | `common_failure`: {count} observed issue(s) | `required_checks`: verification_report.json + reviewer inspection when needed"
            for failure_type, count in top_risks
        ]

    recent_lessons = ["- none"]
    lessons: list[str] = []
    for entry in validated_patterns[:2]:
        lessons.append(
            f"- `date`: {entry.get('recorded_at', local_timestamp())} | `lesson`: {(entry.get('reusable_notes') or entry.get('validated_evidence') or ['validated pattern'])[0]} | `source_mb`: {entry['mb_id']}"
        )
    for entry in repeated_failures[:2]:
        lessons.append(
            f"- `date`: {entry.get('recorded_at', local_timestamp())} | `lesson`: Avoid repeating {entry['failure_type']} without a new repair strategy. | `source_mb`: {entry['mb_id']}"
        )
    if lessons:
        recent_lessons = lessons

    content = "\n".join(
        [
            "# Quality Memory",
            "",
            "## Purpose",
            "",
            "Store only reusable quality lessons across function blocks and mission blocks.",
            "",
            "## Stable Rules",
            "",
            *stable_rules,
            "",
            "## Repeated Failure Patterns",
            "",
            *repeated_failure_lines,
            "",
            "## Validated Good Patterns",
            "",
            *validated_pattern_lines,
            "",
            "## High-Risk Areas",
            "",
            *high_risk_lines,
            "",
            "## Recent Lessons",
            "",
            *recent_lessons,
            "",
            "## Usage Rules",
            "",
            "- Do not use this file as a running log of every MB.",
            "- Record only reusable lessons, repeated failures, stable good patterns, and high-risk reminders.",
            "- Update this file when a repeated failure appears, a new high-value lesson is confirmed, or a rule should become stable.",
            "- Do not record routine success with no reusable insight.",
            "- Every lesson should point back to a concrete `fb` or `mb` reference when possible.",
            "",
        ]
    )
    target.write_text(content, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync QUALITY_MEMORY.md from runtime memory artifacts.")
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    target = sync_quality_memory(project_root)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
