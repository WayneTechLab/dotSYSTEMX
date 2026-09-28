#!/usr/bin/env python3
"""Build the reviewed distribution inventory; never includes unlisted project files."""

import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import systemx
from versions import package_version, version_id


def check_metadata(root):
    version = version_id((root / "VERSION").read_text(encoding="utf-8").strip())
    provenance = json.loads((root / "SOURCE.json").read_text(encoding="utf-8"))
    if provenance.get("templateVersion") != version:
        raise ValueError("SOURCE.json must match VERSION")
    metadata = root.parent / "pyproject.toml"
    if metadata.is_file():
        text = metadata.read_text(encoding="utf-8")
        project = re.search(r"(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)", text)
        match = re.search(r'(?m)^version = "([^"]+)"$', project.group(1)) if project else None
        if not match or match.group(1) != package_version(version):
            raise ValueError("pyproject.toml must match VERSION using Python version spelling")
        license_path = root.parent / "LICENSE"
        if not license_path.is_file() or license_path.read_bytes() != (root / "LICENSE").read_bytes():
            raise ValueError("Root and portable MIT licenses must match")
    return version


def main():
    root = Path(__file__).resolve().parents[1]
    version = check_metadata(root)
    if sys.argv[1:] == ["--check"]:
        return systemx.validate_template(distribution=True)
    if sys.argv[1:]:
        raise ValueError("Usage: release.py [--check]")
    manifest = "config/distribution.json"
    files = {}
    for name in sorted(systemx.REQUIRED):
        if name == manifest:
            continue
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing or non-regular distribution file: " + name)
        files[name] = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    (root / manifest).write_text(json.dumps({"schemaVersion": 1, "version": version,
                                           "files": files}, indent=2) + "\n", encoding="utf-8")
    return systemx.validate_template(distribution=True)


if __name__ == "__main__":
    raise SystemExit(main())
