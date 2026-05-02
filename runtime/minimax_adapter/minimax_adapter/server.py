from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_LAUNCHER = Path("~/.claude/providers/launchers/claude-minimax").expanduser()


@dataclass
class LauncherResult:
    success: bool
    text: str
    stdout: str
    stderr: str
    exit_code: int


class MiniMaxAppServer:
    def __init__(self) -> None:
        self._thread_counter = 0
        self._turn_counter = 0

    def run(self) -> int:
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            self._handle_message(payload)

        return 0

    def _handle_message(self, payload: dict[str, Any]) -> None:
        method = payload.get("method")

        if method == "initialize":
            self._send({"id": payload.get("id"), "result": {}})
            return

        if method == "initialized":
            return

        if method == "thread/start":
            self._thread_counter += 1
            self._send(
                {
                    "id": payload.get("id"),
                    "result": {"thread": {"id": f"minimax-thread-{self._thread_counter}"}},
                }
            )
            return

        if method == "turn/start":
            self._turn_counter += 1
            turn_id = f"minimax-turn-{self._turn_counter}"
            self._send({"id": payload.get("id"), "result": {"turn": {"id": turn_id}}})
            self._run_turn(turn_id, payload.get("params") or {})
            return

    def _run_turn(self, turn_id: str, params: dict[str, Any]) -> None:
        approval_policy = params.get("approvalPolicy")
        prompt = self._prompt_from_params(params)

        if approval_policy != "never":
            self._send(
                {
                    "method": "turn/failed",
                    "params": {
                        "turn_id": turn_id,
                        "message": "MiniMax adapter only supports approvalPolicy=never in v1.",
                        "reason": "unsupported_approval_policy",
                    },
                }
            )
            return

        result = self._invoke_launcher(prompt)

        if result.success:
            if result.text:
                self._send(
                    {
                        "method": "codex/event/agent_message_content_delta",
                        "params": {"msg": {"content": result.text}},
                    }
                )

            self._send({"method": "turn/completed", "params": {"turn_id": turn_id}})
            return

        self._send(
            {
                "method": "turn/failed",
                "params": {
                    "turn_id": turn_id,
                    "message": result.text or "MiniMax launcher failed.",
                    "exit_code": result.exit_code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            }
        )

    def _invoke_launcher(self, prompt: str) -> LauncherResult:
        launcher = Path(os.environ.get("MINIMAX_CLAUDE_LAUNCHER", DEFAULT_LAUNCHER)).expanduser()

        if not launcher.is_file():
            return LauncherResult(
                success=False,
                text=f"MiniMax launcher not found: {launcher}",
                stdout="",
                stderr="",
                exit_code=127,
            )

        command = [
            str(launcher),
            "-p",
            "--output-format",
            "json",
            "--permission-mode",
            "bypassPermissions",
            prompt,
        ]

        completed = subprocess.run(command, text=True, capture_output=True)
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        text = extract_launcher_text(stdout) or stderr or stdout

        return LauncherResult(
            success=completed.returncode == 0,
            text=text,
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
        )

    @staticmethod
    def _prompt_from_params(params: dict[str, Any]) -> str:
        items = params.get("input") or []
        texts = []

        for item in items:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str):
                    texts.append(text)

        return "\n\n".join(texts)

    @staticmethod
    def _send(payload: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
        sys.stdout.flush()


def extract_launcher_text(stdout: str) -> str:
    if not stdout:
        return ""

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout.strip()

    if isinstance(payload, dict):
        for key in ("result", "text", "content"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        content = payload.get("messages") or payload.get("content")
        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str) and text.strip():
                        chunks.append(text.strip())
            if chunks:
                return "\n".join(chunks)

    return stdout.strip()
