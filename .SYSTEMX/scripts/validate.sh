#!/usr/bin/env bash
set -euo pipefail
SYSTEMX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$SYSTEMX_DIR/SYSTEMX.sh" validate "$@"
