#!/usr/bin/env bash
# Run from a reviewed checkout or extracted release; does not install OS packages.
set -euo pipefail
SYSTEMX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SYSTEMX_DIR/manager.py" install "$@"
