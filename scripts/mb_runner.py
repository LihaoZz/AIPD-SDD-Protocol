#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from harness_common import (
    attempt_dir,
    initialize_runtime_memory,
    local_timezone_name,
    mb_preflight_path,
    mission_machine_spec_path,
    mission_markdown_path,
    read_json,
    read_text,
    resolve_path,
    runtime_state_path,
    local_timestamp,
    validate_with_schema,
    write_json,
)
from hook_runtime import run_post_tool_hook, run_pre_tool_hook, run_stop_hook
from memory_bridge import lookup_memory_context, render_memory_context
from preflight import mb_preflight
from provider_registry import ensure_known_provider, load_provider_registry
from scope_guard import changed_files, evaluate_scope, snapshot_workspace
from state_writer import append_failure_log, append_project_memory, load_state, sync_session_state, write_state
from verifier import run_verification


def next_attempt_id(project_root: Path, mb_id: str) -> str:
    root = project_root / "runtime" / "attempts" / mb_id
    if not root.exists():
        return "attempt-001"
    numbers = []
    for child in root.iterdir():
        if child.is_dir() and child.name.startswith("attempt-"):
            try:
                numbers.append(int(child.name.split("-")[-1]))
            except ValueError:
                continue
    next_number = (max(numbers) + 1) if numbers else 1
    return f"attempt-{next_number:03d}"


def build_verification_digest(report: dict[str, Any]) -> str:
    failed = [check for check in report["checks"] if check["status"] == "fail"]
    if not failed:
        return "All verification checks passed."
    parts = []
    for check in failed:
        parts.append(f"{check['check_id']}: {check['evidence']}")
    return " | ".join(parts)


def summarize_output(last_message_path: Path) -> str:
    if not last_message_path.exists():
        return "No final assistant message was produced."
    text = last_message_path.read_text(encoding="utf-8").strip()
    if not text:
        return "Assistant message was empty."
    return text[:400]


def effective_autonomy_level(spec: dict[str, Any]) -> str:
    return spec.get("autonomy_level", "L2_auto_with_review")


def provider_policy(spec: dict[str, Any]) -> dict[str, Any]:
    registry = load_provider_registry()
    raw_policy = spec.get("provider_policy") or {}
    legacy_provider = spec.get("execution_provider")
    default_provider = raw_policy.get(
        "default_provider",
        legacy_provider or registry.role_provider("default_execution_provider"),
    )
    ensure_known_provider(default_provider, registry)

    force_precision_when = raw_policy.get("force_precision_when", [])
    force_deepseek_when = raw_policy.get("force_deepseek_when", [])
    valid_deepseek_force_reasons = {
        "backend_logic",
        "algorithmic_logic",
        "precision_debugging",
        "test_repair",
        "data_transform",
    }
    invalid_precision_reasons = [
        reason for reason in (force_precision_when + force_deepseek_when)
        if reason not in valid_deepseek_force_reasons
    ]
    if invalid_precision_reasons:
        raise ValueError(
            f"Unsupported precision force reasons: {invalid_precision_reasons}"
        )

    force_high_complexity_when = raw_policy.get("force_high_complexity_when", [])
    force_codex_when = raw_policy.get("force_codex_when", [])
    valid_force_reasons = {
        "protocol_change",
        "state_machine_change",
        "multi_subsystem_change",
        "high_risk_migration",
        "deep_debugging",
    }
    invalid_force_reasons = [
        reason for reason in (force_high_complexity_when + force_codex_when)
        if reason not in valid_force_reasons
    ]
    if invalid_force_reasons:
        raise ValueError(f"Unsupported high complexity force reasons: {invalid_force_reasons}")

    escalate_to = raw_policy.get("escalate_to", registry.role_provider("escalation_provider"))
    ensure_known_provider(escalate_to, registry)

    escalate_on_issue_types = raw_policy.get(
        "escalate_on_issue_types",
        ["implementation_bug", "quality_evidence_gap"],
    )
    valid_issue_types = {"implementation_bug", "quality_evidence_gap"}
    invalid_issue_types = [issue_type for issue_type in escalate_on_issue_types if issue_type not in valid_issue_types]
    if invalid_issue_types:
        raise ValueError(f"Unsupported provider_policy.escalate_on_issue_types: {invalid_issue_types}")

    escalate_after_failures = int(
        raw_policy.get(
            "escalate_after_provider_failures",
            raw_policy.get("escalate_after_minimax_failures", 2),
        )
    )
    if escalate_after_failures < 1:
        raise ValueError("provider_policy.escalate_after_provider_failures must be >= 1")

    return {
        "default_provider": default_provider,
        "force_precision_when": force_precision_when,
        "force_deepseek_when": force_deepseek_when,
        "force_high_complexity_when": force_high_complexity_when,
        "force_codex_when": force_codex_when,
        "escalate_to": escalate_to,
        "escalate_after_provider_failures": escalate_after_failures,
        "escalate_on_issue_types": escalate_on_issue_types,
    }


