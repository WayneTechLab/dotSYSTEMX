#!/usr/bin/env python3
"""Build the reviewed distribution inventory; never includes unlisted project files."""

import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import systemx


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = "config/distribution.json"
    files = {}
    for name in sorted(systemx.REQUIRED):
        if name == manifest:
            continue
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing or non-regular distribution file: " + name)
        files[name] = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    (root / manifest).write_text(json.dumps({"schemaVersion": 1, "version": (root / "VERSION").read_text().strip(),
                                           "files": files}, indent=2) + "\n", encoding="utf-8")
    return systemx.validate_template(distribution=True)


if __name__ == "__main__":
    raise SystemExit(main())
