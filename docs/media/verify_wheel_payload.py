#!/usr/bin/env python3
"""Fail if a wheel differs from this checkout's current distribution.

Usage: python3 -I -B docs/media/verify_wheel_payload.py path/to/dotsystemx.whl
Only Python's standard library is required. The wheel must be built from this
checkout, whose .SYSTEMX/config/distribution.json is the comparison baseline.
"""

from __future__ import annotations

import argparse
import base64
import csv
from email.parser import Parser
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".SYSTEMX"
MANIFEST = "config/distribution.json"
TEXT_SUFFIXES = frozenset({".json", ".md", ".ps1", ".py", ".sh"})
TEXT_NAMES = frozenset({".gitattributes", ".gitignore", "LICENSE", "VERSION"})
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 1000
MAX_PAYLOAD = 32 * 1024 * 1024


def unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field: " + key)
        result[key] = value
    return result


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (name == str(path) and bool(name) and not path.is_absolute()
            and all(part not in ("", ".", "..") for part in path.parts)
            and "\\" not in name and ":" not in name)


def distribution_digest(name: str, data: bytes) -> str:
    """Match the schema-2 text rule used by .SYSTEMX/manager.py."""
    path = PurePosixPath(name)
    if path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES:
        data.decode("utf-8")
        if b"\x00" in data:
            raise ValueError("NUL in distribution text file: " + name)
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def verify(wheel: Path) -> int:
    manifest_path = SOURCE / MANIFEST
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes, object_pairs_hook=unique_fields)
    if not isinstance(manifest, dict):
        raise ValueError("Distribution manifest is not an object")
    if manifest.get("schemaVersion") != 2:
        raise ValueError("Expected a schema-2 distribution manifest")
    if manifest.get("version") != (SOURCE / "VERSION").read_text(
            encoding="utf-8").strip():
        raise ValueError("Manifest version differs from source VERSION")
    files = manifest.get("files")
    if not isinstance(files, dict) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError("Manifest has an invalid file inventory")
    if MANIFEST in files or any(not safe_name(name) or not re.fullmatch(
            r"[0-9a-f]{64}", digest) for name, digest in files.items()):
        raise ValueError("Manifest has an unsafe name or invalid digest")
    expected = set(files) | {MANIFEST}
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project = re.search(r"(?ms)^\[project\]\s*\n(.*?)(?=^\[|\Z)", pyproject)
    if project is None:
        raise ValueError("Missing [project] package metadata")
    expected_meta = {}
    for key in ("name", "version", "requires-python"):
        match = re.search(r'(?m)^' + key + r' = "([^"]+)"$', project.group(1))
        if match is None:
            raise ValueError("Missing package " + key)
        expected_meta[key] = match.group(1)
    if expected_meta["name"] != "dotsystemx":
        raise ValueError("Unexpected project package name")
    scripts = re.search(r"(?ms)^\[project\.scripts\]\s*\n(.*?)(?=^\[|\Z)", pyproject)
    if scripts is None or scripts.group(1).strip() != 'systemx = "systemx.cli:main"':
        raise ValueError("Unexpected project console script")
    info_dir = expected_meta["name"] + "-" + expected_meta["version"] + ".dist-info/"
    info_names = {info_dir + suffix for suffix in (
        "licenses/.SYSTEMX/LICENSE", "METADATA", "WHEEL", "entry_points.txt",
        "top_level.txt", "RECORD")}
    expected_members = {"systemx/" + name for name in expected} | info_names
    with ZipFile(wheel) as archive:
        members = {}
        total = 0
        for info in archive.infolist():
            name = info.filename
            if info.is_dir() or not safe_name(name) or name in members:
                raise ValueError("Directory, unsafe or duplicate wheel member: " + name)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode) or info.file_size > MAX_FILE:
                raise ValueError("Link or oversized wheel member: " + name)
            if name.startswith("systemx/"):
                total += info.file_size
                if total > MAX_PAYLOAD:
                    raise ValueError("Wheel package exceeds release size bound")
            members[name] = info
            if len(members) > MAX_FILES + len(info_names):
                raise ValueError("Wheel contains too many files")
        missing = sorted(expected_members - members.keys())
        extra = sorted(members.keys() - expected_members)
        if missing or extra:
            raise ValueError(f"Wheel inventory mismatch: missing={missing}; extra={extra}")
        meta = Parser().parsestr(archive.read(info_dir + "METADATA").decode("utf-8"))
        if meta.get_all("Name") != [expected_meta["name"]] or \
                meta.get_all("Version") != [expected_meta["version"]] or \
                meta.get_all("Requires-Python") != [expected_meta["requires-python"]] or \
                meta.get_all("Requires-Dist"):
            raise ValueError("Wheel package metadata differs from pyproject.toml")
        if meta.get_payload().encode("utf-8") != (ROOT / "README.md").read_bytes():
            raise ValueError("Wheel metadata README differs from source")
        wheel_meta = Parser().parsestr(archive.read(info_dir + "WHEEL").decode("utf-8"))
        if wheel_meta.get_all("Wheel-Version") != ["1.0"] or \
                wheel_meta.get_all("Root-Is-Purelib") != ["true"] or \
                wheel_meta.get_all("Tag") != ["py3-none-any"]:
            raise ValueError("Unexpected wheel format or platform tag")
        if archive.read(info_dir + "entry_points.txt") != (
                b"[console_scripts]\nsystemx = systemx.cli:main\n") or \
                archive.read(info_dir + "top_level.txt") != b"systemx\n" or \
                archive.read(info_dir + "licenses/.SYSTEMX/LICENSE") != (
                    SOURCE / "LICENSE").read_bytes():
            raise ValueError("Unexpected wheel entry point, package root or license")
        record_name = info_dir + "RECORD"
        records = {}
        for row in csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))):
            if len(row) != 3 or row[0] in records:
                raise ValueError("Malformed or duplicate wheel RECORD entry")
            records[row[0]] = row[1:]
        if set(records) != set(members):
            raise ValueError("Wheel RECORD inventory differs from ZIP inventory")
        for name in sorted(members):
            digest, size = records[name]
            if name == record_name:
                if digest or size:
                    raise ValueError("RECORD must not hash itself")
                continue
            data = archive.read(name)
            expected_hash = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode(
                "ascii").rstrip("=")
            if digest != "sha256=" + expected_hash or size != str(len(data)):
                raise ValueError("Wheel RECORD digest/size mismatch: " + name)
        for name in sorted(expected):
            source = SOURCE / name
            if not source.is_file() or source.is_symlink():
                raise ValueError("Missing ordinary source file: " + name)
            wheel_bytes = archive.read("systemx/" + name)
            source_bytes = source.read_bytes()
            if wheel_bytes != source_bytes:
                raise ValueError("Wheel/source exact-byte mismatch: " + name)
            if name == MANIFEST:
                if wheel_bytes != manifest_bytes:
                    raise ValueError("Wheel distribution manifest differs from source")
            elif distribution_digest(name, wheel_bytes) != files[name]:
                raise ValueError("Wheel payload fails distribution digest: " + name)
    return len(expected)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path, help="wheel built from this checkout")
    args = parser.parse_args()
    try:
        count = verify(args.wheel)
    except (BadZipFile, OSError, UnicodeError, ValueError, KeyError, TypeError,
            RuntimeError) as error:
        print("Wheel payload verification failed: " + str(error), file=sys.stderr)
        return 1
    print(f"Verified {count} exact systemx/ wheel files against {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
