#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bootstrap/run_symphony.sh /absolute/path/to/project-root" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$1"
WORKFLOW_PATH="${PROJECT_ROOT}/runtime/symphony.WORKFLOW.md"

python3 "${ROOT_DIR}/bootstrap/render_workflow.py" \
  --project-root "${PROJECT_ROOT}" \
  --output "${WORKFLOW_PATH}"

echo "Rendered workflow: ${WORKFLOW_PATH}"
echo "Starting bundled Symphony..."

cd "${ROOT_DIR}/runtime/symphony/elixir"
exec mise exec -- ./bin/symphony "${WORKFLOW_PATH}" --port 4040
