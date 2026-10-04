"""Additive, versioned SYSTEMX installs. Python standard library; no shell evaluation."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import urllib.request
import uuid
import zipfile

if __package__:
    from . import lifecycle
    from .versions import version_id, version_key, release_channel, package_version
    from .systemx_paths import (SystemXPathError, inspect_layout, is_link, lexical_path,
                               lowercase_alias as path_alias, project_directory, record_directory)
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import lifecycle
    from versions import version_id, version_key, release_channel, package_version
    from systemx_paths import (SystemXPathError, inspect_layout, is_link, lexical_path,
                              lowercase_alias as path_alias, project_directory, record_directory)

DEFAULT_REPOSITORY = "WayneTechLab/dotSYSTEMX"
PACKAGE = Path(__file__).resolve().parent
MANIFEST = "config/distribution.json"
STATE = "INSTALLATION.json"
PROFILES = ("project", "directory", "drive", "chat")
MAX_ARCHIVE = 32 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024
MAX_FILES = 1000
SEEDS = ("GLOBAL/CONTEXT.md", "PLAN/MASTER-PLAN.md", "MEMORY/PROJECT.md",
         "AGENTS/agent.0/MEMORY.md", "AGENTS/REGISTRY.json", "WORK/TASKS.json",
         "WORK/FOCUS.json", "config/project.example.json")


InstallError = SystemXPathError


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def repository_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", value):
        raise InstallError("Repository must be an explicit GitHub OWNER/REPO")
    return value


def portable_path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise InstallError("Invalid distribution path")
    parts = value.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", *("COM" + str(n) for n in range(1, 10)),
                *("LPT" + str(n) for n in range(1, 10))}
    if any(p in {"", ".", ".."} or p.endswith((" ", ".")) or
           re.search(r'[<>"|?*\x00-\x1f]', p) or p.split(".")[0].upper() in reserved for p in parts):
        raise InstallError("Nonportable or escaping distribution path: " + value)
    if (any(p.casefold() == ".systemx" for p in parts) or
            parts[0].casefold() in {STATE.casefold(), "project.json", "local", "logs", "state"}):
        raise InstallError("Distribution must not contain installation or private project state")
    return value


def safe_path(root, relative):
    """Reject links below the explicitly selected root, including missing-leaf parents."""
    path = root / relative
    for part in (path, *path.parents):
        if part == root.parent:
            break
        if is_link(part):
            raise InstallError("Refusing symlink: " + str(part))
        if part != path and part.exists() and not part.is_dir():
            raise InstallError("A file occupies a required parent directory: " + str(part))
    if not path.resolve().is_relative_to(root.resolve()):
        raise InstallError("Path escapes the selected SYSTEMX directory")
    return path


def digest(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def decode(data):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise InstallError("Duplicate JSON field: " + key)
            value[key] = item
        return value
    def invalid(value):
        raise InstallError("Non-finite JSON value: " + value)
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid)


def verified_bundle(files):
    if MANIFEST not in files:
        raise InstallError("Source has no distribution manifest; use a managed-install release")
    manifest = decode(files[MANIFEST])
    if not isinstance(manifest, dict) or set(manifest) != {"schemaVersion", "version", "files"}:
        raise InstallError("Invalid distribution manifest fields")
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise InstallError("Unsupported distribution manifest schema")
    version_id(manifest["version"])
    inventory = manifest["files"]
    if not isinstance(inventory, dict) or not 1 <= len(inventory) <= MAX_FILES:
        raise InstallError("Invalid distribution inventory")
    if set(files) != set(inventory) | {MANIFEST}:
        raise InstallError("Distribution inventory does not match the supplied files")
    required = {"VERSION", "LICENSE", "SOURCE.json", "STANDARD.md", "START-HERE.md",
                "manager.py", "scripts/systemx.py", "scripts/project_memory.py",
                "config/template-records.json", *SEEDS}
    base_version = version_key(manifest["version"])[:3]
    if base_version >= (1, 4, 0):
        required.add("systemx_paths.py")
    if base_version >= (1, 5, 0):
        required.add("lifecycle.py")
    if base_version >= (1, 6, 0):
        required.add("versions.py")
    if base_version >= (1, 7, 0):
        required.update({"scripts/project_workspaces.py", "Projects/REGISTRY.json",
                         "templates/project/WORK/TASKS.json", "templates/project/WORK/FOCUS.json",
                         "templates/project/AGENTS/REGISTRY.json", "templates/project/project.json"})
    if base_version >= (1, 8, 0):
        required.update({"scripts/agent_standards.py", "scripts/agent_x.py", "scripts/agent_z.py",
                         "config/agent-z-policy.json", "templates/AGENT-X-MEMORY.md", "templates/AGENT-Z-MEMORY.md"})
    if not required.issubset(inventory):
        raise InstallError("Distribution is missing core files")
    folded = set()
    directory_spellings = {}
    inventory_names = {name.casefold() for name in inventory}
    for name, expected in inventory.items():
        portable_path(name)
        if name.casefold() in folded or name == MANIFEST:
            raise InstallError("Duplicate or self-referencing distribution path")
        folded.add(name.casefold())
        for parent in PurePosixPath(name).parents:
            spelling = str(parent)
            previous = directory_spellings.setdefault(spelling.casefold(), spelling)
            if previous != spelling:
                raise InstallError("Distribution directory has conflicting case spellings: " + spelling)
        if any(str(parent).casefold() in inventory_names for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise InstallError("Distribution file conflicts with a directory path")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise InstallError("Invalid distribution fingerprint")
        if len(files[name]) > MAX_FILE or digest(files[name]) != expected:
            raise InstallError("Distribution fingerprint mismatch: " + name)
    if files["VERSION"].decode().strip() != manifest["version"]:
        raise InstallError("Distribution version mismatch")
    seeds = decode(files["config/template-records.json"])
    if (not isinstance(seeds, dict) or set(seeds) != {"schemaVersion", "sha256"} or
            type(seeds["schemaVersion"]) is not int or seeds["schemaVersion"] != 1 or
            not isinstance(seeds["sha256"], dict) or set(seeds["sha256"]) != set(SEEDS)):
        raise InstallError("Invalid blank-record manifest")
    if any(digest(files[name]) != seeds["sha256"][name] for name in SEEDS):
        raise InstallError("Distribution contains changed project seeds")
    if decode(files["WORK/TASKS.json"]) != {"schemaVersion": 1, "tasks": []}:
        raise InstallError("Distribution task ledger must be empty")
    if base_version >= (1, 7, 0):
        if decode(files["Projects/REGISTRY.json"]) != {"schemaVersion": 1, "projects": []}:
            raise InstallError("Distribution project registry must be empty")
        for name in ("WORK/TASKS.json", "WORK/FOCUS.json", "AGENTS/REGISTRY.json"):
            if decode(files["templates/project/" + name]) != decode(files[name]):
                raise InstallError("Project blueprint coordination records must be blank")
        if decode(files["templates/project/project.json"]) != decode(files["config/project.example.json"]):
            raise InstallError("Project blueprint command configuration must be blank")
    if decode(files["WORK/FOCUS.json"]) != {"schemaVersion": 1, "objective": "", "taskIds": [], "checkpoint": "", "updatedAt": ""}:
        raise InstallError("Distribution focus must be empty")
    if decode(files["AGENTS/REGISTRY.json"]) != {"schemaVersion": 1, "agents": [
            {"id": "agent.0", "role": "coordinator", "memory": "AGENTS/agent.0/MEMORY.md"}]}:
        raise InstallError("Distribution must contain only the Agent 0 role")
    if decode(files["config/project.example.json"]) != {"schemaVersion": 1,
            "project": {"name": "", "description": ""}, "checks": [],
            "commands": {"dev": [], "build": [], "deploy": []}}:
        raise InstallError("Distribution commands must be empty")
    return {"version": manifest["version"], "manifestSha256": digest(files[MANIFEST]), "files": files}


def read_bundle(source):
    raw = lexical_path(source)
    if raw.name.casefold() == ".systemx":
        source = record_directory(raw)
    else:
        source = raw.resolve()
        layout = inspect_layout(source)
        if layout["aliasStatus"] != "not-installed":
            source = source / ".SYSTEMX"
    manifest_path = safe_path(source, MANIFEST)
    if manifest_path.stat().st_size > MAX_FILE:
        raise InstallError("Oversized distribution manifest")
    raw = manifest_path.read_bytes()
    manifest = decode(raw)
    if not isinstance(manifest, dict):
        raise InstallError("Distribution manifest must be an object")
    names = manifest.get("files", {})
    if not isinstance(names, dict) or len(names) > MAX_FILES:
        raise InstallError("Invalid distribution inventory")
    files = {MANIFEST: raw}
    for name in names:
        path = safe_path(source, portable_path(name))
        if not path.is_file() or path.stat().st_size > MAX_FILE:
            raise InstallError("Missing or oversized distribution file: " + name)
        files[name] = path.read_bytes()
    return verified_bundle(files)


def get_url(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "SYSTEMX-template-manager", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise InstallError("Remote response exceeds the download limit")
    return data


def latest_version(repository=DEFAULT_REPOSITORY, channel="stable"):
    repository_id(repository)
    if channel not in {"stable", "alpha"}:
        raise InstallError("Unknown release channel")
    # Stable installations never discover alpha releases implicitly. Alpha users
    # explicitly selected an alpha first; they can also graduate to a final tag.
    base = "https://api.github.com/repos/" + repository + "/releases"
    if channel == "stable":
        release = decode(get_url(base + "/latest", MAX_FILE))
        if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
            raise InstallError("Expected a stable published release")
        tag = release.get("tag_name", "")
        value = version_id(tag[1:] if isinstance(tag, str) and tag.startswith("v") else tag)
        if release_channel(value) != "stable":
            raise InstallError("Stable discovery refused an alpha tag")
        return value
    candidates = []
    # Bounded discovery; fail rather than silently select from a truncated list.
    for page in range(1, 11):
        releases = decode(get_url(base + "?per_page=100&page=" + str(page), MAX_ARCHIVE))
        if not isinstance(releases, list) or len(releases) > 100:
            raise InstallError("Invalid release list")
        for release in releases:
            if not isinstance(release, dict) or release.get("draft"):
                continue
            tag = release.get("tag_name", "")
            try:
                value = version_id(tag[1:] if isinstance(tag, str) and tag.startswith("v") else tag)
            except ValueError:
                continue
            expected_prerelease = release_channel(value) == "alpha"
            if release.get("prerelease") is expected_prerelease:
                candidates.append(value)
        if len(releases) < 100:
            if not candidates:
                raise InstallError("No compatible published alpha or final release found")
            return max(candidates, key=version_key)
    raise InstallError("Release discovery limit reached; select an exact --version")


def remote_bundle(version, repository=DEFAULT_REPOSITORY):
    version_id(version)
    repository_id(repository)
    data = get_url("https://codeload.github.com/" + repository + "/zip/refs/tags/v" + version, MAX_ARCHIVE)
    files = {}
    total = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for entry in archive.infolist():
            parts = PurePosixPath(entry.filename).parts
            if len(parts) >= 2 and parts[1].casefold() == ".systemx" and parts[1] != ".SYSTEMX":
                raise InstallError("Archive has a noncanonical .SYSTEMX folder spelling")
            if len(parts) < 3 or parts[1] != ".SYSTEMX" or entry.is_dir():
                continue
            name = portable_path("/".join(parts[2:]))
            total += entry.file_size
            if entry.file_size > MAX_FILE or total > MAX_ARCHIVE or len(files) >= MAX_FILES:
                raise InstallError("Distribution archive exceeds extraction limits")
            if (entry.external_attr >> 16) & 0o170000 == 0o120000 or name in files:
                raise InstallError("Archive contains a link or duplicate path")
            files[name] = archive.read(entry)
    bundle = verified_bundle(files)
    if bundle["version"] != version:
        raise InstallError("Tag does not match the distribution version")
    return bundle


def project_root(target):
    return project_directory(target)


def state_path(root):
    inspect_layout(root)
    return safe_path(root / ".SYSTEMX", STATE)


def load_state(root):
    value = decode(state_path(root).read_bytes())
    required = {"schemaVersion", "profile", "repository", "activeVersion", "pinnedVersion",
                "autoUpdate", "installedAt", "updatedAt", "releases"}
    if not isinstance(value, dict) or set(value) != required or type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        raise InstallError("Unrecognized INSTALLATION.json; it was not changed")
    if value["profile"] not in PROFILES or value["autoUpdate"] not in {"manual", "on-start"}:
        raise InstallError("Invalid installation profile or update policy")
    repository_id(value["repository"])
    version_id(value["activeVersion"])
    if value["pinnedVersion"] is not None:
        version_id(value["pinnedVersion"])
        if value["pinnedVersion"] != value["activeVersion"] or value["autoUpdate"] != "manual":
            raise InstallError("A pinned installation must use its pinned release and manual updates")
    if not isinstance(value["releases"], dict) or value["activeVersion"] not in value["releases"]:
        raise InstallError("Missing active release fingerprint")
    for release, fingerprint in value["releases"].items():
        version_id(release)
        if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            raise InstallError("Invalid stored release fingerprint")
    dates = []
    for field in ("installedAt", "updatedAt"):
        if not isinstance(value[field], str):
            raise InstallError("Installation timestamps must be timezone-aware strings")
        parsed = datetime.fromisoformat(value[field].replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise InstallError("Installation timestamps need an explicit timezone")
        dates.append(parsed)
    if dates[1] < dates[0]:
        raise InstallError("Installation update time precedes creation")
    return value


@contextmanager
def update_lock(root):
    inspect_layout(root)
    folder = safe_path(root / ".SYSTEMX", ".systemx")
    folder.mkdir(parents=True, exist_ok=True)
    path = safe_path(root / ".SYSTEMX", ".systemx/update.lock")
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise InstallError("Another install/update holds .systemx/update.lock; inspect its owner before recovery") from error
    handle = {"path": path}
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(json.dumps({"pid": os.getpid(), "createdAt": now()}))
        yield handle
    finally:
        handle["path"].unlink()


@contextmanager
def operation_log(root, action, details):
    folder = safe_path(root / ".SYSTEMX", ".systemx/operations")
    folder.mkdir(parents=True, exist_ok=True)
    create_missing(safe_path(root / ".SYSTEMX", ".systemx/operations/.gitignore"), b"*\n")
    path = folder / (uuid.uuid4().hex + ".json")
    value = {"schemaVersion": 1, "action": action, "startedAt": now(),
             "status": "started", "details": details}
    lifecycle.atomic_json(path, value)
    try:
        yield value
    except BaseException as error:
        value.update({"status": "failed", "errorType": type(error).__name__})
        raise
    else:
        value["status"] = "complete"
    finally:
        value["finishedAt"] = now()
        lifecycle.atomic_json(path, value)


def save_state(root, state):
    path = state_path(root)
    raw = (json.dumps(state, indent=2) + "\n").encode()
    # Keep every previous manager-owned state, including version selection history.
    if path.exists():
        history = safe_path(root / ".SYSTEMX", ".systemx/history")
        history.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix="state-", suffix=".json", dir=history, delete=False) as backup:
            backup.write(path.read_bytes())
    descriptor, temporary = tempfile.mkstemp(prefix="state-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def release_path(root, version):
    return safe_path(root / ".SYSTEMX", ".systemx/releases/" + version_id(version))


def active_bundle(root, state):
    path = release_path(root, state["activeVersion"])
    bundle = read_bundle(path)
    if bundle["version"] != state["activeVersion"]:
        raise InstallError("Selected version differs from the stored release")
    if bundle["manifestSha256"] != state["releases"][state["activeVersion"]]:
        raise InstallError("Installed release fingerprint changed; restore the exact release before running it")
    return path, bundle


def prepare(root, bundle):
    folder = root / ".SYSTEMX"
    snapshot = release_path(root, bundle["version"])
    result = {"version": bundle["version"], "target": str(root), "add": [], "preserve": [], "conflicts": []}
    for name, data in sorted(bundle["files"].items()):
        destination = safe_path(folder, name)
        cached = safe_path(snapshot, name)
        if cached.exists() and (not cached.is_file() or digest(cached.read_bytes()) != digest(data)):
            result["conflicts"].append("Existing release differs: " + name)
        if destination.exists():
            result["preserve"].append(name)
            if not destination.is_file():
                result["conflicts"].append("A directory occupies a required file path: " + name)
        else:
            result["add"].append(name)
    return result


def create_missing(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        return False
    return True


def apply_bundle(root, bundle, state, profile, repository):
    plan = prepare(root, bundle)
    if plan["conflicts"]:
        raise InstallError("; ".join(plan["conflicts"]))
    snapshot = release_path(root, bundle["version"])
    for name, data in bundle["files"].items():
        cached = safe_path(snapshot, name)
        create_missing(cached, data)
        if not cached.is_file() or digest(cached.read_bytes()) != digest(data):
            raise InstallError("Concurrent change or incomplete release file: " + name)
    # Verify the full immutable copy before selecting it or seeding any project file.
    read_bundle(snapshot)
    for name, data in bundle["files"].items():
        create_missing(safe_path(root / ".SYSTEMX", name), data)
    if state is None:
        state = {"schemaVersion": 1, "profile": profile, "repository": repository,
                 "activeVersion": bundle["version"], "pinnedVersion": bundle["version"],
                 "autoUpdate": "manual", "installedAt": now(), "updatedAt": now(), "releases": {}}
    state["activeVersion"] = bundle["version"]
    state["releases"][bundle["version"]] = bundle["manifestSha256"]
    state["updatedAt"] = now()
    save_state(root, state)
    plan.update({"applied": True, "defaults": str(snapshot), "policy": state["autoUpdate"], "pinnedVersion": state["pinnedVersion"]})
    return plan


def install(target, *, source=None, version=None, profile="project", repository=DEFAULT_REPOSITORY,
            dry_run=False, lowercase_alias=False):
    """Create only absent files, store immutable defaults, and pin the initial release."""
    root = project_root(target)
    if profile not in PROFILES:
        raise InstallError("Unknown setup profile")
    repository_id(repository)
    if state_path(root).exists():
        raise InstallError("Already managed; use update or policy")
    bundle = read_bundle(source or PACKAGE) if version is None or source else remote_bundle(version, repository)
    if version is not None and bundle["version"] != version_id(version):
        raise InstallError("Requested version differs from the supplied source")
    if dry_run:
        return {**prepare(root, bundle), "applied": False, "profile": profile, "pinnedVersion": bundle["version"],
                "pathLayout": alias(root, create=lowercase_alias, dry_run=True)}
    with update_lock(root):
        if state_path(root).exists():
            raise InstallError("Another installer initialized this project")
        with operation_log(root, "install", {"version": bundle["version"], "profile": profile}) as log:
            result = apply_bundle(root, bundle, None, profile, repository)
            # The complete installation is retained if optional link setup fails.
            result["pathLayout"] = path_alias(root, create=lowercase_alias)
            log["result"] = result
            return result


def alias(target, *, create=False, dry_run=False):
    """Inspect exact casing or opt in to a local .systemx -> .SYSTEMX link."""
    if not create or dry_run:
        return path_alias(target, create=create, dry_run=dry_run)
    root = project_root(target)
    if inspect_layout(root, required=True)["aliasStatus"] != "absent":
        return path_alias(root, create=True)
    with update_lock(root), operation_log(root, "alias", {"target": ".systemx -> .SYSTEMX"}) as log:
        result = path_alias(root, create=True)
        log["result"] = result
        return result


def update(target, *, source=None, version=None, dry_run=False):
    """Append a release and missing root files; never replace or delete existing root files."""
    root = project_root(target)
    state = load_state(root)
    if state["pinnedVersion"] and version not in {None, state["pinnedVersion"]}:
        raise InstallError("Version is pinned; explicitly unpin before selecting another release")
    desired = version or (state["pinnedVersion"] if not source else None)
    bundle = read_bundle(source) if source else remote_bundle(
        desired or latest_version(state["repository"], channel=release_channel(state["activeVersion"])), state["repository"])
    if not source and version is None and version_key(bundle["version"]) < version_key(state["activeVersion"]):
        raise InstallError("Discovery would downgrade this project; select an exact --version to roll back")
    if version is not None and bundle["version"] != version_id(version):
        raise InstallError("Requested version differs from the supplied source")
    if state["pinnedVersion"] and bundle["version"] != state["pinnedVersion"]:
        raise InstallError("Version is pinned; explicitly unpin before selecting another release")
    if dry_run:
        return {**prepare(root, bundle), "applied": False}
    with update_lock(root):
        current = load_state(root)
        if current != state:
            raise InstallError("Installation policy changed while preparing the update; retry")
        with operation_log(root, "update", {"fromVersion": state["activeVersion"], "toVersion": bundle["version"]}) as log:
            result = apply_bundle(root, bundle, state, state["profile"], state["repository"])
            log["result"] = result
            return result


def set_policy(target, *, pin=None, auto_update=None):
    """pin='current' locks the selected release; pin='none' explicitly unlocks it."""
    root = project_root(target)
    load_state(root)
    with update_lock(root):
        state = load_state(root)
        if pin is not None:
            if pin not in {"current", "none"}:
                raise InstallError("Pin must be current or none; select a release with update first")
            state["pinnedVersion"] = state["activeVersion"] if pin == "current" else None
            if pin == "current":
                state["autoUpdate"] = "manual"
        if auto_update is not None:
            if auto_update not in {"manual", "on-start"}:
                raise InstallError("Automatic updates must be manual or on-start")
            if auto_update == "on-start" and state["pinnedVersion"]:
                raise InstallError("Unpin explicitly before enabling automatic updates")
            state["autoUpdate"] = auto_update
        state["updatedAt"] = now()
        with operation_log(root, "policy", {"pinnedVersion": state["pinnedVersion"], "autoUpdate": state["autoUpdate"]}):
            save_state(root, state)
        return state


def status(target):
    root = project_root(target)
    state = load_state(root)
    path, bundle = active_bundle(root, state)
    return {"target": str(root), "profile": state["profile"], "activeVersion": bundle["version"],
            "pinnedVersion": state["pinnedVersion"], "autoUpdate": state["autoUpdate"],
            "releaseChannel": release_channel(bundle["version"]),
            "defaults": str(path), "retainedVersions": sorted(state["releases"], key=version_key), "integrity": "verified",
            "pathLayout": alias(root)}


def startup_update(root):
    state = load_state(root)
    if state["autoUpdate"] != "on-start" or state["pinnedVersion"]:
        return
    marker = safe_path(root / ".SYSTEMX", ".systemx/last-check.json")
    if marker.exists():
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(decode(marker.read_bytes())["at"].replace("Z", "+00:00"))).total_seconds()
            if 0 <= age < 86400:
                return
        except (ValueError, KeyError, TypeError):
            pass
    try:
        version = latest_version(state["repository"], channel=release_channel(state["activeVersion"]))
        new, old = version_key(version), version_key(state["activeVersion"])
        if new > old and new[0] == old[0]:
            update(root, version=version)
            print("SYSTEMX selected new defaults: " + version, file=sys.stderr)
        elif new[0] != old[0]:
            print("SYSTEMX: a different major release needs a manual upgrade review", file=sys.stderr)
        # This is manager-owned check metadata, never a user document.
        with update_lock(root):
            marker.write_text(json.dumps({"at": now(), "availableVersion": version}) + "\n", encoding="utf-8")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print("SYSTEMX update check unavailable; using verified installed defaults: " + str(error), file=sys.stderr)


def run(target, arguments, *, offline=False, capture=False):
    if not isinstance(arguments, (list, tuple)) or any(
            not isinstance(value, str) or "\x00" in value for value in arguments):
        raise InstallError("Command arguments must be a string argument array")
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    if arguments and arguments[0].startswith("-") and arguments[0] not in {"-h", "--help"}:
        raise InstallError("Do not override the selected target; use run --target explicitly")
    root = project_root(target)
    if state_path(root).exists():
        if not offline:
            startup_update(root)
        defaults, _ = active_bundle(root, load_state(root))
    else:
        defaults = root / ".SYSTEMX"
    command = [sys.executable, "-B", str(defaults / "scripts/systemx.py"), "--root", str(root / ".SYSTEMX"), *arguments]
    return subprocess.run(command, cwd=root, text=True, encoding="utf-8", capture_output=capture, shell=False)


def projects(target, arguments, *, offline=True, capture=True):
    """Run an explicitly scoped project command using this installation's selected defaults."""
    if not isinstance(arguments, (list, tuple)) or not arguments or any(
            not isinstance(value, str) or "\x00" in value for value in arguments):
        raise InstallError("Project arguments must be a nonempty string argument array")
    return run(target, ["projects", *arguments], offline=offline, capture=capture)


