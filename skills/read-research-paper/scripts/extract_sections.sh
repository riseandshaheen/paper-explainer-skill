#!/usr/bin/env bash
# Per-section body text with page numbers. Bootstraps a local venv once.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [[ $# -lt 1 ]]; then
  echo "Usage: extract_sections.sh <path-to.pdf> [--text] [--section N] [--max-chars N]" >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q pypdf
fi

exec "$VENV/bin/python" "$SCRIPT_DIR/extract_sections.py" "$@"
