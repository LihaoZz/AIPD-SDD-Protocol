from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "bin" / "{{provider_id}}_app_server.py"


class {{class_name}}AppServerTest(unittest.TestCase):
    def test_successful_turn_emits_completion(self) -> None:
        launcher = self._write_launcher(
            """
            #!/usr/bin/env python3
            import json
            print(json.dumps({"result": "{{provider_id}} success"}))
            """
        )
        messages = self._run_session(launcher, approval_policy="never")
        self.assertEqual(messages[3]["method"], "codex/event/agent_message_content_delta")
        self.assertEqual(messages[4]["method"], "turn/completed")

    def test_failed_turn_emits_failed_event(self) -> None:
        launcher = self._write_launcher(
            """
            #!/usr/bin/env python3
            import sys
            sys.stderr.write("{{provider_id}} failure\\n")
            sys.exit(4)
            """
        )
        messages = self._run_session(launcher, approval_policy="never")
        self.assertEqual(messages[3]["method"], "turn/failed")

    def _run_session(self, launcher: Path, approval_policy: str) -> list[dict[str, object]]:
        env = dict(os.environ)
        env["{{provider_id_upper}}_CLAUDE_LAUNCHER"] = str(launcher)
        session = subprocess.run(
            [sys.executable, str(ENTRYPOINT), "app-server"],
            input="\\n".join(
                [
                    json.dumps({"method": "initialize", "id": 1, "params": {}}),
                    json.dumps({"method": "initialized", "params": {}}),
                    json.dumps({"method": "thread/start", "id": 2, "params": {"cwd": "/tmp/project", "approvalPolicy": approval_policy}}),
                    json.dumps({"method": "turn/start", "id": 3, "params": {"threadId": "thread-1", "approvalPolicy": approval_policy, "input": [{"type": "text", "text": "Build the mission block."}]}}),
                ]
            ) + "\\n",
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        self.assertEqual(session.returncode, 0, session.stderr)
        return [json.loads(line) for line in session.stdout.splitlines() if line.strip()]

    def _write_launcher(self, body: str) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="{{provider_id}}-launcher-"))
        launcher = temp_dir / "claude-{{provider_id}}"
        launcher.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
        return launcher


if __name__ == "__main__":
    unittest.main()
