#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_arg(flag: str, args: list[str]) -> str | None:
    for index, arg in enumerate(args):
        if arg == flag and index + 1 < len(args):
            return args[index + 1]
    return None


def main() -> int:
    args = sys.argv[1:]
    cwd = parse_arg("--cd", args)
    output_last_message = parse_arg("--output-last-message", args)
    prompt = sys.stdin.read()
    mb_match = re.search(r"MB ID:\s*(fb[0-9]+-mb[0-9]+)", prompt)
    retry_match = re.search(r"Retry Count:\s*([0-9]+)", prompt)
    mb_id = mb_match.group(1) if mb_match else "unknown"
    retry_count = int(retry_match.group(1)) if retry_match else 0

    project_root = Path(cwd).resolve()
    src_file = project_root / "src" / "app.py"
    out_of_scope = project_root / "src" / "out_of_scope.txt"
    out_of_scope.parent.mkdir(parents=True, exist_ok=True)

    if mb_id == "fb1-mb1":
        src_file.write_text("PASS_ONE\n", encoding="utf-8")
        message = "Applied PASS_ONE to src/app.py"
    elif mb_id == "fb1-mb2":
        out_of_scope.write_text("VIOLATION\n", encoding="utf-8")
        message = "Wrote an out-of-scope file."
    elif mb_id == "fb1-mb3":
        if retry_count == 0:
            src_file.write_text("NOT_YET\n", encoding="utf-8")
            message = "First attempt did not satisfy verification."
        else:
            src_file.write_text("PASS_THREE\n", encoding="utf-8")
            message = "Retry fixed the verification failure."
    elif mb_id == "fb1-mb4":
        src_file.write_text("STILL_FAILING\n", encoding="utf-8")
        message = "Attempt still fails verification."
    elif mb_id == "fb1-mb5":
        message = (
            "Blocked by contract conflict, so I did not edit `src/app.py`.\n\n"
            "This should be routed as a `spec_gap` before implementation.\n\n"
            "Changed files: none."
        )
    elif mb_id == "fb1-mb6":
        src_file.write_text("PASS_SIX\n", encoding="utf-8")
        message = "Applied PASS_SIX to src/app.py for eval asset verification."
    elif mb_id == "fb1-mb7":
        src_file.write_text("PASS_SEVEN\n", encoding="utf-8")
        message = "Applied PASS_SEVEN to src/app.py after human approval."
    else:
        message = "Unknown MB."

    if output_last_message:
        Path(output_last_message).write_text(message + "\n", encoding="utf-8")
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
