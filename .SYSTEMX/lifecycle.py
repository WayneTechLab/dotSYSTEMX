"""Local lifecycle inventories and durable JSON receipts; never follow content links."""

import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

if __package__:
    from .systemx_paths import is_link, SystemXPathError
else:
    from systemx_paths import is_link, SystemXPathError


def atomic_json(path, value):
    descriptor, temporary = tempfile.mkstemp(prefix="receipt-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inventory(root, *, exclude=()):
    """Raw-byte hashes, empty directories, and link targets; no link traversal."""
    if is_link(root) or not root.is_dir():
        raise SystemXPathError("Inventory root must be a real directory")
    entries = {}
    pending = [root]
    while pending:
        folder = pending.pop()
        for path in sorted(folder.iterdir()):
            name = path.relative_to(root).as_posix()
            if name in exclude:
                continue
            info = path.lstat()
            if is_link(path):
                entries[name] = {"kind": "link", "target": os.readlink(path)}
            elif stat.S_ISDIR(info.st_mode):
                entries[name] = {"kind": "directory"}
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                fingerprint = hashlib.sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        fingerprint.update(chunk)
                after = path.lstat()
                if (info.st_size, info.st_mtime_ns, info.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                    raise SystemXPathError("A file changed during inventory; stop other writers and retry: " + name)
                entries[name] = {"kind": "file", "bytes": info.st_size, "sha256": fingerprint.hexdigest()}
            else:
                raise SystemXPathError("Stop the owner of this special filesystem entry before removal: " + name)
    return dict(sorted(entries.items()))


def external_backup(root, value, *, must_exist=False):
    raw = Path(value).expanduser().absolute()
    if is_link(raw):
        raise SystemXPathError("Backup must be a real directory, not a link")
    backup = raw.resolve()
    if backup.is_relative_to(root) or root.is_relative_to(backup):
        raise SystemXPathError("Choose a backup outside the project, not an ancestor of it")
    if not backup.parent.is_dir():
        raise SystemXPathError("The backup parent directory must already exist")
    if must_exist:
        if not backup.is_dir():
            raise SystemXPathError("Backup directory does not exist")
    elif backup.exists():
        raise SystemXPathError("Backup destination already exists; choose a new directory")
    if root.stat().st_dev != backup.parent.stat().st_dev:
        raise SystemXPathError("Use a backup on the same filesystem for an atomic move; copy it elsewhere after verification")
    return backup


def path_entries(root):
    """Report residual case variants without following links, including dangling aliases."""
    if not root.exists():
        return []
    return [{"name": p.name, "kind": "link" if is_link(p) else "directory" if p.is_dir() else "file"}
            for p in sorted(root.iterdir()) if p.name.casefold() == ".systemx"]
