#!/usr/bin/env bash
# Validate a paper pack. Pass --pdf to also verify claims against the source.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ $# -lt 1 ]]; then
  echo "Usage: validate_pack.sh <examples/slug/> [--pdf <path-to.pdf>]" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q pypdf
fi

exec "$VENV/bin/python" "$SCRIPT_DIR/validate_pack.py" "$@"
