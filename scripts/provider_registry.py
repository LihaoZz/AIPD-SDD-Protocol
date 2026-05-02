#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness_common import read_json, validate_with_schema, write_json


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "config" / "provider_registry.json"


@dataclass(frozen=True)
class ProviderRegistry:
    raw: dict[str, Any]

    @property
    def providers(self) -> dict[str, dict[str, Any]]:
        return self.raw["providers"]

    @property
    def role_defaults(self) -> dict[str, str]:
        return self.raw["role_defaults"]

    def provider_ids(self) -> set[str]:
        return set(self.providers.keys())

    def provider(self, provider_id: str) -> dict[str, Any]:
        if provider_id not in self.providers:
            raise ValueError(f"Unknown provider id: {provider_id}")
        return self.providers[provider_id]

    def command_template(self, provider_id: str) -> str:
        return self.provider(provider_id)["workflow_command_template"]

    def command_for_project(self, provider_id: str, project_root: Path) -> str:
        return self.command_template(provider_id).format(project_root=project_root)

    def role_provider(self, role_name: str) -> str:
        provider_id = self.role_defaults[role_name]
        self.provider(provider_id)
        return provider_id


def load_provider_registry(path: Path | None = None) -> ProviderRegistry:
    target = path or REGISTRY_PATH
    raw = read_json(target)
    errors = validate_with_schema(raw, "provider-registry.schema.json")
    if errors:
        raise ValueError("; ".join(errors))

    registry = ProviderRegistry(raw)
    _validate_role_targets(registry)
    return registry


def save_provider_registry(registry: dict[str, Any], path: Path | None = None) -> Path:
    errors = validate_with_schema(registry, "provider-registry.schema.json")
    if errors:
        raise ValueError("; ".join(errors))

    target = path or REGISTRY_PATH
    write_json(target, registry)
    return target


def ensure_known_provider(provider_id: str, registry: ProviderRegistry) -> str:
    registry.provider(provider_id)
    return provider_id


def _validate_role_targets(registry: ProviderRegistry) -> None:
    for role_name, provider_id in registry.role_defaults.items():
        if provider_id not in registry.providers:
            raise ValueError(f"role_defaults.{role_name} references unknown provider: {provider_id}")
