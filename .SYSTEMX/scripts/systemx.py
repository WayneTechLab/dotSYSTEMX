#!/usr/bin/env python3
"""Standalone SYSTEMX tools. Python standard library only; no shell evaluation."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

# Inspection commands must not create bytecode files in a copied distribution.
if __name__ == "__main__":
    sys.dont_write_bytecode = True
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
import project_memory

DEFAULTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEFAULTS))
from systemx_paths import inspect_layout, lowercase_alias, record_directory

SYSTEMX = DEFAULTS
PROJECT_ROOT = SYSTEMX.parent
REQUIRED = (
    ".gitignore", ".gitattributes", "README.md", "STANDARD.md", "LICENSE", "VERSION",
    "CHANGELOG.md", "SOURCE.json", "SYSTEMX.sh", "WSG-MENU.sh",
    "config/project.example.json", "docs/SETUP.md", "docs/DEVELOPMENT.md",
    "docs/SECURITY.md", "docs/QUALITY.md", "docs/OPERATIONS.md",
    "AI/README.md", "AI/AGENT-MESH-STANDARD.md", "AI/agent-mesh.schema.json",
    "AI/TOOLCALLING-AND-BROWSER-AUTOMATION.md",
    "AI/EXTERNAL-SERVICE-CONNECTOR-STANDARD.md", "AI/RECOVERY-PLAYBOOK.md",
    "templates/PROJECT-BRIEF.md", "templates/ARCHITECTURE.md",
    "templates/DECISION.md", "templates/TASK.md", "templates/HANDOFF.md",
    "templates/RELEASE.md", "scripts/systemx.py", "scripts/validate.sh",
    "scripts/quality-check.sh", "tests/test_systemx.py",
    "FORMAT.md", "config/template-records.json",
    "__init__.py", "__main__.py", "manager.py", "INSTALL.sh", "INSTALL.ps1", "SYSTEMX.ps1",
    "config/distribution.json", "config/profiles.json", "scripts/release.py", "tests/test_manager.py",
    "profiles/project.md", "profiles/directory.md", "profiles/drive.md", "profiles/chat.md",
    "docs/INSTALLATION.md", "docs/LIBRARY.md", "docs/EXACT-CASE.md", "systemx_paths.py", "tests/test_paths.py",
) + project_memory.REQUIRED
BLANK_RECORDS = (
    "GLOBAL/CONTEXT.md", "PLAN/MASTER-PLAN.md", "MEMORY/PROJECT.md",
    "AGENTS/agent.0/MEMORY.md", "AGENTS/REGISTRY.json", "WORK/TASKS.json",
    "WORK/FOCUS.json", "config/project.example.json",
)
IGNORED_DIRS = {"local", "logs", "state", ".git", ".systemx", "__pycache__", "node_modules"}
LINK = re.compile(r"\]\((?:<([^>]+)>|([^\s)]+))(?:\s+\"[^\"]*\")?\)")


class ConfigError(Exception):
    """A readable, actionable configuration or template error."""


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ConfigError("Cannot read {}: {}".format(path.name, error)) from error


def exact_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ConfigError("{} must contain exactly: {}".format(label, ", ".join(expected)))


def command_array(value, label, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ConfigError("{} must be {}argument array".format(
            label, "an " if allow_empty else "a nonempty "))
    if any(not isinstance(item, str) or not item.strip() or "\x00" in item for item in value):
        raise ConfigError("{} must contain nonempty strings without NUL characters".format(label))


def validate_config(config):
    exact_keys(config, ("schemaVersion", "project", "checks", "commands"), "config")
    if type(config["schemaVersion"]) is not int or config["schemaVersion"] != 1:
        raise ConfigError("schemaVersion must be the integer 1")
    exact_keys(config["project"], ("name", "description"), "project")
    if any(not isinstance(value, str) for value in config["project"].values()):
        raise ConfigError("project name and description must be strings")
    exact_keys(config["commands"], ("dev", "build", "deploy"), "commands")
    for name, command in config["commands"].items():
        command_array(command, "commands." + name, allow_empty=True)
    if not isinstance(config["checks"], list):
        raise ConfigError("checks must be an array")
    names = set()
    for check in config["checks"]:
        exact_keys(check, ("name", "command"), "each check")
        name = check["name"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ConfigError("Each check needs a nonempty, unique name")
        names.add(name)
        command_array(check["command"], "check " + name)
    return config


def load_config():
    path = SYSTEMX / "project.json"
    if path.is_symlink():
        raise ConfigError("project.json must be a regular project file, not a symlink")
    if not path.is_file():
        raise ConfigError("No project.json. Run 'init', then configure the project commands.")
    return validate_config(read_json(path))


def template_files(include_runtime=False):
    for directory, dirs, files in os.walk(SYSTEMX, followlinks=False):
        dirs[:] = sorted(name for name in dirs if include_runtime or name not in IGNORED_DIRS)
        for name in dirs + sorted(files):
            path = Path(directory) / name
            if path.is_symlink():
                raise ConfigError("Symlinks are not supported in template files: " + str(path.relative_to(SYSTEMX)))
        for name in sorted(files):
            yield Path(directory) / name


def distribution_issues(files):
    issues = []
    extra = {path.relative_to(SYSTEMX).as_posix() for path in files} - set(REQUIRED)
    if extra:
        issues.append("Public template contains extra files: " + ", ".join(sorted(extra)))
    try:
        manifest = read_json(SYSTEMX / "config/template-records.json")
        exact_keys(manifest, ("schemaVersion", "sha256"), "Blank-record manifest")
        if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
            raise ConfigError("Blank-record schemaVersion must be the integer 1")
        exact_keys(manifest["sha256"], BLANK_RECORDS, "Blank-record hashes")
        for relative, expected in manifest["sha256"].items():
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ConfigError("Invalid blank-record SHA-256 for " + relative)
            path = project_memory.managed(SYSTEMX, relative)
            # Universal-newline text reading makes Git CRLF checkouts equivalent.
            digest = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            if digest != expected:
                issues.append("Public template record differs from its reviewed blank seed: " + relative)
        ledger, registry = project_memory.load(SYSTEMX)
        focus = project_memory.load_focus(SYSTEMX, ledger)
        config = read_json(SYSTEMX / "config/project.example.json")
        if ledger["tasks"] or focus["objective"] or registry["agents"] != [
                {"id": "agent.0", "role": "coordinator", "memory": "AGENTS/agent.0/MEMORY.md"}]:
            issues.append("Public template must have empty work/focus and only the agent.0 role")
        if (any(config["project"].values()) or config["checks"] or any(config["commands"].values())):
            issues.append("Public template command configuration must be empty")
        sys.path.insert(0, str(DEFAULTS))
        import manager
        manager.read_bundle(SYSTEMX)
    except (ConfigError, OSError, ValueError) as error:
        issues.append("Public template: " + str(error))
    return issues


def validate_template(distribution=False):
    issues = []
    for name in REQUIRED:
        if not (SYSTEMX / name).is_file():
            issues.append("Missing required file: " + name)
    version_path = SYSTEMX / "VERSION"
    if version_path.is_file() and not re.fullmatch(r"\d+\.\d+\.\d+", version_path.read_text().strip()):
        issues.append("VERSION must contain a three-part numeric template version")
    try:
        files = list(template_files(include_runtime=distribution))
    except ConfigError as error:
        issues.append(str(error))
        files = []
    markdown_count = 0
    for path in files:
        relative = path.relative_to(SYSTEMX).as_posix()
        if path.suffix == ".json":
            try:
                data = read_json(path)
                if relative in {"project.json", "config/project.example.json"}:
                    validate_config(data)
                if relative == "SOURCE.json" and version_path.is_file():
                    if not isinstance(data, dict) or data.get("templateVersion") != version_path.read_text().strip():
                        raise ConfigError("SOURCE.json templateVersion must match VERSION")
            except ConfigError as error:
                issues.append(relative + ": " + str(error))
        if path.suffix.lower() != ".md":
            continue
        markdown_count += 1
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            issues.append(relative + ": " + str(error))
            continue
        # Only inline local file links are checked, not URLs or heading anchors.
        content = re.sub(r"^```.*?^```[^\n]*$", "", content, flags=re.M | re.S)
        for match in LINK.finditer(content):
            target = match.group(1) or match.group(2)
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            local_path = unquote(parts.path)
            resolved = (path.parent / local_path).resolve()
            if not resolved.is_relative_to(PROJECT_ROOT) or not resolved.exists():
                issues.append(relative + ": broken or out-of-project link: " + target)
    try:
        project_memory.validate_work(SYSTEMX)
    except (OSError, ValueError) as error:
        issues.append("Project coordination: " + str(error))
    if distribution and not issues:
        issues.extend(distribution_issues(files))
    if issues:
        raise ConfigError("Template validation failed:\n- " + "\n- ".join(issues))
    print("SYSTEMX {} valid: {} files, {} Markdown documents checked.".format(
        "public template" if distribution else "structure", len(files), markdown_count), flush=True)
    return 0


def init_project():
    destination = SYSTEMX / "project.json"
    if destination.exists() or destination.is_symlink():
        raise ConfigError("project.json already exists; it was not changed.")
    config = validate_config(read_json(DEFAULTS / "config/project.example.json"))
    try:
        with destination.open("x", encoding="utf-8") as output:
            output.write(json.dumps(config, indent=2) + "\n")
    except FileExistsError as error:
        raise ConfigError("project.json already exists; it was not changed.") from error
    print("Created .SYSTEMX/project.json. Fill in project context and commands before running checks.")
    return 0


def executable_available(command):
    executable = command[0]
    if "/" in executable or "\\" in executable:
        target = PROJECT_ROOT / executable
        return target.is_file() and os.access(target, os.X_OK)
    # Resolve relative PATH entries from the same working directory used at run time.
    search_path = os.pathsep.join(str(PROJECT_ROOT / entry) for entry in os.get_exec_path())
    return shutil.which(executable, path=search_path) is not None


def doctor():
    print(".SYSTEMX root (canonical exact case): {}".format(SYSTEMX))
    print("Lowercase path: " + inspect_layout(PROJECT_ROOT, required=True)["aliasStatus"])
    print("Project root: {}".format(PROJECT_ROOT))
    print("Python: {}.{}.{}".format(*sys.version_info[:3]))
    if shutil.which("git"):
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=PROJECT_ROOT,
                                text=True, capture_output=True)
        if result.returncode == 0 and Path(result.stdout.strip()).resolve() == PROJECT_ROOT:
            status = subprocess.run(["git", "status", "--short", "--untracked-files=all"],
                                    cwd=PROJECT_ROOT, text=True, capture_output=True)
            branch = subprocess.run(["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
                                    cwd=PROJECT_ROOT, text=True, capture_output=True)
            print("Git branch: " + (branch.stdout.strip() or "detached HEAD"))
            if status.returncode == 0:
                print("Git changed/untracked entries: {} (ignored files excluded)".format(
                    len(status.stdout.splitlines())))
            else:
                print("Git status unavailable")
        else:
            print("Git: project root is not the root of a Git working tree")
    else:
        print("Git: not installed (optional for template use)")
    if not (SYSTEMX / "project.json").exists() and not (SYSTEMX / "project.json").is_symlink():
        print("Project config: not initialized; run 'init' when adopting the template.")
        return 0
    config = load_config()
    print("Project: " + (config["project"]["name"] or "not named"))
    print("Configured checks: {}".format(len(config["checks"])))
    commands = [("check:" + check["name"], check["command"]) for check in config["checks"]]
    commands += list(config["commands"].items())
    missing = False
    for name, command in commands:
        available = bool(command) and executable_available(command)
        print("{}: {}".format(name, "unconfigured" if not command else (
            "executable available" if available else "executable missing")))
        missing = missing or (bool(command) and not available)
    print("Diagnostics only; authentication, project behavior, and service health were not checked.")
    return 2 if missing else 0


def command_plan(action, config):
    plan = []
    if action != "dev":
        if not config["checks"]:
            raise ConfigError("No project checks configured. Add real checks to project.json.")
        plan.extend(("check:" + check["name"], check["command"]) for check in config["checks"])
    if action in {"build", "deploy"}:
        if not config["commands"]["build"]:
            raise ConfigError("Build command is unconfigured.")
        plan.append(("build", config["commands"]["build"]))
    if action in {"dev", "deploy"}:
        if not config["commands"][action]:
            raise ConfigError(action.capitalize() + " command is unconfigured.")
        plan.append((action, config["commands"][action]))
    return plan


def run_action(action, dry_run=False):
    validate_template()
    plan = command_plan(action, load_config())
    print("Working directory: " + str(PROJECT_ROOT), flush=True)
    for label, command in plan:
        print("{}: {}".format(label, shlex.join(command)), flush=True)
    if dry_run:
        print("Dry run: no project commands executed.", flush=True)
        return 0
    # Check the entire plan before executing any commands.
    for label, command in plan:
        if not executable_available(command):
            raise ConfigError("Executable unavailable for {}: {}".format(label, command[0]))
    for label, command in plan:
        print("Running " + label, flush=True)
        result = subprocess.run(command, cwd=PROJECT_ROOT, shell=False)
        if result.returncode:
            print("Stopped: {} failed (exit {}).".format(label, result.returncode), file=sys.stderr)
            return result.returncode if result.returncode > 0 else 128 - result.returncode
    print("Configured {} plan completed.".format(action), flush=True)
    return 0


def menu():
    choices = {"1": ("validate", False), "2": ("doctor", False), "3": ("init", False),
               "4": ("check", False), "5": ("dev", False), "6": ("build", False),
               "7": ("deploy", True), "8": ("deploy", False),
               "9": ("status", False), "10": ("context", False),
               "11": ("paths", False), "12": ("alias-create", False)}
    while True:
        print("\n.SYSTEMX\n1) Validate template\n2) Doctor\n3) Initialize config\n"
              "4) Project checks\n5) Development\n6) Build\n7) Preview deploy plan\n8) Deploy\n"
              "9) Project work status\n10) Agent 0 resume context\n"
              "11) Check exact .SYSTEMX casing and alias\n12) Enable local .systemx -> .SYSTEMX alias\n0) Exit")
        try:
            choice = input("Choice: ").strip()
        except EOFError:
            return 0
        if choice.lower() in {"0", "q", "quit", "exit"}:
            return 0
        if choice not in choices:
            print("Choose a listed option.")
            continue
        action, dry_run = choices[choice]
        try:
            if action == "deploy" and not dry_run:
                run_action("deploy", dry_run=True)
                if input("Type DEPLOY to execute this configured plan: ") != "DEPLOY":
                    print("Deployment cancelled.")
                    continue
            result = dispatch(action, dry_run)
            if result:
                print("Action exited with status {}.".format(result))
        except EOFError:
            return 0
        except (ConfigError, OSError, ValueError) as error:
            print("SYSTEMX: " + str(error), file=sys.stderr)


def dispatch(action, dry_run=False):
    record_directory(SYSTEMX)
    if action in {"paths", "alias-create"}:
        print(json.dumps(lowercase_alias(PROJECT_ROOT, create=action == "alias-create"), indent=2))
        return 0
    if action == "validate":
        return validate_template()
    if action == "doctor":
        return doctor()
    if action == "init":
        return init_project()
    if action == "menu":
        return menu()
    if action == "status":
        return project_memory.status(SYSTEMX)
    if action == "context":
        return project_memory.context(SYSTEMX, "agent.0")
    return run_action(action, dry_run)


def main(argv=None):
    global SYSTEMX, PROJECT_ROOT
    parser = argparse.ArgumentParser(description="Standalone .SYSTEMX project operations (exact-case directory)")
    parser.add_argument("--root", type=Path, help="project record directory when running versioned defaults")
    subparsers = parser.add_subparsers(dest="action")
    for action in ("validate", "doctor", "init", "menu", "help", "paths"):
        command_parser = subparsers.add_parser(action)
        if action == "validate":
            command_parser.add_argument("--template", action="store_true",
                                        help="require only distribution files and reviewed blank project records")
    command_parser = subparsers.add_parser("alias", help="inspect the local lowercase compatibility alias")
    command_parser.add_argument("--create", action="store_true", help="create a relative link if this filesystem needs one")
    for action in ("check", "dev", "build", "deploy"):
        command_parser = subparsers.add_parser(action)
        command_parser.add_argument("--dry-run", action="store_true", help="print plan without executing commands")
    project_memory.add_cli(subparsers)
    args = parser.parse_args(argv)
    if args.action == "help":
        parser.print_help()
        return 0
    try:
        SYSTEMX = record_directory(args.root if args.root is not None else DEFAULTS)
        PROJECT_ROOT = SYSTEMX.parent
        if args.action == "alias":
            return dispatch("alias-create" if args.create else "paths")
        if args.action in {"context", "task-packet"} and SYSTEMX != DEFAULTS:
            print("Selected defaults: " + str(DEFAULTS))
            print("Read STANDARD.md and START-HERE.md from these defaults; read project records from " + str(SYSTEMX))
            print("Retained root guidance may be older or customized; reconcile it with the selected defaults and applicable instructions.")
        if args.action == "validate":
            if args.template and inspect_layout(PROJECT_ROOT)["aliasStatus"] == "linked":
                raise ConfigError("A public template must not include the local sibling .systemx alias")
            return validate_template(args.template)
        if args.action in project_memory.COMMANDS:
            return project_memory.dispatch(SYSTEMX, args, DEFAULTS)
        return dispatch(args.action or "menu", getattr(args, "dry_run", False))
    except (ConfigError, OSError, ValueError) as error:
        print("SYSTEMX: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nSYSTEMX: interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        sys.exit("SYSTEMX requires Python 3.9 or newer.")
    sys.exit(main())
