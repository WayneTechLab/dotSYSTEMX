"""Opt-in root AGENTS.md pointer for harnesses that discover root instructions.

The selected .SYSTEMX/AGENTS.md remains the single project guide. This module
never copies its contents, reads an existing root instruction file, or changes
provider configuration. Creation is exclusive, so a concurrent writer wins
without either file being overwritten.
"""

import hashlib
import os
from pathlib import Path
import stat


POINTER = (
    "# .SYSTEMX agent entry point\n\n"
    "For project work, read `.SYSTEMX/AGENTS.md` for the shared project guide.\n"
    "Apply the current task instructions and host permissions. This pointer\n"
    "does not grant access or start an agent.\n"
)
POINTER_BYTES = POINTER.encode("utf-8")
POINTER_SHA256 = hashlib.sha256(POINTER_BYTES).hexdigest()
LIMIT = ("Opt-in root instruction pointer only. Existing AGENTS.md is preserved; "
         "review and merge it manually. No provider rules, credentials, grants, or runtime are copied.")


def _paths(root):
    """Require the exact selected project layout without following local links."""
    selected = Path(root).absolute()
    if selected.name != ".SYSTEMX":
        raise ValueError("Select the exact .SYSTEMX directory beneath a project root")
    project = selected.parent
    try:
        project_stat, selected_stat = project.lstat(), selected.lstat()
    except FileNotFoundError as error:
        raise ValueError("Selected .SYSTEMX project directory is missing") from error
    if stat.S_ISLNK(project_stat.st_mode) or stat.S_ISLNK(selected_stat.st_mode):
        raise ValueError("Project root and .SYSTEMX must not be symbolic links")
    if not stat.S_ISDIR(project_stat.st_mode) or not stat.S_ISDIR(selected_stat.st_mode):
        raise ValueError("Selected .SYSTEMX project directory is missing")
    guide = selected / "AGENTS.md"
    try:
        guide_stat = guide.lstat()
    except FileNotFoundError as error:
        raise ValueError("Selected .SYSTEMX/AGENTS.md guide is missing") from error
    if not stat.S_ISREG(guide_stat.st_mode):
        raise ValueError("Selected .SYSTEMX/AGENTS.md must be a regular file, not a link")
    return project, project / "AGENTS.md", project_stat, selected_stat, guide_stat


def _same_inode(first, second):
    return first.st_dev == second.st_dev and first.st_ino == second.st_ino


def _anchored_project(project, project_stat, selected_stat, guide_stat):
    """Bind both directories and the inner guide to the inspected inodes."""
    if (not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW") or
            os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd or
            os.unlink not in os.supports_dir_fd):
        raise ValueError("Root AGENTS.md bridge apply needs anchored directory handles; preview remains available")
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    project_fd = root_fd = None
    try:
        project_fd = os.open(project, directory_flags)
        if not _same_inode(os.fstat(project_fd), project_stat):
            raise ValueError("Project root changed since bridge preview; inspect it again")
        root_fd = os.open(".SYSTEMX", directory_flags, dir_fd=project_fd)
        if not _same_inode(os.fstat(root_fd), selected_stat):
            raise ValueError("Selected .SYSTEMX changed since bridge preview; inspect it again")
        guide_fd = os.open("AGENTS.md", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            if (not stat.S_ISREG(os.fstat(guide_fd).st_mode) or
                    not _same_inode(os.fstat(guide_fd), guide_stat)):
                raise ValueError("Selected .SYSTEMX/AGENTS.md changed during bridge apply")
        finally:
            os.close(guide_fd)
        return project_fd, root_fd
    except BaseException:
        if root_fd is not None:
            os.close(root_fd)
        if project_fd is not None:
            os.close(project_fd)
        raise


def _cleanup_created(project_fd, created_stat):
    """Remove a failed partial write only while the leaf is still our inode."""
    try:
        current = os.stat("AGENTS.md", dir_fd=project_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if _same_inode(current, created_stat):
        os.unlink("AGENTS.md", dir_fd=project_fd)


def _state(path):
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "absent"
    return "existing" if stat.S_ISREG(mode) else "conflict"


def bridge_status(root):
    """Preview a fixed pointer without reading or changing project instructions."""
    _, target, _, _, _ = _paths(root)
    state = _state(target)
    return {"path": "AGENTS.md", "state": state, "preview": POINTER,
            "contentSha256": POINTER_SHA256, "applied": False,
            "preserved": state != "absent", "limit": LIMIT}


def bridge_apply(root, expected_sha256):
    """Create a root pointer once; an existing file or link always wins."""
    if expected_sha256 != POINTER_SHA256:
        raise ValueError("Root AGENTS.md pointer preview hash changed; preview again")
    project, target, project_stat, selected_stat, guide_stat = _paths(root)
    if _state(target) != "absent":
        raise ValueError("Existing root AGENTS.md is preserved; review and merge manually")
    project_fd, root_fd = _anchored_project(project, project_stat, selected_stat, guide_stat)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        try:
            descriptor = os.open("AGENTS.md", flags, 0o644, dir_fd=project_fd)
        except (FileExistsError, IsADirectoryError) as error:
            raise ValueError("Root AGENTS.md appeared or conflicts; preserved without overwrite") from error
        created_stat = os.fstat(descriptor)
        try:
            remaining = memoryview(POINTER_BYTES)
            while remaining:
                written = os.write(descriptor, remaining)
                if written <= 0:
                    raise OSError("Root AGENTS.md pointer write made no progress")
                remaining = remaining[written:]
            os.fsync(descriptor)
            if (not _same_inode(project.lstat(), project_stat) or
                    not _same_inode((project / ".SYSTEMX").lstat(), selected_stat)):
                raise ValueError("Project root changed during bridge apply; inspect it again")
        except BaseException:
            _cleanup_created(project_fd, created_stat)
            raise
        finally:
            os.close(descriptor)
    finally:
        os.close(root_fd)
        os.close(project_fd)
    return {"path": "AGENTS.md", "state": "existing", "preview": POINTER,
            "contentSha256": POINTER_SHA256, "applied": True,
            "preserved": False, "limit": LIMIT}