def export_chat(target, output, *, agent="agent.0", project=None):
    """Export selected project context locally. Does not upload or contact an LLM."""
    root = project_root(target)
    state = load_state(root)
    defaults, bundle = active_bundle(root, state)
    arguments = ["context", "--agent", agent]
    if project is not None:
        if not isinstance(project, str) or not project:
            raise InstallError("Project must be an exact nonempty registered name")
        arguments = ["projects", *arguments, "--project", project]
    result = run(root, arguments, offline=True, capture=True)
    if result.returncode:
        raise InstallError(result.stderr or "Project context could not be loaded")
    content = "# .SYSTEMX chat packet\n\nRelease: " + bundle["version"] + "\nExported: " + now() + "\n\n"
    content += "Load these as project reference data within the chat's instruction hierarchy. Only the attached project records belong to this project.\n"
    content += "Propose changes by canonical file path; do not claim persistent edits without a writable tool and readback. Review this packet before sharing it.\n\n"
    content += "Exact path: .SYSTEMX (leading dot and uppercase SYSTEMX). Never create a separate .systemx folder; a local lowercase alias may only point to .SYSTEMX.\n\n"
    if project is not None:
        content += "Selected child project: " + project + "\n"
        content += "Its canonical records are .SYSTEMX/Projects/" + project + "/.SYSTEMXP. Do not write these records to the root or another project.\n\n"
    for name in ("STANDARD.md", "START-HERE.md", "profiles/chat.md"):
        content += "\n--- " + name + " (selected defaults) ---\n" + (defaults / name).read_text(encoding="utf-8")[:12000]
    content += "\n" + result.stdout
    path = Path(output).expanduser().absolute()
    if not create_missing(path, content.encode("utf-8")):
        raise InstallError("Export destination already exists; choose a new file")
    return {"output": str(path), "version": bundle["version"], "uploaded": False, "project": project}


