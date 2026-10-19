"""Additive, local-only DATA scaffold and bounded Git-ignore evidence.

The auditor never reads, hashes, follows links into, or recursively enumerates
payload. Git returns tracked path metadata; filename output is bounded.
"""

import os
from pathlib import Path
import shutil
import stat
import subprocess
import threading
import tempfile

from systemx_paths import inspect_layout, is_link

FOLDERS = ("TEMP", "LARGE", "IMPORTS", "RESEARCH", "ASSETS", "EXPORTS", "CACHE", "ARCHIVE")
SCAFFOLD = (".gitignore", "README.md") + tuple(name + "/README.md" for name in FOLDERS)
BLUEPRINT = "templates/data"
COMMANDS = ("data",)
REQUIRED = ("scripts/data_tools.py", "tests/test_data_tools.py") + tuple(
    base + "/" + name for base in ("DATA", BLUEPRINT) for name in SCAFFOLD)
MAX_DIRECTORY_ENTRIES = 1024
MAX_GIT_BYTES = 256 * 1024
MAX_DISPLAY_PATHS = 20
MAX_SEED_BYTES = 32 * 1024


def _entries(directory):
    """Bound name-only scans needed to detect case aliases; no payload stat/read."""
    result = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(result) >= MAX_DIRECTORY_ENTRIES:
                raise ValueError("DATA scaffold case check exceeded 1024 direct entries; no payload was read")
            result.append(entry.name)
    return result


def _root(root):
    root = Path(os.path.abspath(os.fspath(root)))
    if root.name not in {".SYSTEMX", ".SYSTEMXP"}:
        raise ValueError("DATA scope must use exact .SYSTEMX or explicitly selected .SYSTEMXP records")
    if is_link(root) or not root.is_dir():
        raise ValueError("DATA record scope must be a real directory, not a link")
    if root.name == ".SYSTEMX":
        inspect_layout(root.parent, required=True)
    elif [name for name in _entries(root.parent) if name.casefold() == ".systemxp"] != [".SYSTEMXP"]:
        raise ValueError("DATA record scope must use its exact stored case without duplicates")
    return root


def _managed(root, relative):
    """Inspect known scaffold paths only; final payload links are never followed."""
    path = root
    for part in relative.split("/"):
        if path.exists():
            if not path.is_dir():
                raise ValueError("DATA scaffold parent is not a directory: " + relative)
            matches = [name for name in _entries(path) if name.casefold() == part.casefold()]
            if matches and matches != [part]:
                raise ValueError("DATA exact-case conflict: " + relative)
        path = path / part
        if is_link(path):
            raise ValueError("DATA scaffold links are refused: " + relative)
        if path.exists():
            metadata = path.stat()
            if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1:
                raise ValueError("Hard-linked DATA scaffold is refused: " + relative)
    return path


def _guard(root):
    root = _root(root)
    base = _managed(root, "DATA")
    if base.exists() and not base.is_dir():
        raise ValueError("DATA must be a directory")
    for name in FOLDERS:
        path = _managed(root, "DATA/" + name)
        if path.exists() and not path.is_dir():
            raise ValueError("DATA scaffold folder is not a directory: " + name)
    for name in SCAFFOLD:
        path = _managed(root, "DATA/" + name)
        if path.exists() and not path.is_file():
            raise ValueError("DATA scaffold file is not regular: " + name)
    return root, base


def _blueprint(defaults):
    # The caller selects reviewed defaults; managed releases and wheel packages
    # have version/package directory names rather than a record-scope marker.
    defaults = Path(os.path.abspath(os.fspath(defaults)))
    if is_link(defaults) or not defaults.is_dir():
        raise ValueError("DATA defaults must be a real directory, not a link")
    content = {}
    for name in SCAFFOLD:
        path = _managed(defaults, BLUEPRINT + "/" + name)
        if (not path.is_file() or not stat.S_ISREG(path.stat().st_mode) or
                path.stat().st_size > MAX_SEED_BYTES):
            raise ValueError("Missing, special, or oversized DATA blueprint: " + name)
        content[name] = path.read_bytes()
    return content


def validate_optional(root):
    """Adopted validation guards only known scaffold paths, never user payload."""
    _guard(root)


