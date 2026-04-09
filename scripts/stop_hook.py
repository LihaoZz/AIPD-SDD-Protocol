#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from harness_common import read_json, resolve_path
from hook_runtime import run_stop_hook


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the harness stop hook.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--attempt-dir", required=True)
    parser.add_argument("--final-status", required=True)
    parser.add_argument("--verification-report")
    args = parser.parse_args()

    event = run_stop_hook(
        read_json(resolve_path(args.spec)),
        resolve_path(args.attempt_dir),
        args.final_status,
        resolve_path(args.verification_report) if args.verification_report else None,
    )
    print(json.dumps(event, ensure_ascii=True, indent=2))
    return 0 if event["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
