#!/usr/bin/env bash
# Run from a reviewed checkout or extracted release; does not install OS packages.
set -euo pipefail
SYSTEMX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMX_PYTHON="${SYSTEMX_PYTHON:-}"
if [[ -z "$SYSTEMX_PYTHON" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    SYSTEMX_PYTHON=python3
  elif command -v python >/dev/null 2>&1; then
    SYSTEMX_PYTHON=python
  else
    printf '%s\n' 'SYSTEMX requires Python 3.9+ for installation.' >&2
    exit 2
  fi
fi
exec "$SYSTEMX_PYTHON" -I -B "$SYSTEMX_DIR/manager.py" install "$@"
