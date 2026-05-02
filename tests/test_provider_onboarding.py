from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ProviderOnboardingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="provider-onboarding-")
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.repo_root.mkdir(parents=True)
        (self.repo_root / "config").mkdir()
        (self.repo_root / "runtime").mkdir()
        (self.repo_root / "templates").mkdir()
        self._copy(REPO_ROOT / "config" / "provider_registry.json", self.repo_root / "config" / "provider_registry.json")
        self._copy(REPO_ROOT / "schemas" / "provider-registry.schema.json", self.repo_root / "schemas" / "provider-registry.schema.json")
        for path in [
            "templates/provider_profile.template.env",
            "templates/provider_launcher.template.sh",
            "templates/provider_launcher_aipd.template.sh",
        ]:
            self._copy(REPO_ROOT / path, self.repo_root / path)
        for path in (REPO_ROOT / "templates" / "provider_adapter.template").rglob("*"):
            if path.is_file():
                self._copy(path, self.repo_root / path.relative_to(REPO_ROOT))
        self.local_providers_root = Path(self.temp_dir.name) / "local-providers"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_register_provider_updates_registry_and_generates_files(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "register_provider.py"),
                "--repo-root",
                str(self.repo_root),
                "--provider-id",
                "glm",
                "--api-base-url",
                "https://api.glm.example/anthropic",
                "--model-id",
                "glm-4.5",
                "--local-providers-root",
                str(self.local_providers_root),
                "--assign-roles",
                "precision",
                "--generate-aipd-launcher",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

        registry = json.loads((self.repo_root / "config" / "provider_registry.json").read_text(encoding="utf-8"))
        self.assertIn("glm", registry["providers"])
        self.assertEqual(registry["role_defaults"]["precision_execution_provider"], "glm")

        self.assertTrue((self.local_providers_root / "profiles" / "glm.env.example").exists())
        self.assertTrue((self.local_providers_root / "launchers" / "claude-glm").exists())
        self.assertTrue((self.local_providers_root / "launchers" / "claude-glm-aipd").exists())
        self.assertTrue((self.repo_root / "runtime" / "glm_adapter" / "bin" / "glm_app_server.py").exists())

    def _copy(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