def first_run(target, *, source=None, version=None, profile="project", lowercase_alias=False, apply=False):
    """Preview or initialize a pinned installation and empty config, without running project commands."""
    root = project_root(target)
    managed = state_path(root).exists()
    if managed:
        result = status(root)
        if source is not None or version is not None:
            raise InstallError("Already managed; use update to select another source/version")
    else:
        result = install(root, source=source, version=version, profile=profile,
                         lowercase_alias=lowercase_alias, dry_run=not apply)
    result = {"action": "first-run", "applied": apply, "installation": result,
              "config": "preserve" if safe_path(root / ".SYSTEMX", "project.json").exists() else "create-empty",
              "nextSteps": ["Fill .SYSTEMX/GLOBAL/CONTEXT.md with approved project facts",
                            "Define outcomes and acceptance in .SYSTEMX/PLAN/MASTER-PLAN.md",
                            "Configure only real project checks in .SYSTEMX/project.json",
                            "Run validate, then load context --agent agent.0"],
              "guide": "https://github.com/WayneTechLab/dotSYSTEMX/wiki/First-Time-Setup"}
    if not apply:
        return result
    if managed and lowercase_alias:
        alias(root, create=True)
    with update_lock(root), operation_log(root, "first-run", {"alreadyManaged": managed}) as log:
        _, bundle = active_bundle(root, load_state(root))
        created = create_missing(safe_path(root / ".SYSTEMX", "project.json"), bundle["files"]["config/project.example.json"])
        result["config"] = "created-empty" if created else "preserved"
        log["result"] = result
    return result


