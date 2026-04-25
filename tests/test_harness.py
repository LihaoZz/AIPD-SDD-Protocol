from __future__ import annotations

import hashlib
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

    def run_mb(self, mb_id: str, *extra_args: str, expected: int | None = 0) -> subprocess.CompletedProcess[str]:
        return self.run_python(
            "mb_runner.py",
            "--project-root",
            str(self.project_root),
            "--mb-id",
            mb_id,
            "--codex-command",
            str(FAKE_CODEX),
            *extra_args,
            expected=expected,
        )

    def read_json(self, relative_path: str) -> dict:
        return json.loads((self.project_root / relative_path).read_text(encoding="utf-8"))

    def write_lock(self, kind: str, name: str) -> None:
        path = self.project_root / "runtime" / "locks" / kind / f"{name}.lock"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"held_by": "test"}), encoding="utf-8")

    def lock_token(self, raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def test_validate_mb_spec_passes(self) -> None:
        self.run_python("validate_mb_spec.py", str(self.project_root / "missions" / "fb1-mb1.machine.json"))

    def test_validate_mb_spec_fails_on_missing_field(self) -> None:
        spec_path = self.project_root / "missions" / "broken.machine.json"
        spec = self.read_json("missions/fb1-mb1.machine.json")
        spec.pop("allowed_touch")
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        completed = self.run_python("validate_mb_spec.py", str(spec_path), expected=1)
        self.assertIn("allowed_touch", completed.stdout)

    def test_gate_outcome_examples_validate(self) -> None:
        examples_dir = REPO_ROOT / "schemas" / "examples" / "aipd-gate-outcome"
        for path in sorted(examples_dir.glob("*.json")):
            self.run_python("sdd_guard.py", "check-gate-outcome", str(path))

    def test_gate_outcome_rejects_unknown_symphony_action(self) -> None:
        example_path = REPO_ROOT / "schemas" / "examples" / "aipd-gate-outcome" / "start-pass.json"
        gate_outcome = json.loads(example_path.read_text(encoding="utf-8"))
        gate_outcome["symphony_instruction"]["action"] = "invent_action"
        broken_path = self.project_root / "runtime" / "broken-gate-outcome.json"
        broken_path.parent.mkdir(parents=True, exist_ok=True)
        broken_path.write_text(json.dumps(gate_outcome), encoding="utf-8")
        completed = self.run_python("sdd_guard.py", "check-gate-outcome", str(broken_path), expected=1)
        self.assertIn("invent_action", completed.stdout)

    def test_gate_outcome_rejects_malformed_json(self) -> None:
        broken_path = self.project_root / "runtime" / "malformed-gate-outcome.json"
        broken_path.parent.mkdir(parents=True, exist_ok=True)
        broken_path.write_text('{"gate": "attempt_start"', encoding="utf-8")
        completed = self.run_python("sdd_guard.py", "check-gate-outcome", str(broken_path), expected=1)
        self.assertIn("not valid JSON", completed.stdout)

    def test_gate_outcome_rejects_non_dispatch_codex_start(self) -> None:
        example_path = REPO_ROOT / "schemas" / "examples" / "aipd-gate-outcome" / "start-reject.json"
        gate_outcome = json.loads(example_path.read_text(encoding="utf-8"))
        gate_outcome["symphony_instruction"]["may_start_codex"] = True
        broken_path = self.project_root / "runtime" / "unsafe-gate-outcome.json"
        broken_path.parent.mkdir(parents=True, exist_ok=True)
        broken_path.write_text(json.dumps(gate_outcome), encoding="utf-8")
        completed = self.run_python("sdd_guard.py", "check-gate-outcome", str(broken_path), expected=1)
        self.assertIn("dispatch_codex", completed.stdout)

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
            "autonomy_level": "L2_auto_with_review",
            "approval_status": "not_required",
            "review_required": False,
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
        self.assertEqual(state["autonomy_level"], "L2_auto_with_review")
        self.assertTrue(state["review_required"])
        self.assertEqual(state["next_action"], "handoff_to_review")
        report = self.read_json("runtime/attempts/fb1-mb1/attempt-001/verification_report.json")
        self.assertEqual(report["result"], "pass")
        project_memory = self.read_json("runtime/memory/project_memory.json")
        self.assertEqual(project_memory["completed_mbs"][0]["mb_id"], "fb1-mb1")
        session_state = (self.project_root / "SESSION_STATE.md").read_text(encoding="utf-8")
        self.assertIn("runtime/state/fb1-mb1.state.json", session_state)
        self.assertTrue((self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001" / "pre_tool_hook.json").exists())
        self.assertTrue((self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001" / "post_tool_hook.json").exists())
        self.assertTrue((self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001" / "stop_hook.json").exists())
        start_outcome = self.read_json("runtime/attempts/fb1-mb1/attempt-001/attempt_start_gate_outcome.json")
        finish_outcome = self.read_json("runtime/attempts/fb1-mb1/attempt-001/attempt_finish_gate_outcome.json")
        self.assertEqual(start_outcome["symphony_instruction"]["action"], "dispatch_codex")
        self.assertEqual(finish_outcome["symphony_instruction"]["action"], "release_to_review")
        locks_root = self.project_root / "runtime" / "locks"
        self.assertFalse(locks_root.exists() and list(locks_root.rglob("*.lock")))

    def test_mb_runner_scope_violation_routes_recovery(self) -> None:
        self.run_mb("fb1-mb2", expected=1)
        state = self.read_json("runtime/state/fb1-mb2.state.json")
        self.assertEqual(state["status"], "routed_to_recovery")
        self.assertEqual(state["last_failure_reason"], "scope_violation")
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb2" / "attempt-001" / "verification_report.json").exists())
        finish_outcome = self.read_json("runtime/attempts/fb1-mb2/attempt-001/attempt_finish_gate_outcome.json")
        self.assertEqual(finish_outcome["aipd_decision"]["issue_type"], "state_drift")
        self.assertEqual(finish_outcome["aipd_decision"]["route_to"], "recovery_coordinator")
        self.assertEqual(finish_outcome["symphony_instruction"]["action"], "stop_and_route_recovery")
        failure_log = self.read_json("runtime/memory/failure_log.json")
        self.assertEqual(failure_log["failures"][0]["failure_type"], "scope_violation")

    def test_mb_runner_retry_uses_verification_feedback_then_passes(self) -> None:
        self.run_mb("fb1-mb3")
        state = self.read_json("runtime/state/fb1-mb3.state.json")
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["retry_count"], 1)
        self.assertTrue(state["review_required"])
        second_prompt = (self.project_root / "runtime" / "attempts" / "fb1-mb3" / "attempt-002" / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("Verification Digest:", second_prompt)
        self.assertIn("Retry Count: 1", second_prompt)
        retry_outcome = self.read_json("runtime/attempts/fb1-mb3/attempt-001/attempt_finish_gate_outcome.json")
        pass_outcome = self.read_json("runtime/attempts/fb1-mb3/attempt-002/attempt_finish_gate_outcome.json")
        self.assertEqual(retry_outcome["symphony_instruction"]["action"], "schedule_semantic_retry")
        self.assertTrue(retry_outcome["symphony_instruction"]["retryable"])
        self.assertEqual(pass_outcome["symphony_instruction"]["action"], "release_to_review")
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
        recovery_outcome = self.read_json("runtime/attempts/fb1-mb4/attempt-003/attempt_finish_gate_outcome.json")
        self.assertEqual(recovery_outcome["symphony_instruction"]["action"], "stop_and_route_recovery")
        self.assertFalse(recovery_outcome["symphony_instruction"]["retryable"])

    def test_mb_runner_routes_explicit_spec_gap_without_retry(self) -> None:
        self.run_mb("fb1-mb5", expected=1)
        state = self.read_json("runtime/state/fb1-mb5.state.json")
        self.assertEqual(state["status"], "routed_to_recovery")
        self.assertEqual(state["retry_count"], 0)
        self.assertEqual(state["last_attempt_id"], "attempt-001")
        self.assertEqual(state["last_failure_reason"], "spec_gap")
        report_path = self.project_root / "runtime" / "attempts" / "fb1-mb5" / "attempt-001" / "verification_report.json"
        self.assertFalse(report_path.exists())
        finish_outcome = self.read_json("runtime/attempts/fb1-mb5/attempt-001/attempt_finish_gate_outcome.json")
        self.assertEqual(finish_outcome["aipd_decision"]["status"], "routed_to_owner")
        self.assertEqual(finish_outcome["aipd_decision"]["issue_type"], "spec_gap")
        self.assertEqual(finish_outcome["aipd_decision"]["route_to"], "spec_architect")
        self.assertEqual(finish_outcome["symphony_instruction"]["action"], "stop_and_route_owner")
        failure_log = self.read_json("runtime/memory/failure_log.json")
        self.assertEqual(failure_log["failures"][0]["failure_type"], "spec_gap")
        self.assertEqual(failure_log["failures"][0]["result"], "routed_to_recovery")

    def test_mb_runner_eval_asset_success_l3_closes(self) -> None:
        self.run_mb("fb1-mb6")
        state = self.read_json("runtime/state/fb1-mb6.state.json")
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["autonomy_level"], "L3_full_auto")
        self.assertFalse(state["review_required"])
        self.assertEqual(state["next_action"], "close_mb")
        report = self.read_json("runtime/attempts/fb1-mb6/attempt-001/verification_report.json")
        check_sources = {(item["check_id"], item["source_kind"]) for item in report["checks"]}
        self.assertIn(("contains_pass_six", "eval_asset"), check_sources)

    def test_mb_runner_l1_requires_approval_then_runs(self) -> None:
        self.run_mb("fb1-mb7", expected=1)
        blocked_state = self.read_json("runtime/state/fb1-mb7.state.json")
        self.assertEqual(blocked_state["status"], "blocked")
        self.assertEqual(blocked_state["approval_status"], "pending")
        self.assertEqual(blocked_state["last_failure_reason"], "human_approval_required")
        start_reject = self.read_json("runtime/gate_outcomes/fb1-mb7/attempt_start.json")
        self.assertEqual(start_reject["symphony_instruction"]["action"], "pause_wait_human")
        self.assertFalse(start_reject["symphony_instruction"]["may_start_codex"])
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb7").exists())

        self.run_mb("fb1-mb7", "--approve")
        state = self.read_json("runtime/state/fb1-mb7.state.json")
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["approval_status"], "approved")
        self.assertTrue(state["review_required"])
        self.assertEqual(state["next_action"], "handoff_to_review")

    def test_mb_runner_defers_when_same_mb_lock_exists(self) -> None:
        self.write_lock("mb", "fb1-mb1")
        self.run_mb("fb1-mb1", expected=1)
        start_reject = self.read_json("runtime/gate_outcomes/fb1-mb1/attempt_start.json")
        self.assertEqual(start_reject["symphony_instruction"]["action"], "defer_retry")
        self.assertFalse(start_reject["symphony_instruction"]["may_start_codex"])
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb1").exists())

    def test_mb_runner_defers_on_exclusive_touch_overlap(self) -> None:
        self.write_lock("touch", self.lock_token("src/app.py"))
        self.run_mb("fb1-mb1", expected=1)
        start_reject = self.read_json("runtime/gate_outcomes/fb1-mb1/attempt_start.json")
        self.assertEqual(start_reject["symphony_instruction"]["action"], "defer_retry")
        self.assertIn("touch", start_reject["reason"])
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb1").exists())

    def test_mb_runner_defers_on_shared_write_artifact_overlap(self) -> None:
        spec_path = self.project_root / "missions" / "fb1-mb1.machine.json"
        spec = self.read_json("missions/fb1-mb1.machine.json")
        spec["concurrency"] = {
            "shared_write_artifacts": ["SESSION_STATE.md"]
        }
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        self.write_lock("artifact", self.lock_token("SESSION_STATE.md"))
        self.run_mb("fb1-mb1", expected=1)
        start_reject = self.read_json("runtime/gate_outcomes/fb1-mb1/attempt_start.json")
        self.assertEqual(start_reject["symphony_instruction"]["action"], "defer_retry")
        self.assertIn("artifact", start_reject["reason"])
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb1").exists())

    def test_mb_runner_blocks_on_unresolved_mb_dependency(self) -> None:
        spec_path = self.project_root / "missions" / "fb1-mb1.machine.json"
        spec = self.read_json("missions/fb1-mb1.machine.json")
        spec["concurrency"] = {
            "blocked_by_mbs": ["fb1-mb2"]
        }
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        self.run_mb("fb1-mb1", expected=1)
        start_reject = self.read_json("runtime/gate_outcomes/fb1-mb1/attempt_start.json")
        self.assertEqual(start_reject["symphony_instruction"]["action"], "release_and_wait_input")
        self.assertFalse(start_reject["symphony_instruction"]["may_start_codex"])
        self.assertFalse((self.project_root / "runtime" / "attempts" / "fb1-mb1").exists())

    def test_legacy_mb_without_autonomy_defaults_to_l2(self) -> None:
        spec_path = self.project_root / "missions" / "fb1-mb1.machine.json"
        spec = self.read_json("missions/fb1-mb1.machine.json")
        spec.pop("autonomy_level")
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        self.run_mb("fb1-mb1")
        state = self.read_json("runtime/state/fb1-mb1.state.json")
        self.assertEqual(state["autonomy_level"], "L2_auto_with_review")
        self.assertTrue(state["review_required"])

    def test_memory_bridge_injects_failure_and_validated_patterns(self) -> None:
        (self.project_root / "runtime" / "memory").mkdir(parents=True, exist_ok=True)
        (self.project_root / "runtime" / "memory" / "project_memory.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "completed_mbs": [
                        {
                            "mb_id": "fb1-mb0",
                            "parent_fb_id": "fb1",
                            "result": "passed",
                            "validated_evidence": ["A validated fix path exists."],
                            "key_decisions": ["Prior validated pattern."],
                            "reusable_notes": ["Prefer the small validated write path."],
                            "tags": ["fb1", "validated"],
                            "pattern_type": "validated_good_pattern",
                            "applicability": {
                                "mb_ids": [],
                                "parent_fb_ids": ["fb1"],
                                "notes": "fixture"
                            },
                            "recorded_at": "2026-04-09T08:00:00-07:00",
                            "timezone_name": "America/Los_Angeles"
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (self.project_root / "runtime" / "memory" / "failure_log.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "failures": [
                        {
                            "mb_id": "fb1-mb0",
                            "parent_fb_id": "fb1",
                            "attempt_id": "attempt-001",
                            "failure_type": "verification_failed",
                            "condition": "Regex-only fix failed to reach the real entry path.",
                            "attempted_fix": "Avoid regex-only fix",
                            "result": "retry",
                            "root_cause_guess": "verification_failed",
                            "repeated_failure_key": "verification_failed:regex-only",
                            "tags": ["fb1", "verification_failed"],
                            "recorded_at": "2026-04-09T08:05:00-07:00",
                            "timezone_name": "America/Los_Angeles"
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.run_mb("fb1-mb1")
        prompt = (self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001" / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("## Memory Context", prompt)
        self.assertIn("Regex-only fix failed to reach the real entry path.", prompt)
        self.assertIn("Prefer the small validated write path.", prompt)

    def test_quality_memory_is_synced_from_runtime_memory(self) -> None:
        self.run_mb("fb1-mb3")
        quality_memory = (self.project_root / "QUALITY_MEMORY.md").read_text(encoding="utf-8")
        self.assertIn("## Repeated Failure Patterns", quality_memory)
        self.assertIn("## Validated Good Patterns", quality_memory)
        self.assertIn("fb1-mb3", quality_memory)

    def test_pre_tool_hook_blocks_dangerous_action(self) -> None:
        attempt_dir = self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        completed = self.run_python(
            "pre_tool_hook.py",
            "--project-root",
            str(self.project_root),
            "--spec",
            str(self.project_root / "missions" / "fb1-mb1.machine.json"),
            "--attempt-dir",
            str(attempt_dir),
            "--tool-action",
            "rm -rf /tmp/danger",
            expected=1,
        )
        self.assertIn('"status": "block"', completed.stdout)

    def test_stop_hook_blocks_when_verification_is_missing(self) -> None:
        attempt_dir = self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        completed = self.run_python(
            "stop_hook.py",
            "--spec",
            str(self.project_root / "missions" / "fb1-mb1.machine.json"),
            "--attempt-dir",
            str(attempt_dir),
            "--final-status",
            "passed",
            expected=1,
        )
        self.assertIn('"status": "block"', completed.stdout)

    def test_direct_codex_wrapper_uses_same_hooks(self) -> None:
        self.run_python(
            "codex_exec_with_hooks.py",
            "--project-root",
            str(self.project_root),
            "--mb-id",
            "fb1-mb1",
            "--codex-command",
            str(FAKE_CODEX),
        )
        attempt_root = self.project_root / "runtime" / "attempts" / "fb1-mb1" / "attempt-001"
        self.assertTrue((attempt_root / "pre_tool_hook.json").exists())
        self.assertTrue((attempt_root / "post_tool_hook.json").exists())


if __name__ == "__main__":
    unittest.main()
