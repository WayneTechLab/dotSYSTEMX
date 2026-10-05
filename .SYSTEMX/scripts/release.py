#!/usr/bin/env python3
"""Build the reviewed distribution inventory; never includes unlisted project files."""

import sys
if __name__ == "__main__" and not sys.flags.isolated:
    _bootstrap_os = sys.modules.get("os")
    if _bootstrap_os is None or not sys.executable:
        sys.exit("SYSTEMX release requires Python's initialized OS module to enter isolated mode")
    try:
        _bootstrap_os.execv(sys.executable, [sys.executable, "-I", "-B", __file__, *sys.argv[1:]])
    except OSError as error:
        sys.exit("SYSTEMX release could not enter isolated mode: " + str(error))

import hashlib
import importlib.util
import json
from pathlib import Path
import re

sys.dont_write_bytecode = True
_systemx_source = Path(__file__).resolve().with_name("systemx.py")
_systemx_spec = importlib.util.spec_from_file_location("systemx", _systemx_source)
if _systemx_spec is None:
    raise ImportError("Cannot load SYSTEMX release runner")
systemx = importlib.util.module_from_spec(_systemx_spec)
sys.modules["systemx"] = systemx
exec(compile(_systemx_source.read_bytes(), str(_systemx_source), "exec"), systemx.__dict__)
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
