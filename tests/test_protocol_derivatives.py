from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ProtocolDerivativesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="protocol-derivatives-")
        self.repo_root = Path(self.temp_dir.name) / "repo"
        self.repo_root.mkdir(parents=True, exist_ok=True)
        for rel_path in [
            "README.md",
            "HARNESS.md",
            "config",
            "docs",
            "prompts",
            "schemas",
            "scripts",
            "templates",
            "translations",
        ]:
            source = REPO_ROOT / rel_path
            target = self.repo_root / rel_path
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_python(self, script_rel: str, *args: str, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(self.repo_root / script_rel), *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        if expected is not None:
            self.assertEqual(completed.returncode, expected, msg=completed.stdout + completed.stderr)
        return completed

    def test_generate_all_creates_compact_manifest_and_zh_outputs(self) -> None:
        self.run_python("scripts/generate_protocol_derivatives.py", "all")
        self.assertTrue((self.repo_root / "generated" / "protocol_compact.json").exists())
        self.assertTrue((self.repo_root / "generated" / "protocol_derivatives_manifest.json").exists())
        self.assertTrue((self.repo_root / "README.zh.md").exists())
        self.assertTrue((self.repo_root / "docs" / "zh" / "00_lifecycle.md").exists())
        self.assertTrue((self.repo_root / "templates" / "zh" / "CONSTITUTION.template.md").exists())
        self.run_python("scripts/sdd_guard.py", "check-protocol")

    def test_check_protocol_fails_when_compact_source_changes_without_regeneration(self) -> None:
        self.run_python("scripts/generate_protocol_derivatives.py", "all")
        readme = self.repo_root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n<!-- stale -->\n", encoding="utf-8")
        completed = self.run_python("scripts/sdd_guard.py", "check-protocol", expected=1)
        self.assertIn("stale source digest", completed.stdout)

    def test_check_protocol_fails_when_manifest_is_missing(self) -> None:
        self.run_python("scripts/generate_protocol_derivatives.py", "all")
        (self.repo_root / "generated" / "protocol_derivatives_manifest.json").unlink()
        completed = self.run_python("scripts/sdd_guard.py", "check-protocol", expected=1)
        self.assertIn("missing file: generated/protocol_derivatives_manifest.json", completed.stdout)

    def test_check_protocol_fails_when_generated_translation_is_missing(self) -> None:
        self.run_python("scripts/generate_protocol_derivatives.py", "all")
        (self.repo_root / "docs" / "zh" / "01_principles.md").unlink()
        completed = self.run_python("scripts/sdd_guard.py", "check-protocol", expected=1)
        self.assertIn("missing file: docs/zh/01_principles.md", completed.stdout)

    def test_prompts_no_longer_embed_full_chinese_mirror(self) -> None:
        for rel_path in [
            "prompts/BUILDER.system.md",
            "prompts/SPEC_ARCHITECT.system.md",
            "prompts/REVIEWER.system.md",
        ]:
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertNotIn("## 中文翻译", text)
            self.assertNotIn("Read `README.md` and `docs/00_lifecycle.md` before acting.", text)
            self.assertIn("generated/protocol_compact.json", text)


if __name__ == "__main__":
    unittest.main()
