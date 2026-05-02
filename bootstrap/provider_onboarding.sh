#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

prompt() {
  local label="$1"
  local default_value="${2:-}"
  local value
  if [ -n "$default_value" ]; then
    read -r -p "$label [$default_value]: " value
    printf '%s' "${value:-$default_value}"
  else
    read -r -p "$label: " value
    printf '%s' "$value"
  fi
}

provider_id="$(prompt "Provider id (e.g. glm, kimi, minimax)" "")"
api_base_url="$(prompt "Anthropic-compatible base URL" "https://api.example.com/anthropic")"
model_id="$(prompt "Model id" "__REPLACE_WITH_MODEL_ID__")"
role="$(prompt "Primary role (default|precision|high_complexity|escalation|none)" "none")"
generate_aipd="$(prompt "Generate AIPD launcher? (yes|no)" "yes")"

role_args=()
if [ "$role" != "none" ]; then
  role_args=(--assign-roles "$role")
fi

aipd_args=()
if [ "$generate_aipd" = "yes" ]; then
  aipd_args=(--generate-aipd-launcher)
fi

python3 "$ROOT_DIR/scripts/register_provider.py" \
  --provider-id "$provider_id" \
  --api-base-url "$api_base_url" \
  --model-id "$model_id" \
  --allow-default \
  "${role_args[@]}" \
  "${aipd_args[@]}"
