#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "AIPD single-repo install check"
echo "Protocol root: ${ROOT_DIR}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing required dependency: python3" >&2
  exit 1
fi

if ! command -v mise >/dev/null 2>&1; then
  echo "Missing required dependency: mise" >&2
  echo "Install mise first, then re-run bootstrap/install.sh" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Missing required dependency: codex" >&2
  echo "Install Codex CLI / app-server first, then re-run bootstrap/install.sh" >&2
  exit 1
fi

echo "Running protocol validation..."
python3 "${ROOT_DIR}/scripts/sdd_guard.py" check-protocol

echo "Preparing bundled Symphony runtime..."
(
  cd "${ROOT_DIR}/runtime/symphony/elixir"
  mise trust
  mise install
  mise exec -- mix deps.get
  mise exec -- mix build
)

echo
echo "Install check complete."
echo "Next:"
echo "  1. bootstrap/init_project.sh /path/to/project"
echo "  2. bootstrap/run_symphony.sh /path/to/project"
