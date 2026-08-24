#!/usr/bin/env bash
# Bootstraps a local venv once, then runs the readability check.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ $# -ne 1 ]]; then
  echo "Usage: check_pdf.sh <path-to.pdf>" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q pypdf
fi

exec "$VENV/bin/python" "$SCRIPT_DIR/check_pdf.py" "$1"
