from __future__ import annotations

from pathlib import Path


COMPACT_SOURCE_PATHS = (
    "README.md",
    "docs/00_lifecycle.md",
    "docs/01_principles.md",
    "docs/05_operating_playbook.md",
    "docs/06_session_bootstrap.md",
    "HARNESS.md",
)

TRANSLATION_SOURCE_PATHS = (
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
    "docs/provider_onboarding.md",
    "templates/API_CONTRACT.template.md",
    "templates/CONSTITUTION.template.md",
    "templates/DATA_MODEL.template.md",
    "templates/DECISIONS.template.md",
    "templates/EXPERIENCE_PROMPT.template.md",
    "templates/FUNCTION_BLOCK.template.md",
    "templates/MISSION_BLOCK.template.md",
    "templates/PREFLIGHT_RESULT.template.md",
    "templates/QUALITY_MEMORY.template.md",
    "templates/QUALITY_RULEBOOK.template.md",
    "templates/RESEARCH_NOTE.template.md",
    "templates/SCOPE.template.md",
    "templates/SESSION_STATE.template.md",
)

CHINESE_SECTION_MARKERS = ("## 中文翻译", "## 中文说明")

ZH_AUTHORITY_NOTE = "Chinese reference only; the English source file is authoritative."


def translation_source_path(source_rel: str) -> Path:
    return Path("translations/zh") / source_rel


def generated_translation_path(source_rel: str) -> Path:
    source = Path(source_rel)
    if source_rel == "README.md":
        return Path("README.zh.md")
    if source.parts[0] == "docs":
        return Path("docs/zh") / source.name
    if source.parts[0] == "templates":
        return Path("templates/zh") / source.name
    raise ValueError(f"unsupported translation source: {source_rel}")


def generated_header(source_rel: str, translation_source_rel: str, generated_at: str) -> str:
    return (
        "<!--\n"
        "GENERATED FILE - DO NOT EDIT DIRECTLY\n"
        f"Source: {source_rel}\n"
        f"Translation source: {translation_source_rel}\n"
        f"Generated at: {generated_at}\n"
        f"Authority: {ZH_AUTHORITY_NOTE}\n"
        "-->\n\n"
    )
