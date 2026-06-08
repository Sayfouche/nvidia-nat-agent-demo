#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

source .venv/bin/activate

nat validate --config_file config.yml
python -m pytest
python -m ruff check .
bash -n scripts/*.sh

