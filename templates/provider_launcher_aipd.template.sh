#!/bin/zsh
set -euo pipefail

unset ANTHROPIC_BASE_URL
unset ANTHROPIC_AUTH_TOKEN
unset ANTHROPIC_MODEL
unset ANTHROPIC_SMALL_FAST_MODEL
unset ANTHROPIC_DEFAULT_SONNET_MODEL
unset ANTHROPIC_DEFAULT_OPUS_MODEL
unset ANTHROPIC_DEFAULT_HAIKU_MODEL
unset CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
unset API_TIMEOUT_MS
unset ANTHROPIC_CUSTOM_MODEL_OPTION
unset ANTHROPIC_CUSTOM_MODEL_OPTION_NAME
unset ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION

PROFILE="{{profile_path}}"
PROMPT_FILE="{{prompt_file}}"
SYNC_SCRIPT="{{sync_script}}"
MIRROR_ROOT="{{mirror_root}}"
CLAUDE_BIN="/opt/homebrew/bin/claude"
PROJECT_ROOT="${PWD}"

if [ "$#" -gt 0 ] && [ -d "$1" ]; then
  PROJECT_ROOT="$1"
  shift
fi

if [ -f "$PROFILE" ]; then
  source "$PROFILE"
fi

for cmd in "$CLAUDE_BIN" "$SYNC_SCRIPT"; do
  if [ ! -x "$cmd" ]; then
    echo "Required executable missing: $cmd" >&2
    exit 1
  fi
done

AIPD_PROTOCOL_MIRROR_TARGET="$MIRROR_ROOT" "$SYNC_SCRIPT"
if [ ! -d "$PROJECT_ROOT" ]; then
  echo "Project root not found: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
printf "[AIPD mode] protocol_mirror=%s project_root=%s\n" "$MIRROR_ROOT" "$PROJECT_ROOT" >&2

if [ -f "$PROMPT_FILE" ]; then
  exec env AIPD_PROTOCOL_MIRROR="$MIRROR_ROOT" AIPD_PROJECT_ROOT="$PROJECT_ROOT" \
    "$CLAUDE_BIN" --append-system-prompt "$(cat "$PROMPT_FILE")" "$@"
else
  exec env AIPD_PROTOCOL_MIRROR="$MIRROR_ROOT" AIPD_PROJECT_ROOT="$PROJECT_ROOT" \
    "$CLAUDE_BIN" "$@"
fi