def selected_execution_provider(spec: dict[str, Any], state: dict[str, Any]) -> tuple[str, str]:
    registry = load_provider_registry()
    policy = provider_policy(spec)
    high_complexity_reasons = policy["force_high_complexity_when"] or policy["force_codex_when"]
    if high_complexity_reasons:
        provider_id = registry.role_provider("high_complexity_provider")
        reason_key = "force_codex_when" if policy["force_codex_when"] else "force_high_complexity_when"
        return provider_id, f"{reason_key}={','.join(high_complexity_reasons)}"

    precision_reasons = policy["force_precision_when"] or policy["force_deepseek_when"]
    if precision_reasons:
        provider_id = registry.role_provider("precision_execution_provider")
        reason_key = "force_deepseek_when" if policy["force_deepseek_when"] else "force_precision_when"
        return provider_id, f"{reason_key}={','.join(precision_reasons)}"

    default_provider = policy["default_provider"]
    if default_provider == registry.role_provider("high_complexity_provider"):
        return default_provider, f"default_provider={default_provider}"

    provider_failures = int((state.get("provider_failure_counts") or {}).get(default_provider, 0))
    threshold = policy["escalate_after_provider_failures"]
    last_issue_type = state.get("last_failure_issue_type")
    if provider_failures >= threshold and last_issue_type in set(policy["escalate_on_issue_types"]):
        return policy["escalate_to"], f"escalated_after_{default_provider}_failures={provider_failures}"

    return default_provider, f"default_provider={default_provider}"


def provider_command(
    provider: str,
    codex_command: str,
    minimax_command: str | None,
    deepseek_command: str | None,
) -> str:
    if provider == "codex":
        return codex_command
    if provider == "minimax":
        return minimax_command or codex_command
    if provider == "deepseek":
        return deepseek_command or codex_command
    raise ValueError(f"Unsupported execution provider: {provider}")


def increment_provider_counter(state: dict[str, Any], counter_key: str, provider: str) -> None:
    registry = load_provider_registry()
    counters = state.setdefault(counter_key, {provider_id: 0 for provider_id in registry.provider_ids()})
    for known_provider in registry.provider_ids():
        counters.setdefault(known_provider, 0)
    counters[provider] += 1


def set_failure_issue_type(state: dict[str, Any], issue_type: str | None) -> None:
    state["last_failure_issue_type"] = issue_type


def classify_execution_failure(message_text: str, changed_files: list[str]) -> dict[str, str] | None:
    lower = message_text.lower()
    explicit_routes = {
        "state_drift": "state_drift",
        "environment_issue": "environment_issue",
        "review_context_gap": "review_context_gap",
        "spec_gap": "spec_gap",
    }
    for marker, failure_type in explicit_routes.items():
        if marker in lower:
            return {
                "failure_type": failure_type,
                "condition": f"Assistant explicitly reported {failure_type}.",
            }

    blocked_spec_gap_patterns = [
        r"blocked by protocol conflicts",
        r"upstream conflicts prevent a compliant run",
        r"required upstream inputs (are )?missing",
        r"required inputs are missing",
        r"contract fix before implementation",
        r"scope conflict needs resolution",
        r"missing upstream inputs",
    ]
    if not changed_files and "blocked" in lower:
        for pattern in blocked_spec_gap_patterns:
            if re.search(pattern, lower):
                return {
                    "failure_type": "spec_gap",
                    "condition": "Assistant reported a blocked contract or input conflict.",
                }
    return None


