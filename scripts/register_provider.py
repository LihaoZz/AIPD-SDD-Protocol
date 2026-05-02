#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from provider_registry import load_provider_registry, save_provider_registry


def render_template(path: Path, replacements: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def sanitize_provider_id(provider_id: str) -> str:
    normalized = provider_id.strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z0-9_]+", normalized):
        raise ValueError("provider_id must contain only lowercase letters, digits, or underscores")
    return normalized


def provider_class_name(provider_id: str) -> str:
    return "".join(part.capitalize() for part in provider_id.split("_"))


def update_registry(args: argparse.Namespace, registry_path: Path) -> dict:
    registry = load_provider_registry(registry_path).raw
    provider_id = sanitize_provider_id(args.provider_id)
    workflow_command_template = (
        args.workflow_command_template
        or f"python3 {{project_root}}/runtime/{provider_id}_adapter/bin/{provider_id}_app_server.py app-server"
    )

    registry["providers"][provider_id] = {
        "adapter_kind": args.adapter_kind,
        "launcher_family": args.launcher_family,
        "supports_aipd_mode": args.generate_aipd_launcher,
        "may_be_default": args.allow_default,
        "may_be_escalate_to": args.allow_escalate_to,
        "role_tags": args.role_tags,
        "workflow_command_template": workflow_command_template,
    }

    role_map = {
        "default": "default_execution_provider",
        "precision": "precision_execution_provider",
        "high_complexity": "high_complexity_provider",
        "escalation": "escalation_provider",
    }
    for role in args.assign_roles:
        registry["role_defaults"][role_map[role]] = provider_id

    save_provider_registry(registry, registry_path)
    return registry


def scaffold_local_provider_files(args: argparse.Namespace, templates_root: Path) -> None:
    provider_id = sanitize_provider_id(args.provider_id)
    local_root = Path(args.local_providers_root).expanduser().resolve()
    launchers = local_root / "launchers"
    profiles = local_root / "profiles"
    prompts = local_root / "prompts"
    scripts_root = local_root / "scripts"
    launchers.mkdir(parents=True, exist_ok=True)
    profiles.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)
    scripts_root.mkdir(parents=True, exist_ok=True)

    replacements = {
        "provider_id": provider_id,
        "provider_id_upper": provider_id.upper(),
        "api_base_url": args.api_base_url,
        "model_id": args.model_id,
        "profile_path": str((profiles / f"{provider_id}.env").expanduser()),
        "prompt_file": str((prompts / "aipd_bootstrap.md").expanduser()),
        "sync_script": str((scripts_root / "sync_aipd_readonly.sh").expanduser()),
        "mirror_root": args.mirror_root,
    }

    profile_template = templates_root / "provider_profile.template.env"
    launcher_template = templates_root / "provider_launcher.template.sh"
    aipd_launcher_template = templates_root / "provider_launcher_aipd.template.sh"

    profile_path = profiles / f"{provider_id}.env.example"
    profile_path.write_text(render_template(profile_template, replacements), encoding="utf-8")

    launcher_path = launchers / f"claude-{provider_id}"
    launcher_path.write_text(render_template(launcher_template, replacements), encoding="utf-8")
    launcher_path.chmod(0o755)

    if args.generate_aipd_launcher:
        aipd_launcher_path = launchers / f"claude-{provider_id}-aipd"
        aipd_launcher_path.write_text(render_template(aipd_launcher_template, replacements), encoding="utf-8")
        aipd_launcher_path.chmod(0o755)


def scaffold_adapter(args: argparse.Namespace, repo_root: Path, adapter_template_root: Path) -> None:
    provider_id = sanitize_provider_id(args.provider_id)
    adapter_root = repo_root / "runtime" / f"{provider_id}_adapter"
    adapter_root.mkdir(parents=True, exist_ok=True)
    replacements = {
        "provider_id": provider_id,
        "provider_id_upper": provider_id.upper(),
        "adapter_kind": args.adapter_kind,
        "launcher_family": args.launcher_family,
        "workflow_command_template": args.workflow_command_template
        or f"python3 {{project_root}}/runtime/{provider_id}_adapter/bin/{provider_id}_app_server.py app-server",
        "launcher_path": f"~/.claude/providers/launchers/claude-{provider_id}",
        "class_name": provider_class_name(provider_id),
        "module_name": f"{provider_id}_adapter",
    }

    for template_path in adapter_template_root.rglob("*"):
        relative = template_path.relative_to(adapter_template_root)
        if template_path.is_dir():
            target_dir = adapter_root / relative
            if relative.name == "adapter_pkg":
                target_dir = adapter_root / f"{provider_id}_adapter"
            target_dir.mkdir(parents=True, exist_ok=True)
            continue

        target = adapter_root / relative
        target_name = target.name.replace("provider_app_server", f"{provider_id}_app_server")
        if "adapter_pkg" in target.parts:
            target = adapter_root / f"{provider_id}_adapter" / target.name
        else:
            target = target.with_name(target_name)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_template(template_path, replacements), encoding="utf-8")
        if target.suffix == ".py" or "/bin/" in target.as_posix():
            target.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a provider for forked AIPD setups.")
    parser.add_argument("--repo-root")
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--adapter-kind", default="claude_compatible_adapter")
    parser.add_argument("--launcher-family", default="claude-compatible")
    parser.add_argument("--api-base-url", default="https://api.example.com/anthropic")
    parser.add_argument("--model-id", default="__REPLACE_WITH_MODEL_ID__")
    parser.add_argument("--local-providers-root", default="~/.claude/providers")
    parser.add_argument("--mirror-root", default="/Users/lihaozheng/Documents/AI/Product-Dev-aipd-readonly")
    parser.add_argument("--workflow-command-template")
    parser.add_argument("--role-tags", nargs="*", default=["custom_provider"])
    parser.add_argument(
        "--assign-roles",
        nargs="*",
        choices=["default", "precision", "high_complexity", "escalation"],
        default=[],
    )
    parser.add_argument("--allow-default", action="store_true")
    parser.add_argument("--allow-escalate-to", action="store_true")
    parser.add_argument("--generate-aipd-launcher", action="store_true")
    parser.add_argument("--skip-adapter", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else Path(__file__).resolve().parent.parent
    templates_root = repo_root / "templates"
    adapter_template_root = templates_root / "provider_adapter.template"
    registry_path = repo_root / "config" / "provider_registry.json"

    update_registry(args, registry_path)
    scaffold_local_provider_files(args, templates_root)
    if not args.skip_adapter:
        scaffold_adapter(args, repo_root, adapter_template_root)

    print(json.dumps({"provider_id": sanitize_provider_id(args.provider_id), "registry_path": str(registry_path)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
