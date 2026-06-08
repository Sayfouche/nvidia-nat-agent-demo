#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UI_DIR="$PROJECT_DIR/external/nat-ui"

if [[ ! -d "$UI_DIR" ]]; then
  echo "NVIDIA NAT UI not found at $UI_DIR"
  echo "Run scripts/bootstrap_ui.sh first."
  exit 1
fi

cd "$UI_DIR"

PORT="${PORT:-3001}" npm run dev