def build_prompt(project_root: Path, spec: dict[str, Any], state: dict[str, Any], memory_context: dict[str, list[dict[str, str]]]) -> str:
    builder_prompt = read_text(Path(__file__).resolve().parent.parent / "prompts" / "BUILDER.system.md")
    mission_md = read_text(mission_markdown_path(project_root, spec["mb_id"]))
    context_sections = []
    for rel_path in spec["context_files"]:
        path = project_root / rel_path
        if path.is_file():
            context_sections.append(f"## Context File: {rel_path}\n\n```\n{read_text(path)}\n```")
    retry_section = ""
    prompt_feedback = spec.get("prompt_feedback") or {}
    if state["retry_count"] > 0:
        retry_parts = []
        if prompt_feedback.get("include_last_verification_digest", True) and state.get("last_verification_digest"):
            retry_parts.append(f"Verification Digest: {state['last_verification_digest']}")
        if prompt_feedback.get("include_last_failure_reason", True) and state.get("last_failure_reason"):
            retry_parts.append(f"Last Failure Reason: {state['last_failure_reason']}")
        if prompt_feedback.get("include_retry_count", True):
            retry_parts.append(f"Retry Count: {state['retry_count']}")
        retry_section = "## Retry Feedback\n\n" + "\n".join(f"- {line}" for line in retry_parts) + "\n"
    memory_section = render_memory_context(memory_context)
    autonomy_level = effective_autonomy_level(spec)

    prompt = f"""{builder_prompt}

## Harness Mission Packet

- Timestamp: {local_timestamp()}
- MB ID: {spec["mb_id"]}
- Parent FB ID: {spec["parent_fb_id"]}
- Goal: {spec["goal"]}
- Autonomy Level: {autonomy_level}
- Allowed Touch: {", ".join(spec["allowed_touch"])}
- Forbidden Touch: {", ".join(spec["forbidden_touch"]) if spec["forbidden_touch"] else "none"}
- Acceptance Checks: {", ".join(check["check_id"] for check in spec["acceptance"])}
- Eval Refs: {", ".join(spec.get("eval_refs", [])) if spec.get("eval_refs") else "none"}

## Active Mission Markdown

```
{mission_md}
```

{retry_section}
{memory_section}
## Execution Rules

- Stay strictly inside allowed touch.
- Do not edit files under forbidden touch.
- Use the retry feedback to fix only the failed checks.
- The workspace may not be a Git repository. Do not use git status or git diff just to report changed files.
- Report changed files from the files you directly edited.
- At the end, reply with a short summary and the changed files.

{chr(10).join(context_sections)}
"""
    return prompt


def build_codex_exec_command(
    project_root: Path,
    attempt_root: Path,
    codex_command: str,
    model: str | None,
    json_output: bool,
) -> list[str]:
    last_message_path = attempt_root / "last_message.txt"
    command = [
        codex_command,
        "exec",
        "--cd",
        str(project_root),
        "--skip-git-repo-check",
        "--full-auto",
        "--ephemeral",
        "--color",
        "never",
        "--output-last-message",
        str(last_message_path),
        "-",
    ]
    if model:
        command[2:2] = ["-m", model]
    if json_output:
        command.insert(-2, "--json")
    return command


