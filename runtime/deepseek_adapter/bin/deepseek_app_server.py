#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = CURRENT_DIR.parent

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from deepseek_adapter.server import DeepSeekAppServer  # noqa: E402


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] not in {"app-server"}:
        sys.stderr.write(f"Unsupported subcommand: {sys.argv[1]}\n")
        return 2

    server = DeepSeekAppServer()
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main())
