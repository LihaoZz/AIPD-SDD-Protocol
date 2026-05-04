#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from harness_common import PROTOCOL_ROOT, validate_with_schema, write_json, write_text
from protocol_derivatives_common import (
    CHINESE_SECTION_MARKERS,
    COMPACT_SOURCE_PATHS,
    TRANSLATION_SOURCE_PATHS,
    generated_header,
    generated_translation_path,
    translation_source_path,
)


def local_timestamp() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_bilingual_text(text: str) -> tuple[str, str | None]:
    for marker in CHINESE_SECTION_MARKERS:
        if marker in text:
            english, chinese = text.split(marker, 1)
            return english.rstrip() + "\n", chinese.lstrip("\n")
    return text.rstrip() + "\n", None


def read_english_source(protocol_root: Path, rel_path: str) -> str:
    text = (protocol_root / rel_path).read_text(encoding="utf-8")
    english, _ = split_bilingual_text(text)
    return english


def load_translation_source(protocol_root: Path, rel_path: str) -> str:
    path = protocol_root / translation_source_path(rel_path)
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def section_map(text: str) -> dict[str, str]:
    lines = text.splitlines()
    headers: list[tuple[int, str, int]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if match:
            headers.append((len(match.group(1)), match.group(2).strip(), index))
    sections: dict[str, str] = {}
    for pos, (_, heading, start) in enumerate(headers):
        end = headers[pos + 1][2] if pos + 1 < len(headers) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        sections[heading] = body
    return sections


def bullet_list(body: str) -> list[str]:
    items: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "---":
            continue
        match = re.match(r"^[-*]\s+(.+)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return items


def ordered_list(body: str) -> list[str]:
    items: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "---":
            continue
        match = re.match(r"^[0-9]+\.\s+(.+)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return items


def paragraph(body: str) -> str:
    return " ".join(
        line.strip()
        for line in body.splitlines()
        if line.strip() and line.strip() != "---"
    )


def leading_bullet_list(body: str) -> list[str]:
    items: list[str] = []
    started = False
    for line in body.splitlines():
        stripped = line.strip()
        match = re.match(r"^[-*]\s+(.+)$", stripped)
        if match:
            started = True
            items.append(match.group(1).strip())
            continue
        if started:
            break
    return items


def parse_scene_body(body: str) -> dict[str, list[str]]:
    labels = [
        "Read after the global bootstrap files:",
        "Read after the compact startup summary:",
        "Read these too when relevant:",
        "Also read when needed:",
        "First role:",
        "First action:",
        "Do not:",
    ]
    current = None
    buckets: dict[str, list[str]] = {label: [] for label in labels}
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped in buckets:
            current = stripped
            continue
        if current is None or not stripped:
            continue
        match = re.match(r"^-\s+(.+)$", stripped)
        if match:
            buckets[current].append(match.group(1).strip())
    scene: dict[str, list[str]] = {
        "required_reads": buckets["Read after the global bootstrap files:"] or buckets["Read after the compact startup summary:"],
        "first_role": buckets["First role:"],
        "first_action": buckets["First action:"],
        "do_not": buckets["Do not:"],
    }
    if buckets["Read these too when relevant:"]:
        scene["also_read_when_relevant"] = buckets["Read these too when relevant:"]
    if buckets["Also read when needed:"]:
        scene["also_read_when_needed"] = buckets["Also read when needed:"]
    return scene


def extract_numbered_rules(body: str) -> list[str]:
    return ordered_list(body)


def generate_protocol_compact(protocol_root: Path) -> dict[str, Any]:
    readme_sections = section_map(read_english_source(protocol_root, "README.md"))
    lifecycle_sections = section_map(read_english_source(protocol_root, "docs/00_lifecycle.md"))
    principles_sections = section_map(read_english_source(protocol_root, "docs/01_principles.md"))
    bootstrap_sections = section_map(read_english_source(protocol_root, "docs/06_session_bootstrap.md"))
    harness_sections = section_map(read_english_source(protocol_root, "HARNESS.md"))
    builder_sections = section_map(read_english_source(protocol_root, "prompts/BUILDER.system.md"))

    compact = {
        "schema_version": "1.0",
        "generated_from": list(COMPACT_SOURCE_PATHS),
        "authority": {
            "english_markdown_authoritative": True,
            "machine_summary_kind": "derived_compact",
            "chinese_reference_kind": "generated_reference_only",
        },
        "startup": {
            "machine_default_entrypoint": "generated/protocol_compact.json",
            "human_authority_refs": list(COMPACT_SOURCE_PATHS),
            "global_bootstrap_files": leading_bullet_list(bootstrap_sections["Global Bootstrap Files"]),
            "automatic_reading_path_steps": ordered_list(readme_sections["Automatic Reading Path"]),
            "minimum_startup_checklist": bullet_list(readme_sections["Minimum Startup Checklist"]),
        },
        "scenes": {
            "greenfield": parse_scene_body(bootstrap_sections["`greenfield`"]),
            "expansion": parse_scene_body(bootstrap_sections["`expansion`"]),
            "continue": parse_scene_body(bootstrap_sections["`continue`"]),
            "review": parse_scene_body(bootstrap_sections["`review`"]),
            "recovery": parse_scene_body(bootstrap_sections["`recovery`"]),
        },
        "protocol_rules": {
            "three_layers": bullet_list(readme_sections["Three Layers"]),
            "core_principles": bullet_list(principles_sections["Core Principles"]),
            "plain_writing_rule": paragraph(principles_sections["Plain Writing Rule"]),
            "preflight_rule": paragraph(lifecycle_sections["Preflight Rule"]),
            "research_rule": paragraph(lifecycle_sections["Research Rule"]),
            "role_handoff_rule": paragraph(lifecycle_sections["Role Handoff Rule"]),
            "issue_routing_rule": paragraph(lifecycle_sections["Issue Routing Rule"]),
            "bootstrap_rule": paragraph(lifecycle_sections["Bootstrap Rule"]),
            "failure_modes": bullet_list(readme_sections["Failure Modes This Protocol Tries To Prevent"]),
        },
        "harness_rules": {
            "purpose": bullet_list(harness_sections["Purpose"]),
            "execution_policy_rule": paragraph(harness_sections["Execution Policy Rule"]),
            "dual_preflight_rule": paragraph(harness_sections["Dual Preflight Rule"]),
            "retry_feedback_rule": paragraph(harness_sections["Retry Feedback Rule"]),
            "structural_route_rule": paragraph(harness_sections["Structural Route Rule"]),
            "runtime_state_rule": paragraph(harness_sections["Runtime State Rule"]),
            "non_git_workspace_rule": paragraph(harness_sections["Non-Git Workspace Rule"]),
            "memory_bridge_rule": paragraph(harness_sections["Memory Bridge Rule"]),
            "verification_report_vs_digest": paragraph(harness_sections["Verification Report vs Digest"]),
        },
        "builder_runtime_contract": {
            "core_rules": extract_numbered_rules(builder_sections["Core Rules"]),
            "required_inputs": bullet_list(builder_sections["Required Inputs"]),
            "forbidden_behaviors": bullet_list(builder_sections["Forbidden Behaviors"]),
        },
    }
    errors = validate_with_schema(compact, "protocol-compact.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    return compact


def render_translation(protocol_root: Path, source_rel: str, generated_at: str) -> str:
    translation_rel = translation_source_path(source_rel).as_posix()
    body = load_translation_source(protocol_root, source_rel)
    header = generated_header(source_rel, translation_rel, generated_at)
    return header + body.rstrip() + "\n"


def write_compact(protocol_root: Path, generated_at: str) -> dict[str, Any]:
    compact = generate_protocol_compact(protocol_root)
    path = protocol_root / "generated" / "protocol_compact.json"
    write_json(path, compact)
    return compact


def write_translations(protocol_root: Path, generated_at: str) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for source_rel in TRANSLATION_SOURCE_PATHS:
        output_rel = generated_translation_path(source_rel).as_posix()
        rendered = render_translation(protocol_root, source_rel, generated_at)
        write_text(protocol_root / output_rel, rendered)
        outputs[output_rel] = rendered
    return outputs


def write_manifest(protocol_root: Path, generated_at: str, compact: dict[str, Any], translations: dict[str, str]) -> dict[str, Any]:
    source_paths = sorted(
        set(COMPACT_SOURCE_PATHS)
        | set(TRANSLATION_SOURCE_PATHS)
        | {translation_source_path(source).as_posix() for source in TRANSLATION_SOURCE_PATHS}
    )
    source_digests = {
        rel: sha256_file(protocol_root / rel)
        for rel in source_paths
    }
    artifacts: dict[str, dict[str, Any]] = {
        "generated/protocol_compact.json": {
            "kind": "compact",
            "sha256": sha256_text(json.dumps(compact, ensure_ascii=True, indent=2) + "\n"),
            "source_paths": list(COMPACT_SOURCE_PATHS),
        }
    }
    for source_rel in TRANSLATION_SOURCE_PATHS:
        output_rel = generated_translation_path(source_rel).as_posix()
        artifacts[output_rel] = {
            "kind": "translation",
            "sha256": sha256_text(translations[output_rel]),
            "source_paths": [source_rel, translation_source_path(source_rel).as_posix()],
        }
    manifest = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "source_digests": source_digests,
        "artifacts": artifacts,
    }
    write_json(protocol_root / "generated" / "protocol_derivatives_manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate compact and Chinese derivative protocol artifacts.")
    parser.add_argument("target", choices=["compact", "zh", "all"])
    parser.add_argument("--protocol-root", default=str(PROTOCOL_ROOT))
    args = parser.parse_args()

    protocol_root = Path(args.protocol_root).expanduser().resolve()
    generated_at = local_timestamp()
    compact: dict[str, Any] | None = None
    translations: dict[str, str] = {}

    if args.target in {"compact", "all"}:
        compact = write_compact(protocol_root, generated_at)
    if args.target in {"zh", "all"}:
        translations = write_translations(protocol_root, generated_at)
    if args.target == "all":
        assert compact is not None
        write_manifest(protocol_root, generated_at, compact, translations)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