def run_codex_cli(
    command: list[str],
    prompt: str,
    attempt_root: Path,
    dry_run: bool,
    stream_output: bool,
) -> dict[str, Any]:
    last_message_path = attempt_root / "last_message.txt"
    if dry_run:
        last_message_path.write_text("DRY RUN: no Codex execution performed.\n", encoding="utf-8")
        return {"returncode": 0, "stdout": "", "stderr": "", "command": command}

    if not stream_output:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "command": command,
        }

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    def consume(stream: Any, buffer: list[str], sink: Any) -> None:
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            buffer.append(line)
            sink.write(line)
            sink.flush()
        stream.close()

    assert process.stdin is not None
    process.stdin.write(prompt)
    process.stdin.close()

    stdout_thread = threading.Thread(target=consume, args=(process.stdout, stdout_chunks, sys.stdout), daemon=True)
    stderr_thread = threading.Thread(target=consume, args=(process.stderr, stderr_chunks, sys.stderr), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    returncode = process.wait()
    stdout_thread.join()
    stderr_thread.join()

    return {
        "returncode": returncode,
        "stdout": "".join(stdout_chunks),
        "stderr": "".join(stderr_chunks),
        "command": command,
    }


def gate_outcome_archive_path(project_root: Path, mb_id: str, gate: str) -> Path:
    return project_root / "runtime" / "gate_outcomes" / mb_id / f"{gate}.json"


def attempt_gate_outcome_path(current_attempt_dir: Path, gate: str) -> Path:
    return current_attempt_dir / f"{gate}_gate_outcome.json"


def build_gate_outcome(
    gate: str,
    mb_id: str,
    attempt_id: str | None,
    status: str,
    issue_type: str | None,
    route_to: str | None,
    next_action: str,
    action: str,
    may_start_agent: bool,
    execution_provider: str | None,
    retryable: bool,
    retry_after_ms: int | None,
    reason: str,
    evidence_refs: list[str],
    state_ref: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "gate": gate,
        "mb_id": mb_id,
        "attempt_id": attempt_id,
        "aipd_decision": {
            "status": status,
            "issue_type": issue_type,
            "route_to": route_to,
            "next_action": next_action,
        },
        "symphony_instruction": {
            "action": action,
            "may_start_agent": may_start_agent,
            "may_start_codex": may_start_agent,
            "execution_provider": execution_provider,
            "retryable": retryable,
            "retry_after_ms": retry_after_ms,
        },
        "reason": reason,
        "evidence_refs": evidence_refs,
        "state_ref": state_ref,
    }


def write_gate_outcome(path: Path, outcome: dict[str, Any]) -> None:
    errors = validate_with_schema(outcome, "aipd-gate-outcome.schema.json")
    if errors:
        raise ValueError("; ".join(errors))
    write_json(path, outcome)


def issue_route(issue_type: str | None) -> str | None:
    return {
        "spec_gap": "spec_architect",
        "implementation_bug": "builder",
        "quality_evidence_gap": "builder",
        "state_drift": "recovery_coordinator",
        "environment_issue": "recovery_coordinator",
        "review_context_gap": "current_scene_lead",
    }.get(issue_type)


def record_attempt_start_rejection(
    project_root: Path,
    mb_id: str,
    issue_type: str,
    route_to: str,
    next_action: str,
    action: str,
    reason: str,
) -> None:
    retryable = action == "defer_retry"
    outcome = build_gate_outcome(
        gate="attempt_start",
        mb_id=mb_id,
        attempt_id=None,
        status="blocked",
        issue_type=issue_type,
        route_to=route_to,
        next_action=next_action,
        action=action,
        may_start_agent=False,
        execution_provider=None,
        retryable=retryable,
        retry_after_ms=1000 if retryable else None,
        reason=reason,
        evidence_refs=[str(mb_preflight_path(project_root, mb_id).relative_to(project_root))],
        state_ref=str(runtime_state_path(project_root, mb_id).relative_to(project_root)),
    )
    write_gate_outcome(gate_outcome_archive_path(project_root, mb_id, "attempt_start"), outcome)


def lock_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def lock_path(project_root: Path, kind: str, name: str) -> Path:
    return project_root / "runtime" / "locks" / kind / f"{name}.lock"


def concurrency_config(spec: dict[str, Any]) -> dict[str, Any]:
    config = spec.get("concurrency") or {}
    return {
        "concurrency_group": config.get("concurrency_group"),
        "exclusive_touch": config.get("exclusive_touch", spec.get("allowed_touch", [])),
        "shared_read_artifacts": config.get("shared_read_artifacts", []),
        "shared_write_artifacts": config.get("shared_write_artifacts", []),
        "blocked_by_mbs": config.get("blocked_by_mbs", []),
        "can_run_parallel": config.get("can_run_parallel", False),
        "parallel_safe_reason": config.get("parallel_safe_reason", "not_declared"),
    }


def dependency_blocker(project_root: Path, spec: dict[str, Any]) -> str | None:
    for blocked_by_mb in concurrency_config(spec)["blocked_by_mbs"]:
        state_path = runtime_state_path(project_root, blocked_by_mb)
        if not state_path.is_file():
            return f"blocked_by_mbs dependency has no passed runtime state: {blocked_by_mb}"
        state = read_json(state_path)
        if state.get("status") != "passed":
            return f"blocked_by_mbs dependency is not passed: {blocked_by_mb}"
    return None


def desired_lock_paths(project_root: Path, spec: dict[str, Any]) -> list[Path]:
    config = concurrency_config(spec)
    paths = [lock_path(project_root, "mb", spec["mb_id"])]
    if config["concurrency_group"]:
        paths.append(lock_path(project_root, "concurrency_group", lock_token(str(config["concurrency_group"]))))
    for rel_path in config["exclusive_touch"]:
        paths.append(lock_path(project_root, "touch", lock_token(str(rel_path))))
    for rel_path in config["shared_write_artifacts"]:
        paths.append(lock_path(project_root, "artifact", lock_token(str(rel_path))))
    return paths


def acquire_locks(project_root: Path, spec: dict[str, Any], attempt_id: str) -> tuple[list[Path], str | None]:
    acquired: list[Path] = []
    for path in desired_lock_paths(project_root, spec):
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as handle:
                json.dump(
                    {
                        "schema_version": "1.0",
                        "mb_id": spec["mb_id"],
                        "attempt_id": attempt_id,
                        "created_at": local_timestamp(),
                    },
                    handle,
                    ensure_ascii=True,
                    indent=2,
                )
                handle.write("\n")
            acquired.append(path)
        except FileExistsError:
            release_locks(acquired)
            return [], str(path.relative_to(project_root))
    return acquired, None


def release_locks(paths: list[Path]) -> None:
    for path in reversed(paths):
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def attempt_start(
    project_root: Path,
    mb_id: str,
    spec: dict[str, Any],
    state: dict[str, Any],
    codex_command: str,
    minimax_command: str | None,
    deepseek_command: str | None,
    model: str | None,
    json_output: bool,
) -> dict[str, Any]:
    blocker = dependency_blocker(project_root, spec)
    if blocker is not None:
        record_attempt_start_rejection(
            project_root,
            mb_id,
            "review_context_gap",
            "current_scene_lead",
            "wait_for_blocking_mb",
            "release_and_wait_input",
            blocker,
        )
        print(json.dumps({"status": "blocked", "reason": blocker}, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 1}

    attempt_id = next_attempt_id(project_root, mb_id)
    provider, routing_reason = selected_execution_provider(spec, state)
    locks, lock_conflict = acquire_locks(project_root, spec, attempt_id)
    if lock_conflict is not None:
        record_attempt_start_rejection(
            project_root,
            mb_id,
            "environment_issue",
            "recovery_coordinator",
            "defer_retry",
            "defer_retry",
            f"Concurrency lock is already held: {lock_conflict}",
        )
        print(json.dumps({"status": "blocked", "reason": f"lock held: {lock_conflict}"}, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 1}

    current_attempt_dir = attempt_dir(project_root, mb_id, attempt_id)
    current_attempt_dir.mkdir(parents=True, exist_ok=True)

    memory_context = lookup_memory_context(project_root, spec, state)
    prompt = build_prompt(project_root, spec, state, memory_context)
    prompt_path = current_attempt_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    before = snapshot_workspace(project_root)
    before_path = current_attempt_dir / "before_snapshot.json"
    write_json(before_path, before)
    provider_routing_path = current_attempt_dir / "provider_routing.json"
    write_json(
        provider_routing_path,
        {
            "selected_provider": provider,
            "reason": routing_reason,
            "provider_policy": provider_policy(spec),
            "provider_attempt_counts": state.get("provider_attempt_counts", {}),
            "provider_failure_counts": state.get("provider_failure_counts", {}),
            "last_failure_issue_type": state.get("last_failure_issue_type"),
        },
    )

    state.update(
        {
            "status": "running",
            "last_attempt_id": attempt_id,
            "next_action": "await_codex_result",
            "last_execution_provider": provider,
        }
    )
    increment_provider_counter(state, "provider_attempt_counts", provider)
    write_state(project_root, state)

    start_outcome = build_gate_outcome(
        gate="attempt_start",
        mb_id=mb_id,
        attempt_id=attempt_id,
        status="authorized",
        issue_type=None,
        route_to=None,
        next_action="start_agent",
        action="dispatch_agent",
        may_start_agent=True,
        execution_provider=provider,
        retryable=False,
        retry_after_ms=None,
        reason="MB preflight passed, runtime state is ready, and attempt execution is authorized.",
        evidence_refs=[
            str(mb_preflight_path(project_root, mb_id).relative_to(project_root)),
            str(before_path.relative_to(project_root)),
            str(provider_routing_path.relative_to(project_root)),
        ],
        state_ref=str(runtime_state_path(project_root, mb_id).relative_to(project_root)),
    )
    write_gate_outcome(attempt_gate_outcome_path(current_attempt_dir, "attempt_start"), start_outcome)

    command = build_codex_exec_command(
        project_root,
        current_attempt_dir,
        provider_command(provider, codex_command, minimax_command, deepseek_command),
        model,
        json_output,
    )
    pre_hook = run_pre_tool_hook(project_root, spec, current_attempt_dir, command)
    if pre_hook["status"] != "pass":
        state.update(
            {
                "status": "blocked",
                "last_failure_reason": "hook_pre_block",
                "last_failure_issue_type": "environment_issue",
                "review_required": False,
                "next_action": "inspect_pre_tool_hook",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "parent_fb_id": spec["parent_fb_id"],
                "attempt_id": attempt_id,
                "failure_type": "hook_pre_block",
                "condition": pre_hook["summary"],
                "attempted_fix": "execution blocked before Codex invocation",
                "result": "blocked",
            },
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        release_locks(locks)
        return {"status": "stop", "exit_code": 1}

    return {
        "status": "ready",
        "attempt_id": attempt_id,
        "attempt_dir": current_attempt_dir,
        "before": before,
        "command": command,
        "prompt": prompt,
        "locks": locks,
    }


def record_attempt_finish_outcome(
    project_root: Path,
    spec: dict[str, Any],
    attempt_id: str,
        current_attempt_dir: Path,
        status: str,
        issue_type: str | None,
    route_to: str | None,
    next_action: str,
    action: str,
    retryable: bool,
    retry_after_ms: int | None,
    reason: str,
    evidence_refs: list[str],
) -> None:
    outcome = build_gate_outcome(
        gate="attempt_finish",
        mb_id=spec["mb_id"],
        attempt_id=attempt_id,
        status=status,
        issue_type=issue_type,
        route_to=route_to,
        next_action=next_action,
        action=action,
        may_start_agent=False,
        execution_provider=None,
        retryable=retryable,
        retry_after_ms=retry_after_ms,
        reason=reason,
        evidence_refs=evidence_refs,
        state_ref=str(runtime_state_path(project_root, spec["mb_id"]).relative_to(project_root)),
    )
    write_gate_outcome(attempt_gate_outcome_path(current_attempt_dir, "attempt_finish"), outcome)


def attempt_finish(
    project_root: Path,
    spec: dict[str, Any],
    state: dict[str, Any],
    attempt_id: str,
    current_attempt_dir: Path,
    before: dict[str, Any],
    execution: dict[str, Any],
    autonomy_level: str,
) -> dict[str, Any]:
    mb_id = spec["mb_id"]
    after = snapshot_workspace(project_root)
    after_path = current_attempt_dir / "after_snapshot.json"
    write_json(after_path, after)

    changes = changed_files(before, after)
    write_json(current_attempt_dir / "changed_files.json", changes)
    run_post_tool_hook(spec, current_attempt_dir, execution, changes)
    scope_result = evaluate_scope(changes, spec["allowed_touch"], spec["forbidden_touch"])
    scope_path = current_attempt_dir / "scope_guard.json"
    write_json(scope_path, scope_result)

    if scope_result["status"] != "pass":
        state.update(
            {
                "status": "routed_to_recovery",
                "retry_count": state["retry_count"] + 1,
                "last_failure_reason": "scope_violation",
                "last_failure_issue_type": "state_drift",
                "last_verification_report_path": None,
                "last_verification_digest": None,
                "review_required": False,
                "next_action": "route_to_recovery",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "parent_fb_id": spec["parent_fb_id"],
                "attempt_id": attempt_id,
                "failure_type": "scope_violation",
                "condition": scope_result["summary"],
                "attempted_fix": summarize_output(current_attempt_dir / "last_message.txt"),
                "result": "routed_to_recovery",
            },
        )
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", None)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "routed_to_recovery",
            "state_drift",
            "recovery_coordinator",
            "route_to_recovery",
            "stop_and_route_recovery",
            False,
            None,
            scope_result["summary"],
            [str(scope_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 1}

    assistant_message = summarize_output(current_attempt_dir / "last_message.txt")
    classified_failure = classify_execution_failure(assistant_message, changes)
    if classified_failure is not None:
        issue_type = classified_failure["failure_type"]
        route_to = issue_route(issue_type)
        action = "stop_and_route_owner" if issue_type == "spec_gap" else "stop_and_route_recovery"
        status = "routed_to_owner" if issue_type == "spec_gap" else "routed_to_recovery"
        state.update(
            {
                "status": "routed_to_recovery",
                "last_failure_reason": issue_type,
                "last_failure_issue_type": issue_type,
                "review_required": False,
                "next_action": "route_to_recovery",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_failure_log(
            project_root,
            {
                "mb_id": mb_id,
                "parent_fb_id": spec["parent_fb_id"],
                "attempt_id": attempt_id,
                "failure_type": issue_type,
                "condition": classified_failure["condition"],
                "attempted_fix": assistant_message,
                "result": "routed_to_recovery",
            },
        )
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", None)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            status,
            issue_type,
            route_to,
            "route_to_recovery",
            action,
            False,
            None,
            classified_failure["condition"],
            [str(current_attempt_dir.joinpath("last_message.txt").relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 1}

    state.update({"status": "verifying", "next_action": "run_verification"})
    write_state(project_root, state)

    report = run_verification(project_root, spec, attempt_id, changes, scope_result)
    report_path = current_attempt_dir / "verification_report.json"
    write_json(report_path, report)

    if report["result"] == "pass":
        stop_hook = run_stop_hook(spec, current_attempt_dir, "passed", report_path)
        if stop_hook["status"] != "pass":
            state.update(
                {
                "status": "blocked",
                "last_failure_reason": "stop_hook_blocked",
                "last_failure_issue_type": "environment_issue",
                "review_required": False,
                "next_action": "inspect_stop_hook",
            }
            )
            write_state(project_root, state)
            sync_session_state(project_root, spec["parent_fb_id"], state)
            append_failure_log(
                project_root,
                {
                    "mb_id": mb_id,
                    "parent_fb_id": spec["parent_fb_id"],
                    "attempt_id": attempt_id,
                    "failure_type": "stop_hook_blocked",
                    "condition": stop_hook["summary"],
                    "attempted_fix": summarize_output(current_attempt_dir / "last_message.txt"),
                    "result": "blocked",
                },
            )
            print(json.dumps(state, ensure_ascii=True, indent=2))
            return {"status": "stop", "exit_code": 1}
        next_action = "handoff_to_review" if autonomy_level in {"L1_human_approval", "L2_auto_with_review"} else "close_mb"
        state.update(
            {
                "status": "passed",
                "last_verification_report_path": str(report_path.relative_to(project_root)),
                "last_verification_digest": build_verification_digest(report),
                "last_failure_reason": None,
                "last_failure_issue_type": None,
                "review_required": autonomy_level in {"L1_human_approval", "L2_auto_with_review"},
                "next_action": next_action,
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        append_project_memory(project_root, spec["parent_fb_id"], mb_id, report)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "passed",
            None,
            None,
            next_action,
            "release_to_review" if state["review_required"] else "close_mb",
            False,
            None,
            report["summary"],
            [str(report_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 0}

    state["retry_count"] += 1
    state["last_verification_report_path"] = str(report_path.relative_to(project_root))
    state["last_verification_digest"] = build_verification_digest(report)
    state["last_failure_reason"] = report["summary"]
    state["last_failure_issue_type"] = "implementation_bug"
    state["review_required"] = False
    if state.get("last_execution_provider") in {"codex", "minimax", "deepseek"}:
        increment_provider_counter(state, "provider_failure_counts", state["last_execution_provider"])
    retry_limit_reached = state["retry_count"] >= spec["retry_policy"]["max_retries"]
    append_failure_log(
        project_root,
        {
            "mb_id": mb_id,
            "parent_fb_id": spec["parent_fb_id"],
            "attempt_id": attempt_id,
            "failure_type": "verification_failed",
            "condition": report["summary"],
            "attempted_fix": summarize_output(current_attempt_dir / "last_message.txt"),
            "result": "routed_to_recovery" if retry_limit_reached else "retry",
        },
    )

    if retry_limit_reached:
        state["status"] = "routed_to_recovery"
        state["next_action"] = "route_to_recovery"
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        run_stop_hook(spec, current_attempt_dir, "routed_to_recovery", report_path)
        record_attempt_finish_outcome(
            project_root,
            spec,
            attempt_id,
            current_attempt_dir,
            "routed_to_recovery",
            "implementation_bug",
            "recovery_coordinator",
            "route_to_recovery",
            "stop_and_route_recovery",
            False,
            None,
            report["summary"],
            [str(report_path.relative_to(project_root))],
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return {"status": "stop", "exit_code": 1}

    state["status"] = "failed"
    state["next_action"] = "retry"
    write_state(project_root, state)
    sync_session_state(project_root, spec["parent_fb_id"], state)
    record_attempt_finish_outcome(
        project_root,
        spec,
        attempt_id,
        current_attempt_dir,
        "retry_allowed",
        "implementation_bug",
        "builder",
        "retry_with_verification_feedback",
        "schedule_semantic_retry",
        True,
        0,
        report["summary"],
        [str(report_path.relative_to(project_root))],
    )
    return {"status": "retry", "exit_code": None}


def run_once(
    project_root: Path,
    mb_id: str,
    codex_command: str,
    minimax_command: str | None,
    deepseek_command: str | None,
    model: str | None,
    dry_run: bool,
    stream_output: bool,
    json_output: bool,
    approve: bool,
) -> int:
    initialize_runtime_memory(project_root)
    preflight_result, preflight_errors = mb_preflight(project_root, mb_id)
    if preflight_errors:
        print("\n".join(preflight_errors))
        return 1
    if preflight_result["result"] != "ready":
        print(json.dumps(preflight_result, ensure_ascii=True, indent=2))
        return 1

    spec = read_json(mission_machine_spec_path(project_root, mb_id))
    state = load_state(project_root, mb_id)
    autonomy_level = effective_autonomy_level(spec)
    state["autonomy_level"] = autonomy_level
    if autonomy_level == "L1_human_approval":
        state["approval_status"] = "approved" if approve else state.get("approval_status", "pending")
        if state["approval_status"] == "not_required":
            state["approval_status"] = "pending"
    else:
        state["approval_status"] = "not_required"
    state["review_required"] = autonomy_level in {"L1_human_approval", "L2_auto_with_review"} and state["status"] == "passed"
    if approve and autonomy_level == "L1_human_approval":
        state["approval_status"] = "approved"
        state["next_action"] = "run"
        write_state(project_root, state)
    if state["status"] in {"passed", "routed_to_recovery"}:
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 0
    if autonomy_level == "L1_human_approval" and state["approval_status"] != "approved":
        state.update(
            {
                "status": "blocked",
                "last_failure_reason": "human_approval_required",
                "last_failure_issue_type": "review_context_gap",
                "review_required": True,
                "next_action": "await_human_approval",
            }
        )
        write_state(project_root, state)
        sync_session_state(project_root, spec["parent_fb_id"], state)
        record_attempt_start_rejection(
            project_root,
            mb_id,
            "review_context_gap",
            "current_scene_lead",
            "await_human_approval",
            "pause_wait_human",
            "Human approval is required before this L1 MB can start.",
        )
        print(json.dumps(state, ensure_ascii=True, indent=2))
        return 1

    while True:
        start_result = attempt_start(
            project_root,
            mb_id,
            spec,
            state,
            codex_command,
            minimax_command,
            deepseek_command,
            model,
            json_output,
        )
        if start_result["status"] == "stop":
            return int(start_result["exit_code"])

        current_attempt_dir = start_result["attempt_dir"]
        try:
            execution = run_codex_cli(
                start_result["command"],
                start_result["prompt"],
                current_attempt_dir,
                dry_run,
                stream_output,
            )
            write_json(current_attempt_dir / "execution_result.json", execution)
            (current_attempt_dir / "raw_output.txt").write_text(execution["stdout"], encoding="utf-8")
            (current_attempt_dir / "raw_error.txt").write_text(execution["stderr"], encoding="utf-8")

            finish_result = attempt_finish(
                project_root,
                spec,
                state,
                start_result["attempt_id"],
                current_attempt_dir,
                start_result["before"],
                execution,
                autonomy_level,
            )
        finally:
            release_locks(start_result["locks"])
        if finish_result["status"] == "retry":
            continue
        return int(finish_result["exit_code"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one MB through the harness loop using Codex CLI.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--mb-id", required=True)
    parser.add_argument("--codex-command", default="codex")
    parser.add_argument("--minimax-command")
    parser.add_argument("--deepseek-command")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stream-codex-output", action="store_true")
    parser.add_argument("--codex-json", action="store_true")
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    return run_once(
        resolve_path(args.project_root),
        args.mb_id,
        args.codex_command,
        args.minimax_command,
        args.deepseek_command,
        args.model,
        args.dry_run,
        args.stream_codex_output,
        args.codex_json,
        args.approve,
    )


if __name__ == "__main__":
    raise SystemExit(main())
