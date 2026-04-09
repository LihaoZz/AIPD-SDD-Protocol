#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from harness_common import read_json, resolve_path
from hook_runtime import run_post_tool_hook


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the harness post-tool hook.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--execution-result", required=True)
    parser.add_argument("--changed-files-json", required=True)
    args = parser.parse_args()

    event = run_post_tool_hook(
        read_json(resolve_path(args.spec)),
        resolve_path(args.attempt_dir),
        read_json(resolve_path(args.execution_result)),
        read_json(resolve_path(args.changed_files_json)),
    )
    print(json.dumps(event, ensure_ascii=True, indent=2))
    return 0 if event["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
