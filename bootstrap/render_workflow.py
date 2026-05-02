#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "scripts"))

from provider_registry import load_provider_registry
TEMPLATE = """---
tracker:
  kind: aipd_mb
  aipd_root: {project_root}
  active_states:
    - ready
    - retry_waiting
  terminal_states:
    - done
    - closed
polling:
  interval_ms: 5000
workspace:
  root: {workspace_root}
agent:
  max_concurrent_agents: 3
  max_turns: 10
agent_runtime:
  default_provider: {default_provider}
  providers: {providers_json}
  approval_policy: never
  thread_sandbox: workspace-write
  turn_sandbox_policy:
    type: workspaceWrite
---

You are working on AIPD mission block `{{{{ issue.identifier }}}}`.

Read and follow:
- `missions/{{{{ issue.identifier }}}}.md`
- `missions/{{{{ issue.identifier }}}}.machine.json`

Stay inside the mission boundary.
Do not expand scope on your own.
If AIPD gate files are missing or invalid, fail closed.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a bundled AIPD Symphony workflow file.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workspace-root")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    workspace_root = (
        Path(args.workspace_root).expanduser().resolve()
        if args.workspace_root
        else project_root.parent / f"{project_root.name}-symphony-workspaces"
    )
    registry = load_provider_registry()
    providers = {
        provider_id: {"command": registry.command_for_project(provider_id, project_root)}
        for provider_id in sorted(registry.provider_ids())
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        TEMPLATE.format(
            project_root=project_root,
            workspace_root=workspace_root,
            default_provider=registry.role_provider("default_execution_provider"),
            providers_json=json.dumps(providers, ensure_ascii=True),
        ),
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
