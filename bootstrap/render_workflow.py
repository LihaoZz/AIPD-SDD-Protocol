#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


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
codex:
  command: codex app-server
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

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        TEMPLATE.format(
            project_root=project_root,
            workspace_root=workspace_root,
        ),
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
