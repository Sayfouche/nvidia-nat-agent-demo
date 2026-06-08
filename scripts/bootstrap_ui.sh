#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UI_DIR="$PROJECT_DIR/external/nat-ui"
UI_REPO="https://github.com/NVIDIA/NeMo-Agent-Toolkit-UI.git"
UI_COMMIT="e5d91c68b913287cbcc4d4689a956a7b3b36333e"

mkdir -p "$PROJECT_DIR/external"

if [[ ! -d "$UI_DIR/.git" ]]; then
  git clone "$UI_REPO" "$UI_DIR"
fi

git -C "$UI_DIR" fetch --depth 1 origin "$UI_COMMIT"
git -C "$UI_DIR" checkout "$UI_COMMIT"

cd "$UI_DIR"
npm ci

echo "NVIDIA NAT UI is ready in $UI_DIR"

