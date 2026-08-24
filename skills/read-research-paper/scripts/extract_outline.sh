#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ $# -ne 1 ]]; then
  echo "Usage: extract_outline.sh <path-to.pdf>" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q pypdf
fi

exec "$VENV/bin/python" "$SCRIPT_DIR/extract_outline.py" "$1"
