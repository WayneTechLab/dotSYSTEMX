"""One exact-case project directory, with an optional local lowercase alias."""

import os
from pathlib import Path

CANONICAL = ".SYSTEMX"
ALIAS = ".systemx"


class SystemXPathError(ValueError):
    """A path or installation was refused without replacing user content."""


def _require_explicit_path(value):
    if isinstance(value, (str, os.PathLike)):
        spelling = os.fspath(value)
        if isinstance(spelling, str) and not spelling.strip():
            raise SystemXPathError("An explicit path cannot be empty or whitespace")


def lexical_path(value):
    """Make absolute without resolving away spelling or a final symlink."""
    _require_explicit_path(value)
    return Path(os.path.abspath(Path(value).expanduser()))


def is_link(path):
    # Python 3.9 supports Windows junction tags but not Path.is_junction().
    try:
        return path.is_symlink() or getattr(path.lstat(), "st_reparse_tag", 0) == 0xA0000003
    except (FileNotFoundError, NotADirectoryError):
        return False


def inspect_layout(project, *, required=False):
    """Inspect real entry names, even on a filesystem that ignores case."""
    _require_explicit_path(project)
    project = Path(project)
    canonical = project / CANONICAL
    alias = project / ALIAS
    entries = {p.name: p for p in project.iterdir()
               if p.name.casefold() == CANONICAL.casefold()} if project.exists() else {}
    if CANONICAL not in entries:
        if entries:
            raise SystemXPathError(
                "Exact-case conflict: found " + ", ".join(sorted(entries)) +
                " but the stored directory name must be .SYSTEMX. Nothing was merged or renamed; "
                "back up and reconcile the existing paths before retrying.")
        if required:
            raise SystemXPathError("Missing canonical .SYSTEMX directory in " + str(project))
        return {"canonical": str(canonical), "alias": str(alias), "aliasStatus": "not-installed"}
    if is_link(canonical) or not canonical.is_dir():
        raise SystemXPathError("Canonical .SYSTEMX must be a real directory, not a symlink, junction, or file")
    for name, path in entries.items():
        if name == CANONICAL:
            continue
        # Only this exact relative sibling link is portable and unambiguous.
        if name == ALIAS and path.is_symlink() and os.readlink(path) == CANONICAL and path.samefile(canonical):
            continue
        raise SystemXPathError(
            "Exact-case conflict: " + str(path) +
            " is a separate or unsupported path beside .SYSTEMX. Preserve both paths, "
            "back up and reconcile their contents; no automatic merge, rename, or deletion is performed.")
    if ALIAS in entries:
        status = "linked"
    elif alias.exists() and alias.samefile(canonical):
        status = "filesystem-equivalent"
    else:
        status = "absent"
    return {"canonical": str(canonical), "alias": str(alias), "aliasStatus": status}


def project_directory(target, *, check_layout=True):
    if str(target).startswith(("http://", "https://", "drive://")):
        raise SystemXPathError("Target must be a local folder; use a Drive desktop folder or export a chat packet")
    raw = lexical_path(target)
    root = raw.resolve()
    if (root == Path(root.anchor) or
            any(p.casefold() == ALIAS for p in (*raw.parts, *root.parts))):
        raise SystemXPathError("Choose the containing project directory, not an OS root, .SYSTEMX, or a directory inside it")
    if root.exists() and not root.is_dir():
        raise SystemXPathError("Target is not a directory")
    if check_layout:
        inspect_layout(root)
    return root


def record_directory(path):
    raw = lexical_path(path)
    if raw.name.casefold() != ALIAS:
        raise SystemXPathError("Project records must use .SYSTEMX; pass --root /path/to/project/.SYSTEMX for versioned tools")
    project = project_directory(raw.parent)
    result = inspect_layout(project, required=True)
    canonical = Path(result["canonical"])
    if not raw.exists() or not raw.samefile(canonical):
        raise SystemXPathError("Use the exact path .SYSTEMX; the requested spelling does not resolve to it")
    return canonical


def lowercase_alias(target, *, create=False, dry_run=False):
    """Check or create a relative sibling alias; never remove or replace a path."""
    project = project_directory(target)
    result = inspect_layout(project, required=not dry_run)
    result.update({"created": False, "requested": create})
    if not create or result["aliasStatus"] in {"linked", "filesystem-equivalent"}:
        return result
    if dry_run:
        result["action"] = "Create a relative link if the installed filesystem needs it; otherwise use its existing case equivalence"
        return result
    try:
        (project / ALIAS).symlink_to(CANONICAL, target_is_directory=True)
    except FileExistsError:
        # A concurrent creator may have installed the same valid alias.
        return {**inspect_layout(project, required=True), "created": False, "requested": True}
    except OSError as error:
        raise SystemXPathError(
            "Could not create the optional .systemx -> .SYSTEMX link. The canonical directory "
            "is preserved; use .SYSTEMX directly or enable symlink support for this location. " + str(error)) from error
    return {**inspect_layout(project, required=True), "created": True, "requested": True}
