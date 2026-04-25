#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bootstrap/init_project.sh /absolute/path/to/project-root" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$1"

mkdir -p "${PROJECT_ROOT}"
mkdir -p \
  "${PROJECT_ROOT}/function_blocks" \
  "${PROJECT_ROOT}/missions" \
  "${PROJECT_ROOT}/reviews" \
  "${PROJECT_ROOT}/research" \
  "${PROJECT_ROOT}/experience_prompts" \
  "${PROJECT_ROOT}/runtime"

copy_if_missing() {
  local src="$1"
  local dest="$2"
  if [[ ! -e "${dest}" ]]; then
    cp "${src}" "${dest}"
  fi
}

copy_if_missing "${ROOT_DIR}/templates/CONSTITUTION.template.md" "${PROJECT_ROOT}/CONSTITUTION.md"
copy_if_missing "${ROOT_DIR}/templates/SCOPE.template.md" "${PROJECT_ROOT}/SCOPE.md"
copy_if_missing "${ROOT_DIR}/templates/DECISIONS.template.md" "${PROJECT_ROOT}/DECISIONS.md"
copy_if_missing "${ROOT_DIR}/templates/QUALITY_RULEBOOK.template.md" "${PROJECT_ROOT}/QUALITY_RULEBOOK.md"
copy_if_missing "${ROOT_DIR}/templates/QUALITY_MEMORY.template.md" "${PROJECT_ROOT}/QUALITY_MEMORY.md"
copy_if_missing "${ROOT_DIR}/templates/SESSION_STATE.template.md" "${PROJECT_ROOT}/SESSION_STATE.md"

echo "Initialized PROJECT_ROOT at ${PROJECT_ROOT}"
echo
echo "Next:"
echo "  1. Start Codex with Protocol Root = ${ROOT_DIR}"
echo "  2. Use Scene: greenfield or expansion"
echo "  3. After runnable MBs exist, run bootstrap/run_symphony.sh ${PROJECT_ROOT}"
