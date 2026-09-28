#!/usr/bin/env bash
# Portable entry point. Project commands always run from the containing project.
set -euo pipefail
SYSTEMX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'SYSTEMX requires Python 3.9+ for command tools. Documentation is usable without it.' >&2
  exit 2
fi
if [[ -f "$SYSTEMX_DIR/INSTALLATION.json" ]]; then
  exec python3 -B "$SYSTEMX_DIR/manager.py" run --target "$(dirname "$SYSTEMX_DIR")" -- "$@"
fi
exec python3 -B "$SYSTEMX_DIR/scripts/systemx.py" "$@"
