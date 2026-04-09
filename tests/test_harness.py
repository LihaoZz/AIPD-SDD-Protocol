from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_PROJECT = REPO_ROOT / "tests" / "fixtures" / "base_project"
FAKE_CODEX = REPO_ROOT / "tests" / "fixtures" / "bin" / "fake_codex.py"


class HarnessTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="harness-test-")
        self.project_root = Path(self.temp_dir.name) / "project"
        shutil.copytree(BASE_PROJECT, self.project_root)
        runtime_dir = self.project_root / "runtime"
        if runtime_dir.exists():
            shutil.rmtree(runtime_dir)
        (self.project_root / "src" / "app.py").write_text("INITIAL\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_python(self, script: str, *args: str, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / script), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if expected is not None:
            self.assertEqual(completed.returncode, expected, msg=completed.stdout + completed.stderr)
        return completed

    def run_mb(self, mb_id: str, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
        return self.run_python(
            "mb_runner.py",
            "--project-root",
            str(self.project_root),
            "--mb-id",
            mb_id,
            "--codex-command",
            str(FAKE_CODEX),
            expected=expected,
        )

    def read_json(self, relative_path: str) -> dict:
        return json.loads((self.project_root / relative_path).read_text(encoding="utf-8"))

    def test_validate_mb_spec_passes(self) -> None:
        self.run_python("validate_mb_spec.py", str(self.project_root / "missions" / "fb1-mb1.machine.json"))

    def test_validate_mb_spec_fails_on_missing_field(self) -> None:
        spec_path = self.project_root / "missions" / "broken.machine.json"
        spec = self.read_json("missions/fb1-mb1.machine.json")
        spec.pop("allowed_touch")
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        completed = self.run_python("validate_mb_spec.py", str(spec_path), expected=1)
        self.assertIn("allowed_touch", completed.stdout)

    def test_validate_mission_rejects_runtime_managed_session_state_update(self) -> None:
        mission_path = self.project_root / "missions" / "broken-session-state.md"
        mission_text = (self.project_root / "missions" / "fb1-mb1.md").read_text(encoding="utf-8")
        mission_text = mission_text.replace(
            "- `required_artifact_updates`: none",
            "- `required_artifact_updates`: SESSION_STATE.md",
        )
        mission_text += "\n\n## Usage Rules\n\n- Fixture only\n"
        mission_path.write_text(mission_text, encoding="utf-8")
        completed = self.run_python("sdd_guard.py", "check-mission", str(mission_path), expected=1)
        self.assertIn("must not list SESSION_STATE.md", completed.stdout)

    def test_session_preflight_ready_bootstrap_and_blocked(self) -> None:
        ready = self.run_python("preflight.py", "--level", "session", "--project-root", str(self.project_root))
        self.assertIn('"result": "ready"', ready.stdout)

        bootstrap_root = Path(self.temp_dir.name) / "bootstrap"
        shutil.copytree(BASE_PROJECT, bootstrap_root)
        (bootstrap_root / "DECISIONS.md").unlink()
        bootstrap = self.run_python("preflight.py", "--level", "session", "--project-root", str(bootstrap_root))
        self.assertIn('"result": "bootstrap_required"', bootstrap.stdout)

        blocked_root = Path(self.temp_dir.name) / "blocked"
        shutil.copytree(BASE_PROJECT, blocked_root)
        session_state = blocked_root / "SESSION_STATE.md"
        session_state.write_text(
            """# Session State

## Current Context

- `project`: blocked
- `mode`: continue
- `stage`: SCENE_WORK
- `active_function_block`: fb9
- `active_mission_block`: fb9-mb1

## Latest Status

- `completed`: none
- `failed`: none
- `blocked_by`: none
- `runtime_state_ref`: none
- `last_attempt_id`: none
- `last_verification_report_path`: none

## Required Reads

- artifact 1: missions/fb9-mb1.md
- artifact 2: missions/fb9-mb1.machine.json
- artifact 3: function_blocks/fb9.md

## Next Single Action

- `action`: inspect

## Notes For The Next Session

- `assumptions_still_active`: none
- `risks_to_watch`: none
""",
            encoding="utf-8",
        )
        blocked = self.run_python("preflight.py", "--level", "session", "--project-root", str(blocked_root))
        self.assertIn('"result": "blocked"', blocked.stdout)

    def test_mb_preflight_blocks_when_retry_limit_reached(self) -> None:
        state_dir = self.project_root / "runtime" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "schema_version": "1.0",
            "mb_id": "fb1-mb4",
            "status": "failed",
            "retry_count": 3,
            "last_attempt_id": "attempt-003",
            "last_verification_report_path": None,
            "last_verification_digest": None,
            "last_failure_reason": "verification_failed",
            "next_action": "route_to_recovery",
            "updated_at": "2026-04-02T08:00:00-07:00",
            "timezone_name": "America/Los_Angeles",
        }
        (state_dir / "fb1-mb4.state.json").write_text(json.dumps(state), encoding="utf-8")
        completed = self.run_python(
            "preflight.py",
            "--level",
            "mb",
            "--project-root",
            str(self.project_root),
            "--mb-id",
            "fb1-mb4",
        )
        self.assertIn('"result": "blocked"', completed.stdout)

    def test_mb_runner_success_writes_state_and_memory(self) -> None:
        self.run_mb("fb1-mb1")
        state = self.read_json("runtime/state/fb1-mb1.state.json")
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["last_attempt_id"], "attempt-001")
        report = self.read_json("runtime/attempts/fb1-mb1/attempt-001/verification_report.json")
        self.assertEqual(report["result"], "pass")
        project_memory = self.read_json("runtime/memory/project_memory.json")
        self.assertEqual(project_memory["completed_mbs"][0]["mb_id"], "fb1-mb1")
        session_state = (self.project_root / "SESSION_STATE.md").read_text(encoding="utf-8")
        self.assertIn("runtime/state/fb1-mb1.state.json", session_state)

    def test_mb_runner_scope_violation_routes_recovery(self) -> None:
        self.run_mb("fb1-mb2", expected=1)
        state = self.read_json("runtime/state/fb1-mb2.state.json")
        self.assertEqual(state["status"], "routed_to_recovery")
        self.assertEqual(state["last_failure_reason"], "scope_violation")
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb2" / "attempt-001" / "verification_report.json").exists())
        failure_log = self.read_json("runtime/memory/failure_log.json")
        self.assertEqual(failure_log["failures"][0]["failure_type"], "scope_violation")

    def test_mb_runner_retry_uses_verification_feedback_then_passes(self) -> None:
        self.run_mb("fb1-mb3")
        state = self.read_json("runtime/state/fb1-mb3.state.json")
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["retry_count"], 1)
        second_prompt = (self.project_root / "runtime" / "attempts" / "fb1-mb3" / "attempt-002" / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("Verification Digest:", second_prompt)
        self.assertIn("Retry Count: 1", second_prompt)
        failure_log = self.read_json("runtime/memory/failure_log.json")
        self.assertEqual(failure_log["failures"][0]["result"], "retry")

    def test_mb_runner_prompt_warns_about_non_git_workspaces(self) -> None:
        self.run_mb("fb1-mb1")
        prompt_text = (self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001" / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("The workspace may not be a Git repository.", prompt_text)
        self.assertIn("Do not use git status or git diff just to report changed files.", prompt_text)

    def test_mb_runner_stops_at_retry_limit(self) -> None:
        self.run_mb("fb1-mb4", expected=1)
        state = self.read_json("runtime/state/fb1-mb4.state.json")
        self.assertEqual(state["status"], "routed_to_recovery")
        attempts_root = self.project_root / "runtime" / "attempts" / "fb1-mb4"
        attempts = sorted(path.name for path in attempts_root.iterdir() if path.is_dir())
        self.assertEqual(attempts, ["attempt-001", "attempt-002", "attempt-003"])
        third_prompt = (attempts_root / "attempt-003" / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("Retry Count: 2", third_prompt)

    def test_mb_runner_routes_explicit_spec_gap_without_retry(self) -> None:
        self.run_mb("fb1-mb5", expected=1)
        state = self.read_json("runtime/state/fb1-mb5.state.json")
        self.assertEqual(state["status"], "routed_to_recovery")
        self.assertEqual(state["retry_count"], 0)
        self.assertEqual(state["last_attempt_id"], "attempt-001")
        self.assertEqual(state["last_failure_reason"], "spec_gap")
        report_path = self.project_root / "runtime" / "attempts" / "fb1-mb5" / "attempt-001" / "verification_report.json"
        self.assertFalse(report_path.exists())
        failure_log = self.read_json("runtime/memory/failure_log.json")
        self.assertEqual(failure_log["failures"][0]["failure_type"], "spec_gap")
        self.assertEqual(failure_log["failures"][0]["result"], "routed_to_recovery")


if __name__ == "__main__":
    unittest.main()