def audit(target):
    """Read-only audit of the selected project's footprint, never a whole-computer cleanup claim."""
    root = project_directory(target, check_layout=False)
    entries = lifecycle.path_entries(root)
    result = {"target": str(root), "scope": "Project .SYSTEMX directory and case variants only",
              "entries": entries, "clean": not entries, "issues": [], "operationLogs": [],
              "externalRemoval": "Use the installing Python environment's pip uninstall dotsystemx separately; shared runtimes and host files are outside this audit"}
    try:
        result["pathLayout"] = inspect_layout(root)
        if state_path(root).exists():
            result["installation"] = status(root)
        logs = safe_path(root / ".SYSTEMX", ".systemx/operations")
        if logs.is_dir():
            for path in sorted(logs.glob("*.json")):
                safe_path(root / ".SYSTEMX", path.relative_to(root / ".SYSTEMX"))
                value = decode(path.read_bytes())
                result["operationLogs"].append({"file": str(path), "action": value.get("action"), "status": value.get("status")})
                if value.get("status") != "complete":
                    result["issues"].append("Incomplete operation: " + path.name)
        lock = safe_path(root / ".SYSTEMX", ".systemx/update.lock")
        if lock.exists():
            result["issues"].append("Writer lock present; verify its owner before any recovery")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        result["issues"].append(str(error))
    return result


