#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from harness_common import read_json, resolve_path
from hook_runtime import run_pre_tool_hook


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the harness pre-tool hook.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--tool-name", default="codex_exec")
    parser.add_argument("--tool-action", required=True)
    args = parser.parse_args()

    event = run_pre_tool_hook(
        resolve_path(args.project_root),
        read_json(resolve_path(args.spec)),
        resolve_path(args.attempt_dir),
        [args.tool_action],
        args.tool_name,
    )
    print(json.dumps(event, ensure_ascii=True, indent=2))
    return 0 if event["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
