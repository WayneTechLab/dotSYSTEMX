"""Optional Agent 1 security and access review: bounded, warning-only observations.

This module never installs a service or sends telemetry. Dotenv inventory
temporarily parses source lines in process memory; values are not returned,
logged, stored, or uploaded. Assessments do not change the reviewed project.
GitHub secret creation is a separate per-name, per-target, terminal action.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
import getpass
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import stat
import subprocess
import sys
from types import SimpleNamespace


COMMANDS = {"agent-1"}
REQUIRED = ("scripts/security_agent1.py", "SECURITY/AGENT1/questions.json",
            "SECURITY/AGENT1/event_buckets.json", "SECURITY/AGENT1/README.md",
            "tests/test_security_agent1.py")
PROFILES = ("all-in-one", "app", "webapp", "code", "cloud", "device")
MAX_WALK_ENTRIES = 10000
MAX_ENV_BYTES = 1024 * 1024
KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
SKIP_DIRS = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", ".next",
                       "dist", "build", "coverage", "LOCAL-ARCHIVES"})
SAMPLE_ENV_SUFFIXES = frozenset({"example", "sample", "template", "dist"})
SETUP_QUESTIONS = (
    ("accountContext", "Is this a personal or enterprise workspace?", ("personal", "enterprise")),
    ("repository", "What exact OWNER/REPO identifies the GitHub repository?", None),
    ("reviewScope", "Is this review for the root template or a selected project?", ("root", "project")),
    ("actorRole", "Will this user act as owner, operator, or guest?", ("owner", "operator", "guest")),
    ("githubActionsSecretTarget", "Will GitHub Actions secrets target a repository, environment, or nowhere?",
     ("repository", "environment", "none")),
    ("localSecretStore", "Which local runtime secret store is selected, if any?",
     ("macos-keychain", "windows-credential-manager", "linux-secret-service", "none")),
    ("envTrackedHistoryReviewed", "Has tracked .env history been checked for exposed values?", ("yes", "no")),
    ("envRotationDecision", "Were exposed values rotated, or is rotation still needed?",
     ("rotated", "needed", "not-applicable")),
)


def _defaults(defaults: Path | str | None) -> Path:
    return Path(defaults) if defaults is not None else Path(__file__).resolve().parents[1]


def _project(root: Path | str) -> tuple[Path, Path]:
    selected = Path(root).expanduser()
    if not selected.exists() or not selected.is_dir() or selected.is_symlink():
        raise ValueError("Selected review root must be an existing, nonlinked directory")
    selected = selected.resolve()
    if selected.name in {".SYSTEMX", ".SYSTEMXP"} and (selected / "START-HERE.md").is_file():
        return selected, selected.parent
    if (selected / ".SYSTEMXP").is_dir():
        return selected / ".SYSTEMXP", selected
    if (selected / ".SYSTEMX").is_dir():
        return selected / ".SYSTEMX", selected
    return selected / ".SYSTEMX", selected


def _secure_file_ops_available() -> bool:
    return (os.name == "posix" and all(hasattr(os, flag) for flag in
            ("O_DIRECTORY", "O_NOFOLLOW", "O_NONBLOCK")) and
            os.open in os.supports_dir_fd and os.rename in os.supports_dir_fd and
            os.unlink in os.supports_dir_fd and os.mkdir in os.supports_dir_fd)


@contextmanager
def _anchored_parent(project: Path, path: Path | str):
    """Hold a no-follow directory chain from the selected project to a leaf."""
    if not _secure_file_ops_available():
        raise ValueError("Secure Agent 1 file operations are unavailable on this OS")
    candidate = Path(path).expanduser()
    try:
        relative = candidate.relative_to(project) if candidate.is_absolute() else candidate
    except ValueError:
        raise ValueError("Selected file must remain within the selected project") from None
    if not relative.parts or any(part == ".." for part in relative.parts):
        raise ValueError("Selected file must remain within the selected project")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    opened = []
    try:
        directory = os.open(project, flags)
        opened.append(directory)
        for part in relative.parts[:-1]:
            directory = os.open(part, flags, dir_fd=directory)
            opened.append(directory)
        yield directory, relative
    except OSError:
        raise ValueError("Selected file path is missing, linked, or inaccessible") from None
    finally:
        for descriptor in reversed(opened):
            os.close(descriptor)


def _read_regular_at(directory: int, name: str, *, missing_ok: bool = False) -> bytes | None:
    """Read one regular no-follow file with a byte limit enforced after open."""
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise ValueError("Selected file is missing") from None
    except OSError:
        raise ValueError("Selected file is linked or inaccessible") from None
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Selected file must be a regular file")
        if metadata.st_size > MAX_ENV_BYTES:
            raise ValueError("Selected file exceeds the one MiB limit")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            content = stream.read(MAX_ENV_BYTES + 1)
        if len(content) > MAX_ENV_BYTES:
            raise ValueError("Selected file exceeds the one MiB limit")
        return content
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _read_contained(project: Path, path: Path | str) -> tuple[str, bytes]:
    with _anchored_parent(project, path) as (directory, relative):
        return relative.as_posix(), _read_regular_at(directory, relative.name)


def _write_at(directory: int, name: str, content: bytes, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    with os.fdopen(os.open(name, flags, mode, dir_fd=directory), "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def _guarded_replace_at(directory: int, name: str, content: bytes,
                        expected_sha256: str, changed_message: str) -> None:
    temporary = "." + name + ".systemx-" + secrets.token_hex(12)
    try:
        _write_at(directory, temporary, content)
        latest = _read_regular_at(directory, name)
        if hashlib.sha256(latest).hexdigest() != expected_sha256:
            raise ValueError(changed_message)
        os.rename(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


def _catalog(defaults: Path) -> tuple[dict, dict]:
    home = defaults / "SECURITY" / "AGENT1"
    question_path = home / "questions.json"
    bucket_path = home / "event_buckets.json"
    for path in (question_path, bucket_path):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Agent 1 catalog is missing or linked")
    questions = json.loads(question_path.read_text(encoding="utf-8"))
    buckets = json.loads(bucket_path.read_text(encoding="utf-8"))
    categories = questions.get("categories")
    events = buckets.get("buckets")
    if not isinstance(categories, list) or len(categories) != 20:
        raise ValueError("Agent 1 requires exactly 20 questionnaire categories")
    if not isinstance(events, list) or len(events) != 10:
        raise ValueError("Agent 1 requires exactly 10 event buckets")
    seen_ids, seen_text = set(), set()
    for index, category in enumerate(categories, 1):
        if not isinstance(category, dict) or category.get("id") != f"C{index:02d}" or \
                not isinstance(category.get("questions"), list):
            raise ValueError("Agent 1 category IDs or question arrays differ")
        if not isinstance(category.get("title"), str) or not category["title"].strip() or \
                not isinstance(category.get("scope"), str) or not category["scope"].strip() or \
                not isinstance(category.get("profiles"), list) or \
                not category["profiles"] or any(profile not in PROFILES[1:] for profile in category["profiles"]):
            raise ValueError("Agent 1 category title, scope, or profile is invalid")
        if len(category["questions"]) != 20:
            raise ValueError("Every Agent 1 category must contain exactly 20 questions")
        for position, item in enumerate(category["questions"], 1):
            identifier = f"C{index:02d}.Q{position:02d}"
            if not isinstance(item, dict) or item.get("id") != identifier:
                raise ValueError("Agent 1 question IDs must be ordered and unique")
            phrase = item.get("text")
            if not isinstance(phrase, str) or not phrase.endswith("?") or len(phrase) < 20:
                raise ValueError("Agent 1 questions must be substantive questions")
            normalized = " ".join(phrase.casefold().split())
            if identifier in seen_ids or normalized in seen_text:
                raise ValueError("Duplicate Agent 1 question")
            seen_ids.add(identifier)
            seen_text.add(normalized)
    if any(not isinstance(item, dict) for item in events):
        raise ValueError("Agent 1 event buckets must be records")
    event_ids = [item.get("id") for item in events]
    if event_ids != [f"E{index:02d}" for index in range(1, 11)] or \
            any(not isinstance(item.get("title"), str) or not item["title"].strip() or
                not isinstance(item.get("ownershipRule"), str) or not item["ownershipRule"].strip()
                for item in events):
        raise ValueError("Agent 1 event buckets need unique IDs and ownership rules")
    return questions, buckets


def validate_catalog(defaults: Path | str | None = None) -> dict:
    questions, events = _catalog(_defaults(defaults))
    return {"valid": True, "categories": len(questions["categories"]),
            "questions": sum(len(item["questions"]) for item in questions["categories"]),
            "eventBuckets": len(events["buckets"])}


def validate_template(root: Path | str, defaults: Path | str | None = None) -> dict:
    records, _project_root = _project(root)
    if records.name != ".SYSTEMX":
        raise ValueError("Public template validation requires the outer .SYSTEMX scope")
    result = validate_catalog(defaults)
    home = records / "SECURITY" / "AGENT1"
    if home.is_symlink() or not home.is_dir():
        raise ValueError("Public Agent 1 policy directory is missing or linked")
    for item in home.iterdir():
        lowered = item.name.casefold()
        if lowered.startswith(".env") or "answer" in lowered or "config" in lowered:
            raise ValueError("Public Agent 1 policy contains local answers, configuration, or dotenv data")
    return {**result, "publicLocalState": False}


def _env_name(name: str) -> bool:
    if name == ".env":
        return True
    if not name.startswith(".env."):
        return False
    suffix = name[5:].casefold()
    return suffix not in SAMPLE_ENV_SUFFIXES


def _walk_names(project: Path) -> tuple[list[str], list[str], bool]:
    """Inventory bounded filenames only; never open candidate source contents."""
    env_names, dependency_names = [], []
    count = 0
    truncated = False
    for base, dirs, files in os.walk(project, topdown=True, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS and
                         not (Path(base) / name).is_symlink())
        for name in sorted(files):
            count += 1
            if count > MAX_WALK_ENTRIES:
                truncated = True
                break
            path = Path(base) / name
            relative = path.relative_to(project).as_posix()
            if _env_name(name):
                env_names.append(relative)
            if path.is_symlink():
                continue
            if name in {"package.json", "pyproject.toml", "requirements.txt", "Pipfile", "Cargo.toml",
                        "go.mod", "Gemfile", "composer.json", "pom.xml", "build.gradle", "build.gradle.kts"}:
                dependency_names.append(relative)
        if truncated:
            break
    return env_names, dependency_names, truncated


def _tracked_env(project: Path) -> tuple[set[str] | None, str | None]:
    command = ["git", "-C", str(project), "-c", "core.fsmonitor=false", "-c", "core.hooksPath=" + os.devnull,
               "ls-files", "--cached", "-z", "--", ":(glob)**/.env", ":(glob)**/.env.*", ".env", ".env.*"]
    environment = {"PATH": os.environ.get("PATH", ""), "GIT_OPTIONAL_LOCKS": "0",
                   "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    try:
        run = subprocess.run(command, capture_output=True, timeout=10, check=False, env=environment)
    except (OSError, subprocess.TimeoutExpired):
        return None, "Git tracked-file check unavailable"
    if run.returncode != 0 or len(run.stdout) > 1024 * 1024:
        return None, "Git tracked-file check unavailable"
    return {os.fsdecode(item) for item in run.stdout.split(b"\0") if item}, None


def _dependency_warnings(project: Path, names: list[str]) -> list[dict]:
    findings = []
    for relative in names:
        path = project / relative
        if path.name == "package.json" and not any((path.parent / name).is_file() and
                                                  not (path.parent / name).is_symlink() for name in
                                                  ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb")):
            findings.append({"code": "JS_LOCKFILE_NOT_SEEN", "severity": "warning", "path": relative,
                             "message": "No adjacent JavaScript lockfile was found; dependency versions were not verified."})
    return findings


def assess(root: Path | str, defaults: Path | str | None = None, profile: str = "all-in-one") -> dict:
    """Return a sanitized, warning-only local review; no network or writes."""
    if profile not in PROFILES:
        raise ValueError("Unknown Agent 1 profile")
    _records, project = _project(root)
    questions, buckets = _catalog(_defaults(defaults))
    env_names, dependency_names, truncated = _walk_names(project)
    tracked, tracked_error = _tracked_env(project)
    findings = [{"code": "QUESTIONNAIRE_UNASSESSED", "severity": "warning",
                 "message": "The selected evidence questions have not been answered by this filename scan."}]
    findings.extend(_dependency_warnings(project, dependency_names))
    for name in env_names:
        if (project / name).is_symlink():
            code, message = "ENV_LINK", "Dotenv filename is a link; inspect its target and tracking manually."
        elif tracked is None:
            code, message = "ENV_TRACKING_UNKNOWN", "Dotenv filename found; Git tracking could not be determined."
        elif name in tracked:
            code, message = "ENV_TRACKED", "Dotenv filename is tracked by Git; inspect history and rotate exposed values."
        else:
            code, message = "ENV_LOCAL", "Dotenv filename exists locally; review storage and exclusion policy."
        findings.append({"code": code, "severity": "warning", "path": name, "message": message})
    if tracked_error:
        findings.append({"code": "GIT_TRACKING_UNAVAILABLE", "severity": "warning", "message": tracked_error})
    if truncated:
        findings.append({"code": "SCAN_TRUNCATED", "severity": "warning",
                         "message": f"Filename inventory stopped after {MAX_WALK_ENTRIES} entries."})
    selected = [category for category in questions["categories"]
                if profile == "all-in-one" or profile in category.get("profiles", [])]
    return {"agent": "agent.1", "mode": "warning-only", "profile": profile,
            "targetRoot": str(project), "categoriesAvailable": len(questions["categories"]),
            "categoriesSelected": [category["id"] for category in selected],
            "questionsAvailable": 400, "questionsSelected": 20 * len(selected), "questionsAnswered": 0,
            "questionnaireStatus": "not_assessed", "overallVerdict": "insufficient_evidence",
            "eventBuckets": len(buckets["buckets"]), "findings": findings,
            "inventory": {"dotenvFileNames": env_names, "dependencyManifestNames": dependency_names,
                          "truncated": truncated},
            "hostSignals": {"os": platform.system(), "architecture": platform.machine(),
                            "projectReadable": os.access(project, os.R_OK)},
            "limits": ["Filename and local host signal check only; no CVE, cloud, device, or full 400-question assessment.",
                       "No dotenv values, tokens, account names, device identifiers, or provider records were read.",
                       "Findings are warnings; no fix, service, deployment, or policy change was made."]}


def _env_names(content: bytes) -> tuple[list[str], list[str], list[int]]:
    names, duplicates, invalid_lines = [], [], []
    seen = set()
    for number, raw in enumerate(io.BytesIO(content), 1):
        if number > 10000:
            raise ValueError("Dotenv source exceeds the 10,000-line inventory limit")
        try:
            line = raw.decode("utf-8", errors="strict").strip()
        except UnicodeDecodeError:
            raise ValueError(f"Dotenv source has non-UTF-8 data at line {number}") from None
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            invalid_lines.append(number)
            continue
        name, _value = line.split("=", 1)
        name = name.strip()
        if not KEY.fullmatch(name):
            invalid_lines.append(number)
        elif name in seen:
            duplicates.append(name)
        else:
            names.append(name)
            seen.add(name)
    return names, sorted(set(duplicates)), invalid_lines


def env_inventory(root: Path | str, env_file: Path | str) -> dict:
    """Inspect dotenv key names only; values are discarded and never returned."""
    _records, project = _project(root)
    relative, content = _read_contained(project, env_file)
    names, duplicates, invalid_lines = _env_names(content)
    tracked, error = _tracked_env(project)
    return {"source": relative, "names": names, "duplicateNames": duplicates,
            "unsupportedLineNumbers": invalid_lines, "trackedByGit": None if tracked is None else relative in tracked,
            "trackingWarning": error, "valuesReturned": False, "valuesCopied": False,
            "limits": "Only simple KEY=value names are inventoried; no values are logged or uploaded."}


def env_sanitize(root: Path | str, args) -> dict:
    """Create a names-only .env.example, never changing the source .env."""
    _records, project = _project(root)
    with _anchored_parent(project, args.env_file) as (directory, relative):
        if relative.name == ".env.example":
            raise ValueError("Sanitized dotenv destination equals source")
        names, duplicates, invalid_lines = _env_names(_read_regular_at(directory, relative.name))
        if duplicates or invalid_lines:
            raise ValueError("Resolve duplicate names and unsupported dotenv lines before sanitizing")
        destination = relative.parent / ".env.example"
        encoded = ("# Names only. Provide values through an approved runtime store or hidden prompt.\n" +
                   "".join(name + "=\n" for name in names)).encode("utf-8")
        existing = _read_regular_at(directory, ".env.example", missing_ok=True)
        current = hashlib.sha256(existing).hexdigest() if existing is not None else None
        proposed = hashlib.sha256(encoded).hexdigest()
        output = {"mode": "preview", "source": relative.as_posix(),
                  "destination": destination.as_posix(), "names": names,
                  "existingSHA256": current, "proposedSHA256": proposed,
                  "sourcePreserved": True, "providerSet": False, "localStoreWired": False,
                  "rotationStillRequired": True, "valuesReturned": False, "changed": False}
        if not args.apply:
            return output
        if current == proposed:
            return {**output, "mode": "applied", "alreadyCurrent": True}
        if current is not None and not args.replace_existing:
            raise ValueError("Existing .env.example differs; explicit guarded replacement is required")
        if current is not None and (args.expect_sha256 is None or args.expect_sha256 != current):
            raise ValueError("Existing .env.example SHA-256 does not match --expect-sha256")
        if current is None:
            _write_at(directory, ".env.example", encoded, mode=0o644)
        else:
            _guarded_replace_at(directory, ".env.example", encoded, current,
                                "Existing .env.example changed during guarded replacement")
        return {**output, "mode": "applied", "changed": True}


def _setup_config(root: Path | str) -> Path:
    records, _project_root = _project(root)
    if not records.is_dir() or records.is_symlink():
        raise ValueError("Selected .SYSTEMX record directory is missing or linked")
    for part in (records / "local",):
        if part.is_symlink():
            raise ValueError("Agent 1 configuration path is linked")
    return records / "local" / "AGENT1-CONFIG.json"


def _memory():
    """Load the fixed local record helper required by project_memory."""
    if "systemx_paths" not in sys.modules:
        path = Path(__file__).resolve().parents[1] / "systemx_paths.py"
        spec = importlib.util.spec_from_file_location("systemx_paths", path)
        if spec is None or spec.loader is None:
            raise ValueError("Selected defaults lack the record path helper")
        module = importlib.util.module_from_spec(spec)
        sys.modules["systemx_paths"] = module
        spec.loader.exec_module(module)
    import project_memory
    return project_memory


def _registration(records: Path) -> dict:
    memory = _memory()
    try:
        _ledger, registry = memory.load(records)
    except FileNotFoundError:
        return {"registryAvailable": False, "registered": False, "conflict": False}
    matches = [item for item in registry["agents"] if item["id"] == "agent.1"]
    if not matches:
        return {"registryAvailable": True, "registered": False, "conflict": False}
    role = matches[0]["role"]
    return {"registryAvailable": True, "registered": role == "security-access",
            "conflict": role != "security-access"}


def _register_if_needed(records: Path, defaults: Path | str | None) -> dict:
    current = _registration(records)
    if not current["registryAvailable"]:
        raise ValueError("Initialize the selected .SYSTEMX records before Agent 1 setup")
    if current["conflict"]:
        raise ValueError("agent.1 is registered with another role; review before setup")
    if current["registered"]:
        return {**current, "changed": False}
    memory = _memory()
    with redirect_stdout(io.StringIO()):
        memory.add_agent(records, SimpleNamespace(agent_id="agent.1", role="security-access"),
                         _defaults(defaults))
    return {**_registration(records), "changed": True}


def _parse_config(content: bytes) -> dict:
    raw = json.loads(content.decode("utf-8"))
    field_names = {key for key, _question, _choices in SETUP_QUESTIONS}
    fixed = {"schemaVersion": 1, "mode": "warning-only", "profile": "all-in-one",
             "serviceInstalled": False, "networkEnabled": False, "automaticFixes": False}
    if not isinstance(raw, dict) or set(raw) != field_names | set(fixed) or \
            any(raw.get(key) != value for key, value in fixed.items()):
        raise ValueError("Agent 1 configuration is not the warning-only setup record")
    fields = {}
    for key, _question, choices in SETUP_QUESTIONS:
        value = raw.get(key)
        if value is not None and (not isinstance(value, str) or
                                  (choices is not None and value not in choices) or
                                  (key == "repository" and not REPO.fullmatch(value))):
            raise ValueError("Agent 1 configuration contains an invalid setup field")
        fields[key] = value
    return fields | fixed


def _read_config(target: Path) -> dict:
    if _secure_file_ops_available():
        _relative, content = _read_contained(target.parent.parent, "local/AGENT1-CONFIG.json")
    else:
        with target.open("rb") as stream:
            content = stream.read(MAX_ENV_BYTES + 1)
        if len(content) > MAX_ENV_BYTES:
            raise ValueError("Agent 1 configuration exceeds the one MiB limit")
    return _parse_config(content)


def _create_config(records: Path, target: Path, encoded: bytes) -> None:
    if _secure_file_ops_available():
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            root_directory = os.open(records, flags)
            try:
                try:
                    os.mkdir("local", mode=0o700, dir_fd=root_directory)
                except FileExistsError:
                    pass
                local_directory = os.open("local", flags, dir_fd=root_directory)
                try:
                    _write_at(local_directory, target.name, encoded)
                finally:
                    os.close(local_directory)
            finally:
                os.close(root_directory)
        except OSError:
            raise ValueError("Agent 1 configuration path is linked or inaccessible") from None
    else:
        # Metadata-only first-run setup remains available on Windows. Dotenv
        # commands and guarded reconfiguration require the anchored POSIX path.
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.parent.is_symlink():
            raise ValueError("Agent 1 configuration directory is linked")
        with target.open("xb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())


def _setup_values(args) -> dict:
    fields = {"accountContext": args.account_context, "repository": args.repo,
              "reviewScope": args.review_scope, "actorRole": args.actor_role,
              "githubActionsSecretTarget": args.secret_target, "localSecretStore": args.local_secret_store,
              "envTrackedHistoryReviewed": args.env_history_reviewed, "envRotationDecision": args.rotation_decision}
    if fields["repository"] is not None and not REPO.fullmatch(fields["repository"]):
        raise ValueError("Repository must be exact OWNER/REPO")
    return fields


def setup(root: Path | str, defaults: Path | str | None, args) -> dict:
    target = _setup_config(root)
    records, _project_root = _project(root)
    registration = _registration(records)
    if registration["conflict"]:
        raise ValueError("agent.1 is registered with another role; review before setup")
    if target.is_symlink():
        raise ValueError("Agent 1 configuration is linked")
    fields = _setup_values(args)
    provided = any(value is not None for value in fields.values())
    if target.exists():
        if provided:
            _relative, existing_bytes = _read_contained(records, "local/AGENT1-CONFIG.json")
            stored = _parse_config(existing_bytes)
        else:
            stored = _read_config(target)
        if not provided:
            if args.replace_existing or args.expect_sha256:
                raise ValueError("Provide all setup answers to preview guarded reconfiguration")
            if args.apply and not registration["registered"]:
                registration = _register_if_needed(records, defaults)
            return {"configured": True, "config": stored, "changed": False,
                    "registration": registration,
                    "missingQuestions": [label for key, label, _choices in SETUP_QUESTIONS if stored.get(key) is None]}
        missing = [label for key, label, _choices in SETUP_QUESTIONS if fields[key] is None]
        proposed = {**stored, **fields}
        existing_sha256 = hashlib.sha256(existing_bytes).hexdigest()
        preview = {"configured": True, "config": stored, "proposed": proposed,
                   "existingSHA256": existing_sha256, "changed": False,
                   "registration": registration, "missingQuestions": missing,
                   "applyRequired": proposed != stored}
        if not args.apply:
            return preview
        if missing:
            raise ValueError("Answer all first-run questions before applying setup")
        if proposed == stored:
            return preview
        if not args.replace_existing:
            raise ValueError("Existing Agent 1 configuration requires guarded replacement")
        if args.expect_sha256 != existing_sha256:
            raise ValueError("Existing Agent 1 configuration SHA-256 does not match --expect-sha256")
        if not registration["registered"]:
            registration = _register_if_needed(records, defaults)
        encoded = (json.dumps(proposed, indent=2) + "\n").encode("utf-8")
        with _anchored_parent(records, "local/AGENT1-CONFIG.json") as (directory, relative):
            _guarded_replace_at(directory, relative.name, encoded, existing_sha256,
                                "Existing Agent 1 configuration changed during guarded replacement")
        return {**preview, "config": proposed, "changed": True, "registration": registration,
                "applyRequired": False}
    missing = [label for key, label, _choices in SETUP_QUESTIONS if fields[key] is None]
    proposed = {"schemaVersion": 1, "mode": "warning-only", "profile": "all-in-one",
                "serviceInstalled": False, "networkEnabled": False, "automaticFixes": False, **fields}
    if not args.apply:
        return {"configured": False, "preview": proposed, "changed": False,
                "missingQuestions": missing, "registration": registration,
                "registrationPlanned": not registration["registered"], "applyRequired": True}
    if missing:
        raise ValueError("Answer all first-run questions before applying setup")
    if args.replace_existing or args.expect_sha256:
        raise ValueError("No existing Agent 1 configuration needs guarded replacement")
    if not registration["registryAvailable"]:
        raise ValueError("Initialize the selected .SYSTEMX records before Agent 1 setup")
    registration = _register_if_needed(records, defaults)
    _create_config(records, target, (json.dumps(proposed, indent=2) + "\n").encode("utf-8"))
    return {"configured": True, "config": proposed, "changed": True,
            "missingQuestions": missing, "registration": registration, "serviceInstalled": False}


def questions(defaults: Path | str | None = None, profile: str = "all-in-one",
              category_id: str | None = None) -> dict:
    if profile not in PROFILES:
        raise ValueError("Unknown Agent 1 profile")
    catalog, _buckets = _catalog(_defaults(defaults))
    selected = [item for item in catalog["categories"] if
                (profile == "all-in-one" or profile in item.get("profiles", [])) and
                (category_id is None or item["id"] == category_id)]
    if category_id is not None and not selected:
        raise ValueError("Unknown or inapplicable Agent 1 category")
    return {"profile": profile, "categoryCount": len(selected),
            "questionCount": 20 * len(selected), "categories": selected,
            "limit": "Questions request evidence; this command does not evaluate controls."}


def review_answers(root: Path | str, defaults: Path | str | None, answers_file: Path | str,
                   profile: str = "all-in-one") -> dict:
    """Validate a complete answer matrix without opening evidence paths or changing policy."""
    _records, project = _project(root)
    _relative, content = _read_contained(project, answers_file)
    selected = questions(defaults, profile)
    expected = {question["id"] for category in selected["categories"] for question in category["questions"]}

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Review answer file has duplicate JSON fields")
            result[key] = value
        return result

    record = json.loads(content.decode("utf-8"), object_pairs_hook=unique)
    answers = record.get("answers") if isinstance(record, dict) else None
    if not isinstance(answers, list) or len(answers) != len(expected):
        raise ValueError("Review must provide exactly one answer per selected question")
    counts = {name: 0 for name in ("pass", "fail", "unknown", "na")}
    seen = set()
    flagged = []
    for item in answers:
        if not isinstance(item, dict) or set(item) != {"id", "result", "evidence"}:
            raise ValueError("Review answer must contain only id, result, and evidence")
        identifier, result, evidence = item["id"], item["result"], item["evidence"]
        if not isinstance(identifier, str) or not isinstance(result, str) or \
                identifier not in expected or identifier in seen or result not in counts:
            raise ValueError("Review answer ID or result is invalid or repeated")
        if not isinstance(evidence, list) or len(evidence) > 10 or any(
                not isinstance(ref, str) or len(ref) > 300 or not ref or
                Path(ref).is_absolute() or ".." in Path(ref).parts or
                any(ord(char) < 32 for char in ref) for ref in evidence):
            raise ValueError("Review evidence must use short contained relative references")
        if result != "unknown" and not evidence:
            raise ValueError("Pass, fail, and N/A answers require an evidence reference")
        counts[result] += 1
        seen.add(identifier)
        if result in {"fail", "unknown"}:
            flagged.append(identifier)
    if seen != expected:
        raise ValueError("Review answer IDs do not cover the selected questions")
    return {"agent": "agent.1", "mode": "warning-only", "profile": profile,
            "questionsSelected": len(expected), "questionsAnswered": len(answers),
            "counts": counts, "flaggedQuestionIDs": flagged[:25], "flaggedTotal": len(flagged),
            "overallVerdict": "requires_review" if flagged else "evidence_recorded",
            "evidenceAuthenticity": "not_verified", "automaticFixes": False,
            "limit": "Answer syntax and coverage checked only; references were not opened or authenticated."}


def status(root: Path | str) -> dict:
    target = _setup_config(root)
    records, _project_root = _project(root)
    registration = _registration(records)
    if target.is_symlink():
        raise ValueError("Agent 1 configuration is linked")
    if not target.is_file():
        return {"configured": False, "mode": "warning-only", "profile": "all-in-one",
                "registration": registration,
                "missingQuestions": [label for _key, label, _choices in SETUP_QUESTIONS]}
    stored = _read_config(target)
    return {"configured": True, "config": stored, "registration": registration,
            "missingQuestions": [label for key, label, _choices in SETUP_QUESTIONS if stored.get(key) is None]}


def _require_repository_admin(repo: str) -> None:
    """Fail closed when gh cannot prove this account can administer the target repo."""
    try:
        permission = subprocess.run(["gh", "api", f"repos/{repo}", "--jq", ".permissions.admin"],
                                    capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("GitHub repository admin capability could not be verified; no secret was sent") from None
    if permission.returncode != 0 or permission.stdout.strip() != "true":
        raise ValueError("GitHub repository admin capability could not be verified; no secret was sent")


def _secret_metadata_readback(repo: str, environment: str | None, name: str) -> str:
    """Read only names in the chosen Actions scope after a successful set command."""
    command = ["gh", "secret", "list", "--app", "actions", "--repo", repo]
    if environment:
        command += ["--env", environment]
    command += ["--json", "name"]
    try:
        listed = subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
        if listed.returncode != 0 or len(listed.stdout) > MAX_ENV_BYTES:
            return "unknown"
        records = json.loads(listed.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return "unknown"
    if not isinstance(records, list):
        return "unknown"
    return "verified" if any(isinstance(item, dict) and item.get("name") == name
                             for item in records) else "unknown"


def env_migration(root: Path | str, args) -> dict:
    inventory = env_inventory(root, args.env_file)
    if not REPO.fullmatch(args.repo):
        raise ValueError("GitHub target must be exact OWNER/REPO")
    if args.environment and not re.fullmatch(r"[A-Za-z0-9_.-]+", args.environment):
        raise ValueError("GitHub environment name has unsupported characters")
    if args.credential_class == "existing-test" and not args.ack_test_only:
        raise ValueError("Existing credential reuse requires --ack-test-only")
    target = {"repository": args.repo, "kind": "environment" if args.environment else "repository",
              "environment": args.environment, "application": "actions"}
    preview = {"mode": "preview", "source": inventory["source"], "names": inventory["names"],
               "target": target, "trackedByGit": inventory["trackedByGit"],
               "unsupportedLineNumbers": inventory["unsupportedLineNumbers"],
               "migrationMethod": "Per-secret hidden terminal input; source file is never uploaded or deleted.",
               "credentialClass": args.credential_class,
               "testOnly": args.credential_class == "existing-test",
               "historicalValuesRotated": False, "secretSet": False}
    if not args.apply:
        return preview
    setup_state = status(root)
    if not setup_state["configured"] or not setup_state["registration"]["registered"]:
        raise ValueError("Complete Agent 1 setup and registration before GitHub secret setup")
    configured = setup_state["config"]
    if configured["repository"] != args.repo or configured["githubActionsSecretTarget"] != target["kind"]:
        raise ValueError("GitHub target differs from first-run setup")
    if not args.name or args.name not in inventory["names"]:
        raise ValueError("Select exactly one inventoried dotenv name with --name")
    if inventory["duplicateNames"] or inventory["unsupportedLineNumbers"]:
        raise ValueError("Resolve duplicate names and unsupported dotenv lines before secret setup")
    if not (sys.stdin.isatty() and sys.stderr.isatty()):
        raise ValueError("Secret setup requires an interactive terminal with hidden input")
    if shutil.which("gh") is None:
        raise ValueError("GitHub CLI is required for interactive secret setup")
    try:
        account = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True,
                                 text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("GitHub CLI account check failed; no secret was sent") from None
    if account.returncode != 0 or not account.stdout.strip():
        raise ValueError("GitHub CLI account check failed; no secret was sent")
    _require_repository_admin(args.repo)
    display_target = f"{args.repo} / environment {args.environment}" if args.environment else \
                     f"{args.repo} / repository"
    print(f"GitHub account: {account.stdout.strip()} | target: {display_target} | secret: {args.name}",
          file=sys.stderr)
    value = getpass.getpass("Enter the " + ("existing test" if args.credential_class == "existing-test" else "new") +
                            " value to send (input hidden; not read from .env): ")
    if not value:
        raise ValueError("Empty secret value refused")
    command = ["gh", "secret", "set", args.name, "--app", "actions", "--repo", args.repo]
    if args.environment:
        command += ["--env", args.environment]
    try:
        result = subprocess.run(command, input=value, text=True, capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("GitHub CLI secret setup outcome is unknown; inspect target manually") from None
    finally:
        del value
    if result.returncode != 0:
        raise ValueError("GitHub CLI secret setup failed; inspect target manually")
    metadata_state = _secret_metadata_readback(args.repo, args.environment, args.name)
    return {**preview, "mode": "applied", "name": args.name, "secretSet": True,
            "providerAdminVerified": True,
            "metadataReadback": {"state": metadata_state, "scope": target["kind"], "name": args.name},
            "valueLogged": False, "valueVerified": False, "sourceDeleted": False,
            "limit": "GitHub accepted the set command; only name/scope metadata may be verified. "
                     "Provider-side use and historical rotation are unverified."}


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("agent-1", help="warning-only security and access review")
    actions = parent.add_subparsers(dest="security_action", required=True)
    scope(actions.add_parser("status", help="show local setup state"))
    command = scope(actions.add_parser("setup", help="preview or apply warning-only local setup"))
    command.add_argument("--apply", action="store_true")
    command.add_argument("--replace-existing", action="store_true")
    command.add_argument("--expect-sha256")
    command.add_argument("--account-context", choices=("personal", "enterprise"))
    command.add_argument("--repo")
    command.add_argument("--review-scope", choices=("root", "project"))
    command.add_argument("--actor-role", choices=("owner", "operator", "guest"))
    command.add_argument("--secret-target", choices=("repository", "environment", "none"))
    command.add_argument("--local-secret-store", choices=("macos-keychain", "windows-credential-manager",
                                                  "linux-secret-service", "none"))
    command.add_argument("--env-history-reviewed", choices=("yes", "no"))
    command.add_argument("--rotation-decision", choices=("rotated", "needed", "not-applicable"))
    command = scope(actions.add_parser("check", help="bounded read-only local check"))
    command.add_argument("--profile", choices=PROFILES, default="all-in-one")
    command = scope(actions.add_parser("questions", help="show fixed evidence questions"))
    command.add_argument("--profile", choices=PROFILES, default="all-in-one")
    command.add_argument("--category")
    command = scope(actions.add_parser("review", help="validate complete answer coverage; warning-only"))
    command.add_argument("--answers", required=True)
    command.add_argument("--profile", choices=PROFILES, default="all-in-one")
    command = scope(actions.add_parser("env-inventory", help="list dotenv key names without values"))
    command.add_argument("--env-file", required=True)
    command = scope(actions.add_parser("env-sanitize", help="preview or create names-only .env.example"))
    command.add_argument("--env-file", required=True)
    command.add_argument("--apply", action="store_true")
    command.add_argument("--replace-existing", action="store_true")
    command.add_argument("--expect-sha256")
    command = scope(actions.add_parser("env-migrate", help="preview or set one Actions secret from hidden input"))
    command.add_argument("--env-file", required=True)
    command.add_argument("--repo", required=True)
    command.add_argument("--environment")
    command.add_argument("--name")
    command.add_argument("--apply", action="store_true")
    command.add_argument("--credential-class", choices=("new", "existing-test"), default="new")
    command.add_argument("--ack-test-only", action="store_true")


def dispatch(root, defaults, args):
    action = args.security_action
    if action == "status":
        return status(root)
    if action == "setup":
        return setup(root, defaults, args)
    if action == "check":
        return assess(root, defaults, args.profile)
    if action == "questions":
        return questions(defaults, args.profile, args.category)
    if action == "review":
        return review_answers(root, defaults, args.answers, args.profile)
    if action == "env-inventory":
        return env_inventory(root, args.env_file)
    if action == "env-sanitize":
        return env_sanitize(root, args)
    if action == "env-migrate":
        return env_migration(root, args)
    raise ValueError("Unknown Agent 1 action")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    add_cli(parser.add_subparsers(dest="action", required=True))
    arguments = parser.parse_args(argv)
    try:
        result = dispatch(arguments.root, _defaults(None), arguments)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        # Error text is deliberately limited to our own fixed messages.
        print("Agent 1: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
