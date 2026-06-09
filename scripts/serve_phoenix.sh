#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

source .venv/bin/activate

if ! command -v phoenix >/dev/null 2>&1; then
  echo "phoenix command not found. Install dependencies first: python -m pip install -r requirements.txt"
  exit 1
fi

export PHOENIX_ALLOWED_SANDBOX_PROVIDERS="${PHOENIX_ALLOWED_SANDBOX_PROVIDERS:-NONE}"

phoenix serve