def uninstall(target, *, backup=None, apply=False):
    """Archive the entire exact-case folder and remove its local alias, with an external receipt."""
    root = project_root(target)
    folder = root / ".SYSTEMX"
    if not folder.exists():
        return {"action": "uninstall", "applied": False, "status": "not-installed", "audit": audit(root)}
    # Running code/working directories cannot be moved reliably on all platforms.
    # The package or a separate reviewed checkout is the removal entry point.
    if PACKAGE.is_relative_to(folder) or Path.cwd().resolve().is_relative_to(folder):
        raise InstallError("Run uninstall from outside the target .SYSTEMX, using the installed library or a separate reviewed checkout")
    destination = lifecycle.external_backup(root, backup) if backup else None
    if apply and destination is None:
        raise InstallError("Uninstall --apply requires --backup pointing to a new directory outside the project")
    layout = inspect_layout(root, required=True)
    records = lifecycle.inventory(folder, exclude=(".systemx/update.lock",))
    result = {"action": "uninstall", "applied": False, "target": str(root),
              "scope": "Archive the entire .SYSTEMX folder, including all user tasks, memory, configuration, defaults, and logs",
              "backup": str(destination) if destination else None, "entries": len(records),
              "fileBytes": sum(entry.get("bytes", 0) for entry in records.values()),
              "removeAlias": layout["aliasStatus"] == "linked", "permanentDeletion": False}
    if not apply:
        return result
    with update_lock(root) as lock:
        layout = inspect_layout(root, required=True)
        records = lifecycle.inventory(folder, exclude=(".systemx/update.lock",))
        result.update({"entries": len(records), "fileBytes": sum(entry.get("bytes", 0) for entry in records.values()),
                       "removeAlias": layout["aliasStatus"] == "linked"})
        destination.mkdir(mode=0o700)  # Exclusive destination; never reuse or overwrite a backup.
        create_missing(destination / ".gitignore", b"*\n")
        receipt_path = destination / "UNINSTALL-LOG.json"
        receipt = {"schemaVersion": 1, "action": "uninstall", "status": "prepared", "startedAt": now(),
                   "target": str(root), "aliasWasLinked": layout["aliasStatus"] == "linked", "inventory": records}
        lifecycle.atomic_json(receipt_path, receipt)
        try:
            os.rename(folder, destination / ".SYSTEMX")
            lock["path"] = destination / ".SYSTEMX/.systemx/update.lock"
            receipt["status"] = "archived"
            lifecycle.atomic_json(receipt_path, receipt)
            if receipt["aliasWasLinked"]:
                alias_path = root / ".systemx"
                if not alias_path.is_symlink() or os.readlink(alias_path) != ".SYSTEMX":
                    raise InstallError("Alias changed during removal; archived data is safe, inspect the remaining entry")
                alias_path.unlink()
            if lifecycle.inventory(destination / ".SYSTEMX", exclude=(".systemx/update.lock",)) != records:
                raise InstallError("Archived files changed during removal; inspect the backup before restoring")
            receipt.update({"status": "complete", "finishedAt": now(), "audit": audit(root)})
            lifecycle.atomic_json(receipt_path, receipt)
        except BaseException as error:
            receipt.update({"status": "incomplete", "errorType": type(error).__name__, "finishedAt": now()})
            lifecycle.atomic_json(receipt_path, receipt)
            raise
    result.update({"applied": True, "log": str(receipt_path), "audit": audit(root)})
    return result


