#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json

from harness_common import (
    attempt_dir,
    initialize_runtime_memory,
    load_execution_policy,
    mission_machine_spec_path,
    read_json,
    resolve_execution_policy,
    resolve_path,
    write_json,
)
from hook_runtime import run_post_tool_hook, run_pre_tool_hook
from mb_runner import build_codex_exec_command, build_prompt, effective_autonomy_level, next_attempt_id, run_codex_cli
from memory_bridge import lookup_memory_context
from scope_guard import changed_files, snapshot_workspace
from state_writer import load_state


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one direct Codex exec attempt with mandatory harness hooks.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--codex-command", default="codex")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stream-codex-output", action="store_true")
    parser.add_argument("--codex-json", action="store_true")
    args = parser.parse_args()

    project_root = resolve_path(args.project_root)
    initialize_runtime_memory(project_root)
    spec = read_json(mission_machine_spec_path(project_root, args.mb_id))
    state = load_state(project_root, args.mb_id)
    state["autonomy_level"] = effective_autonomy_level(spec)
    memory_context = lookup_memory_context(project_root, spec, state)

    attempt_id = next_attempt_id(project_root, args.mb_id)
    current_attempt_dir = attempt_dir(project_root, args.mb_id, attempt_id)
    current_attempt_dir.mkdir(parents=True, exist_ok=True)
    execution_policy = resolve_execution_policy(load_execution_policy(), args.mb_id, attempt_id)
    write_json(current_attempt_dir / "resolved_execution_policy.json", execution_policy)

    prompt = build_prompt(project_root, spec, state, memory_context)
    (current_attempt_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    command = build_codex_exec_command(
        project_root,
        current_attempt_dir,
        args.codex_command,
        execution_policy["sandbox"]["mode"],
        args.model,
        args.codex_json,
    )
    pre_hook = run_pre_tool_hook(project_root, spec, current_attempt_dir, command)
    if pre_hook["status"] != "pass":
        print(json.dumps(pre_hook, ensure_ascii=True, indent=2))
        return 1

    before = snapshot_workspace(project_root)
    execution = run_codex_cli(command, prompt, current_attempt_dir, args.dry_run, args.stream_codex_output)
    write_json(current_attempt_dir / "execution_result.json", execution)
    (current_attempt_dir / "raw_output.txt").write_text(execution["stdout"], encoding="utf-8")
    (current_attempt_dir / "raw_error.txt").write_text(execution["stderr"], encoding="utf-8")

    after = snapshot_workspace(project_root)
    changes = changed_files(before, after)
    write_json(current_attempt_dir / "changed_files.json", changes)
    post_hook = run_post_tool_hook(spec, current_attempt_dir, execution, changes)

    print(
        json.dumps(
            {
                "attempt_id": attempt_id,
                "pre_tool_hook": pre_hook["status"],
                "post_tool_hook": post_hook["status"],
                "changed_files": changes,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0 if execution["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
