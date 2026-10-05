#!/usr/bin/env bash
# Portable entry point. Project commands always run from the containing project.
set -euo pipefail
SYSTEMX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMX_PYTHON="${SYSTEMX_PYTHON:-}"
if [[ -z "$SYSTEMX_PYTHON" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    SYSTEMX_PYTHON=python3
  elif command -v python >/dev/null 2>&1; then
    SYSTEMX_PYTHON=python
  fi
fi
if [[ -z "$SYSTEMX_PYTHON" ]]; then
  printf '%s\n' 'SYSTEMX requires Python 3.9+ for command tools. Documentation is usable without it.' >&2
  exit 2
fi
if [[ -f "$SYSTEMX_DIR/INSTALLATION.json" ]]; then
  exec "$SYSTEMX_PYTHON" -I -B "$SYSTEMX_DIR/manager.py" run --target "$(dirname "$SYSTEMX_DIR")" -- "$@"
fi
exec "$SYSTEMX_PYTHON" -I -B "$SYSTEMX_DIR/scripts/systemx.py" "$@"