def restore(target, *, backup, apply=False):
    """Verify a removal backup, then restore only into an empty project slot."""
    root = project_directory(target, check_layout=False)
    if not root.is_dir():
        raise InstallError("Restore target must be an existing containing project directory")
    destination = lifecycle.external_backup(root, backup, must_exist=True)
    receipt_path = destination / "UNINSTALL-LOG.json"
    if is_link(receipt_path):
        raise InstallError("Refusing a linked uninstall receipt")
    receipt = decode(receipt_path.read_bytes())
    if (not isinstance(receipt, dict) or type(receipt.get("schemaVersion")) is not int or receipt["schemaVersion"] != 1 or
            receipt.get("action") != "uninstall" or receipt.get("status") not in {"prepared", "archived", "complete", "incomplete"} or
            not isinstance(receipt.get("inventory"), dict) or type(receipt.get("aliasWasLinked")) is not bool):
        raise InstallError("Unrecognized uninstall receipt")
    # A previous partial uninstall may have left its exact, dangling alias.
    for entry in lifecycle.path_entries(root):
        path = root / entry["name"]
        if not (entry["name"] == ".systemx" and receipt["aliasWasLinked"] and
                path.is_symlink() and os.readlink(path) == ".SYSTEMX" and not path.exists()):
            raise InstallError("Restore will not overwrite an existing .SYSTEMX or case variant")
    archived = destination / ".SYSTEMX"
    if PACKAGE.is_relative_to(archived) or Path.cwd().resolve().is_relative_to(archived):
        raise InstallError("Run restore from outside the archived .SYSTEMX using the installed library or a separate reviewed checkout")
    if (archived / ".systemx/update.lock").exists():
        raise InstallError("Backup has a writer lock; verify its owner before recovery")
    if lifecycle.inventory(archived) != receipt["inventory"]:
        raise InstallError("Backup inventory differs from the uninstall log; inspect it before manual recovery")
    result = {"action": "restore", "target": str(root), "backup": str(destination),
              "applied": False, "entries": len(receipt["inventory"])}
    if not apply:
        return result
    restore_lock = destination / "restore.lock"
    descriptor = os.open(restore_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(descriptor)
        # Recheck after claiming the backup lock; no existing directory is replaced.
        if (root / ".SYSTEMX").exists() or (root / ".SYSTEMX").is_symlink():
            raise InstallError("A .SYSTEMX entry appeared during restore; nothing was overwritten")
        if lifecycle.inventory(archived) != receipt["inventory"]:
            raise InstallError("Backup changed while preparing restore")
        receipt["restore"] = {"target": str(root), "startedAt": now(), "status": "started"}
        lifecycle.atomic_json(receipt_path, receipt)
        try:
            os.rename(archived, root / ".SYSTEMX")
            if receipt["aliasWasLinked"]:
                path_alias(root, create=True)
            receipt["restore"].update({"status": "complete", "finishedAt": now()})
        except BaseException as error:
            receipt["restore"].update({"status": "incomplete", "errorType": type(error).__name__, "finishedAt": now()})
            raise
        finally:
            lifecycle.atomic_json(receipt_path, receipt)
    finally:
        restore_lock.unlink()
    return {**result, "applied": True, "log": str(receipt_path), "audit": audit(root)}


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=".SYSTEMX additive installation and version management")
    tool_version = version_id((PACKAGE / "VERSION").read_text(encoding="utf-8").strip())
    parser.add_argument("--version", action="version", version=".SYSTEMX " + tool_version +
                        " (" + release_channel(tool_version) + "; Python package " + package_version(tool_version) + ")")
    sub = parser.add_subparsers(dest="action", required=True)
    command = sub.add_parser("install")
    command.add_argument("--target", required=True)
    command.add_argument("--profile", choices=PROFILES, default="project")
    command.add_argument("--source")
    command.add_argument("--version")
    command.add_argument("--repository", default=DEFAULT_REPOSITORY)
    command.add_argument("--dry-run", action="store_true")
    command.add_argument("--lowercase-alias", action="store_true", help="optionally create a local .systemx -> .SYSTEMX link")
    command = sub.add_parser("alias", help="check exact casing and optionally create the lowercase alias")
    command.add_argument("--target", required=True)
    command.add_argument("--create", action="store_true")
    command.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("update")
    command.add_argument("--target", required=True)
    command.add_argument("--source")
    command.add_argument("--version")
    command.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("policy")
    command.add_argument("--target", required=True)
    command.add_argument("--pin", choices=("current", "none"))
    command.add_argument("--auto", choices=("manual", "on-start"))
    command = sub.add_parser("status")
    command.add_argument("--target", required=True)
    command = sub.add_parser("run")
    command.add_argument("--target", required=True)
    command.add_argument("--offline", action="store_true")
    command.add_argument("arguments", nargs=argparse.REMAINDER)
    command = sub.add_parser("export-chat")
    command.add_argument("--target", required=True)
    command.add_argument("--output", required=True)
    command.add_argument("--agent", default="agent.0")
    command.add_argument("--project", help="export only this registered .SYSTEMXP scope")
    command = sub.add_parser("setup")
    command.add_argument("--profile", choices=PROFILES, required=True)
    command = sub.add_parser("first-run", help="preview or initialize a project without running project commands")
    command.add_argument("--target", required=True)
    command.add_argument("--profile", choices=PROFILES, default="project")
    command.add_argument("--source")
    command.add_argument("--version")
    command.add_argument("--lowercase-alias", action="store_true")
    mode = command.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    command = sub.add_parser("audit", help="read-only inspection of this project's installation footprint")
    command.add_argument("--target", required=True)
    for name in ("uninstall", "restore"):
        command = sub.add_parser(name, help="preview by default; --apply performs a reversible folder move")
        command.add_argument("--target", required=True)
        command.add_argument("--backup", required=name == "restore")
        mode = command.add_mutually_exclusive_group()
        mode.add_argument("--apply", action="store_true")
        mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "install":
            result = install(args.target, source=args.source, version=args.version, profile=args.profile,
                             repository=args.repository, dry_run=args.dry_run, lowercase_alias=args.lowercase_alias)
        elif args.action == "alias":
            result = alias(args.target, create=args.create, dry_run=args.dry_run)
        elif args.action == "update":
            result = update(args.target, source=args.source, version=args.version, dry_run=args.dry_run)
        elif args.action == "policy":
            result = set_policy(args.target, pin=args.pin, auto_update=args.auto)
        elif args.action == "status":
            result = status(args.target)
        elif args.action == "run":
            return run(args.target, args.arguments, offline=args.offline).returncode
        elif args.action == "export-chat":
            result = export_chat(args.target, args.output, agent=args.agent, project=args.project)
        elif args.action == "first-run":
            result = first_run(args.target, source=args.source, version=args.version, profile=args.profile,
                               lowercase_alias=args.lowercase_alias, apply=args.apply)
        elif args.action == "audit":
            result = audit(args.target)
        elif args.action == "uninstall":
            result = uninstall(args.target, backup=args.backup, apply=args.apply)
        elif args.action == "restore":
            result = restore(args.target, backup=args.backup, apply=args.apply)
        else:
            profiles = decode((PACKAGE / "config/profiles.json").read_bytes())
            result = profiles["profiles"][args.profile]
        print(json.dumps(result, indent=2))
        if args.action == "audit" and result["issues"]:
            return 2
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print("SYSTEMX manager: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("SYSTEMX manager interrupted; existing project files and earlier releases are retained", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