def validate_template(root, defaults):
    """Published template must have the exact blank local-data scaffold."""
    root, base = _guard(root)
    seeds = _blueprint(defaults)
    expected = {".gitignore", "README.md", *FOLDERS}
    if not base.is_dir() or set(_entries(base)) != expected:
        raise ValueError("Published DATA must contain only the blank scaffold")
    for folder in FOLDERS:
        if set(_entries(base / folder)) != {"README.md"}:
            raise ValueError("Published DATA contains payload: " + folder)
    for name, content in seeds.items():
        path = _managed(root, "DATA/" + name)
        if (path.stat().st_size > MAX_SEED_BYTES or
                path.read_bytes().replace(b"\r\n", b"\n") != content.replace(b"\r\n", b"\n")):
            raise ValueError("Published DATA scaffold differs from its dedicated seed: " + name)


def _git(git, directory, arguments, *, input_bytes=None, limit=MAX_GIT_BYTES):
    """Read bounded Git metadata output, with a process deadline and no hooks."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    command = [git, "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
               "-C", str(directory), *arguments]
    # An anonymous, bounded synthetic-probe input avoids pipe deadlocks when
    # check-ignore writes evidence before it has consumed every input pathname.
    input_file = tempfile.TemporaryFile() if input_bytes is not None else None
    if input_file is not None:
        if len(input_bytes) > MAX_GIT_BYTES:
            input_file.close()
            raise ValueError("Git probe input exceeds its metadata bound")
        input_file.write(input_bytes)
        input_file.seek(0)
    try:
        process = subprocess.Popen(command, stdin=input_file if input_file is not None else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
    except BaseException:
        if input_file is not None:
            input_file.close()
        raise
    timer = threading.Timer(10, process.kill)
    timer.daemon = True
    timer.start()
    try:
        output = process.stdout.read(limit + 1)
        truncated = len(output) > limit
        if truncated:
            process.kill()
        code = process.wait(timeout=2)
        return code, output[:limit], truncated
    finally:
        timer.cancel()
        if input_file is not None:
            input_file.close()
        process.stdout.close()
        if process.poll() is None:
            process.kill()
            process.wait()


def _git_audit(root):
    result = {"state": "unverified", "payloadIgnored": None, "scaffoldTrackable": None,
              "ignoreEvidence": "synthetic-probes-and-tracked-index-only",
              "allUntrackedPayloadVerified": False,
              "limitation": ("Verified means only the fixed synthetic path probes and bounded tracked-index check passed; "
                             "arbitrary customized ignore exceptions and actual untracked payload are not exhaustively checked. "
                             "Use git check-ignore --verbose --no-index -- PATH for a specific payload path."),
              "trackedPayloadCount": None, "trackedPayloadPaths": [], "trackedPathsTruncated": False,
              "probes": [], "warnings": []}
    git = shutil.which("git")
    if not git:
        result["warnings"].append("Git is unavailable; payload ignore protection is unverified")
        return result
    try:
        code, output, truncated = _git(git, root, ["rev-parse", "--show-toplevel"], limit=8192)
        if code or truncated:
            result["warnings"].append("Scope is not a verified Git worktree; ignore protection is unverified")
            return result
        repo = Path(os.fsdecode(output).strip())
        scope_path = root.resolve().relative_to(repo.resolve()).as_posix()
        relative = ("" if scope_path == "." else scope_path + "/") + "DATA/"
        if relative.startswith("/"):
            raise ValueError("Unexpected Git root")
        # Synthetic path probes do not create files, enumerate payload, or read it.
        payload = ["__systemx_ignore_probe__.bin", "nested/README.md"]
        for folder in FOLDERS:
            payload.extend([folder + "/__systemx_ignore_probe__.bin", folder + "/nested/README.md"])
        targets = payload + list(SCAFFOLD)
        probe_input = b"\0".join(os.fsencode(relative + name) for name in targets) + b"\0"
        code, output, truncated = _git(git, repo,
            ["check-ignore", "--no-index", "--verbose", "--non-matching", "-z", "--stdin"],
            input_bytes=probe_input)
        fields = output.split(b"\0")
        if code not in (0, 1) or truncated or fields[-1] != b"" or len(fields[:-1]) != len(targets) * 4:
            result["warnings"].append("Git ignore probes did not return complete evidence")
            return result
        evidence = {}
        for index in range(0, len(fields) - 1, 4):
            source, line, pattern, path = (os.fsdecode(value) for value in fields[index:index + 4])
            name = path[len(relative):] if path.startswith(relative) else ""
            if name not in targets or name in evidence:
                result["warnings"].append("Git ignore probes returned unexpected path evidence")
                return result
            evidence[name] = {"path": name, "ignored": bool(pattern and not pattern.startswith("!")),
                              "ruleSource": source, "ruleLine": line, "rulePattern": pattern}
        result["probes"] = [evidence[name] for name in targets]
        result["payloadIgnored"] = all(evidence[name]["ignored"] for name in payload)
        result["scaffoldTrackable"] = all(not evidence[name]["ignored"] for name in SCAFFOLD)
        code, output, truncated = _git(git, repo, ["ls-files", "--cached", "-z", "--", relative.rstrip("/")])
        if code and not truncated:
            result["warnings"].append("Git tracked-path inventory failed; already tracked payload is unverified")
            return result
        paths = output.split(b"\0")
        # A truncated final path is never displayed as complete evidence.
        if paths[-1] == b"":
            paths.pop()
        elif truncated:
            paths.pop()
        tracked = sorted({os.fsdecode(path)[len(relative):] for path in paths
                          if os.fsdecode(path).startswith(relative) and
                          os.fsdecode(path)[len(relative):] not in SCAFFOLD})
        result["trackedPayloadCount"] = len(tracked)
        result["trackedPayloadCountIsLowerBound"] = truncated
        result["trackedPayloadPaths"] = tracked[:MAX_DISPLAY_PATHS]
        result["trackedPathsTruncated"] = truncated or len(tracked) > MAX_DISPLAY_PATHS
        if not result["payloadIgnored"]:
            result["warnings"].append("One or more payload path probes are not ignored by effective Git rules")
        if not result["scaffoldTrackable"]:
            result["warnings"].append("One or more exact scaffold files are ignored; review parent/local rules")
        if tracked:
            result["warnings"].append("Already tracked DATA payload remains in Git; ignore rules cannot hide it or remove history")
        if truncated:
            result["warnings"].append("Tracked path metadata exceeded the bound; counts are lower bounds")
        result["state"] = ("verified" if result["payloadIgnored"] and result["scaffoldTrackable"] and
                           not tracked and not truncated else "warning")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result["warnings"].append("Git ignore audit is unverified: " + str(error))
    return result


def status(root):
    root, base = _guard(root)
    return {"schemaVersion": 1, "kind": "local-data-status", "path": str(base),
            "exists": base.is_dir(), "scaffoldMissing": [name for name in SCAFFOLD if not (base / name).is_file()],
            "payloadRead": False, "payloadTraversed": False, "payloadSynced": False,
            "git": _git_audit(root)}


def initialize(root, defaults, apply=False):
    root, _ = _guard(root)
    seeds = _blueprint(defaults)
    missing = [name for name in SCAFFOLD if not _managed(root, "DATA/" + name).exists()]
    created = []
    if apply:
        # Every existing document is preserved, even when customized. Recheck
        # before each exclusive create; never replace an existing pathname.
        for name in missing:
            root, _ = _guard(root)
            path = _managed(root, "DATA/" + name)
            path.parent.mkdir(parents=True, exist_ok=True)
            root, _ = _guard(root)
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                                     getattr(os, "O_NOFOLLOW", 0), 0o644)
            except FileExistsError:
                continue
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(seeds[name])
            created.append(name)
    return {"schemaVersion": 1, "kind": "local-data-init", "applied": bool(apply),
            "wouldCreate": missing, "created": created, "preservedExisting": True,
            "payloadRead": False, "payloadSynced": False, "payloadDeleted": False}


def add_cli(subparsers, scope=None):
    command = subparsers.add_parser("data", help="local ignored payload scaffold and bounded Git-ignore audit")
    actions = command.add_subparsers(dest="data_action", required=True)
    for action in ("init", "status", "audit"):
        parser = actions.add_parser(action)
        if scope is not None:
            parser = scope(parser)
        if action == "init":
            parser.add_argument("--apply", action="store_true", help="add missing scaffold only; preserve existing files")


def dispatch(root, defaults, args):
    if args.data_action == "init":
        return initialize(root, defaults, args.apply)
    if args.data_action in {"status", "audit"}:
        return status(root)
    raise ValueError("Unknown DATA action")
