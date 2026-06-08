#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

source .venv/bin/activate

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export SSL_CERT_FILE="${SSL_CERT_FILE:-$(python -m certifi)}"

nat run --config_file config.yml "$@"
